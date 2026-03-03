"""
QuadTree spatial partitioning for efficient collision detection.

Divides 2D space into quadrants for O(log n) collision queries
instead of O(n) brute force checking.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import pygame as pg


class QuadTree:
    """
    QuadTree data structure for spatial partitioning.

    Recursively subdivides space into 4 quadrants to efficiently
    store and query objects in 2D space.

    Example:
        qt = QuadTree(pg.Rect(0, 0, 1000, 1000), capacity=4)
        qt.insert(sprite)
        nearby = qt.query(pg.Rect(100, 100, 50, 50))
    """

    def __init__(self, boundary: pg.Rect, capacity: int = 4) -> None:
        """
        Initialize QuadTree.

        Args:
            boundary: Rectangular boundary of this quadrant
            capacity: Max objects before subdivision
        """
        self.boundary = boundary
        self.capacity = capacity
        self.objects: List[Any] = []
        self.divided = False

        # Child quadrants (NE, NW, SE, SW)
        self.northeast: Optional[QuadTree] = None
        self.northwest: Optional[QuadTree] = None
        self.southeast: Optional[QuadTree] = None
        self.southwest: Optional[QuadTree] = None

    def subdivide(self) -> None:
        """Subdivide current quadrant into 4 children."""
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width // 2
        h = self.boundary.height // 2

        self.northeast = QuadTree(pg.Rect(x + w, y, w, h), self.capacity)
        self.northwest = QuadTree(pg.Rect(x, y, w, h), self.capacity)
        self.southeast = QuadTree(pg.Rect(x + w, y + h, w, h), self.capacity)
        self.southwest = QuadTree(pg.Rect(x, y + h, w, h), self.capacity)

        self.divided = True

    def insert(self, obj: Any) -> bool:
        """
        Insert object into QuadTree.

        Args:
            obj: Object with 'rect' attribute (pygame.Sprite-like)

        Returns:
            True if object was inserted successfully
        """
        if not hasattr(obj, "rect"):
            return False

        rect = obj.rect

        # Check if object is within boundary
        if not self._intersects(rect):
            return False

        # If capacity not reached, add here
        if len(self.objects) < self.capacity and not self.divided:
            self.objects.append(obj)
            return True

        # Subdivide if needed
        if not self.divided:
            self.subdivide()

        # Try to insert into children
        if self.northeast and self.northeast.insert(obj):
            return True
        if self.northwest and self.northwest.insert(obj):
            return True
        if self.southeast and self.southeast.insert(obj):
            return True
        if self.southwest and self.southwest.insert(obj):
            return True

        # If doesn't fit in children, keep here
        self.objects.append(obj)
        return True

    def _intersects(self, rect: pg.Rect) -> bool:
        """Check if rect intersects boundary."""
        return not (
            rect.right < self.boundary.left
            or rect.left > self.boundary.right
            or rect.bottom < self.boundary.top
            or rect.top > self.boundary.bottom
        )

    def query(self, range_rect: pg.Rect) -> List[Any]:
        """
        Query all objects within a range.

        Args:
            range_rect: Area to search

        Returns:
            List of objects found
        """
        found: List[Any] = []

        # Return if no intersection
        if not self._intersects(range_rect):
            return found

        # Check objects in this node
        for obj in self.objects:
            if hasattr(obj, "rect") and obj.rect.colliderect(range_rect):
                found.append(obj)

        # Recursively query children
        if self.divided:
            if self.northeast:
                found.extend(self.northeast.query(range_rect))
            if self.northwest:
                found.extend(self.northwest.query(range_rect))
            if self.southeast:
                found.extend(self.southeast.query(range_rect))
            if self.southwest:
                found.extend(self.southwest.query(range_rect))

        return found

    def query_point(self, x: float, y: float, radius: float = 0) -> List[Any]:
        """
        Query objects near a point.

        Args:
            x, y: Point coordinates
            radius: Search radius (0 for exact point)

        Returns:
            List of objects found
        """
        if radius > 0:
            return self.query(pg.Rect(x - radius, y - radius, radius * 2, radius * 2))
        else:
            return self.query(pg.Rect(x, y, 1, 1))

    def clear(self) -> None:
        """Clear all objects from QuadTree."""
        self.objects.clear()

        if self.divided:
            if self.northeast:
                self.northeast.clear()
            if self.northwest:
                self.northwest.clear()
            if self.southeast:
                self.southeast.clear()
            if self.southwest:
                self.southwest.clear()

        # Reset division state
        self.divided = False
        self.northeast = None
        self.northwest = None
        self.southeast = None
        self.southwest = None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get QuadTree statistics.

        Returns:
            Dictionary with stats
        """
        stats = {
            "depth": 0,
            "total_objects": len(self.objects),
            "divided": self.divided,
        }

        if self.divided:
            ne_stats = self.northeast.get_stats() if self.northeast else {}
            nw_stats = self.northwest.get_stats() if self.northwest else {}
            se_stats = self.southeast.get_stats() if self.southeast else {}
            sw_stats = self.southwest.get_stats() if self.southwest else {}

            stats["depth"] = 1 + max(
                ne_stats.get("depth", 0),
                nw_stats.get("depth", 0),
                se_stats.get("depth", 0),
                sw_stats.get("depth", 0),
            )
            stats["total_objects"] += (
                ne_stats.get("total_objects", 0)
                + nw_stats.get("total_objects", 0)
                + se_stats.get("total_objects", 0)
                + sw_stats.get("total_objects", 0)
            )
            stats["children"] = 4

        return stats


