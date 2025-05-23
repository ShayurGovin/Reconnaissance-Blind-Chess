import subprocess
import itertools
from collections import defaultdict

# Define bots and paths
BOTS = {
    "RandomSensing": "Part4/RandomSensing.py",       
    "RandomBot": "Part4/RandomBot.py",
    "TroutBot": "Part4/TroutBot.py",
    "ImprovedAgent": "Part4/ImprovedAgent.py"
}

match_results = []
win_counts = defaultdict(int)
loss_counts = defaultdict(int)
draw_counts = defaultdict(int)

def run_match(white_name, black_name, white_path, black_path):
    print(f"\n▶ {white_name} (White) vs {black_name} (Black)")
    
    try:
        result = subprocess.run(
            ["rc-bot-match", white_path, black_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300
        )
    except subprocess.TimeoutExpired:
        print(f"⏱ Match between {white_name} and {black_name} timed out.")
        match_results.append({
            "White": white_name,
            "Black": black_name,
            "Winner": "Timeout"
        })
        return

    output = result.stdout
    print(output)

    lower_output = output.lower()

    if "winner: white!" in lower_output:
        winner = white_name
        win_counts[white_name] += 1
        loss_counts[black_name] += 1
    elif "winner: black!" in lower_output:
        winner = black_name
        win_counts[black_name] += 1
        loss_counts[white_name] += 1
    elif "winner: draw" in lower_output or "draw" in lower_output:
        winner = "Draw"
        draw_counts[white_name] += 1
        draw_counts[black_name] += 1
    else:
        winner = None

    match_results.append({
        "White": white_name,
        "Black": black_name,
        "Winner": winner
    })

bot_items = list(BOTS.items())
for (name1, path1), (name2, path2) in itertools.combinations(bot_items, 2):
    run_match(name1, name2, path1, path2)
    run_match(name2, name1, path2, path1)

print("\n=== 🏁 Final Bot Statistics ===")
for bot in BOTS:
    print(f"{bot}: {win_counts[bot]}W / {loss_counts[bot]}L / {draw_counts[bot]}D")

print("\n=== 🧾 Match Results ===")
for match in match_results:
    print(f"{match['White']} (White) vs {match['Black']} (Black) => Winner: {match['Winner']}")
