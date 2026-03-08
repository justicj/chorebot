# JusticeChoreBot

A Discord bot that manages weekly chore assignments for the Justice family kids. Chore sets rotate automatically every Sunday morning at 8 AM Pacific, and parents can manually trigger a rotation on demand.

---

## Features

| Command | Who | Description |
|---|---|---|
| `/mychores` | Kids | Shows your own currently assigned chores (visible only to you) |
| `/allchores` | Anyone | Shows all kids' chore assignments |
| `/rotatechores` | Parents | Manually advances the rotation by one week |

The bot also posts an automatic reminder every **Sunday at 8:00 AM Pacific** to the configured channel, @mentioning each child with their new assignments.

---

## Step 1 — Create the Discord Application & Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → name it `JusticeChoreBot` → **Create**
3. In the left sidebar, click **Bot**
4. Click **Add Bot** → confirm
5. Under **Token**, click **Reset Token**, copy it — this is your `DISCORD_TOKEN`
6. Scroll down to **Privileged Gateway Intents** and enable:
   - **Server Members Intent** *(required to read member roles for the parent permission check)*
7. Click **Save Changes**

---

## Step 2 — Invite the Bot to Your Server

1. In the left sidebar, click **OAuth2 → URL Generator**
2. Under **Scopes**, select:
   - `bot`
   - `applications.commands`
3. Under **Bot Permissions**, select:
   - `Send Messages`
   - `Embed Links`
   - `Read Message History`
   - `View Channels`
4. Copy the generated URL, open it in a browser, and invite the bot to your server

---

## Step 3 — Enable Developer Mode in Discord

You need Developer Mode to copy IDs.

1. Open Discord → **Settings** (gear icon)
2. Go to **Advanced**
3. Toggle **Developer Mode** ON

---

## Step 4 — Gather Your IDs

| Value | How to get it |
|---|---|
| **Server (Guild) ID** | Right-click your server icon in the sidebar → **Copy Server ID** |
| **Reminder Channel ID** | Right-click the channel you want reminders posted in → **Copy Channel ID** |
| **Each kid's Discord User ID** | Right-click the kid's username anywhere in Discord → **Copy User ID** |

---

## Step 5 — Configure the Bot

### 5a — Set Discord IDs in `bot/chores.yaml`

Open `bot/chores.yaml` and replace the placeholder values for each child:

```yaml
kids:
  Isaiah:
    email: isaiahjustice07@gmail.com
    discord_id: 123456789012345678   # ← paste Isaiah's User ID here
  Jeremiah:
    email: jeremiahjustice09@gmail.com
    discord_id: 234567890123456789   # ← paste Jeremiah's User ID here
  Ava:
    email: avajustice10@gmail.com
    discord_id: 345678901234567890   # ← paste Ava's User ID here
```

> **Important:** Discord user IDs are plain integers — no quotes needed.

### 5b — Create the `.env` file

Copy `.env.example` to `.env` in the repo root and fill in your values:

```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_REMINDER_CHANNEL_ID=your_channel_id_here
PARENT_ROLE_NAME=Parents
```

> **Never commit `.env` to source control.** Add it to `.gitignore`.

---

## Step 6 — Set Up Server Roles

The `/rotatechores` command is restricted to members who have the role named `Parents` (or whatever you set `PARENT_ROLE_NAME` to).

1. In your Discord server, go to **Server Settings → Roles**
2. Create a role called **Parents**
3. Assign it to Mom and Dad's accounts
4. Optionally assign the role appropriate channel permissions

The kids do **not** need any special role to use `/mychores` or `/allchores`.

---

## Step 7 — Run with Docker

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.

```bash
cd docker
docker-compose up -d
```

To view live logs:

```bash
docker logs -f justicechorebot
```

To stop:

```bash
docker-compose down
```

### Updating code

Because `bot/` is volume-mounted, most code changes are live immediately. To pick them up:

```bash
docker restart justicechorebot
```

If you change `requirements.txt`, you need to rebuild the image:

```bash
docker-compose up -d --build
```

---

## How Chore Rotation Works

- There are 3 chore sets (`set_1`, `set_2`, `set_3`) — one per child.
- Each set has a **daily** group and a **Sunday** group from `bot/chores.yaml`.
- Every Sunday at 8 AM Pacific the bot automatically rotates all kids forward by one set and posts to the reminder channel.
- Parents can trigger an early/manual rotation at any time with `/rotatechores`.
- The current assignments are persisted in `bot/chores_history.json` so they survive bot restarts.

---

## Project Structure

```
chores/
├── bot/
│   ├── bot.py                # Discord bot — commands & scheduler
│   ├── chore_manager.py      # Chore loading, rotation, and lookup logic
│   ├── chores.yaml           # Chore definitions & kid config (source of truth)
│   ├── chores_history.json   # Current rotation state (auto-managed)
│   └── requirements.txt
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── archive/                  # Legacy scripts (not used by the bot)
│   ├── chore_reminder.py
│   └── web_server.py
├── .env.example
└── README.md
```
