#!/usr/bin/env python3
import argparse
import json
import os
import sys
import yaml


# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)
# from library import gmail

CHORES_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__), "chores_history.json"
)

CHORES_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "chores.yaml")
KIDS = ["Isaiah", "Jeremiah", "Ava"]
INIT_JSON = {
    "Isaiah": "set_1",
    "Jeremiah": "set_2",
    "Ava": "set_3",
}


def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"Must need to init the json file: {file_path}")
            data = {}
    return data


def write_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


def rotate_set(chore_set):
    if chore_set == "set_1":
        return "set_2"
    elif chore_set == "set_2":
        return "set_3"
    return "set_1"


def assign_chores(chores, chore_history, _day):
    result = {}
    new_history = {}
    for kid in KIDS:
        set_name = chore_history.get(kid)
        if _day == "sunday":
            set_name = rotate_set(set_name)
        result[kid] = {}
        result[kid]["sunday"] = chores["sunday"][set_name]
        result[kid]["daily"] = chores["daily"][set_name]
        new_history[kid] = set_name
    write_json_file(CHORES_HISTORY_FILE, new_history)
    return result


def rotate_only(chores_history):
    new_history = {}
    for kid in KIDS:
        set_name = chores_history.get(kid)
        set_name = rotate_set(set_name)
        new_history[kid] = set_name
    write_json_file(CHORES_HISTORY_FILE, new_history)


def format_chores(chores):
    if isinstance(chores, dict):
        lines = []
        for key, value in chores.items():
            lines.append(f"{key.capitalize()}:")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"  {value}")
        return "\n".join(lines)
    if isinstance(chores, list):
        return "\n".join(f"- {item}" for item in chores)
    return str(chores)


def send_emails(_kids_emails, _chores, _day):
    for kid in _kids_emails:
        email_address = _kids_emails[kid]["email"]
        chores = _chores[kid][_day]
        if _day == "sunday":
            chores = chores + list(_chores[kid]["daily"])
        subject = f"{_day} chores for {kid}"
        body = (
            f"Here are your {_day} chores:\n\n{json.dumps(chores, indent=4)}"
        )
        try:
            gmail.send_email(email_address, subject, body)
        except Exception as e:
            print(f"Failed to send email to {email_address}: {e}")
        print(f"Emails sent to: {kid}")


def send_parent_email(_parents_emails, _chores, _day):
    for parent in _parents_emails:
        email_address = _parents_emails[parent]["email"]
        subject = f"{_day} chores"
        body = (
            f"Here are your {_day} chores:\n\n{json.dumps(_chores, indent=4)}"
        )
        try:
            gmail.send_email(email_address, subject, body)
        except Exception as e:
            print(f"Failed to send email to {email_address}: {e}")
        print(f"Emails sent to: {parent}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chore Reminder")
    parser.add_argument(
        "day",
        choices=["daily", "sunday", "rotate"],
        help="Specify which day's chores to send (weekday or sunday)",
    )
    parser.parse_args()
    day = parser.parse_args().day
    config = read_yaml(CHORES_CONFIG_FILE)
    chore_sets = config["chore_sets"]
    kids_email = config["kids"]
    parents_email = config["parents"]
    history = read_json_file(CHORES_HISTORY_FILE)
    if day == "rotate":
        rotate_only(history)
        sys.exit(0)
    if not history:
        write_json_file(CHORES_HISTORY_FILE, INIT_JSON)
        history = INIT_JSON

    new_chores = assign_chores(chore_sets, history, day)
    send_emails(kids_email, new_chores, day)
    send_parent_email(parents_email, new_chores, day)
