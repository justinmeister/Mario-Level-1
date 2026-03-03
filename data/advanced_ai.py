"""
Advanced AI System for Super Mario Bros Enemies.

Features:
- Enemy coordination
- Tactical behaviors
- Group AI
- Dynamic difficulty
- Patrol patterns
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any

from . import constants as c


class AIBehavior(Enum):
    """AI behavior types."""

    PASSIVE = auto()
    AGGRESSIVE = auto()
    DEFENSIVE = auto()
    PATROL = auto()
    AMBUSH = auto()
    FLEE = auto()
    GROUP = auto()
    GUARD = auto()


class AlertState(Enum):
    """Enemy alert states."""

    IDLE = auto()
    SUSPICIOUS = auto()
    ALERTED = auto()
    COMBAT = auto()
    RETREATING = auto()


@dataclass
class AITarget:
    """AI target information."""

    position: Tuple[float, float]
    distance: float
    visible: bool
    last_known_position: Optional[Tuple[float, float]] = None
    time_since_seen: float = 0.0


@dataclass
class EnemyAIConfig:
    """AI configuration for an enemy."""

    behavior: AIBehavior = AIBehavior.PASSIVE
    detection_range: float = 300.0
    attack_range: float = 50.0
    patrol_points: List[Tuple[float, float]] = field(default_factory=list)
    group_radius: float = 150.0
    aggression: float = 0.5  # 0-1
    caution: float = 0.5  # 0-1
    memory_time: float = 5.0  # seconds


class EnemyAI:
    """
    Advanced AI controller for enemies.

    Features:
    - State machine
    - Target tracking
    - Decision making
    - Group coordination
    """

    def __init__(self, enemy: Any, config: Optional[EnemyAIConfig] = None) -> None:
        """
        Initialize enemy AI.

        Args:
            enemy: Enemy sprite instance
            config: AI configuration
        """
        self.enemy = enemy
        self.config = config or EnemyAIConfig()

        self.alert_state = AlertState.IDLE
        self.target: Optional[AITarget] = None

        # Timing
        self.state_timer: float = 0.0
        self.last_update: float = 0.0
        self.think_interval: float = 100.0  # ms between thinks

        # Patrol
        self.current_patrol_index: int = 0
        self.patrol_direction: int = 1

        # Group
        self.group_id: Optional[str] = None
        self.allies: List[EnemyAI] = []

        # Memory
        self.known_targets: Dict[str, AITarget] = {}

        # Decision weights
        self.weights = {
            "attack": 0.0,
            "chase": 0.0,
            "patrol": 0.0,
            "flee": 0.0,
            "guard": 0.0,
        }

    def update(
        self, game_info: Dict[str, Any], mario: Optional[Any] = None, all_enemies: Optional[List[Any]] = None
    ) -> None:
        """
        Update AI state.

        Args:
            game_info: Game info dict
            mario: Mario instance
            all_enemies: List of all enemies
        """
        current_time = game_info.get(c.CURRENT_TIME, 0)

        # Throttle updates
        if current_time - self.last_update < self.think_interval:
            self._update_timers(current_time)
            return

        self.last_update = current_time

        # Update target detection
        if mario:
            self._detect_target(mario, game_info)

        # Update group coordination
        if all_enemies:
            self._update_group(all_enemies)

        # Update state machine
        self._update_state(current_time)

        # Make decision
        self._make_decision(mario)

        # Execute behavior
        self._execute_behavior(game_info)

        self._update_timers(current_time)

    def _update_timers(self, current_time: float) -> None:
        """Update internal timers."""
        self.state_timer = current_time

        # Update target memory
        for target_id, target in list(self.known_targets.items()):
            if target.last_known_position is not None:
                target.time_since_seen = (current_time - target.last_known_position[0]) / 1000
                if target.time_since_seen > self.config.memory_time:
                    del self.known_targets[target_id]

    def _detect_target(self, mario: Any, game_info: Dict[str, Any]) -> None:
        """Detect and track target."""
        if not hasattr(mario, "rect"):
            return

        enemy_pos = (self.enemy.rect.centerx, self.enemy.rect.centery)
        mario_pos = (mario.rect.centerx, mario.rect.centery)

        # Calculate distance
        distance = math.sqrt((mario_pos[0] - enemy_pos[0]) ** 2 + (mario_pos[1] - enemy_pos[1]) ** 2)

        # Check visibility
        visible = distance <= self.config.detection_range

        # Check line of sight (simplified)
        if visible:
            # Simple check - could be enhanced with raycasting
            visible = abs(mario.rect.centery - self.enemy.rect.centery) < 100

        # Update target
        if visible:
            self.target = AITarget(
                position=mario_pos,
                distance=distance,
                visible=True,
                last_known_position=(mario_pos[0], mario_pos[1]),
            )

            # Update alert state
            if self.alert_state in (AlertState.IDLE, AlertState.SUSPICIOUS):
                self.alert_state = AlertState.ALERTED
            elif self.alert_state == AlertState.ALERTED and distance < self.config.attack_range:
                self.alert_state = AlertState.COMBAT
        else:
            # Lost sight - remember last position
            if self.target and self.target.last_known_position:
                self.target.visible = False
                self.target.time_since_seen += 0.1

    def _update_group(self, all_enemies: List[Any]) -> None:
        """Update group coordination with nearby enemies."""
        self.allies.clear()

        enemy_pos = (self.enemy.rect.centerx, self.enemy.rect.centery)

        for other in all_enemies:
            if other is self.enemy:
                continue

            if not hasattr(other, "rect"):
                continue

            other_pos = (other.rect.centerx, other.rect.centery)
            distance = math.sqrt((other_pos[0] - enemy_pos[0]) ** 2 + (other_pos[1] - enemy_pos[1]) ** 2)

            if distance <= self.config.group_radius:
                if hasattr(other, "ai"):
                    self.allies.append(other.ai)

        # Update group ID based on nearby allies
        if self.allies:
            # Join largest group
            groups: Dict[str, List[EnemyAI]] = {}
            for ally in self.allies:
                if ally.group_id:
                    if ally.group_id not in groups:
                        groups[ally.group_id] = []
                    groups[ally.group_id].append(ally)

            if groups:
                largest_group = max(groups.keys(), key=lambda k: len(groups[k]))
                self.group_id = largest_group

    def _update_state(self, current_time: float) -> None:
        """Update AI state machine."""
        # Timeout states
        if self.alert_state == AlertState.SUSPICIOUS:
            if current_time - self.state_timer > 3000:  # 3 seconds
                self.alert_state = AlertState.IDLE

        elif self.alert_state == AlertState.ALERTED:
            if not self.target or not self.target.visible:
                if current_time - self.state_timer > 5000:  # 5 seconds
                    self.alert_state = AlertState.SUSPICIOUS

        elif self.alert_state == AlertState.COMBAT:
            if not self.target or self.target.distance > self.config.detection_range * 1.5:
                self.alert_state = AlertState.ALERTED

    def _make_decision(self, mario: Optional[Any]) -> None:
        """Make AI decision based on weights."""
        # Reset weights
        for key in self.weights:
            self.weights[key] = 0.0

        if not self.target:
            # No target - patrol or guard
            if self.config.patrol_points:
                self.weights["patrol"] = 1.0
            else:
                self.weights["guard"] = 1.0
            return

        distance = self.target.distance

        # Calculate weights based on situation
        if self.target.visible:
            # Can see target
            if distance < self.config.attack_range:
                self.weights["attack"] = self.config.aggression
            else:
                self.weights["chase"] = self.config.aggression * 0.8

            # Consider fleeing if low health (if enemy has health)
            if hasattr(self.enemy, "health"):
                health_ratio = self.enemy.health / self.enemy.max_health
                if health_ratio < 0.3:
                    self.weights["flee"] = 1.0 - self.config.aggression

        else:
            # Can't see target - guard last known position
            self.weights["guard"] = 0.7
            self.weights["patrol"] = 0.3

    def _execute_behavior(self, game_info: Dict[str, Any]) -> None:
        """Execute chosen behavior."""
        # Get highest weight behavior
        if not self.weights:
            return

        behavior = max(self.weights.keys(), key=lambda k: self.weights[k])

        if behavior == "attack":
            self._execute_attack(game_info)
        elif behavior == "chase":
            self._execute_chase(game_info)
        elif behavior == "patrol":
            self._execute_patrol(game_info)
        elif behavior == "flee":
            self._execute_flee(game_info)
        elif behavior == "guard":
            self._execute_guard(game_info)

    def _execute_attack(self, game_info: Dict[str, Any]) -> None:
        """Execute attack behavior."""
        if not self.target:
            return

        # Face target
        if self.target.position[0] < self.enemy.rect.centerx:
            self.enemy.direction = c.LEFT
        else:
            self.enemy.direction = c.RIGHT

        # Perform attack if available
        if hasattr(self.enemy, "perform_attack"):
            self.enemy.perform_attack()

    def _execute_chase(self, game_info: Dict[str, Any]) -> None:
        """Execute chase behavior."""
        if not self.target:
            return

        # Move towards target
        if self.target.position[0] < self.enemy.rect.centerx:
            self.enemy.direction = c.LEFT
            self.enemy.x_vel = self.enemy.max_speed
        else:
            self.enemy.direction = c.RIGHT
            self.enemy.x_vel = self.enemy.max_speed

    def _execute_patrol(self, game_info: Dict[str, Any]) -> None:
        """Execute patrol behavior."""
        if not self.config.patrol_points:
            # Simple back-and-forth patrol
            self.enemy.x_vel = self.enemy.max_speed * 0.5 * self.patrol_direction
            return

        # Patrol between points
        if self.current_patrol_index >= len(self.config.patrol_points):
            self.current_patrol_index = 0
            self.patrol_direction *= -1

        target_point = self.config.patrol_points[self.current_patrol_index]
        enemy_pos = (self.enemy.rect.centerx, self.enemy.rect.centery)

        distance = math.sqrt((target_point[0] - enemy_pos[0]) ** 2 + (target_point[1] - enemy_pos[1]) ** 2)

        if distance < 10:
            self.current_patrol_index += 1
        else:
            # Move towards point
            if target_point[0] < enemy_pos[0]:
                self.enemy.direction = c.LEFT
                self.enemy.x_vel = -self.enemy.max_speed * 0.5
            else:
                self.enemy.direction = c.RIGHT
                self.enemy.x_vel = self.enemy.max_speed * 0.5

    def _execute_flee(self, game_info: Dict[str, Any]) -> None:
        """Execute flee behavior."""
        if not self.target:
            return

        # Move away from target
        if self.target.position[0] < self.enemy.rect.centerx:
            self.enemy.direction = c.RIGHT
            self.enemy.x_vel = self.enemy.max_speed * 1.2  # Faster when fleeing
        else:
            self.enemy.direction = c.LEFT
            self.enemy.x_vel = -self.enemy.max_speed * 1.2

    def _execute_guard(self, game_info: Dict[str, Any]) -> None:
        """Execute guard behavior."""
        if not self.target or not self.target.last_known_position:
            # Guard current position
            self.enemy.x_vel = 0
            return

        # Move to last known position
        last_pos = self.target.last_known_position
        if last_pos is None:
            self.enemy.x_vel = 0
            return

        enemy_pos: Tuple[float, float] = (float(self.enemy.rect.centerx), float(self.enemy.rect.centery))

        distance = math.sqrt((last_pos[0] - enemy_pos[0]) ** 2 + (last_pos[1] - enemy_pos[1]) ** 2)

        if distance < 10:
            # Arrived - stop guarding
            self.enemy.x_vel = 0
        else:
            # Move towards position
            if last_pos[0] < enemy_pos[0]:
                self.enemy.direction = c.LEFT
                self.enemy.x_vel = -self.enemy.max_speed * 0.7
            else:
                self.enemy.direction = c.RIGHT
                self.enemy.x_vel = self.enemy.max_speed * 0.7

    def set_behavior(self, behavior: AIBehavior) -> None:
        """Set AI behavior."""
        self.config.behavior = behavior

    def add_patrol_point(self, x: float, y: float) -> None:
        """Add patrol point."""
        self.config.patrol_points.append((x, y))

    def set_group_id(self, group_id: str) -> None:
        """Set group ID for coordination."""
        self.group_id = group_id


class GroupAI:
    """
    Group AI coordinator for enemy squads.

    Features:
    - Coordinated attacks
    - Flanking maneuvers
    - Role assignment
    - Communication
    """

    def __init__(self) -> None:
        """Initialize group AI."""
        self.groups: Dict[str, List[EnemyAI]] = {}
        self.strategies: Dict[str, Dict[str, Any]] = {}

    def create_group(self, group_id: str, enemies: List[EnemyAI], strategy: str = "assault") -> None:
        """
        Create enemy group.

        Args:
            group_id: Group identifier
            enemies: List of enemy AIs
            strategy: Group strategy
        """
        self.groups[group_id] = enemies

        # Set group ID for all members
        for enemy in enemies:
            enemy.group_id = group_id

        # Apply strategy
        self.apply_strategy(group_id, strategy)

    def apply_strategy(self, group_id: str, strategy: str) -> None:
        """
        Apply strategy to group.

        Args:
            group_id: Group identifier
            strategy: Strategy name
        """
        if group_id not in self.groups:
            return

        enemies = self.groups[group_id]

        if strategy == "assault":
            # All enemies aggressive
            for enemy in enemies:
                enemy.config.aggression = 0.9
                enemy.config.behavior = AIBehavior.AGGRESSIVE

        elif strategy == "flank":
            # Split into attackers and flankers
            mid = len(enemies) // 2
            for i, enemy in enumerate(enemies):
                if i < mid:
                    enemy.config.aggression = 0.8
                    enemy.config.behavior = AIBehavior.AGGRESSIVE
                else:
                    enemy.config.aggression = 0.5
                    enemy.config.behavior = AIBehavior.AMBUSH

        elif strategy == "defensive":
            # All enemies defensive
            for enemy in enemies:
                enemy.config.aggression = 0.3
                enemy.config.behavior = AIBehavior.DEFENSIVE

        elif strategy == "patrol":
            # Coordinated patrol
            for i, enemy in enumerate(enemies):
                enemy.config.behavior = AIBehavior.PATROL
                # Stagger patrol points
                if enemy.config.patrol_points:
                    enemy.current_patrol_index = i % len(enemy.config.patrol_points)

    def update_group(self, group_id: str, game_info: Dict[str, Any], mario: Optional[Any] = None) -> None:
        """
        Update all enemies in group.

        Args:
            group_id: Group identifier
            game_info: Game info dict
            mario: Mario instance
        """
        if group_id not in self.groups:
            return

        enemies = self.groups[group_id]
        all_enemy_sprites = [ai.enemy for ai in enemies]

        for enemy_ai in enemies:
            enemy_ai.update(game_info, mario, all_enemy_sprites)

    def get_group_status(self, group_id: str) -> Dict[str, Any]:
        """Get group status."""
        if group_id not in self.groups:
            return {}

        enemies = self.groups[group_id]

        return {
            "member_count": len(enemies),
            "active_members": sum(1 for e in enemies if e.alert_state != AlertState.IDLE),
            "average_health": self._calculate_average_health(enemies),
        }

    def _calculate_average_health(self, enemies: List[EnemyAI]) -> float:
        """Calculate average group health."""
        total_health = 0
        count = 0

        for enemy in enemies:
            if hasattr(enemy.enemy, "health") and hasattr(enemy.enemy, "max_health"):
                total_health += enemy.enemy.health / enemy.enemy.max_health
                count += 1

        return (total_health / count * 100) if count > 0 else 0


class AIDirector:
    """
    AI Director for dynamic difficulty adjustment.

    Features:
    - Tracks player performance
    - Adjusts enemy behavior
    - Spawns enemies dynamically
    - Creates tension curves
    """

    def __init__(self) -> None:
        """Initialize AI director."""
        self.player_performance: float = 0.5  # 0-1
        self.tension_level: float = 0.0  # 0-1
        self.death_count: int = 0
        self.success_count: int = 0

        # Timing
        self.last_adjustment: float = 0
        self.adjustment_interval: float = 30000  # 30 seconds

        # Configuration
        self.max_enemies: int = 10
        self.spawn_rate: float = 1.0  # Multiplier

    def update(
        self, game_info: Dict[str, Any], player_alive: bool, player_health: float, enemies_remaining: int
    ) -> Dict[str, Any]:
        """
        Update director state.

        Args:
            game_info: Game info dict
            player_alive: Is player alive
            player_health: Player health ratio
            enemies_remaining: Remaining enemies

        Returns:
            Director decisions
        """
        current_time = game_info.get(c.CURRENT_TIME, 0)

        # Update performance tracking
        if not player_alive:
            self.death_count += 1
            self.player_performance = max(0, self.player_performance - 0.1)
        else:
            self.success_count += 1
            self.player_performance = min(1, self.player_performance + 0.01)

        # Update tension
        self._update_tension(player_health, enemies_remaining)

        # Make adjustments
        decisions = {}
        if current_time - self.last_adjustment > self.adjustment_interval:
            decisions = self._make_adjustments()
            self.last_adjustment = current_time

        return decisions

    def _update_tension(self, player_health: float, enemies_remaining: int) -> None:
        """Update tension level."""
        # Tension increases with:
        # - Low player health
        # - Many enemies
        # - Recent deaths

        health_factor = 1.0 - player_health
        enemy_factor = min(1.0, enemies_remaining / self.max_enemies)
        death_factor = min(1.0, self.death_count * 0.1)

        target_tension = health_factor * 0.4 + enemy_factor * 0.4 + death_factor * 0.2

        # Smooth transition
        self.tension_level += (target_tension - self.tension_level) * 0.1

    def _make_adjustments(self) -> Dict[str, Any]:
        """Make difficulty adjustments."""
        decisions = {}

        # Adjust spawn rate based on performance
        if self.player_performance < 0.3:
            # Player struggling - reduce difficulty
            decisions["spawn_rate"] = 0.7
            decisions["enemy_aggression"] = 0.3
        elif self.player_performance > 0.7:
            # Player doing well - increase difficulty
            decisions["spawn_rate"] = 1.3
            decisions["enemy_aggression"] = 0.8
        else:
            # Balanced
            decisions["spawn_rate"] = 1.0
            decisions["enemy_aggression"] = 0.5

        return decisions

    def get_tension_level(self) -> float:
        """Get current tension level."""
        return self.tension_level

    def reset(self) -> None:
        """Reset director state."""
        self.player_performance = 0.5
        self.tension_level = 0.0
        self.death_count = 0
        self.success_count = 0
