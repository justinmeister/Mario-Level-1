"""
A* Pathfinding System for Super Mario Bros.

Features:
- A* algorithm implementation
- Grid-based pathfinding
- Jump trajectory calculation
- Platform detection
- Dynamic obstacle avoidance
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Node:
    """A* node."""

    x: int
    y: int
    g_cost: float = 0  # Cost from start
    h_cost: float = 0  # Heuristic to goal
    parent: Optional[Node] = None
    walkable: bool = True

    @property
    def f_cost(self) -> float:
        """Total cost."""
        return self.g_cost + self.h_cost

    @property
    def pos(self) -> Tuple[int, int]:
        """Position tuple."""
        return (self.x, self.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: Node) -> bool:
        return self.f_cost < other.f_cost


@dataclass
class PathResult:
    """Pathfinding result."""

    path: List[Tuple[float, float]]
    success: bool
    length: int
    cost: float
    message: str = ""


class Grid:
    """Pathfinding grid."""

    def __init__(
        self,
        width: int,
        height: int,
        cell_size: int = 20,
    ) -> None:
        """
        Initialize grid.

        Args:
            width: World width
            height: World height
            cell_size: Size of each cell
        """
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size

        # Initialize nodes
        self.nodes: Dict[Tuple[int, int], Node] = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.nodes[(x, y)] = Node(x, y)

        # Obstacles
        self.obstacles: Set[Tuple[int, int]] = set()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world to grid coordinates."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def grid_to_world(self, x: int, y: int) -> Tuple[int, int]:
        """Convert grid to world coordinates."""
        return (x * self.cell_size, y * self.cell_size)

    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Get node at position."""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.nodes.get((x, y))
        return None

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if cell is walkable."""
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return False
        node = self.nodes.get((x, y))
        if node is None:
            return False
        return node.walkable and (x, y) not in self.obstacles

    def set_obstacle(self, x: int, y: int, obstacle: bool = True) -> None:
        """Set obstacle at position."""
        if obstacle:
            self.obstacles.add((x, y))
        else:
            self.obstacles.discard((x, y))

    def set_walkable(self, x: int, y: int, walkable: bool) -> None:
        """Set walkable state."""
        node = self.get_node(x, y)
        if node:
            node.walkable = walkable

    def get_neighbors(self, node: Node, allow_diagonal: bool = False) -> List[Node]:
        """Get walkable neighbors."""
        neighbors = []

        # Cardinal directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        if allow_diagonal:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if self.is_walkable(nx, ny):
                neighbor = self.get_node(nx, ny)
                if neighbor:
                    neighbors.append(neighbor)

        return neighbors

    def clear(self) -> None:
        """Clear obstacles."""
        self.obstacles.clear()
        for node in self.nodes.values():
            node.walkable = True


class AStarPathfinder:
    """
    A* pathfinding algorithm with path caching.

    Features:
    - Optimal path finding
    - Multiple heuristics
    - Jump support
    - Path caching for performance
    """

    def __init__(self, grid: Grid, cache_size: int = 100) -> None:
        """
        Initialize pathfinder.

        Args:
            grid: Pathfinding grid
            cache_size: Maximum cached paths
        """
        self.grid = grid
        self.cache_size = cache_size
        self._path_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], PathResult] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        allow_diagonal: bool = False,
        max_iterations: int = 10000,
        use_cache: bool = True,
    ) -> PathResult:
        """
        Find path using A* with caching.

        Args:
            start: Start position (grid coords)
            goal: Goal position (grid coords)
            allow_diagonal: Allow diagonal movement
            max_iterations: Maximum iterations
            use_cache: Use cached paths

        Returns:
            Path result
        """
        cache_key = (start, goal)

        if use_cache and cache_key in self._path_cache:
            self._cache_hits += 1
            return self._path_cache[cache_key]

        self._cache_misses += 1

        start_node = self.grid.get_node(start[0], start[1])
        goal_node = self.grid.get_node(goal[0], goal[1])

        if not start_node or not goal_node:
            return PathResult([], False, 0, 0, "Invalid start or goal")

        if not start_node.walkable or not goal_node.walkable:
            return PathResult([], False, 0, 0, "Start or goal not walkable")

        # Open and closed sets
        open_set: List[Node] = [start_node]
        closed_set: Set[Node] = set()

        # Reset nodes
        for node in self.grid.nodes.values():
            node.g_cost = float("inf")
            node.h_cost = float("inf")
            node.parent = None

        start_node.g_cost = 0
        start_node.h_cost = self._heuristic(start_node, goal_node)

        iterations = 0

        while open_set:
            iterations += 1
            if iterations > max_iterations:
                result = PathResult([], False, 0, 0, "Max iterations reached")
                self._add_to_cache(cache_key, result)
                return result

            # Get node with lowest f_cost
            current = heapq.heappop(open_set)

            # Check if reached goal
            if current == goal_node:
                path = self._reconstruct_path(current)
                result = PathResult(path, True, len(path), current.g_cost, "Path found")
                self._add_to_cache(cache_key, result)
                return result

            closed_set.add(current)

            # Check neighbors
            for neighbor in self.grid.get_neighbors(current, allow_diagonal):
                if neighbor in closed_set:
                    continue

                # Calculate cost
                move_cost = 1.0
                if allow_diagonal and neighbor.x != current.x and neighbor.y != current.y:
                    move_cost = 1.414  # sqrt(2)

                new_g_cost = current.g_cost + move_cost

                if new_g_cost < neighbor.g_cost:
                    neighbor.g_cost = new_g_cost
                    neighbor.h_cost = self._heuristic(neighbor, goal_node)
                    neighbor.parent = current

                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)

        result = PathResult([], False, 0, 0, "No path found")
        self._add_to_cache(cache_key, result)
        return result

    def _add_to_cache(self, key: Tuple[Tuple[int, int], Tuple[int, int]], result: PathResult) -> None:
        """Add path to cache with LRU eviction."""
        if len(self._path_cache) >= self.cache_size:
            # Remove oldest entry (first key)
            first_key = next(iter(self._path_cache))
            del self._path_cache[first_key]

        self._path_cache[key] = result

    def clear_cache(self) -> None:
        """Clear path cache."""
        self._path_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "size": len(self._path_cache),
            "hit_rate": int(round(hit_rate, 2)),
        }

    def _heuristic(self, a: Node, b: Node) -> float:
        """Calculate heuristic (Manhattan distance)."""
        return abs(a.x - b.x) + abs(a.y - b.y)

    def _reconstruct_path(self, node: Node) -> List[Tuple[float, float]]:
        """Reconstruct path from goal to start."""
        path: List[Tuple[float, float]] = []
        current: Optional[Node] = node

        while current:
            path.append((float(current.pos[0]), float(current.pos[1])))
            current = current.parent

        path.reverse()
        return path

    def find_path_smooth(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """
        Find and smooth path.

        Args:
            start: Start position
            goal: Goal position

        Returns:
            Smoothed path
        """
        result = self.find_path(start, goal)

        if not result.success:
            return []

        return self._smooth_path(result.path)  # type: ignore[return-value]

    def _smooth_path(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Smooth path by removing unnecessary waypoints."""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current = path[0]

        i = 1
        while i < len(path):
            # Try to skip points
            found = False
            for j in range(len(path) - 1, i, -1):
                if self._can_see(current, path[j]):
                    smoothed.append(path[j])
                    current = path[j]
                    i = j + 1
                    found = True
                    break

            if not found:
                smoothed.append(path[i])
                current = path[i]
                i += 1

        return smoothed

    def _can_see(self, a: Tuple[float, float], b: Tuple[float, float]) -> bool:
        """Check if two points have line of sight."""
        x0, y0 = int(a[0]), int(a[1])
        x1, y1 = int(b[0]), int(b[1])

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        x = x0
        y = y0
        n = max(dx, dy)

        if n == 0:
            return self.grid.is_walkable(x, y)

        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1

        for _ in range(n + 1):  # Include end point
            if not self.grid.is_walkable(x, y):
                return False

            x += x_inc
            y += y_inc

        return True


