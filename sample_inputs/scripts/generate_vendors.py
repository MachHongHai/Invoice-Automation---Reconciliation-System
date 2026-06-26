from __future__ import annotations

from generation_core import ensure_directories, generate_vendors


if __name__ == "__main__":
    ensure_directories()
    rows = generate_vendors()
    print(f"Generated vendors: {len(rows)}")

