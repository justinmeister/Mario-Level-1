"""
Tests for the save system module.
"""
from __future__ import annotations

import json
import os
import pytest

from data import save_system
from data import constants as c


class TestGameSave:
    """Tests for GameSave class."""

    def test_game_save_creation(self):
        """Test that GameSave can be created with default values."""
        save = save_system.GameSave()
        assert save.score == 0
        assert save.coin_total == 0
        assert save.lives == 3
        assert save.top_score == 0
        assert save.current_level == c.LEVEL1
        assert save.levels_completed == []

    def test_game_save_to_dict(self):
        """Test converting GameSave to dictionary."""
        save = save_system.GameSave()
        save.score = 1500
        save.lives = 5

        data = save.to_dict()
        assert data["score"] == 1500
        assert data["lives"] == 5
        assert data["coin_total"] == 0

    def test_game_save_from_dict(self):
        """Test creating GameSave from dictionary."""
        data = {
            "score": 2000,
            "coin_total": 50,
            "lives": 2,
            "top_score": 5000,
            "levels_completed": ["1-1", "1-2"],
            "enemies_defeated": 25,
        }

        save = save_system.GameSave.from_dict(data)
        assert save.score == 2000
        assert save.coin_total == 50
        assert save.lives == 2
        assert len(save.levels_completed) == 2

    def test_game_save_roundtrip(self):
        """Test that to_dict and from_dict are inverse operations."""
        original = save_system.GameSave()
        original.score = 3000
        original.coin_total = 100
        original.lives = 4
        original.levels_completed = ["1-1"]
        original.enemies_defeated = 10

        data = original.to_dict()
        restored = save_system.GameSave.from_dict(data)

        assert restored.score == original.score
        assert restored.coin_total == original.coin_total
        assert restored.lives == original.lives
        assert restored.levels_completed == original.levels_completed


class TestSaveLoad:
    """Tests for save/load functions."""

    def test_save_and_load(self, tmp_path):
        """Test saving and loading game."""
        # Temporarily change save directory
        original_dir = save_system.SAVE_DIR
        original_file = save_system.SAVE_FILE

        save_system.SAVE_DIR = str(tmp_path)
        save_system.SAVE_FILE = os.path.join(str(tmp_path), "test_save.json")

        try:
            save = save_system.GameSave()
            save.score = 1000
            save.lives = 5

            # Save
            result = save_system.save_game(save)
            assert result is True
            assert os.path.exists(save_system.SAVE_FILE)

            # Load
            loaded = save_system.load_game()
            assert loaded is not None
            assert loaded.score == 1000
            assert loaded.lives == 5
        finally:
            # Restore original paths
            save_system.SAVE_DIR = original_dir
            save_system.SAVE_FILE = original_file

    def test_load_nonexistent(self, tmp_path):
        """Test loading when no save file exists."""
        original_file = save_system.SAVE_FILE
        save_system.SAVE_FILE = os.path.join(str(tmp_path), "nonexistent.json")

        try:
            result = save_system.load_game()
            assert result is None
        finally:
            save_system.SAVE_FILE = original_file

    def test_delete_save(self, tmp_path):
        """Test deleting save file."""
        original_dir = save_system.SAVE_DIR
        original_file = save_system.SAVE_FILE

        save_system.SAVE_DIR = str(tmp_path)
        save_system.SAVE_FILE = os.path.join(str(tmp_path), "test_save.json")

        try:
            # Create save
            save = save_system.GameSave()
            save_system.save_game(save)
            assert os.path.exists(save_system.SAVE_FILE)

            # Delete save
            result = save_system.delete_save()
            assert result is True
            assert not os.path.exists(save_system.SAVE_FILE)
        finally:
            save_system.SAVE_DIR = original_dir
            save_system.SAVE_FILE = original_file

    def test_save_exists(self, tmp_path):
        """Test save_exists function."""
        original_file = save_system.SAVE_FILE
        save_system.SAVE_FILE = os.path.join(str(tmp_path), "test_save.json")

        try:
            assert save_system.save_exists() is False

            save = save_system.GameSave()
            save_system.save_game(save)
            assert save_system.save_exists() is True
        finally:
            save_system.SAVE_FILE = original_file

    def test_get_save_info(self, tmp_path):
        """Test getting save info without full load."""
        original_file = save_system.SAVE_FILE
        save_system.SAVE_FILE = os.path.join(str(tmp_path), "test_save.json")

        try:
            # No save exists
            assert save_system.get_save_info() is None

            # Create save
            save = save_system.GameSave()
            save.score = 2500
            save_system.save_game(save)

            info = save_system.get_save_info()
            assert info is not None
            assert info["score"] == 2500
            assert "timestamp" in info
        finally:
            save_system.SAVE_FILE = original_file


