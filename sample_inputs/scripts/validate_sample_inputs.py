from __future__ import annotations

from generation_core import validate_sample_inputs


def main() -> None:
    summary = validate_sample_inputs()
    print("Sample inputs are valid.")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
