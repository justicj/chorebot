#!/usr/bin/env python3
import os
import json
import datetime
import logging
import yaml

from flask import Flask, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHORES_HISTORY_FILE = os.path.join(BASE_DIR, "chores_history.json")
CHORES_CONFIG_FILE = os.path.join(BASE_DIR, "chores.yaml")
KIDS = ["Isaiah", "Jeremiah", "Ava"]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "web_server.log")),
        logging.StreamHandler(),
    ],
)


def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}
    return data


def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


def get_current_chores():
    config = read_yaml(CHORES_CONFIG_FILE)
    chore_sets = config["chore_sets"]
    history = read_json_file(CHORES_HISTORY_FILE)
    result = {}
    for kid in KIDS:
        set_name = history.get(kid)
        result[kid] = {
            "sunday": chore_sets["sunday"][set_name],
            "daily": chore_sets["daily"][set_name],
        }
    return result


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
        return "<br>".join(lines)
    if isinstance(chores, list):
        return "<br>".join(f"- {item}" for item in chores)
    return str(chores)


@app.route("/")
def show_chores():
    chores = get_current_chores()
    logging.info("Current chores: %s", chores)
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    html = """
    <html>
    <head>
        <title>Current Chores</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: #181a1b;
                color: #e0e0e0;
                margin: 0;
                padding: 0;
            }
            h1 {
                text-align: center;
                color: #7ecfff;
                margin-top: 24px;
            }
            .date-header {
                text-align: center;
                margin-top: 18px;
                font-size: 1.25em;
                color: #b0cfff;
                letter-spacing: 1px;
            }
            table {
                margin: 24px auto;
                border-collapse: collapse;
                background: #23272a;
                box-shadow: 0 4px 24px #111;
                min-width: 320px;
                max-width: 98vw;
                width: 100%;
                border-radius: 12px;
                overflow: hidden;
            }
            th, td {
                padding: 14px 10px;
                border-bottom: 1px solid #333a40;
                vertical-align: top;
                word-break: break-word;
            }
            th {
                background: linear-gradient(90deg, #23272a 0%, #2d6cdf 100%);
                color: #7ecfff;
                font-size: 1.08em;
                letter-spacing: 1px;
                border-bottom: 3px solid #2d6cdf;
            }
            tr:last-child td { border-bottom: none; }
            tr:nth-child(even) td { background: #202225; }
            tr:hover td { background: #2d3742; transition: background 0.2s; }
            ul { margin: 0; padding-left: 22px; }
            .chore-title {
                font-weight: bold;
                margin-bottom: 6px;
                color: #7ecfff;
                font-size: 1.07em;
            }
            td { color: #e0e0e0; }
            .kid-name {
                font-size: 2.5em;
                font-weight: bold;
                color: #7ecfff;
                letter-spacing: 1px;
            }
            @media (max-width: 700px) {
                table, thead, tbody, th, td, tr {
                    display: block;
                }
                table {
                    min-width: 0;
                    width: 98vw;
                }
                thead tr {
                    display: none;
                }
                tr {
                    margin-bottom: 18px;
                    background: #23272a;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px #111;
                }
                td {
                    border: none;
                    padding: 12px 8px;
                    position: relative;
                }
                td:first-child {
                    font-size: 1.15em;
                    font-weight: bold;
                    color: #7ecfff;
                    background: #181a1b;
                    border-radius: 10px 10px 0 0;
                }
            }
        </style>
        <script>
function toggleChores(kid, type) {
    var div = document.getElementById(kid + '-' + type);
    if (div.style.display === "none") {
        div.style.display = "block";
    } else {
        div.style.display = "none";
    }
}
</script>
    </head>
    <body>
    <div class="date-header">{{ current_date }}</div>
    <h1>Current Chores</h1>
    <table>
        <tr>
            <th>Kid</th>
            <th>Chores</th>
        </tr>
        {% for kid, kid_chores in chores.items() %}
        <tr>
            <td class="kid-name">{{ kid }}</td>
            <td>
                <div class="chore-title" style="margin-top:8px;">Sunday</div>
                {% for set in kid_chores['sunday'] %}
                    <div class="chore-title">{{ set['name'] }}</div>
                    <ul>
                    {% for action in set['actions'] %}
                        <li>{{ action }}</li>
                    {% endfor %}
                    </ul>
                {% endfor %}
                <div class="chore-title" style="margin-top:12px;">Daily</div>
                {% for set in kid_chores['daily'] %}
                    <div class="chore-title">{{ set['name'] }}</div>
                    <ul>
                    {% for action in set['actions'] %}
                        <li>{{ action }}</li>
                    {% endfor %}
                    </ul>
                {% endfor %}
            </td>
        </tr>
        {% endfor %}
    </table>
    </body>
    </html>
    """
    return render_template_string(
        html, chores=chores, current_date=current_date
    )


if __name__ == "__main__":
    logging.info("Starting Flask server on 0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
