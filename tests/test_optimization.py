"""
Tests for optimization utilities.
"""
from __future__ import annotations

import pytest


class TestComputationCache:
    """Tests for ComputationCache."""

    def test_cache_creation(self):
        """Test cache initialization."""
        from data.optimization import ComputationCache

        cache = ComputationCache(max_size=10)
        assert cache.max_size == 10
        assert cache._hits == 0
        assert cache._misses == 0

    def test_cache_put_get(self):
        """Test basic put and get operations."""
        from data.optimization import ComputationCache

        cache = ComputationCache()
        cache.put("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"
        assert cache._hits == 1

    def test_cache_miss(self):
        """Test cache miss."""
        from data.optimization import ComputationCache

        cache = ComputationCache()
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache._misses == 1

    def test_cache_eviction(self):
        """Test LRU eviction."""
        from data.optimization import ComputationCache

        cache = ComputationCache(max_size=3)
        
        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Add one more - should evict key1
        cache.put("key4", "value4")
        
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"

    def test_cache_update(self):
        """Test updating existing entry."""
        from data.optimization import ComputationCache

        cache = ComputationCache()
        cache.put("key1", "value1")
        cache.put("key1", "value2")
        
        assert cache.get("key1") == "value2"

    def test_cache_clear(self):
        """Test clearing cache."""
        from data.optimization import ComputationCache

        cache = ComputationCache()
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache._hits == 0
        assert cache._misses == 1

    def test_cache_stats(self):
        """Test cache statistics."""
        from data.optimization import ComputationCache

        cache = ComputationCache(max_size=10)
        cache.put("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss
        
        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0


class TestMemoize:
    """Tests for memoize decorator."""

    def test_memoize_basic(self):
        """Test basic memoization."""
        from data.optimization import memoize

        call_count = [0]

        @memoize(max_size=10)
        def expensive_func(x, y):
            call_count[0] += 1
            return x + y

        # First call
        result1 = expensive_func(2, 3)
        assert result1 == 5
        assert call_count[0] == 1

        # Second call with same args - should use cache
        result2 = expensive_func(2, 3)
        assert result2 == 5
        assert call_count[0] == 1

    def test_memoize_different_args(self):
        """Test memoization with different arguments."""
        from data.optimization import memoize

        call_count = [0]

        @memoize(max_size=10)
        def expensive_func(x, y):
            call_count[0] += 1
            return x * y

        expensive_func(2, 3)
        expensive_func(3, 4)
        
        assert call_count[0] == 2

    def test_memoize_with_kwargs(self):
        """Test memoization with keyword arguments."""
        from data.optimization import memoize

        @memoize(max_size=10)
        def func(x, y=10):
            return x + y

        result1 = func(5, y=10)
        result2 = func(5, y=10)
        
        assert result1 == result2 == 15


class TestSpatialHash:
    """Tests for SpatialHash."""

    def test_spatial_hash_creation(self):
        """Test spatial hash initialization."""
        from data.optimization import SpatialHash

        sh = SpatialHash(cell_size=64)
        assert sh.cell_size == 64

    def test_insert_and_query(self):
        """Test inserting and querying objects."""
        from data.optimization import SpatialHash

        sh = SpatialHash(cell_size=64)
        
        obj1 = {"id": 1}
        obj2 = {"id": 2}
        
        sh.insert(obj1, 0, 0, 32, 32)
        sh.insert(obj2, 200, 200, 32, 32)  # Far away
        
        # Query near obj1
        results = sh.query(0, 0, 64, 64)
        assert obj1 in results
        assert obj2 not in results

    def test_query_overlapping(self):
        """Test querying overlapping objects."""
        from data.optimization import SpatialHash

        sh = SpatialHash(cell_size=64)
        
        obj1 = {"id": 1}
        obj2 = {"id": 2}
        
        sh.insert(obj1, 0, 0, 32, 32)
        sh.insert(obj2, 30, 30, 32, 32)
        
        # Query area that overlaps both
        results = sh.query(0, 0, 64, 64)
        assert obj1 in results
        assert obj2 in results

    def test_clear(self):
        """Test clearing spatial hash."""
        from data.optimization import SpatialHash

        sh = SpatialHash(cell_size=64)
        
        obj = {"id": 1}
        sh.insert(obj, 0, 0, 32, 32)
        
        sh.clear()
        
        results = sh.query(0, 0, 64, 64)
        assert len(results) == 0

    def test_get_stats(self):
        """Test spatial hash statistics."""
        from data.optimization import SpatialHash

        sh = SpatialHash(cell_size=64)
        
        obj1 = {"id": 1}
        obj2 = {"id": 2}
        
        sh.insert(obj1, 0, 0, 32, 32)
        sh.insert(obj2, 100, 100, 32, 32)
        
        stats = sh.get_stats()
        assert stats["cells"] >= 2
        assert stats["objects"] >= 2


class TestObjectPool:
    """Tests for ObjectPool."""

    def test_pool_creation(self):
        """Test pool initialization."""
        from data.optimization import ObjectPool

        def factory():
            return {"value": 0}

        pool = ObjectPool(factory=factory, max_size=5)
        assert pool.total_count == 0

    def test_acquire_and_release(self):
        """Test acquiring and releasing objects."""
        from data.optimization import ObjectPool

        def factory():
            return {"value": 0}

        pool = ObjectPool(factory=factory, max_size=5)
        
        obj = pool.acquire()
        assert obj is not None
        assert pool.in_use_count == 1
        
        pool.release(obj)
        assert pool.in_use_count == 0
        assert pool.available_count == 1

    def test_pool_reuse(self):
        """Test object reuse."""
        from data.optimization import ObjectPool

        def factory():
            return {"value": 0}

        def reset(obj):
            obj["value"] = 0

        pool = ObjectPool(factory=factory, reset_func=reset, max_size=5)
        
        obj1 = pool.acquire()
        obj1["value"] = 10
        pool.release(obj1)
        
        obj2 = pool.acquire()
        assert obj2 is obj1
        assert obj2["value"] == 0  # Reset was called

    def test_pool_max_size(self):
        """Test pool max size limit."""
        from data.optimization import ObjectPool

        def factory():
            return {"value": 0}

        pool = ObjectPool(factory=factory, max_size=2)
        
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        obj3 = pool.acquire()
        
        pool.release(obj1)
        pool.release(obj2)
        pool.release(obj3)
        
        # Only 2 should be pooled
        assert pool.available_count == 2
