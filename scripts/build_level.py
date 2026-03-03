#!/usr/bin/env python3
"""
Level Builder Script for Super Mario Bros.

Creates level JSON files from text-based level layouts.

Usage:
    python scripts/build_level.py --name level_1_2 --output data/levels/

Example level layout format (in a .txt file):

    # Legend:
    #   = Ground
    #   B = Brick
    #   ? = Coin Box
    #   # = Pipe
    #   G = Goomba
    #   K = Koopa
    #   F = Flag pole
    #   S = Step
    #   . = Empty space

    ........................................................
    ........................................................
    ........................................................
    ........................................................
    ....?...................................................
    ........................................................
    ......B?B?B.............................................
    ....................................##..................
    ................G.................##....................
    ====================...==================...............
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

# Level constants
TILE_SIZE = 40  # pixels
GROUND_Y = 538  # pixels from top


def parse_level_text(text: str) -> Dict[str, Any]:
    """
    Parse text-based level layout.

    Args:
        text: Level layout as text

    Returns:
        Level data dictionary
    """
    lines = [line.rstrip() for line in text.strip().split("\n") if line.strip()]

    # Find dimensions
    max_width = max(len(line) for line in lines)

    # Initialize level data
    level_data: Dict[str, Any] = {
        "name": "custom_level",
        "width": max_width * TILE_SIZE,
        "ground_height": GROUND_Y,
        "bricks": [],
        "coin_boxes": [],
        "pipes": [],
        "enemies": [],
        "steps": [],
        "flag_pole": None,
    }

    # Parse each character
    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line):
            x = col_idx * TILE_SIZE
            y = GROUND_Y - (row_idx * TILE_SIZE)

            if char == "B":
                level_data["bricks"].append({"x": x, "y": y, "contents": None})
            elif char == "?":
                level_data["coin_boxes"].append({"x": x, "y": y, "contents": "coin"})
            elif char == "#":
                # Pipe - calculate height based on consecutive # vertically
                pipe_height = 1
                for check_row in range(row_idx + 1, min(row_idx + 4, len(lines))):
                    if check_row < len(lines) and col_idx < len(lines[check_row]) and lines[check_row][col_idx] == "#":
                        pipe_height += 1
                    else:
                        break

                level_data["pipes"].append(
                    {
                        "x": x,
                        "y": y,
                        "width": TILE_SIZE,
                        "height": pipe_height * TILE_SIZE,
                    }
                )
            elif char == "G":
                level_data["enemies"].append(
                    {
                        "type": "goomba",
                        "x": x,
                        "y": y - TILE_SIZE,
                        "direction": "left",
                    }
                )
            elif char == "K":
                level_data["enemies"].append(
                    {
                        "type": "koopa",
                        "x": x,
                        "y": y - TILE_SIZE,
                        "direction": "left",
                    }
                )
            elif char == "F":
                level_data["flag_pole"] = {
                    "x": x,
                    "y": y - (4 * TILE_SIZE),  # Tall pole
                }
            elif char == "S":
                level_data["steps"].append(
                    {
                        "x": x,
                        "y": y,
                        "width": TILE_SIZE,
                        "height": TILE_SIZE,
                    }
                )

    return level_data


def build_level(name: str, layout_file: str, output_dir: str = "data/levels") -> str:
    """
    Build level from layout file.

    Args:
        name: Level name
        layout_file: Path to layout text file
        output_dir: Output directory for JSON

    Returns:
        Path to created JSON file
    """
    # Read layout file
    with open(layout_file, "r", encoding="utf-8") as f:
        layout_text = f.read()

    # Parse layout
    level_data = parse_level_text(layout_text)
    level_data["name"] = name

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write JSON
    output_path = os.path.join(output_dir, f"{name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(level_data, f, indent=2)

    print(f"Level created: {output_path}")
    print(f"  Width: {level_data['width']}px")
    print(f"  Bricks: {len(level_data['bricks'])}")
    print(f"  Coin boxes: {len(level_data['coin_boxes'])}")
    print(f"  Enemies: {len(level_data['enemies'])}")

    return output_path


def create_sample_layout(output_path: str) -> None:
    """
    Create a sample level layout file.

    Args:
        output_path: Path to save sample layout
    """
    sample_layout = """# Super Mario Bros Level Layout
# ================================
#
# Legend:
#   . = Empty space
#   = = Ground
#   B = Brick block
#   ? = Coin box (contains coin)
#   ! = Coin box (contains mushroom)
#   # = Pipe
#   G = Goomba
#   K = Koopa
#   F = Flag pole
#   S = Step block
#   C = Castle (end)
#
# Tips:
# - Each character represents one tile (40x40 pixels)
# - Ground level is the bottom row of '=' characters
# - Enemies spawn one tile above their position
# - Pipes need consecutive '#' characters vertically

# Row 0 (highest)
................................................................................
................................................................................
................................................................................
................................................................................
....................?...........................................................
................................................................................
........................B?B?B...................................................
................................................................................
.......................................##.......................................
........................G............###........................................
................................................................................
................................................................................
....................K...........................................................
................................................................................
................................................................................
================================================================================
""".strip()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sample_layout)

    print(f"Sample layout created: {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Super Mario Bros levels from text layouts")
    parser.add_argument("--name", "-n", default="custom_level", help="Level name (default: custom_level)")
    parser.add_argument("--input", "-i", help="Input layout file (default: creates sample)")
    parser.add_argument("--output", "-o", default="data/levels", help="Output directory (default: data/levels)")
    parser.add_argument("--sample", "-s", action="store_true", help="Create sample layout file")

    args = parser.parse_args()

    if args.sample:
        sample_path = args.input or "sample_layout.txt"
        create_sample_layout(sample_path)
        return 0

    if not args.input:
        print("Error: --input is required (or use --sample to create example)")
        parser.print_help()
        return 1

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1

    try:
        build_level(args.name, args.input, args.output)
        return 0
    except Exception as e:
        print(f"Error building level: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
