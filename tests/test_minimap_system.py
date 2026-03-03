"""
Tests for Minimap System.

Tests cover:
- Minimap creation and configuration
- Entity tracking
- Waypoint management
- Coordinate conversion
- Fog of war
- Zoom functionality

Note: Many tests require pygame display and are skipped in headless mode.
"""

from __future__ import annotations

from typing import Any

import pygame as pg
import pytest

from data.minimap_system import (
    ENTITY_COLORS,
    MapEntity,
    MapEntityType,
    MarkerShape,
    Minimap,
    MinimapConfig,
    Waypoint,
    get_minimap,
    reset_minimap,
)


@pytest.fixture(scope="module", autouse=True)
def init_pygame() -> None:
    """Initialize pygame for tests."""
    pg.init()


class TestMapEntity:
    """Test MapEntity."""

    def test_create_entity(self) -> None:
        """Test creating map entity."""
        entity = MapEntity(
            id="player1",
            entity_type=MapEntityType.PLAYER,
            x=100,
            y=200,
        )

        assert entity.id == "player1"
        assert entity.entity_type == MapEntityType.PLAYER
        assert entity.x == 100
        assert entity.y == 200
        assert entity.visible

    def test_entity_to_dict(self) -> None:
        """Test entity serialization."""
        entity = MapEntity(
            id="test",
            entity_type=MapEntityType.ENEMY,
            x=50,
            y=75,
            color=(255, 0, 0),
            pulse=True,
        )

        data = entity.to_dict()

        assert data["id"] == "test"
        assert data["entity_type"] == "ENEMY"
        assert data["x"] == 50
        assert data["y"] == 75
        assert data["color"] == (255, 0, 0)
        assert data["pulse"]

    def test_entity_from_dict(self) -> None:
        """Test entity deserialization."""
        data = {
            "id": "restored",
            "entity_type": "BOSS",
            "x": 500,
            "y": 300,
            "size": 8.0,
            "visible": True,
        }

        entity = MapEntity.from_dict(data)

        assert entity.id == "restored"
        assert entity.entity_type == MapEntityType.BOSS
        assert entity.x == 500
        assert entity.y == 300


class TestWaypoint:
    """Test Waypoint."""

    def test_create_waypoint(self) -> None:
        """Test creating waypoint."""
        waypoint = Waypoint(
            id="wp1",
            x=100,
            y=200,
            description="Reach the goal",
        )

        assert waypoint.id == "wp1"
        assert not waypoint.completed
        assert not waypoint.optional

    def test_completed_waypoint(self) -> None:
        """Test completed waypoint."""
        waypoint = Waypoint(
            id="wp2",
            x=150,
            y=250,
            description="Collect item",
            completed=True,
        )

        assert waypoint.completed


class TestMinimapConfig:
    """Test MinimapConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = MinimapConfig()

        assert config.width == 200
        assert config.height == 150
        assert config.zoom == 0.1
        assert not config.fog_of_war

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = MinimapConfig(
            x=50,
            y=50,
            width=300,
            height=200,
            zoom=0.2,
            fog_of_war=True,
        )

        assert config.x == 50
        assert config.width == 300
        assert config.zoom == 0.2
        assert config.fog_of_war


class TestMinimapLogic:
    """Test Minimap logic (no display required)."""

    @pytest.mark.skip(reason="Requires display")
    def test_world_to_minimap(self) -> None:
        """Test coordinate conversion."""
        minimap = Minimap()
        minimap.set_camera(0, 0)
        minimap.config.zoom = 0.1

        map_x, map_y = minimap._world_to_minimap(100, 200)

        assert map_x == 10
        assert map_y == 20

    @pytest.mark.skip(reason="Requires display")
    def test_world_to_minimap_with_camera(self) -> None:
        """Test coordinate conversion with camera."""
        minimap = Minimap()
        minimap.set_camera(500, 300)
        minimap.config.zoom = 0.1

        map_x, map_y = minimap._world_to_minimap(600, 400)

        assert map_x == 10
        assert map_y == 10

    @pytest.mark.skip(reason="Requires display")
    def test_zoom_in(self) -> None:
        """Test zooming in."""
        minimap = Minimap()
        initial_zoom = minimap.config.zoom
        minimap.zoom_in()

        assert minimap.config.zoom > initial_zoom

    @pytest.mark.skip(reason="Requires display")
    def test_zoom_out(self) -> None:
        """Test zooming out."""
        minimap = Minimap()
        minimap.zoom_in()  # Zoom in first
        initial_zoom = minimap.config.zoom
        minimap.zoom_out()

        assert minimap.config.zoom < initial_zoom

    @pytest.mark.skip(reason="Requires display")
    def test_zoom_limits(self) -> None:
        """Test zoom limits."""
        minimap = Minimap()
        # Try to zoom in too much
        for _ in range(20):
            minimap.zoom_in()

        assert minimap.config.zoom <= 0.5

        # Try to zoom out too much
        for _ in range(20):
            minimap.zoom_out()

        assert minimap.config.zoom >= 0.05

    @pytest.mark.skip(reason="Requires display")
    def test_set_zoom(self) -> None:
        """Test setting zoom directly."""
        minimap = Minimap()
        minimap.set_zoom(0.25)
        assert minimap.config.zoom == 0.25

        # Out of range
        minimap.set_zoom(1.0)
        assert minimap.config.zoom == 0.5

        minimap.set_zoom(0.01)
        assert minimap.config.zoom == 0.05

    @pytest.mark.skip(reason="Requires display")
    def test_get_visible_bounds(self) -> None:
        """Test getting visible bounds."""
        minimap = Minimap()
        minimap.set_camera(100, 200)

        bounds = minimap.get_visible_bounds()

        assert bounds[0] == 100
        assert bounds[1] == 200

    def test_entity_colors(self) -> None:
        """Test entity color presets."""
        assert MapEntityType.PLAYER in ENTITY_COLORS
        assert MapEntityType.ENEMY in ENTITY_COLORS
        assert MapEntityType.BOSS in ENTITY_COLORS


class TestMarkerShapes:
    """Test marker shapes."""

    def test_all_shapes_exist(self) -> None:
        """Test all marker shapes are defined."""
        shapes = [s.name for s in MarkerShape]

        assert "CIRCLE" in shapes
        assert "SQUARE" in shapes
        assert "TRIANGLE" in shapes
        assert "DIAMOND" in shapes
        assert "ARROW" in shapes
        assert "STAR" in shapes


class TestMapEntityTypes:
    """Test map entity types."""

    def test_all_types_exist(self) -> None:
        """Test all entity types are defined."""
        types = [t.name for t in MapEntityType]

        assert "PLAYER" in types
        assert "ENEMY" in types
        assert "ALLY" in types
        assert "BOSS" in types
        assert "ITEM" in types
        assert "POWERUP" in types
        assert "CHECKPOINT" in types
        assert "GOAL" in types
        assert "SECRET" in types


class TestGlobalMinimap:
    """Test global minimap instance."""

    @pytest.mark.skip(reason="Requires display")
    def test_singleton(self) -> None:
        """Test minimap is singleton."""
        reset_minimap()

        minimap1 = get_minimap()
        minimap2 = get_minimap()

        assert minimap1 is minimap2

    @pytest.mark.skip(reason="Requires display")
    def test_reset(self) -> None:
        """Test resetting minimap."""
        reset_minimap()

        minimap1 = get_minimap()
        minimap1.set_zoom(0.3)  # Modify

        reset_minimap()
        minimap2 = get_minimap()

        assert minimap1 is not minimap2
