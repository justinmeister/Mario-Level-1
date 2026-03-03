"""
Level loader module for loading level data from JSON files.
Supports both custom JSON format and Tiled map editor format.
"""

from __future__ import annotations

import json
import os
from typing import Any

from data import constants as c


class LevelData:
    """Container for level data parsed from JSON."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width: int = 0
        self.height: int = 0
        self.ground_height: int = c.GROUND_HEIGHT
        self.camera_start_x: int = 0

        # Entity lists
        self.bricks: list[dict[str, Any]] = []
        self.coin_boxes: list[dict[str, Any]] = []
        self.pipes: list[dict[str, Any]] = []
        self.steps: list[dict[str, Any]] = []
        self.enemies: list[dict[str, Any]] = []
        self.checkpoints: list[dict[str, Any]] = []
        self.flag_pole: dict[str, Any] = {}
        self.mario_start: dict[str, Any] = {}
        self.ground_sections: list[dict[str, Any]] = []

        # Background
        self.background_color: tuple[int, int, int] = c.WHITE


def load_level_from_json(filepath: str) -> LevelData:
    """
    Load level data from a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        LevelData object with parsed level configuration
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    level = LevelData()
    level.name = data.get("name", "Unknown Level")
    level.width = data.get("width", 8000)
    level.height = data.get("height", c.SCREEN_HEIGHT)
    level.ground_height = data.get("ground_height", c.GROUND_HEIGHT)
    level.camera_start_x = data.get("camera_start_x", 0)
    level.background_color = tuple(data.get("background_color", c.WHITE))

    # Load entities
    level.bricks = data.get("bricks", [])
    level.coin_boxes = data.get("coin_boxes", [])
    level.pipes = data.get("pipes", [])
    level.steps = data.get("steps", [])
    level.enemies = data.get("enemies", [])
    level.checkpoints = data.get("checkpoints", [])
    level.flag_pole = data.get("flag_pole", {})
    level.mario_start = data.get("mario_start", {"x": 110, "y": c.GROUND_HEIGHT})

    return level


