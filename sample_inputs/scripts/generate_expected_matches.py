from __future__ import annotations

from generation_core import generate_expected_matches


if __name__ == "__main__":
    print(f"Generated expected matches: {len(generate_expected_matches())}")

