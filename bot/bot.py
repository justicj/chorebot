import logging
import os
from datetime import datetime

import discord
import pytz
from discord import app_commands
from discord.ext import commands, tasks

import chore_manager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("JusticeChoreBot")

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------
TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])
REMINDER_CHANNEL_ID = int(os.environ["DISCORD_REMINDER_CHANNEL_ID"])
PARENT_ROLE_NAME = os.environ.get("PARENT_ROLE_NAME", "Parents")

PACIFIC = pytz.timezone("America/Los_Angeles")

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.members = (
    True  # Required to read roles for the parent permission check
)


class ChoreBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        # Copy globally-registered slash commands to the guild for instant sync
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        sunday_reminder.start()
        logger.info(
            "Command tree synced to guild %s. Sunday reminder task started.",
            GUILD_ID,
        )


bot = ChoreBot()


# ---------------------------------------------------------------------------
# Helper: build a Discord embed for one kid's chores
# ---------------------------------------------------------------------------
def build_kid_embed(kid_name: str, chores: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"🧹 {kid_name}'s Chores",
        color=discord.Color.blue(),
    )
    for chore in chores.get("daily", []):
        actions = "\n".join(f"• {a}" for a in chore.get("actions", []))
        embed.add_field(
            name=f"📅 {chore['name']}",
            value=actions or "No actions listed.",
            inline=False,
        )
    for chore in chores.get("sunday", []):
        actions = "\n".join(f"• {a}" for a in chore.get("actions", []))
        embed.add_field(
            name=f"🗓️ Sunday: {chore['name']}",
            value=actions or "No actions listed.",
            inline=False,
        )
    return embed


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------
@bot.tree.command(
    name="mychores", description="Show your currently assigned chores"
)
async def mychores(interaction: discord.Interaction):
    kid_name = chore_manager.get_kid_by_discord_id(str(interaction.user.id))
    if not kid_name:
        await interaction.response.send_message(
            "Your Discord account isn't linked to any chore assignments. "
            "Ask a parent to add your Discord ID to chores.yaml.",
            ephemeral=True,
        )
        return
    chores = chore_manager.get_chores_for_kid(kid_name)
    embed = build_kid_embed(kid_name, chores)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="allchores", description="Show all chores and who is assigned to them"
)
async def allchores(interaction: discord.Interaction):
    all_chores = chore_manager.get_all_chores()
    embeds = [
        build_kid_embed(kid, chores) for kid, chores in all_chores.items()
    ]
    await interaction.response.send_message(embeds=embeds)


@bot.tree.command(
    name="rotatechores",
    description="Manually rotate chore assignments forward by one week (Parents only)",
)
async def rotatechores(interaction: discord.Interaction):
    if not any(
        role.name == PARENT_ROLE_NAME for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            f"You need the **{PARENT_ROLE_NAME}** role to use this command.",
            ephemeral=True,
        )
        return

    chore_manager.rotate_chores()
    all_chores = chore_manager.get_all_chores()
    embeds = [
        build_kid_embed(kid, chores) for kid, chores in all_chores.items()
    ]
    await interaction.response.send_message(
        content="✅ Chores have been rotated one week forward! New assignments:",
        embeds=embeds,
    )
    logger.info(
        "Manual rotation triggered by %s (%s)",
        interaction.user.name,
        interaction.user.id,
    )


# ---------------------------------------------------------------------------
# Scheduled Sunday 8 AM Pacific reminder
# ---------------------------------------------------------------------------
@tasks.loop(hours=1)
async def sunday_reminder():
    now = datetime.now(PACIFIC)

    # Only fire on Sunday at 08:00 Pacific (loop runs hourly, so hour check is sufficient)
    if now.weekday() != 6 or now.hour != 8:
        return

    # Guard against double-firing if bot restarts within the same minute
    today_str = now.strftime("%Y-%m-%d")
    history = chore_manager.load_history()
    if history.get("last_reminded") == today_str:
        return

    # Rotate to the new week's assignments
    chore_manager.rotate_chores()

    # Stamp last_reminded so we don't re-fire this week
    history = chore_manager.load_history()
    history["last_reminded"] = today_str
    chore_manager.save_history(history)

    channel = bot.get_channel(REMINDER_CHANNEL_ID)
    if not channel:
        logger.error(
            "Reminder channel %s not found. Check DISCORD_REMINDER_CHANNEL_ID.",
            REMINDER_CHANNEL_ID,
        )
        return

    config = chore_manager.load_config()
    all_chores = chore_manager.get_all_chores()

    mentions = []
    embeds = []
    for kid_name, chores in all_chores.items():
        discord_id = config["kids"].get(kid_name, {}).get("discord_id", "")
        if discord_id and not str(discord_id).startswith("YOUR_"):
            mentions.append(f"<@{discord_id}>")
        else:
            mentions.append(kid_name)
        embeds.append(build_kid_embed(kid_name, chores))

    header = (
        "☀️ **Good morning, Justice family! Here are this week's chore assignments:**\n"
        + " ".join(mentions)
    )
    await channel.send(content=header, embeds=embeds)
    logger.info("Sunday reminder sent for %s.", today_str)


@sunday_reminder.before_loop
async def before_sunday_reminder():
    await bot.wait_until_ready()


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(TOKEN)
