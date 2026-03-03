"""Tests for QuadTree spatial partitioning."""

from __future__ import annotations

import pytest
import pygame as pg

from data.quadtree import QuadTree, CollisionDetector, get_collision_detector


class TestQuadTree:
    """Tests for QuadTree class."""

    def test_creation(self) -> None:
        """Test QuadTree creation."""
        boundary = pg.Rect(0, 0, 100, 100)
        qt = QuadTree(boundary, capacity=4)
        
        assert qt.boundary == boundary
        assert qt.capacity == 4
        assert len(qt.objects) == 0
        assert not qt.divided

    def test_insert_single(self) -> None:
        """Test inserting single object."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        # Create mock object with rect
        obj = type('MockObj', (), {'rect': pg.Rect(10, 10, 10, 10)})()
        
        assert qt.insert(obj) is True
        assert len(qt.objects) == 1

    def test_insert_outside_boundary(self) -> None:
        """Test inserting object outside boundary."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        obj = type('MockObj', (), {'rect': pg.Rect(200, 200, 10, 10)})()
        
        assert qt.insert(obj) is False
        assert len(qt.objects) == 0

    def test_subdivision(self) -> None:
        """Test automatic subdivision."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=2)
        
        # Insert more than capacity
        for i in range(3):
            obj = type('MockObj', (), {'rect': pg.Rect(i * 10, i * 10, 10, 10)})()
            qt.insert(obj)
        
        assert qt.divided is True
        assert qt.northeast is not None
        assert qt.northwest is not None
        assert qt.southeast is not None
        assert qt.southwest is not None

    def test_query(self) -> None:
        """Test querying objects."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        # Insert objects
        obj1 = type('Obj1', (), {'rect': pg.Rect(10, 10, 10, 10)})()
        obj2 = type('Obj2', (), {'rect': pg.Rect(50, 50, 10, 10)})()
        obj3 = type('Obj3', (), {'rect': pg.Rect(80, 80, 10, 10)})()
        
        qt.insert(obj1)
        qt.insert(obj2)
        qt.insert(obj3)
        
        # Query area around obj1
        results = qt.query(pg.Rect(5, 5, 20, 20))
        assert obj1 in results
        assert obj2 not in results
        assert obj3 not in results

    def test_query_point(self) -> None:
        """Test point query."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        obj = type('MockObj', (), {'rect': pg.Rect(50, 50, 10, 10)})()
        qt.insert(obj)
        
        # Query exact point
        results = qt.query_point(55, 55)
        assert obj in results
        
        # Query with radius
        results = qt.query_point(55, 55, radius=20)
        assert obj in results

    def test_clear(self) -> None:
        """Test clearing QuadTree."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        for i in range(5):
            obj = type('MockObj', (), {'rect': pg.Rect(i * 10, i * 10, 10, 10)})()
            qt.insert(obj)
        
        qt.clear()
        
        assert len(qt.objects) == 0
        assert not qt.divided

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=2)
        
        for i in range(5):
            obj = type('MockObj', (), {'rect': pg.Rect(i * 10, i * 10, 10, 10)})()
            qt.insert(obj)
        
        stats = qt.get_stats()
        
        assert stats["total_objects"] == 5
        assert stats["divided"] is True
        assert stats["depth"] >= 1
        assert stats.get("children") == 4

    def test_insert_sprite(self) -> None:
        """Test inserting pygame Sprite."""
        qt = QuadTree(pg.Rect(0, 0, 100, 100), capacity=4)
        
        sprite = pg.sprite.Sprite()
        sprite.rect = pg.Rect(20, 20, 10, 10)
        
        assert qt.insert(sprite) is True
        assert len(qt.objects) == 1


