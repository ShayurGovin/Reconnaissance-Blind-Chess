import reconchess as rc
from random_bot import RandomBot
from trout_bot import TroutBot
from MyAgent import RandomSensing
from ImprovedAgent import ImprovedAgent
from ImprovedAgent2 import ImprovedAgent2

import sys
import traceback
from itertools import combinations
import random

# === Step 1: Setup CLI args or interactive mode ===
if len(sys.argv) == 3:
    num_rounds = int(sys.argv[1])
    game_length = float(sys.argv[2])
else:
    num_rounds = int(input("Number of rounds: "))
    game_length = float(input("Seconds per player: "))

# === Step 2: Define the agents to test ===
players = [RandomBot, TroutBot, RandomSensing, ImprovedAgent2]  # or add ImprovedAgent, ImprovedAgent2

# === Step 3: Initialize results ===
game_results = {player: {'win': 0, 'loss': 0, 'draw': 0} for player in players}

# === Step 4: Generate all matchups (each agent vs each, both colors) ===
matchups = []
for a, b in combinations(range(len(players)), 2):
    matchups.append((a, b))  # a = white, b = black
    matchups.append((b, a))  # b = white, a = black

# === Step 5: Repeat the matchups for N rounds ===
for round_num in range(num_rounds):
    print(f"\n--- Round {round_num + 1} ---\n")
    random.shuffle(matchups)  # optional: randomize order

    print(f"{'Game': <6}{'White': <20}{'Black': <20}{'Result': <8}Reason")
    print("-" * 70)

    for game_idx, (w_idx, b_idx) in enumerate(matchups):
        white = players[w_idx]
        black = players[b_idx]

        print(f"{round_num + 1}.{game_idx + 1:<4}{white.__name__: <20}{black.__name__: <20}", end='')

        try:
            result, win_reason, _ = rc.play_local_game(white(), black(), seconds_per_player=game_length)

            if result is None:
                result_str = "Draw"
                game_results[white]["draw"] += 1
                game_results[black]["draw"] += 1
            elif result:
                result_str = "White"
                game_results[white]["win"] += 1
                game_results[black]["loss"] += 1
            else:
                result_str = "Black"
                game_results[white]["loss"] += 1
                game_results[black]["win"] += 1

            print(f"{result_str: <8}{win_reason}")
        except Exception as e:
            print(f"(Error: {e})")
            traceback.print_exc()

# === Step 6: Print final scores ===
print("\n" + "-" * 64)
print(f"{'Agent Results': <20}|\tScore\tWins\tLosses\tDraws\tWin %")
print(f"{'-' * 20}|{'-' * 43}")
for agent in players:
    wins = game_results[agent]['win']
    draws = game_results[agent]['draw']
    losses = game_results[agent]['loss']
    score = wins * 1 + draws * 0.5
    total_games = wins + losses + draws
    win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
    print(f"{agent.__name__: <20}|\t{score:.1f}\t{wins}\t{losses}\t{draws}\t{win_rate:.2f}")
print("-" * 64)
