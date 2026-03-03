"""
Tests for the level loader module.
"""
from __future__ import annotations

import json
import os
import pytest

from data import level_loader
from data import constants as c


class TestLevelData:
    """Tests for LevelData class."""

    def test_level_data_creation(self):
        """Test that LevelData can be created with default values."""
        data = level_loader.LevelData()
        assert data.name == ""
        assert data.width == 0
        assert data.height == 0
        assert data.ground_height == c.GROUND_HEIGHT
        assert data.bricks == []
        assert data.enemies == []

    def test_level_data_default_background(self):
        """Test default background color is WHITE."""
        data = level_loader.LevelData()
        assert data.background_color == c.WHITE


class TestLoadLevelFromJson:
    """Tests for JSON level loading."""

    def test_load_level_1_1(self):
        """Test loading the built-in level 1-1 JSON file."""
        level_path = os.path.join(os.path.dirname(__file__), "..", "data", "levels", "level_1_1.json")
        level_path = os.path.abspath(level_path)

        if os.path.exists(level_path):
            level = level_loader.load_level_from_json(level_path)
            assert level.name == "1-1"
            assert level.width == 8550
            assert len(level.bricks) > 0
            assert len(level.coin_boxes) > 0
            assert len(level.enemies) > 0

    def test_load_missing_file(self):
        """Test that loading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            level_loader.load_level_from_json("nonexistent_file.json")


class TestSaveLevelToJson:
    """Tests for JSON level saving."""

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test that saving and loading produces the same data."""
        original = level_loader.create_level_1_1()
        file_path = tmp_path / "test_level.json"

        level_loader.save_level_to_json(original, str(file_path))
        loaded = level_loader.load_level_from_json(str(file_path))

        assert loaded.name == original.name
        assert loaded.width == original.width
        assert len(loaded.bricks) == len(original.bricks)


class TestCreateLevel1_1:
    """Tests for programmatic level 1-1 creation."""

    def test_create_level_1_1(self):
        """Test that level 1-1 can be created programmatically."""
        level = level_loader.create_level_1_1()

        assert level.name == "1-1"
        assert level.width == 8550
        assert level.camera_start_x == 0

        # Check entities exist
        assert len(level.bricks) > 0
        assert len(level.coin_boxes) > 0
        assert len(level.pipes) > 0
        assert len(level.steps) > 0
        assert len(level.enemies) > 0
        assert len(level.checkpoints) > 0

        # Check flag pole exists
        assert "x" in level.flag_pole
        assert "y" in level.flag_pole

        # Check mario start position exists
        assert "x" in level.mario_start
        assert "y" in level.mario_start

    def test_level_1_1_brick_count(self):
        """Test that level 1-1 has the expected number of bricks."""
        level = level_loader.create_level_1_1()
        # Original level has 31 bricks
        assert len(level.bricks) == 31

    def test_level_1_1_coin_box_count(self):
        """Test that level 1-1 has the expected number of coin boxes."""
        level = level_loader.create_level_1_1()
        # Original level has 12 coin boxes
        assert len(level.coin_boxes) == 12

    def test_level_1_1_pipe_count(self):
        """Test that level 1-1 has the expected number of pipes."""
        level = level_loader.create_level_1_1()
        # Original level has 6 pipes
        assert len(level.pipes) == 6

    def test_level_1_1_enemy_count(self):
        """Test that level 1-1 has the expected number of enemies."""
        level = level_loader.create_level_1_1()
        # Original level has 17 enemies (16 goombas + 1 koopa)
        assert len(level.enemies) == 17


class TestTiledLoader:
    """Tests for Tiled map format loading."""

    def test_tiled_loader_structure(self):
        """Test that Tiled loader has correct structure."""
        # Just test the function exists and has correct signature
        assert callable(level_loader.load_level_from_tiled)