class TestGameInfoConversion:
    """Tests for game_info conversion functions."""

    def test_create_save_from_game_info(self):
        """Test creating save from game_info."""
        game_info = {c.SCORE: 1500, c.COIN_TOTAL: 30, c.LIVES: 4, c.TOP_SCORE: 5000}

        save = save_system.create_save_from_game_info(game_info)
        assert save.score == 1500
        assert save.coin_total == 30
        assert save.lives == 4

    def test_update_game_info_from_save(self):
        """Test updating game_info from save."""
        game_info = {c.SCORE: 0, c.LIVES: 3}

        save = save_system.GameSave()
        save.score = 2000
        save.lives = 5

        save_system.update_game_info_from_save(game_info, save)
        assert game_info[c.SCORE] == 2000
        assert game_info[c.LIVES] == 5


class TestSaveManagerCaching:
    """Tests for SaveManager caching functionality."""

    def test_cache_on_load(self, tmp_path):
        """Test that loaded data is cached."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Create and save game data
            game_data = save_system.GameData(score=1000, coin_total=50)
            manager.save_game(1, game_data)

            # Load and check cache
            loaded = manager.load_game(1)
            assert loaded is not None
            assert loaded.score == 1000

            # Check cache stats
            stats = manager.get_cache_stats()
            assert stats["cached_slots"] >= 1

        finally:
            save_system.SAVE_DIR = original_dir

    def test_cache_hit_on_repeated_load(self, tmp_path):
        """Test that repeated loads use cache."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Create and save game data
            game_data = save_system.GameData(score=2000)
            manager.save_game(1, game_data)

            # Load twice - second should use cache
            loaded1 = manager.load_game(1)
            loaded2 = manager.load_game(1)

            assert loaded1 is not None
            assert loaded2 is not None
            assert loaded1.score == 2000
            assert loaded2.score == 2000

            # Should be same object (cached)
            assert loaded1 is loaded2

        finally:
            save_system.SAVE_DIR = original_dir

    def test_cache_invalidation_on_save(self, tmp_path):
        """Test that cache is invalidated on new save."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Create and save game data
            game_data1 = save_system.GameData(score=1000)
            manager.save_game(1, game_data1)

            # Load to populate cache
            loaded = manager.load_game(1)
            assert loaded.score == 1000

            # Save new data
            game_data2 = save_system.GameData(score=2000)
            manager.save_game(1, game_data2)

            # Load should return new data from cache
            loaded2 = manager.load_game(1)
            assert loaded2.score == 2000

        finally:
            save_system.SAVE_DIR = original_dir

    def test_clear_cache(self, tmp_path):
        """Test clearing cache."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Create and save game data
            game_data = save_system.GameData(score=3000)
            manager.save_game(1, game_data)
            manager.load_game(1)  # Populate cache

            # Check cache has data
            stats = manager.get_cache_stats()
            assert stats["cached_slots"] >= 1

            # Clear cache
            manager.clear_cache()

            # Cache should be empty
            stats = manager.get_cache_stats()
            assert stats["cached_slots"] == 0

        finally:
            save_system.SAVE_DIR = original_dir

    def test_clear_cache_single_slot(self, tmp_path):
        """Test clearing cache for single slot."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Create saves in multiple slots
            manager.save_game(1, save_system.GameData(score=1000))
            manager.save_game(2, save_system.GameData(score=2000))

            # Load both
            manager.load_game(1)
            manager.load_game(2)

            # Clear only slot 1
            manager.clear_cache(slot=1)

            # Slot 2 should still be cached
            stats = manager.get_cache_stats()
            assert stats["cached_slots"] == 1

        finally:
            save_system.SAVE_DIR = original_dir

    def test_cache_stats(self, tmp_path):
        """Test cache statistics."""
        original_dir = save_system.SAVE_DIR
        save_system.SAVE_DIR = str(tmp_path)

        try:
            manager = save_system.SaveManager()

            # Initial stats
            stats = manager.get_cache_stats()
            assert stats["cached_slots"] == 0
            assert stats["max_slots"] == save_system.MAX_SAVE_SLOTS
            assert stats["metadata_loaded"] == 1

        finally:
            save_system.SAVE_DIR = original_dir
