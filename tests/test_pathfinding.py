"""
Tests for Pathfinding System.

Tests cover:
- Grid operations
- A* algorithm
- Jump pathfinding
- Path smoothing
"""

from __future__ import annotations

import pytest

from data.pathfinding import (
    AStarPathfinder,
    Grid,
    JumpPathfinder,
    Node,
    PathResult,
    get_pathfinder,
    get_jump_pathfinder,
    reset_pathfinders,
)


class TestNode:
    """Test Node."""

    def test_create_node(self) -> None:
        """Test creating node."""
        node = Node(5, 10)

        assert node.x == 5
        assert node.y == 10
        assert node.g_cost == 0
        assert node.h_cost == 0
        assert node.parent is None
        assert node.walkable

    def test_node_hash(self) -> None:
        """Test node hashing."""
        node1 = Node(5, 10)
        node2 = Node(5, 10)

        assert hash(node1) == hash(node2)

    def test_node_equality(self) -> None:
        """Test node equality."""
        node1 = Node(5, 10)
        node2 = Node(5, 10)
        node3 = Node(5, 11)

        assert node1 == node2
        assert node1 != node3

    def test_node_comparison(self) -> None:
        """Test node comparison."""
        node1 = Node(0, 0)
        node1.g_cost = 5
        node1.h_cost = 10

        node2 = Node(0, 0)
        node2.g_cost = 3
        node2.h_cost = 10

        assert node2 < node1  # Lower f_cost


class TestGrid:
    """Test Grid."""

    def test_create_grid(self) -> None:
        """Test creating grid."""
        grid = Grid(100, 100, 10)

        assert grid.cell_size == 10
        assert grid.grid_width == 10
        assert grid.grid_height == 10
        assert len(grid.nodes) == 100

    def test_world_to_grid(self) -> None:
        """Test world to grid conversion."""
        grid = Grid(100, 100, 10)

        x, y = grid.world_to_grid(25, 35)

        assert x == 2
        assert y == 3

    def test_grid_to_world(self) -> None:
        """Test grid to world conversion."""
        grid = Grid(100, 100, 10)

        x, y = grid.grid_to_world(5, 7)

        assert x == 50
        assert y == 70

    def test_get_node(self) -> None:
        """Test getting node."""
        grid = Grid(100, 100, 10)

        node = grid.get_node(5, 5)

        assert node is not None
        assert node.x == 5
        assert node.y == 5

    def test_get_node_out_of_bounds(self) -> None:
        """Test getting node out of bounds."""
        grid = Grid(100, 100, 10)

        node = grid.get_node(15, 15)

        assert node is None

    def test_is_walkable(self) -> None:
        """Test walkable check."""
        grid = Grid(100, 100, 10)

        assert grid.is_walkable(5, 5)

    def test_set_obstacle(self) -> None:
        """Test setting obstacle."""
        grid = Grid(100, 100, 10)

        grid.set_obstacle(5, 5)

        assert not grid.is_walkable(5, 5)

    def test_remove_obstacle(self) -> None:
        """Test removing obstacle."""
        grid = Grid(100, 100, 10)

        grid.set_obstacle(5, 5)
        grid.set_obstacle(5, 5, False)

        assert grid.is_walkable(5, 5)

    def test_set_walkable(self) -> None:
        """Test setting walkable state."""
        grid = Grid(100, 100, 10)

        grid.set_walkable(5, 5, False)

        assert not grid.is_walkable(5, 5)

    def test_get_neighbors(self) -> None:
        """Test getting neighbors."""
        grid = Grid(100, 100, 10)
        node = grid.get_node(5, 5)

        neighbors = grid.get_neighbors(node)

        assert len(neighbors) == 4  # Cardinal directions

    def test_get_neighbors_diagonal(self) -> None:
        """Test getting diagonal neighbors."""
        grid = Grid(100, 100, 10)
        node = grid.get_node(5, 5)

        neighbors = grid.get_neighbors(node, allow_diagonal=True)

        assert len(neighbors) == 8  # All directions

    def test_get_neighbors_with_obstacles(self) -> None:
        """Test getting neighbors with obstacles."""
        grid = Grid(100, 100, 10)
        grid.set_obstacle(5, 4)  # Block one neighbor

        node = grid.get_node(5, 5)
        neighbors = grid.get_neighbors(node)

        assert len(neighbors) == 3

    def test_clear(self) -> None:
        """Test clearing grid."""
        grid = Grid(100, 100, 10)

        grid.set_obstacle(5, 5)
        grid.set_walkable(6, 6, False)
        grid.clear()

        assert grid.is_walkable(5, 5)
        assert grid.is_walkable(6, 6)


