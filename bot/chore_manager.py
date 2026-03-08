import json
import os

import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHORES_FILE = os.path.join(BASE_DIR, "chores.yaml")
HISTORY_FILE = os.path.join(BASE_DIR, "chores_history.json")

KIDS = ["Isaiah", "Jeremiah", "Ava"]
SETS = ["set_1", "set_2", "set_3"]


def _next_set(set_name: str) -> str:
    idx = SETS.index(set_name)
    return SETS[(idx + 1) % len(SETS)]


def load_config() -> dict:
    with open(CHORES_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_history() -> dict:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history: dict) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


def rotate_chores() -> dict:
    """Advance every kid's chore set by one rotation. Preserves non-kid keys."""
    history = load_history()
    new_history = {kid: _next_set(history[kid]) for kid in KIDS}
    # Preserve metadata keys (e.g., last_reminded)
    for key, value in history.items():
        if key not in KIDS:
            new_history[key] = value
    save_history(new_history)
    return new_history


def get_all_chores() -> dict:
    """Return the current chore assignments for every kid."""
    config = load_config()
    history = load_history()
    chore_sets = config["chore_sets"]
    return {
        kid: {
            "daily": chore_sets["daily"][history[kid]],
            "sunday": chore_sets["sunday"][history[kid]],
        }
        for kid in KIDS
    }


def get_chores_for_kid(kid_name: str) -> dict | None:
    return get_all_chores().get(kid_name)


def get_kid_by_discord_id(discord_id: str) -> str | None:
    config = load_config()
    for kid_name, kid_data in config["kids"].items():
        stored_id = str(kid_data.get("discord_id", ""))
        if stored_id == str(discord_id) and not stored_id.startswith("YOUR_"):
            return kid_name
    return None