class JumpPathfinder:
    """
    Jump trajectory pathfinding.

    Features:
    - Calculate jump arcs
    - Platform detection
    - Jump feasibility check
    """

    def __init__(
        self,
        grid: Grid,
        gravity: float = 1.5,
        jump_velocity: float = 15.0,
    ) -> None:
        """
        Initialize jump pathfinder.

        Args:
            grid: Pathfinding grid
            gravity: Gravity value
            jump_velocity: Initial jump velocity
        """
        self.grid = grid
        self.gravity = gravity
        self.jump_velocity = jump_velocity

    def calculate_jump_arc(
        self,
        start_x: float,
        start_y: float,
        horizontal_velocity: float,
    ) -> List[Tuple[float, float]]:
        """
        Calculate jump trajectory.

        Args:
            start_x, start_y: Start position
            horizontal_velocity: Horizontal velocity

        Returns:
            List of positions along arc
        """
        arc: List[Tuple[float, float]] = []

        x = start_x
        y = start_y
        vy = -self.jump_velocity  # Initial upward velocity
        vx = horizontal_velocity

        dt = 1.0 / 60.0  # 60 FPS

        while vy < self.jump_velocity * 2:  # Until falling back down
            arc.append((x, y))

            # Update position
            x += vx * dt
            y += vy * dt
            vy += self.gravity * dt

            # Check collision
            grid_x, grid_y = self.grid.world_to_grid(x, y)
            if not self.grid.is_walkable(grid_x, grid_y):
                break

        return arc

    def can_reach_platform(
        self,
        start_x: float,
        start_y: float,
        platform_x: float,
        platform_y: float,
    ) -> bool:
        """
        Check if platform is reachable with jump.

        Args:
            start_x, start_y: Start position
            platform_x, platform_y: Platform position

        Returns:
            True if reachable
        """
        dx = abs(platform_x - start_x)
        dy = platform_y - start_y  # Positive = higher

        # Calculate max jump height
        max_height = (self.jump_velocity**2) / (2 * self.gravity)

        # Calculate time to reach platform horizontally
        if dx == 0:
            return dy <= max_height

        # Simplified check
        if dy > max_height:
            return False

        # Check if path is clear
        arc = self.calculate_jump_arc(start_x, start_y, dx / 0.5)

        for x, y in arc:
            if abs(x - platform_x) < 10:
                if abs(y - platform_y) < 20:
                    return True

        return False

    def find_jump_path(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Find path including jumps.

        Args:
            start: Start position (world coords)
            goal: Goal position (world coords)

        Returns:
            Path with jumps or None
        """
        # First try regular path
        start_grid = self.grid.world_to_grid(start[0], start[1])
        goal_grid = self.grid.world_to_grid(goal[0], goal[1])

        pathfinder = AStarPathfinder(self.grid)
        result = pathfinder.find_path(start_grid, goal_grid)

        if result.success:
            # Convert to world coords
            world_path: List[Tuple[float, float]] = [(float(x), float(y)) for x, y in result.path]
            return world_path

        # Try with jumps
        return self._find_jump_path(start, goal)

    def _find_jump_path(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
    ) -> Optional[List[Tuple[float, float]]]:
        """Find path with jumps."""
        # Simplified: just check if goal is reachable with jump
        if self.can_reach_platform(start[0], start[1], goal[0], goal[1]):
            arc = self.calculate_jump_arc(start[0], start[1], (goal[0] - start[0]) / 0.5)
            return arc

        return None


# Global pathfinder instance
_pathfinder: Optional[AStarPathfinder] = None
_jump_pathfinder: Optional[JumpPathfinder] = None


def get_pathfinder() -> AStarPathfinder:
    """Get global pathfinder instance."""
    global _pathfinder
    if _pathfinder is None:
        grid = Grid(8550, 600, 20)  # Level 1-1 dimensions
        _pathfinder = AStarPathfinder(grid)
    return _pathfinder


def get_jump_pathfinder() -> JumpPathfinder:
    """Get global jump pathfinder instance."""
    global _jump_pathfinder
    if _jump_pathfinder is None:
        grid = Grid(8550, 600, 20)
        _jump_pathfinder = JumpPathfinder(grid)
    return _jump_pathfinder


def reset_pathfinders() -> None:
    """Reset pathfinder instances."""
    global _pathfinder, _jump_pathfinder
    _pathfinder = None
    _jump_pathfinder = None
