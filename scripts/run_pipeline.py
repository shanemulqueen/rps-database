import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import parse_capacity
import parse_achievement
import parse_targets_demand
import generate_state_summaries

if __name__ == "__main__":
    print("=== RPS Database Pipeline ===\n")

    print("--- Capacity Additions ---")
    parse_capacity.parse()

    print("\n--- Target Achievement & Compliance Costs ---")
    parse_achievement.parse()

    print("\n--- Targets, Demand & Sales ---")
    parse_targets_demand.parse()

    print("\n--- State Summaries ---")
    generate_state_summaries.generate()

    print("\n=== Done ===")
