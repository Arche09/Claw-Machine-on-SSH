import os
import sys
import time
import json
import random
import msvcrt
import winsound
from pathlib import Path

WIDTH = 40
HEIGHT = 20
PANEL = 24

SAVE_FILE = Path("claw_data.json")
SOUND_FOLDER = Path("sounds")

PRIZES = [
    ("o", "Common", 10, 0.90, 5),
    ("+", "Uncommon", 25, 0.75, 20),
    ("*", "Rare", 50, 0.45, 30),
    ("@", "Legendary", 100, 0.15, 80)
]

SOUND_FILES = {
    "move": "move.wav",
    "drop": "drop.wav",
    "grab": "grab.wav",
    "miss": "miss.wav",
    "hazard": "hazard.wav",
    "jackpot": "jackpot.wav",
    "achievement": "achievement.wav",
    "gameover": "gameover.wav"
}

def play_sound(name):
    if not sound_on:
        return

    filename = SOUND_FILES.get(name)
    if filename is None:
        return

    path = SOUND_FOLDER / filename

    if path.exists():
        winsound.PlaySound(
            str(path),
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
    else:
        print(f"Sound not found: {path}")


COMMENTS = ["The claw is doing its best.. *allegedly*",
            "Your accountant would like a word",
            "BOLD STRAT, questionable execution T_T",
            "The machine delines to elaborate",
            "Perhaps the prize was the friends we made along the way..",
            "Skill issue?",
            "An investment in shiny things",
            "The claw requests a performance review"
           ]

ACHIEVEMENTS = {
    "first": "First Contact",
    "legendary": "The Chosen One",
    "goblin": "Certified Loot Goblin",
    "hazards": "Natural Selection",
    "unlucky": "Professional Button Presser",
    "collector": "Gotta Grab 'Em All",
    "combo": "Suspiciously Lucky",
    "big_score": "Capitalist Machine",
    "untouchable": "Untouchable"
}
data = {
    "scores": [],
    "achievements": [],
    "journal": []
}

try:
    with SAVE_FILE.open("r", encoding="utf-8") as file:
        data.update(json.load(file))
except (OSError, ValueError):
    pass

sound_on = True

def save():
    with SAVE_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def play_sound(name):
    if not sound_on:
        return

    path = SOUND_FOLDER / SOUND_FILES[name]

    if path.exists():
        try:
            winsound.PlaySound(
                str(path),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except (RuntimeError, OSError):
            pass


def new_objects():
    positions = []

    while len(positions) < 12:
        position = (
            random.randint(1, WIDTH - 2),
            random.randint(2, HEIGHT - 3)
        )

        if position not in positions:
            positions.append(position)

    hazard_count = random.randint(0, 2)
    hazard_positions = random.sample(range(12), hazard_count)

    objects = []

    for i in range(12):
        x, y = positions[i]

        objects.append({
            "x": x,
            "y": y,
            "type": random.randint(0, 3),
            "hazard": i in hazard_positions
        })

    return objects


def start_game(mode):
    credits = 5
    lives = 3

    if mode == "Speedrun":
        credits = 999
    elif mode == "Collector":
        credits = 20
        lives = 5
    elif mode == "Challenge":
        credits = 10

    return {
        "mode": mode,
        "credits": credits,
        "lives": lives,
        "score": 0,
        "x": WIDTH // 2,
        "y": 1,
        "state": "ready",
        "held": None,
        "objects": new_objects(),
        "collected": [],
        "delivered": 0,
        "hazards": 0,
        "misses": 0,
        "rare_streak": 0,
        "types": set(),
        "lives_lost": 0,
        "drops": 0,
        "message": "Press S to drop the claw!",
        "start_time": time.monotonic(),
        "running": True
    }


def unlock(game, achievement_id):
    if achievement_id in data["achievements"]:
        return

    data["achievements"].append(achievement_id)
    save()

    game["message"] = (
        "ACHIEVEMENT UNLOCKED: "
        + ACHIEVEMENTS[achievement_id]
    )

    play_sound("achievement")


def check_achievements(game):
    if game["delivered"] >= 1:
        unlock(game, "first")
    if game["delivered"] >= 10:
        unlock(game, "goblin")
    if game["hazards"] >= 2:
        unlock(game, "hazards")
    if game["misses"] >= 5:
        unlock(game, "unlucky")
    if len(game["types"]) == 4:
        unlock(game, "collector")
    if game["rare_streak"] >= 3:
        unlock(game, "combo")
    if game["score"] >= 250:
        unlock(game, "big_score")
    if game["delivered"] > 0 and 3 in game["types"]:
        unlock(game, "legendary")


def text_at(row, x, text):
    for i, character in enumerate(text):
        if x + i < len(row):
            row[x + i] = character


def draw(game):
    lines = []

    lines.append(
        "+" + "-" * (WIDTH - 2)
        + "+" + "-" * (PANEL - 2) + "+"
    )

    for y in range(1, HEIGHT - 1):
        main = [" "] * (WIDTH - 2)
        side = [" "] * (PANEL - 2)

        for obj in game["objects"]:
            if obj["y"] == y:
                main[obj["x"] - 1] = PRIZES[obj["type"]][0]

        if y < game["y"]:
            main[game["x"] - 1] = "|"
        elif y == game["y"]:
            main[game["x"] - 1] = "Ω"

        if y == 2:
            text_at(side, 1, "DROP BOX")
        elif y == 3:
            text_at(side, 1, "Score: " + str(game["score"]))
        elif y == 4:
            text_at(side, 1, "Credits: " + str(game["credits"]))
        elif y == 5:
            text_at(side, 1, "Lives: " + str(game["lives"]))
        elif y == 6:
            text_at(side, 1, "Mode: " + game["mode"])
        elif y == 7:
            text_at(side, 1, "Prizes left: " + str(len(game["objects"])))
        elif y == 8:
            text_at(side, 1, "A/D: Move")
        elif y == 9:
            text_at(side, 1, "S: Drop")
        elif y == 10:
            text_at(side, 1, "M: Toggle sound")
        elif y == 11:
            text_at(side, 1, "Q: Quit run")
        if y == 13:
            text_at(side, 0, "+" + "-" * (PANEL - 4) + "+")
        elif y in (14, 15):
            text_at(side, 0, "|")
            text_at(side, PANEL - 3, "|")
            start = (y - 14) * (PANEL - 4)

            for i, prize_type in enumerate(
                game["collected"][start:start + PANEL - 4]
            ):
                side[i + 1] = PRIZES[prize_type][0]
        elif y == 16:
            text_at(side, 0, "+" + "-" * (PANEL - 4) + "+")

        lines.append(
            "|" + "".join(main) + "|" + "".join(side) + "|"
        )

    lines.append(
        "+" + "-" * (WIDTH - 2)
        + "+" + "-" * (PANEL - 2) + "+"
    )

    lines.append(game["message"])

    if game["mode"] == "Speedrun":
        remaining = max(
            0,
            60 - int(time.monotonic() - game["start_time"])
        )
        lines.append("Time left: " + str(remaining) + " seconds")

    sys.stdout.write("\x1b[H" + "\n".join(lines) + "\n")
    sys.stdout.flush()


def lose_life(game, reason):
    game["lives"] -= 1
    game["lives_lost"] += 1
    game["message"] = reason


def grab(game):
    candidates = []
    for obj in game["objects"]:
        if obj["x"] == game["x"]:
            candidates.append(obj)
    if not candidates:
        lose_life(game, "MISSSS! AHAHABSOLOUTELY NOTHINGGG.")
        game["misses"] += 1
        game["rare_streak"] = 0
        play_sound("miss")
        return
    obj = max(candidates, key=lambda item: item["y"])
    symbol, name, points, chance, penalty = PRIZES[obj["type"]]
    if random.random() > chance:
        lose_life(game, "MAMMA MIA!! THE PRIZE SLIPPED")
        game["misses"] += 1
        game["rare_streak"] = 0
        play_sound("miss")
        return
    game["objects"].remove(obj)
    if obj["hazard"]:
        game["score"] -= penalty
        game["hazards"] += 1
        game["rare_streak"] = 0
        lose_life(game, "HAZARDDDD! Lost " + str(penalty) + " points!")
        play_sound("hazard")
        return
    game["held"] = obj
    game["message"] = "Prize grabbed!"
    play_sound("grab")


def deliver(game):
    obj = game["held"]
    if obj is None:
        return

    prize_type = obj["type"]
    symbol, name, points, chance, penalty = PRIZES[prize_type]

    game["collected"].append(prize_type)
    game["score"] += points
    game["delivered"] += 1
    game["types"].add(prize_type)

    if prize_type >= 2:
        game["rare_streak"] += 1
    else:
        game["rare_streak"] = 0
    if prize_type == 3:
        game["message"] = "JACKPOTTTT! +" + str(points)
        play_sound("jackpot")
    else:
        game["message"] = name + " prize delivered! +" + str(points)
        play_sound("grab")
    if name not in data["journal"]:
        data["journal"].append(name)
    game["held"] = None

    save()
    check_achievements(game)


def update(game):
    if game["state"] == "lowering":
        game["y"] += 1
        if game["y"] >= HEIGHT - 2:
            grab(game)
            game["state"] = "raising"
    elif game["state"] == "raising":
        game["y"] -= 1
        if game["y"] <= 1:
            game["y"] = 1
            if game["held"] is not None:
                deliver(game)
            game["state"] = "ready"

def finish(game, reason):
    if not game["running"]:
        return
    game["running"] = False
    game["message"] = reason
    if game["lives_lost"] == 0:
        unlock(game, "untouchable")
    play_sound("gameover")
    data["scores"].append({
        "mode": game["mode"],
        "score": game["score"],
        "date": time.strftime("%Y-%m-%d %H:%M")
    })
    data["scores"].sort(
        key=lambda item: item["score"],
        reverse=True
    )
    data["scores"] = data["scores"][:5]
    save()

def check_end(game):
    if game["lives"] <= 0:
        finish(game, "Out of lives!")
    elif game["mode"] == "Speedrun":
        if time.monotonic() - game["start_time"] >= 60:
            finish(game, "Time is up!")
    elif game["mode"] == "Challenge" and game["score"] >= 150:
        finish(game, "Challenge complete!")
    elif game["mode"] == "Collector" and len(game["types"]) == 4:
        finish(game, "You collected every rarity!")
    elif game["credits"] <= 0 and game["state"] == "ready":
        finish(game, "Out of credits!")

def show_records():
    os.system("cls")
    print("          ARCADE RECORDS          ")
    print("\nTOP SCORES")
    for entry in data["scores"]:
        print(entry["score"], "points -", entry["mode"], "-", entry["date"])
    print("\nACHIEVEMENTS")
    for achievement in data["achievements"]:
        print("-", ACHIEVEMENTS[achievement])
    print("\nPRIZE JOURNAL")
    for prize in data["journal"]:
        print("-", prize)

    print("\nPress any key to return.")
    msvcrt.getwch()

def play(game):
    global sound_on

    os.system("")
    sys.stdout.write("\x1b[2J\x1b[H\x1b[?25l")
    last_update = time.monotonic()

    try:
        while game["running"]:
            now = time.monotonic()
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key == "q":
                    finish(game, "You left the machine.")
                elif key == "m":
                    sound_on = not sound_on
                    game["message"] = "Sound " + ("ON" if sound_on else "OFF")
                elif key == "a" and game["state"] == "ready":
                    if game["x"] > 1:
                        game["x"] -= 1
                        play_sound("move")
                elif key == "d" and game["state"] == "ready":
                    if game["x"] < WIDTH - 2:
                        game["x"] += 1
                        play_sound("move")
                elif key == "s" and game["state"] == "ready":
                    if game["credits"] > 0:
                        game["credits"] -= 1
                        game["drops"] += 1
                        game["state"] = "lowering"
                        game["message"] = "Claw descending"
                        play_sound("drop")
            if now - last_update >= 0.12:
                update(game)
                check_end(game)
                draw(game)
                last_update = now
            time.sleep(0.01)
    finally:
        sys.stdout.write("\x1b[?25h\n")
        sys.stdout.flush()

def main():
    while True:
        os.system("cls")

        print("      THE EXTREMELY NORMAL CLAW MACHINE      ")
        print("1. Classic")
        print("2. Speedrun (60 seconds)")
        print("3. Collector")
        print("4. Challenge (150 points)")
        print("5. View records")
        print("Q. Quit")
        print("\nChoose: ", end="", flush=True)

        key = msvcrt.getwch().lower()

        if key == "q":
            break
        elif key == "5":
            show_records()
            continue
        elif key in ("1", "2", "3", "4"):
            modes = {
                "1": "Classic",
                "2": "Speedrun",
                "3": "Collector",
                "4": "Challenge"
            }

            game = start_game(modes[key])
            play(game)

            os.system("cls")
            print("GAME OVER")
            print(game["message"])
            print("Score:", game["score"])
            print("Prizes delivered:", game["delivered"])
            print("Hazards:", game["hazards"])
            print("Misses:", game["misses"])
            print("\nPress any key to return to the menu.")
            msvcrt.getwch()

    save()
    os.system("cls")
    print("Thanks for playing. The claw will miss you!")


if __name__ == "__main__":
    main()
