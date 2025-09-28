import random
import tkinter as tk
from dataclasses import dataclass, field
from typing import List

# ----------------- DATA STRUCTURES -----------------
@dataclass
class Player:
    name: str
    skill: int  # 1-100

@dataclass
class Team:
    name: str
    offense: int
    defense: int
    roster: List[Player] = field(default_factory=list)
    score: int = 0
    touchdowns: int = 0
    field_goals: int = 0
    turnovers: int = 0
    big_plays: int = 0
    drives: int = 0

# ----------------- ROSTER CREATION -----------------
def make_roster(teamname: str) -> List[Player]:
    first_names = ["Max", "Jax", "Leo", "Kai", "Finn", "Zeke", "Theo", "Omar", "Ace", "Nico",
                   "Liam", "Milo", "Eli", "Troy", "Rex", "Hugo", "Cal", "Jude", "Ezra", "Ash"]
    last_names = ["Blaze", "Cruz", "Stone", "Knight", "Storm", "Steel", "Vega", "Frost", "Ray", "Hawk",
                  "Wolfe", "Vale", "Swift", "Cage", "Drake", "Shaw", "Cole", "Reed", "Zion", "Gray"]
    roster = []
    for i in range(20):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        roster.append(Player(name, random.randint(50, 95)))
    return roster

# ----------------- WEATHER -----------------
def pick_weather():
    options = ["☀️ Sunny", "🌧️ Rain", "❄️ Snow", "⛈️ Stormy"]
    w = random.choice(options)
    return w

def weather_modifiers(weather):
    if "Sunny" in weather:
        return {"off": 1.0, "def": 1.0}
    if "Rain" in weather:
        return {"off": 0.9, "def": 1.05}
    if "Snow" in weather:
        return {"off": 0.85, "def": 1.1}
    if "Stormy" in weather:
        return {"off": 0.8, "def": 1.15}
    return {"off": 1.0, "def": 1.0}

# ----------------- GAME LOGIC -----------------
def play_drive(off: Team, deff: Team, weather: str):
    off.drives += 1
    mods = weather_modifiers(weather)
    diff = (off.offense * mods["off"]) - (deff.defense * mods["def"])
    diff = max(min(diff, 40), -40)

    td_chance = max(0.02, min(0.4, 0.08 + diff * 0.003))
    fg_chance = max(0.02, min(0.3, 0.12 + diff * 0.002))
    turnover_chance = max(0.01, min(0.25, 0.06 - diff * 0.0015))
    big_play_chance = max(0.02, min(0.4, 0.07 + diff * 0.0025))

    text = ""
    pts = 0
    r = random.random()
    if r < big_play_chance:
        off.big_plays += 1
        if random.random() < 0.5:
            pts = 7
            off.score += pts
            off.touchdowns += 1
            text = f"🔥 {off.name} breaks loose for a huge touchdown!"
        else:
            text = f"💨 {off.name} makes a big gain but stalls."
            if random.random() < 0.35:
                pts = 3
                off.score += pts
                off.field_goals += 1
                text += " Settles for a field goal."
    else:
        r2 = random.random()
        if r2 < td_chance:
            pts = 7
            off.score += pts
            off.touchdowns += 1
            text = f"🏈 Touchdown for {off.name}!"
        elif r2 < td_chance + fg_chance:
            pts = 3
            off.score += pts
            off.field_goals += 1
            text = f"🎯 Field goal by {off.name}."
        elif r2 < td_chance + fg_chance + turnover_chance:
            off.turnovers += 1
            text = f"💥 Turnover! {off.name} gives it away."
        else:
            text = f"🚫 Drive stalls for {off.name}."
    return text, pts

def simulate_game(team_a: Team, team_b: Team):
    commentary = []
    weather = pick_weather()
    commentary.append(f"Weather today: {weather}")
    starter = team_a if random.random() < 0.5 else team_b
    other = team_b if starter is team_a else team_a
    commentary.append(f"🏟️ Kickoff! {starter.name} starts with the ball.")

    for i in range(12):  # 6 drives each
        offense = starter if i % 2 == 0 else other
        defense = other if offense is starter else starter
        text, _ = play_drive(offense, defense, weather)
        commentary.append(f"Drive {i+1}: {text}  (Score: {team_a.name} {team_a.score} - {team_b.score} {team_b.name})")

    commentary.append("🔔 Final Whistle!")
    commentary.append(f"Final Score — {team_a.name} {team_a.score} : {team_b.score} {team_a.name}")
    return commentary

# ----------------- TKINTER GUI -----------------
def run_gui():
    root = tk.Tk()
    root.title("🏈 Fun Football Simulator")

    text_box = tk.Text(root, width=70, height=30, wrap="word", bg="black", fg="lime", font=("Courier", 10))
    text_box.pack(padx=10, pady=10)

    def play():
        text_box.delete("1.0", tk.END)
        team1 = Team("Zephyria Raptors", 78, 72, make_roster("Raptors"))
        team2 = Team("Lyris Lions", 74, 76, make_roster("Lions"))
        result = simulate_game(team1, team2)
        for line in result:
            text_box.insert(tk.END, line + "\n")
        text_box.see(tk.END)

    play_btn = tk.Button(root, text="▶️ Play Game", command=play, font=("Arial", 14), bg="navy", fg="white")
    play_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