class CollisionDetector:
    """
    High-level collision detection using QuadTree.

    Provides optimized collision checks for game objects.
    """

    def __init__(self, world_width: int, world_height: int, capacity: int = 4) -> None:
        """
        Initialize collision detector.

        Args:
            world_width: Total world width
            world_height: Total world height
            capacity: QuadTree node capacity
        """
        self.world_bounds = pg.Rect(0, 0, world_width, world_height)
        self.quadtree = QuadTree(self.world_bounds, capacity)
        self._object_map: Dict[int, Any] = {}  # id(obj) -> obj

    def add_object(self, obj: Any) -> bool:
        """
        Add object to collision detection.

        Args:
            obj: Object with 'rect' attribute

        Returns:
            True if added successfully
        """
        if not hasattr(obj, "rect"):
            return False

        self._object_map[id(obj)] = obj
        return self.quadtree.insert(obj)

    def remove_object(self, obj: Any) -> bool:
        """
        Remove object from collision detection.

        Args:
            obj: Object to remove

        Returns:
            True if removed
        """
        obj_id = id(obj)
        if obj_id in self._object_map:
            del self._object_map[obj_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all objects."""
        self.quadtree.clear()
        self._object_map.clear()

    def rebuild(self, objects: List[Any]) -> None:
        """
        Rebuild QuadTree from object list.

        More efficient than individual add/remove for bulk updates.

        Args:
            objects: List of objects to add
        """
        self.clear()
        for obj in objects:
            self.add_object(obj)

    def check_collision(
        self,
        obj: Any,
        groups: Optional[List[pg.sprite.Group]] = None,
    ) -> Optional[Any]:
        """
        Check if object collides with anything.

        Args:
            obj: Object to check
            groups: Optional groups to check against

        Returns:
            First colliding object or None
        """
        if not hasattr(obj, "rect"):
            return None

        nearby = self.quadtree.query(obj.rect)

        for other in nearby:
            if other is obj:
                continue
            if hasattr(other, "rect") and obj.rect.colliderect(other.rect):
                return other

        # Also check provided groups
        if groups:
            for group in groups:
                hit = pg.sprite.spritecollideany(obj, group)
                if hit:
                    return hit

        return None

    def check_collisions_group(
        self,
        obj: Any,
        target_group: pg.sprite.Group,
    ) -> List[Any]:
        """
        Check all collisions for an object against a group.

        Args:
            obj: Object to check
            target_group: Group to check against

        Returns:
            List of colliding objects
        """
        if not hasattr(obj, "rect"):
            return []

        collisions = []
        nearby = self.quadtree.query(obj.rect)

        for other in nearby:
            if other is obj:
                continue
            if other in target_group:
                if hasattr(other, "rect") and obj.rect.colliderect(other.rect):
                    collisions.append(other)

        return collisions

    def get_nearby(self, obj: Any, margin: int = 0) -> List[Any]:
        """
        Get all objects near an object.

        Args:
            obj: Object to query around
            margin: Extra margin around object

        Returns:
            List of nearby objects
        """
        if not hasattr(obj, "rect"):
            return []

        rect = obj.rect.inflate(margin * 2, margin * 2)
        return self.quadtree.query(rect)

    def get_stats(self) -> Dict[str, Any]:
        """Get collision detector statistics."""
        qt_stats = self.quadtree.get_stats()
        return {
            "total_objects": len(self._object_map),
            "quadtree": qt_stats,
        }


# Global collision detector instance
_collision_detector: Optional[CollisionDetector] = None


def get_collision_detector(
    world_width: int = 10000,
    world_height: int = 1000,
) -> CollisionDetector:
    """
    Get global collision detector instance.

    Args:
        world_width: Total world width
        world_height: Total world height

    Returns:
        Collision detector instance
    """
    global _collision_detector
    if _collision_detector is None:
        _collision_detector = CollisionDetector(world_width, world_height)
    return _collision_detector