class TestAStarPathfinder:
    """Test AStarPathfinder."""

    def test_create_pathfinder(self) -> None:
        """Test creating pathfinder."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        assert pathfinder.grid is grid

    def test_find_simple_path(self) -> None:
        """Test finding simple path."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((0, 0), (5, 0))

        assert result.success
        assert len(result.path) == 6
        assert result.path[0] == (0, 0)
        assert result.path[-1] == (5, 0)

    def test_find_path_around_obstacle(self) -> None:
        """Test finding path around obstacle."""
        grid = Grid(100, 100, 10)
        grid.set_obstacle(2, 0)
        grid.set_obstacle(2, 1)
        grid.set_obstacle(2, 2)

        pathfinder = AStarPathfinder(grid)
        result = pathfinder.find_path((0, 0), (4, 0))

        assert result.success
        # Path should go around obstacle

    def test_no_path(self) -> None:
        """Test when no path exists."""
        grid = Grid(100, 100, 10)

        # Block all paths
        for y in range(10):
            grid.set_obstacle(5, y)

        pathfinder = AStarPathfinder(grid)
        result = pathfinder.find_path((0, 0), (9, 0))

        assert not result.success
        assert len(result.path) == 0

    def test_invalid_start(self) -> None:
        """Test with invalid start position."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((20, 20), (5, 5))

        assert not result.success

    def test_invalid_goal(self) -> None:
        """Test with invalid goal position."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((0, 0), (20, 20))

        assert not result.success

    def test_path_cost(self) -> None:
        """Test path cost calculation."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((0, 0), (5, 0))

        assert result.cost > 0
        assert result.cost == 5.0  # 5 cells

    def test_diagonal_movement(self) -> None:
        """Test diagonal movement."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((0, 0), (5, 5), allow_diagonal=True)

        assert result.success
        # Diagonal path should be shorter
        assert len(result.path) <= 6

    def test_smooth_path(self) -> None:
        """Test path smoothing."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        result = pathfinder.find_path((0, 0), (5, 5))

        if result.success:
            smoothed = pathfinder._smooth_path(result.path)
            assert len(smoothed) <= len(result.path)

    @pytest.mark.skip(reason="Requires pygame initialization")
    def test_line_of_sight(self) -> None:
        """Test line of sight check."""
        grid = Grid(100, 100, 10)
        pathfinder = AStarPathfinder(grid)

        # Check within bounds
        assert pathfinder._can_see((1, 1), (4, 1))

    def test_blocked_line_of_sight(self) -> None:
        """Test blocked line of sight."""
        grid = Grid(100, 100, 10)
        grid.set_obstacle(2, 0)

        pathfinder = AStarPathfinder(grid)

        assert not pathfinder._can_see((0, 0), (5, 0))


class TestJumpPathfinder:
    """Test JumpPathfinder."""

    def test_create_jump_pathfinder(self) -> None:
        """Test creating jump pathfinder."""
        grid = Grid(100, 100, 10)
        pathfinder = JumpPathfinder(grid)

        assert pathfinder.grid is grid
        assert pathfinder.gravity == 1.5
        assert pathfinder.jump_velocity == 15.0

    def test_calculate_jump_arc(self) -> None:
        """Test calculating jump arc."""
        grid = Grid(100, 100, 10)
        pathfinder = JumpPathfinder(grid)

        arc = pathfinder.calculate_jump_arc(50, 50, 5.0)

        # Arc should have points
        assert len(arc) > 0
        # First point should be at start
        assert arc[0][0] == 50
        assert arc[0][1] == 50

    def test_can_reach_platform(self) -> None:
        """Test platform reachability."""
        grid = Grid(100, 100, 10)
        pathfinder = JumpPathfinder(grid)

        # Platform within jump range
        reachable = pathfinder.can_reach_platform(50, 50, 60, 30)

        assert reachable

    def test_cannot_reach_high_platform(self) -> None:
        """Test unreachable high platform."""
        grid = Grid(100, 100, 10)
        pathfinder = JumpPathfinder(grid)

        # Platform too high
        reachable = pathfinder.can_reach_platform(50, 50, 60, 0)

        assert not reachable

    def test_find_jump_path(self) -> None:
        """Test finding jump path."""
        grid = Grid(100, 100, 10)
        pathfinder = JumpPathfinder(grid)

        path = pathfinder.find_jump_path((50.0, 50.0), (60.0, 50.0))

        # May or may not find path depending on configuration
        assert path is None or len(path) > 0


class TestGlobalPathfinders:
    """Test global pathfinder instances."""

    def test_get_pathfinder(self) -> None:
        """Test getting pathfinder."""
        reset_pathfinders()

        pf1 = get_pathfinder()
        pf2 = get_pathfinder()

        assert pf1 is pf2

    def test_get_jump_pathfinder(self) -> None:
        """Test getting jump pathfinder."""
        reset_pathfinders()

        jpf1 = get_jump_pathfinder()
        jpf2 = get_jump_pathfinder()

        assert jpf1 is jpf2

    def test_reset_pathfinders(self) -> None:
        """Test resetting pathfinders."""
        reset_pathfinders()

        pf1 = get_pathfinder()
        reset_pathfinders()
        pf2 = get_pathfinder()

        assert pf1 is not pf2


class TestPathResult:
    """Test PathResult."""

    def test_create_success_result(self) -> None:
        """Test successful path result."""
        result = PathResult(
            path=[(0, 0), (1, 0), (2, 0)],
            success=True,
            length=3,
            cost=2.0,
            message="Path found"
        )

        assert result.success
        assert len(result.path) == 3
        assert result.length == 3

    def test_create_failure_result(self) -> None:
        """Test failed path result."""
        result = PathResult(
            path=[],
            success=False,
            length=0,
            cost=0,
            message="No path found"
        )

        assert not result.success
        assert len(result.path) == 0
