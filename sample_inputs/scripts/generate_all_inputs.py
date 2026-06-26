from __future__ import annotations

from generation_core import generate_all_inputs, print_summary


def main() -> None:
    print_summary(generate_all_inputs())


if __name__ == "__main__":
    main()