def save_level_to_json(level: LevelData, filepath: str) -> None:
    """
    Save level data to a JSON file.

    Args:
        level: LevelData object to save
        filepath: Path to save the JSON file
    """
    data = {
        "name": level.name,
        "width": level.width,
        "height": level.height,
        "ground_height": level.ground_height,
        "camera_start_x": level.camera_start_x,
        "background_color": list(level.background_color),
        "bricks": level.bricks,
        "coin_boxes": level.coin_boxes,
        "pipes": level.pipes,
        "steps": level.steps,
        "enemies": level.enemies,
        "checkpoints": level.checkpoints,
        "flag_pole": level.flag_pole,
        "mario_start": level.mario_start,
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_level_from_tiled(filepath: str) -> LevelData:
    """
    Load level data from a Tiled map editor JSON file.

    Args:
        filepath: Path to the Tiled JSON file

    Returns:
        LevelData object with parsed level configuration

    Note:
        Requires pytmx library for full Tiled support.
        This is a basic implementation for standard Tiled JSON exports.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    level = LevelData()
    level.name = data.get("name", "Tiled Level")
    level.width = data.get("width", 0) * data.get("tilewidth", 16)
    level.height = data.get("height", 0) * data.get("tileheight", 16)

    # Process layers
    for layer in data.get("layers", []):
        layer_name = layer.get("name", "").lower()
        layer_type = layer.get("type", "tilelayer")

        if layer_type == "objectgroup":
            for obj in layer.get("objects", []):
                obj_type = obj.get("type", "")
                props = obj.get("properties", {})
                x = int(obj.get("x", 0))
                y = int(obj.get("y", 0))

                if obj_type == "brick":
                    level.bricks.append(
                        {"x": x, "y": y - obj.get("height", 32), "contents": props.get("contents", None)}
                    )
                elif obj_type == "coin_box":
                    level.coin_boxes.append(
                        {"x": x, "y": y - obj.get("height", 32), "contents": props.get("contents", c.COIN)}
                    )
                elif obj_type == "pipe":
                    level.pipes.append({"x": x, "y": y, "width": obj.get("width", 83), "height": obj.get("height", 82)})
                elif obj_type == "enemy":
                    level.enemies.append(
                        {
                            "type": props.get("enemy_type", "goomba"),
                            "x": x,
                            "y": y,
                            "direction": props.get("direction", c.LEFT),
                        }
                    )
                elif obj_type == "checkpoint":
                    level.checkpoints.append(
                        {
                            "x": x,
                            "name": props.get("name", "1"),
                            "width": obj.get("width", 10),
                            "height": obj.get("height", 600),
                        }
                    )
                elif obj_type == "mario_start":
                    level.mario_start = {"x": x, "y": y}
                elif obj_type == "flag_pole":
                    level.flag_pole = {"x": x, "y": y}

        elif layer_type == "tilelayer" and "ground" in layer_name:
            # Process ground tiles if needed
            pass

    return level


def create_level_1_1() -> LevelData:
    """
    Create the original Level 1-1 data programmatically.
    This replaces the hardcoded setup in level1.py

    Returns:
        LevelData object with Level 1-1 configuration
    """
    level = LevelData()
    level.name = "1-1"
    level.width = 8550
    level.camera_start_x = 0

    # Bricks
    level.bricks = [
        {"x": 858, "y": 365, "contents": None},
        {"x": 944, "y": 365, "contents": None},
        {"x": 1030, "y": 365, "contents": None},
        {"x": 3299, "y": 365, "contents": None},
        {"x": 3385, "y": 365, "contents": None},
        {"x": 3430, "y": 193, "contents": None},
        {"x": 3473, "y": 193, "contents": None},
        {"x": 3516, "y": 193, "contents": None},
        {"x": 3559, "y": 193, "contents": None},
        {"x": 3602, "y": 193, "contents": None},
        {"x": 3645, "y": 193, "contents": None},
        {"x": 3688, "y": 193, "contents": None},
        {"x": 3731, "y": 193, "contents": None},
        {"x": 3901, "y": 193, "contents": None},
        {"x": 3944, "y": 193, "contents": None},
        {"x": 3987, "y": 193, "contents": None},
        {"x": 4030, "y": 365, "contents": c.SIXCOINS},
        {"x": 4287, "y": 365, "contents": None},
        {"x": 4330, "y": 365, "contents": c.STAR},
        {"x": 5058, "y": 365, "contents": None},
        {"x": 5187, "y": 193, "contents": None},
        {"x": 5230, "y": 193, "contents": None},
        {"x": 5273, "y": 193, "contents": None},
        {"x": 5488, "y": 193, "contents": None},
        {"x": 5574, "y": 193, "contents": None},
        {"x": 5617, "y": 193, "contents": None},
        {"x": 5531, "y": 365, "contents": None},
        {"x": 5574, "y": 365, "contents": None},
        {"x": 7202, "y": 365, "contents": None},
        {"x": 7245, "y": 365, "contents": None},
        {"x": 7331, "y": 365, "contents": None},
    ]

    # Coin boxes
    level.coin_boxes = [
        {"x": 685, "y": 365, "contents": c.COIN},
        {"x": 901, "y": 365, "contents": c.MUSHROOM},
        {"x": 987, "y": 365, "contents": c.COIN},
        {"x": 943, "y": 193, "contents": c.COIN},
        {"x": 3342, "y": 365, "contents": c.MUSHROOM},
        {"x": 4030, "y": 193, "contents": c.COIN},
        {"x": 4544, "y": 365, "contents": c.COIN},
        {"x": 4672, "y": 365, "contents": c.COIN},
        {"x": 4672, "y": 193, "contents": c.MUSHROOM},
        {"x": 4800, "y": 365, "contents": c.COIN},
        {"x": 5531, "y": 193, "contents": c.COIN},
        {"x": 7288, "y": 365, "contents": c.COIN},
    ]

    # Pipes
    level.pipes = [
        {"x": 1202, "y": 452, "width": 83, "height": 82},
        {"x": 1631, "y": 409, "width": 83, "height": 140},
        {"x": 1973, "y": 366, "width": 83, "height": 170},
        {"x": 2445, "y": 366, "width": 83, "height": 170},
        {"x": 6989, "y": 452, "width": 83, "height": 82},
        {"x": 7675, "y": 452, "width": 83, "height": 82},
    ]

    # Steps
    level.steps = [
        {"x": 5745, "y": 495, "width": 40, "height": 44},
        {"x": 5788, "y": 452, "width": 40, "height": 44},
        {"x": 5831, "y": 409, "width": 40, "height": 44},
        {"x": 5874, "y": 366, "width": 40, "height": 176},
        {"x": 6001, "y": 366, "width": 40, "height": 176},
        {"x": 6044, "y": 408, "width": 40, "height": 40},
        {"x": 6087, "y": 452, "width": 40, "height": 40},
        {"x": 6130, "y": 495, "width": 40, "height": 40},
        {"x": 6345, "y": 495, "width": 40, "height": 40},
        {"x": 6388, "y": 452, "width": 40, "height": 40},
        {"x": 6431, "y": 409, "width": 40, "height": 40},
        {"x": 6474, "y": 366, "width": 40, "height": 40},
        {"x": 6517, "y": 366, "width": 40, "height": 176},
        {"x": 6644, "y": 366, "width": 40, "height": 176},
        {"x": 6687, "y": 408, "width": 40, "height": 40},
        {"x": 6728, "y": 452, "width": 40, "height": 40},
        {"x": 6771, "y": 495, "width": 40, "height": 40},
        {"x": 7760, "y": 495, "width": 40, "height": 40},
        {"x": 7803, "y": 452, "width": 40, "height": 40},
        {"x": 7845, "y": 409, "width": 40, "height": 40},
        {"x": 7888, "y": 366, "width": 40, "height": 40},
        {"x": 7931, "y": 323, "width": 40, "height": 40},
        {"x": 7974, "y": 280, "width": 40, "height": 40},
        {"x": 8017, "y": 237, "width": 40, "height": 40},
        {"x": 8060, "y": 194, "width": 40, "height": 40},
        {"x": 8103, "y": 194, "width": 40, "height": 360},
        {"x": 8488, "y": 495, "width": 40, "height": 40},
    ]

    # Enemies
    level.enemies = [
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 0},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 1},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 2},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 2},
        {"type": "goomba", "x": 193, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 3},
        {"type": "goomba", "x": 193, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 3},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 4},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 4},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 6},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 6},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 7},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 7},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 8},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 8},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 9},
        {"type": "goomba", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 9},
        {"type": "koopa", "x": 0, "y": c.GROUND_HEIGHT, "direction": c.LEFT, "group": 5},
    ]

    # Checkpoints
    level.checkpoints = [
        {"x": 510, "name": "1"},
        {"x": 1400, "name": "2"},
        {"x": 1740, "name": "3"},
        {"x": 3080, "name": "4"},
        {"x": 3750, "name": "5"},
        {"x": 4150, "name": "6"},
        {"x": 4470, "name": "7"},
        {"x": 4950, "name": "8"},
        {"x": 5100, "name": "9"},
        {"x": 6800, "name": "10"},
        {"x": 8504, "name": "11", "width": 5, "height": 6},
        {"x": 8775, "name": "12"},
        {"x": 2740, "name": "secret_mushroom", "width": 360, "height": 40},
    ]

    # Flag pole
    level.flag_pole = {"x": 8505, "y": 100}

    # Mario start position
    level.mario_start = {"x": 110, "y": c.GROUND_HEIGHT}

    # Ground sections
    level.ground_sections = [
        {"x": 0, "y": c.GROUND_HEIGHT, "width": 2953, "height": 60},
        {"x": 3048, "y": c.GROUND_HEIGHT, "width": 635, "height": 60},
        {"x": 3819, "y": c.GROUND_HEIGHT, "width": 2735, "height": 60},
        {"x": 6647, "y": c.GROUND_HEIGHT, "width": 2300, "height": 60},
    ]

    return level