class TestCollisionDetector:
    """Tests for CollisionDetector class."""

    def test_creation(self) -> None:
        """Test CollisionDetector creation."""
        detector = CollisionDetector(1000, 500)
        
        assert detector.world_bounds.width == 1000
        assert detector.world_bounds.height == 500
        assert len(detector._object_map) == 0

    def test_add_object(self) -> None:
        """Test adding object."""
        detector = CollisionDetector(1000, 500)
        
        obj = pg.sprite.Sprite()
        obj.rect = pg.Rect(100, 100, 20, 20)
        
        assert detector.add_object(obj) is True
        assert len(detector._object_map) == 1

    def test_remove_object(self) -> None:
        """Test removing object."""
        detector = CollisionDetector(1000, 500)
        
        obj = pg.sprite.Sprite()
        obj.rect = pg.Rect(100, 100, 20, 20)
        detector.add_object(obj)
        
        assert detector.remove_object(obj) is True
        assert len(detector._object_map) == 0

    def test_rebuild(self) -> None:
        """Test rebuilding from list."""
        detector = CollisionDetector(1000, 500)
        
        objects = []
        for i in range(10):
            obj = pg.sprite.Sprite()
            obj.rect = pg.Rect(i * 50, 100, 20, 20)
            objects.append(obj)
        
        detector.rebuild(objects)
        
        assert len(detector._object_map) == 10

    def test_check_collision(self) -> None:
        """Test collision detection."""
        detector = CollisionDetector(1000, 500)
        
        # Create two overlapping objects
        obj1 = pg.sprite.Sprite()
        obj1.rect = pg.Rect(100, 100, 20, 20)
        
        obj2 = pg.sprite.Sprite()
        obj2.rect = pg.Rect(110, 110, 20, 20)
        
        detector.add_object(obj1)
        detector.add_object(obj2)
        
        hit = detector.check_collision(obj1)
        assert hit is not None

    def test_check_no_collision(self) -> None:
        """Test no collision detection."""
        detector = CollisionDetector(1000, 500)
        
        obj1 = pg.sprite.Sprite()
        obj1.rect = pg.Rect(100, 100, 20, 20)
        
        obj2 = pg.sprite.Sprite()
        obj2.rect = pg.Rect(500, 500, 20, 20)
        
        detector.add_object(obj1)
        detector.add_object(obj2)
        
        hit = detector.check_collision(obj1)
        assert hit is None

    def test_get_nearby(self) -> None:
        """Test getting nearby objects."""
        detector = CollisionDetector(1000, 500)
        
        obj1 = pg.sprite.Sprite()
        obj1.rect = pg.Rect(100, 100, 20, 20)
        
        obj2 = pg.sprite.Sprite()
        obj2.rect = pg.Rect(110, 110, 20, 20)
        
        obj3 = pg.sprite.Sprite()
        obj3.rect = pg.Rect(500, 500, 20, 20)
        
        detector.add_object(obj1)
        detector.add_object(obj2)
        detector.add_object(obj3)
        
        nearby = detector.get_nearby(obj1)
        
        assert obj1 in nearby
        assert obj2 in nearby
        assert obj3 not in nearby

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        detector = CollisionDetector(1000, 500)
        
        for i in range(5):
            obj = pg.sprite.Sprite()
            obj.rect = pg.Rect(i * 50, 100, 20, 20)
            detector.add_object(obj)
        
        stats = detector.get_stats()
        
        assert stats["total_objects"] == 5
        assert "quadtree" in stats


class TestGetCollisionDetector:
    """Tests for global collision detector instance."""

    def test_singleton(self) -> None:
        """Test that global instance is singleton."""
        detector1 = get_collision_detector()
        detector2 = get_collision_detector()
        
        assert detector1 is detector2

    def test_custom_size(self) -> None:
        """Test custom world size."""
        # Create new instance by clearing global
        import data.quadtree
        data.quadtree._collision_detector = None
        
        detector = get_collision_detector(2000, 1000)
        
        assert detector.world_bounds.width == 2000
        assert detector.world_bounds.height == 1000
        
        # Reset
        data.quadtree._collision_detector = None
