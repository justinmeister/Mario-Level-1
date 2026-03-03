"""
Minimap and Radar System for Super Mario Bros.

Features:
- Real-time minimap rendering
- Entity tracking on radar
- Zoom levels
- Waypoint markers
- Fog of war (optional)
- Interactive map markers
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pygame as pg

from . import constants as c


class MapEntityType(Enum):
    """Types of entities on minimap."""

    PLAYER = auto()
    ENEMY = auto()
    ALLY = auto()
    BOSS = auto()
    ITEM = auto()
    POWERUP = auto()
    CHECKPOINT = auto()
    GOAL = auto()
    SECRET = auto()
    CUSTOM = auto()


class MarkerShape(Enum):
    """Marker shapes for minimap."""

    CIRCLE = auto()
    SQUARE = auto()
    TRIANGLE = auto()
    DIAMOND = auto()
    ARROW = auto()
    STAR = auto()


@dataclass
class MapEntity:
    """Entity displayed on minimap."""

    id: str
    entity_type: MapEntityType
    x: float
    y: float
    color: Tuple[int, int, int] = (255, 255, 255)
    shape: MarkerShape = MarkerShape.CIRCLE
    size: float = 4.0
    visible: bool = True
    pulse: bool = False
    pulse_speed: float = 3.0
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "entity_type": self.entity_type.name,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "shape": self.shape.name,
            "size": self.size,
            "visible": self.visible,
            "pulse": self.pulse,
            "pulse_speed": self.pulse_speed,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapEntity":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            entity_type=MapEntityType[data["entity_type"]],
            x=data["x"],
            y=data["y"],
            color=tuple(data.get("color", (255, 255, 255))),
            shape=MarkerShape[data.get("shape", "CIRCLE")],
            size=data.get("size", 4.0),
            visible=data.get("visible", True),
            pulse=data.get("pulse", False),
            pulse_speed=data.get("pulse_speed", 3.0),
            label=data.get("label"),
        )


@dataclass
class Waypoint:
    """Waypoint marker."""

    id: str
    x: float
    y: float
    description: str
    completed: bool = False
    optional: bool = False


@dataclass
class MinimapConfig:
    """Minimap configuration."""

    # Position
    x: int = 10
    y: int = 10
    width: int = 200
    height: int = 150

    # Scale
    zoom: float = 0.1  # World to minimap scale

    # Appearance
    bg_color: Tuple[int, int, int] = (20, 20, 40)
    border_color: Tuple[int, int, int] = (100, 100, 150)
    border_width: int = 2

    # Features
    show_border: bool = True
    show_grid: bool = False
    grid_spacing: int = 20
    fog_of_war: bool = False
    fog_radius: float = 50.0

    # Player marker
    player_color: Tuple[int, int, int] = (255, 50, 50)
    player_size: float = 6.0
    player_shape: MarkerShape = MarkerShape.ARROW

    # Entity colors
    enemy_color: Tuple[int, int, int] = (255, 0, 0)
    ally_color: Tuple[int, int, int] = (0, 255, 0)
    boss_color: Tuple[int, int, int] = (255, 100, 0)
    item_color: Tuple[int, int, int] = (255, 255, 0)
    powerup_color: Tuple[int, int, int] = (0, 255, 255)
    checkpoint_color: Tuple[int, int, int] = (0, 200, 255)
    goal_color: Tuple[int, int, int] = (100, 255, 100)
    secret_color: Tuple[int, int, int] = (255, 0, 255)


class Minimap:
    """
    Minimap/Radar system.

    Features:
    - Real-time entity tracking
    - Zoom levels
    - Waypoint markers
    - Fog of war
    - Interactive markers
    """

    def __init__(self, config: Optional[MinimapConfig] = None) -> None:
        """
        Initialize minimap.

        Args:
            config: Minimap configuration
        """
        self.config = config or MinimapConfig()

        # Entities
        self.entities: Dict[str, MapEntity] = {}
        self.waypoints: List[Waypoint] = []

        # Camera/viewport
        self.camera_x: float = 0
        self.camera_y: float = 0
        self.camera_width: float = c.SCREEN_WIDTH
        self.camera_height: float = c.SCREEN_HEIGHT

        # Level bounds
        self.level_width: float = 8550  # Default level 1-1 width
        self.level_height: float = c.SCREEN_HEIGHT

        # Fog of war
        self.explored_areas: Set[Tuple[int, int]] = set()
        self.fog_surface: Optional[pg.Surface] = None

        # Pulse animation
        self.pulse_timer: float = 0

        # Callbacks
        self.on_marker_click: Optional[Callable[[MapEntity], None]] = None

        # Create surface
        self._create_surface()

    def _create_surface(self) -> None:
        """Create minimap surface."""
        self.surface = pg.Surface(
            (self.config.width, self.config.height),
            pg.SRCALPHA
        )
        if self.config.fog_of_war:
            self.fog_surface = pg.Surface(
                (self.config.width, self.config.height),
                pg.SRCALPHA
            )

    def set_camera(self, x: float, y: float) -> None:
        """
        Set camera position.

        Args:
            x, y: Camera position in world coordinates
        """
        self.camera_x = x
        self.camera_y = y

    def set_level_bounds(self, width: float, height: float) -> None:
        """
        Set level bounds.

        Args:
            width: Level width
            height: Level height
        """
        self.level_width = width
        self.level_height = height

    def add_entity(self, entity: MapEntity) -> None:
        """
        Add entity to minimap.

        Args:
            entity: Entity to add
        """
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: str) -> None:
        """
        Remove entity from minimap.

        Args:
            entity_id: Entity ID
        """
        if entity_id in self.entities:
            del self.entities[entity_id]

    def update_entity(self, entity_id: str, x: float, y: float) -> None:
        """
        Update entity position.

        Args:
            entity_id: Entity ID
            x, y: New position
        """
        if entity_id in self.entities:
            self.entities[entity_id].x = x
            self.entities[entity_id].y = y

    def add_waypoint(self, waypoint: Waypoint) -> None:
        """
        Add waypoint.

        Args:
            waypoint: Waypoint to add
        """
        self.waypoints.append(waypoint)

    def clear_waypoints(self) -> None:
        """Clear all waypoints."""
        self.waypoints.clear()

    def update_fog_of_war(self, player_x: float, player_y: float) -> None:
        """
        Update fog of war based on player position.

        Args:
            player_x, player_y: Player position
        """
        if not self.config.fog_of_war:
            return

        # Calculate minimap position
        map_x = int((player_x - self.camera_x) * self.config.zoom)
        map_y = int((player_y - self.camera_y) * self.config.zoom)

        # Mark area as explored
        fog_radius_map = int(self.config.fog_radius * self.config.zoom)

        for dx in range(-fog_radius_map, fog_radius_map + 1):
            for dy in range(-fog_radius_map, fog_radius_map + 1):
                if dx * dx + dy * dy <= fog_radius_map * fog_radius_map:
                    mx = map_x + dx
                    my = map_y + dy
                    if 0 <= mx < self.config.width and 0 <= my < self.config.height:
                        self.explored_areas.add((mx, my))

    def _world_to_minimap(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to minimap."""
        map_x = int((x - self.camera_x) * self.config.zoom)
        map_y = int((y - self.camera_y) * self.config.zoom)
        return map_x, map_y

    def _draw_entity(self, entity: MapEntity) -> None:
        """Draw entity on minimap."""
        if not entity.visible:
            return

        map_x, map_y = self._world_to_minimap(entity.x, entity.y)

        # Check if in bounds
        if not (0 <= map_x < self.config.width and 0 <= map_y < self.config.height):
            return

        # Pulse animation
        if entity.pulse:
            self.pulse_timer += 0.05

        # Get color
        color = entity.color
        if entity.entity_type == MapEntityType.PLAYER:
            color = self.config.player_color
        elif entity.entity_type == MapEntityType.ENEMY:
            color = self.config.enemy_color
        elif entity.entity_type == MapEntityType.ALLY:
            color = self.config.ally_color
        elif entity.entity_type == MapEntityType.BOSS:
            color = self.config.boss_color
        elif entity.entity_type == MapEntityType.ITEM:
            color = self.config.item_color
        elif entity.entity_type == MapEntityType.POWERUP:
            color = self.config.powerup_color
        elif entity.entity_type == MapEntityType.CHECKPOINT:
            color = self.config.checkpoint_color
        elif entity.entity_type == MapEntityType.GOAL:
            color = self.config.goal_color
        elif entity.entity_type == MapEntityType.SECRET:
            color = self.config.secret_color

        size = int(entity.size)

        # Draw based on shape
        if entity.shape == MarkerShape.CIRCLE:
            pg.draw.circle(self.surface, color, (map_x, map_y), size)

        elif entity.shape == MarkerShape.SQUARE:
            rect = pg.Rect(map_x - size, map_y - size, size * 2, size * 2)
            pg.draw.rect(self.surface, color, rect)

        elif entity.shape == MarkerShape.TRIANGLE:
            points = [
                (map_x, map_y - size),
                (map_x - size, map_y + size),
                (map_x + size, map_y + size),
            ]
            pg.draw.polygon(self.surface, color, points)

        elif entity.shape == MarkerShape.DIAMOND:
            points = [
                (map_x, map_y - size),
                (map_x - size, map_y),
                (map_x, map_y + size),
                (map_x + size, map_y),
            ]
            pg.draw.polygon(self.surface, color, points)

        elif entity.shape == MarkerShape.ARROW:
            # Arrow pointing up (player direction)
            points = [
                (map_x, map_y - size - 2),
                (map_x - size, map_y + size),
                (map_x + size, map_y + size),
            ]
            pg.draw.polygon(self.surface, color, points)

        elif entity.shape == MarkerShape.STAR:
            # Draw star
            points = []
            for i in range(10):
                angle = math.pi * 2 * i / 10 - math.pi / 2
                r = size if i % 2 == 0 else size // 2
                px = int(map_x + math.cos(angle) * r)
                py = int(map_y + math.sin(angle) * r)
                points.append((px, py))
            pg.draw.polygon(self.surface, color, points)

    def _draw_waypoints(self) -> None:
        """Draw waypoints on minimap."""
        font = pg.font.Font(None, 14)

        for waypoint in self.waypoints:
            map_x, map_y = self._world_to_minimap(waypoint.x, waypoint.y)

            # Diamond shape for waypoints
            size = 5
            color = (100, 255, 100) if not waypoint.completed else (100, 100, 100)

            if waypoint.optional:
                color = (255, 255, 100)

            points = [
                (map_x, map_y - size),
                (map_x - size, map_y),
                (map_x, map_y + size),
                (map_x + size, map_y),
            ]
            pg.draw.polygon(self.surface, color, points, width=2)

            # Label
            if waypoint.description:
                label = font.render(waypoint.description[:10], True, color)
                self.surface.blit(label, (map_x + 8, map_y - 8))

    def _draw_grid(self) -> None:
        """Draw grid on minimap."""
        if not self.config.show_grid:
            return

        for x in range(0, self.config.width, self.config.grid_spacing):
            pg.draw.line(
                self.surface,
                (60, 60, 80),
                (x, 0),
                (x, self.config.height),
            )

        for y in range(0, self.config.height, self.config.grid_spacing):
            pg.draw.line(
                self.surface,
                (60, 60, 80),
                (0, y),
                (self.config.width, y),
            )

    def _draw_fog_of_war(self) -> None:
        """Draw fog of war overlay."""
        if not self.config.fog_of_war or self.fog_surface is None:
            return

        # Clear fog surface
        self.fog_surface.fill((0, 0, 0, 0))

        # Draw unexplored areas as black
        for x in range(self.config.width):
            for y in range(self.config.height):
                if (x, y) not in self.explored_areas:
                    self.fog_surface.set_at((x, y), (0, 0, 0, 200))

        # Blit fog surface
        self.surface.blit(self.fog_surface, (0, 0))

    def _draw_border(self) -> None:
        """Draw minimap border."""
        if not self.config.show_border:
            return

        rect = pg.Rect(0, 0, self.config.width, self.config.height)
        pg.draw.rect(self.surface, self.config.border_color, rect, self.config.border_width)

    def update(self, dt: float, player_x: float, player_y: float) -> None:
        """
        Update minimap.

        Args:
            dt: Delta time
            player_x, player_y: Player position
        """
        # Clear surface
        self.surface.fill((0, 0, 0, 0))

        # Fill background
        bg_rect = pg.Rect(0, 0, self.config.width, self.config.height)
        pg.draw.rect(self.surface, (*self.config.bg_color, 200), bg_rect)

        # Draw grid
        self._draw_grid()

        # Update fog of war
        if self.config.fog_of_war:
            self.update_fog_of_war(player_x, player_y)

        # Draw entities
        for entity in self.entities.values():
            self._draw_entity(entity)

        # Draw waypoints
        self._draw_waypoints()

        # Draw fog
        self._draw_fog_of_war()

        # Draw border
        self._draw_border()

        # Update pulse timer
        self.pulse_timer += dt

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw minimap on surface.

        Args:
            surface: Surface to draw on
        """
        surface.blit(self.surface, (self.config.x, self.config.y))

    def handle_click(self, mouse_x: int, mouse_y: int) -> Optional[MapEntity]:
        """
        Handle click on minimap.

        Args:
            mouse_x, mouse_y: Mouse position

        Returns:
            Clicked entity or None
        """
        # Adjust for minimap position
        rel_x = mouse_x - self.config.x
        rel_y = mouse_y - self.config.y

        if not (0 <= rel_x < self.config.width and 0 <= rel_y < self.config.height):
            return None

        # Check entities
        for entity in self.entities.values():
            map_x, map_y = self._world_to_minimap(entity.x, entity.y)
            dist = math.sqrt((rel_x - map_x) ** 2 + (rel_y - map_y) ** 2)

            if dist <= entity.size + 5:
                if self.on_marker_click:
                    self.on_marker_click(entity)
                return entity

        return None

    def set_zoom(self, zoom: float) -> None:
        """
        Set zoom level.

        Args:
            zoom: Zoom factor (0.05-0.5)
        """
        self.config.zoom = max(0.05, min(0.5, zoom))

    def zoom_in(self) -> None:
        """Zoom in."""
        self.set_zoom(self.config.zoom * 1.2)

    def zoom_out(self) -> None:
        """Zoom out."""
        self.set_zoom(self.config.zoom / 1.2)

    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get visible world bounds.

        Returns:
            Tuple of (x, y, width, height)
        """
        return (
            self.camera_x,
            self.camera_y,
            self.camera_width,
            self.camera_height,
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get minimap summary."""
        return {
            "entities": len(self.entities),
            "waypoints": len(self.waypoints),
            "zoom": self.config.zoom,
            "camera": (self.camera_x, self.camera_y),
            "explored": len(self.explored_areas) if self.config.fog_of_war else 0,
        }


# Entity color presets
ENTITY_COLORS: Dict[MapEntityType, Tuple[int, int, int]] = {
    MapEntityType.PLAYER: (255, 50, 50),
    MapEntityType.ENEMY: (255, 0, 0),
    MapEntityType.ALLY: (0, 255, 0),
    MapEntityType.BOSS: (255, 100, 0),
    MapEntityType.ITEM: (255, 255, 0),
    MapEntityType.POWERUP: (0, 255, 255),
    MapEntityType.CHECKPOINT: (0, 200, 255),
    MapEntityType.GOAL: (100, 255, 100),
    MapEntityType.SECRET: (255, 0, 255),
    MapEntityType.CUSTOM: (200, 200, 200),
}


# Global minimap instance
_minimap: Optional[Minimap] = None


def get_minimap() -> Minimap:
    """Get global minimap instance."""
    global _minimap
    if _minimap is None:
        _minimap = Minimap()
    return _minimap


def reset_minimap() -> None:
    """Reset global minimap instance."""
    global _minimap
    _minimap = None
