"""
Game Controller Support for Super Mario Bros.

Features:
- Controller detection and hot-plugging
- Button mapping configuration
- Vibration/haptic feedback
- Analog stick support
- Multiple controller support
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg


# Default button mappings
DEFAULT_MAPPINGS: Dict[str, int] = {
    "jump": 0,  # A button (Xbox) / Cross (PS)
    "action": 1,  # B button (Xbox) / Circle (PS)
    "start": 7,  # Start button
    "select": 6,  # Back button
    "dpad_up": 0,
    "dpad_down": 1,
    "dpad_left": 2,
    "dpad_right": 3,
}

# Axis mappings
DEFAULT_AXIS_MAPPINGS: Dict[str, Tuple[int, float]] = {
    "left_stick_x": (0, 0.3),  # axis_index, deadzone
    "left_stick_y": (1, 0.3),
    "right_stick_x": (2, 0.3),
    "right_stick_y": (3, 0.3),
}

# Trigger mappings
DEFAULT_TRIGGER_MAPPINGS: Dict[str, int] = {
    "left_trigger": 2,
    "right_trigger": 5,
}


@dataclass
class ControllerConfig:
    """Controller configuration."""

    button_mappings: Dict[str, int] = field(default_factory=lambda: DEFAULT_MAPPINGS.copy())
    axis_mappings: Dict[str, Tuple[int, float]] = field(default_factory=lambda: DEFAULT_AXIS_MAPPINGS.copy())
    trigger_mappings: Dict[str, int] = field(default_factory=lambda: DEFAULT_TRIGGER_MAPPINGS.copy())
    vibration_enabled: bool = True
    vibration_strength: float = 1.0
    deadzone: float = 0.15

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "button_mappings": self.button_mappings,
            "axis_mappings": {k: list(v) for k, v in self.axis_mappings.items()},
            "trigger_mappings": self.trigger_mappings,
            "vibration_enabled": self.vibration_enabled,
            "vibration_strength": self.vibration_strength,
            "deadzone": self.deadzone,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ControllerConfig":
        """Create from dictionary."""
        config = cls()
        config.button_mappings = data.get("button_mappings", DEFAULT_MAPPINGS.copy())
        axis_data = data.get("axis_mappings", DEFAULT_AXIS_MAPPINGS)
        # Ensure we have a mapping dict; convert values to tuples
        config.axis_mappings = {k: tuple(v) for k, v in axis_data.items()}
        config.trigger_mappings = data.get("trigger_mappings", DEFAULT_TRIGGER_MAPPINGS.copy())
        config.vibration_enabled = data.get("vibration_enabled", True)
        config.vibration_strength = data.get("vibration_strength", 1.0)
        config.deadzone = data.get("deadzone", 0.15)
        return config


@dataclass
class ControllerState:
    """Current controller state."""

    connected: bool = False
    button_states: Dict[str, bool] = field(default_factory=dict)
    axis_values: Dict[str, float] = field(default_factory=dict)
    trigger_values: Dict[str, float] = field(default_factory=dict)

    def is_pressed(self, button: str) -> bool:
        """Check if button is pressed."""
        return self.button_states.get(button, False)

    def get_axis(self, axis: str) -> float:
        """Get axis value."""
        return self.axis_values.get(axis, 0.0)

    def get_trigger(self, trigger: str) -> float:
        """Get trigger value."""
        return self.trigger_values.get(trigger, 0.0)


class GameController:
    """
    Game controller wrapper.

    Provides unified interface for controller input.
    """

    def __init__(self, joystick_id: int = 0, config: Optional[ControllerConfig] = None) -> None:
        """
        Initialize game controller.

        Args:
            joystick_id: Joystick ID
            config: Controller configuration
        """
        self.id = joystick_id
        self.config = config or ControllerConfig()
        self._controller: Optional[pg.joystick.JoystickType] = None
        self._state = ControllerState()
        self._initialized = False

        # Try to initialize
        self._initialize()

    def _initialize(self) -> None:
        """Initialize controller."""
        try:
            if pg.joystick.get_count() > self.id:
                self._controller = pg.joystick.Joystick(self.id)
                self._controller.init()
                self._initialized = True
                self._state.connected = True
        except pg.error:
            self._state.connected = False

    @property
    def name(self) -> str:
        """Get controller name."""
        if self._controller:
            try:
                return self._controller.get_name()
            except AttributeError:
                return "Unknown Controller"
        return "Unknown"

    @property
    def is_connected(self) -> bool:
        """Check if controller is connected."""
        return self._state.connected and self._initialized

    def update(self) -> ControllerState:
        """
        Update controller state.

        Returns:
            Current controller state
        """
        if not self.is_connected or self._controller is None:
            self._state = ControllerState()
            return self._state

        # Read buttons
        for name, button_id in self.config.button_mappings.items():
            try:
                pressed = self._controller.get_button(button_id)
                self._state.button_states[name] = pressed
            except (pg.error, AttributeError):
                self._state.button_states[name] = False

        # Read axes
        for name, (axis_id, deadzone) in self.config.axis_mappings.items():
            try:
                value = self._controller.get_axis(axis_id)
                # Apply deadzone
                if abs(value) < deadzone:
                    value = 0.0
                self._state.axis_values[name] = value
            except (pg.error, AttributeError):
                self._state.axis_values[name] = 0.0

        # Read triggers (as axes or buttons depending on controller)
        for name, axis_id in self.config.trigger_mappings.items():
            try:
                value = self._controller.get_axis(axis_id)
                # Convert 0-1 range for triggers
                value = max(0.0, (value + 1) / 2)
                self._state.trigger_values[name] = value
            except (pg.error, AttributeError):
                self._state.trigger_values[name] = 0.0

        # Read D-pad (as hat or buttons)
        try:
            hat = self._controller.get_hat(0)
            self._state.button_states["dpad_up"] = hat[1] > 0
            self._state.button_states["dpad_down"] = hat[1] < 0
            self._state.button_states["dpad_left"] = hat[0] < 0
            self._state.button_states["dpad_right"] = hat[0] > 0
        except (pg.error, IndexError, AttributeError):
            pass

        return self._state

    def vibrate(self, duration: float = 0.5, strength: float = 1.0) -> bool:
        """
        Vibrate controller.

        Args:
            duration: Vibration duration in seconds
            strength: Vibration strength (0.0 to 1.0)

        Returns:
            True if vibration started
        """
        if not self.is_connected or not self.config.vibration_enabled:
            return False

        try:
            # Check for rumble support
            if self._controller and hasattr(self._controller, "rumble"):
                self._controller.rumble(
                    0.0,
                    strength * self.config.vibration_strength,
                    int(duration * 1000),
                )
                return True
        except pg.error:
            pass

        return False

    def vibrate_trigger(self, trigger: str, duration: float = 0.3, strength: float = 1.0) -> bool:
        """
        Vibrate specific trigger.

        Args:
            trigger: Trigger name ('left_trigger' or 'right_trigger')
            duration: Duration in seconds
            strength: Strength (0.0 to 1.0)

        Returns:
            True if vibration started
        """
        if not self.is_connected:
            return False

        try:
            if self._controller and hasattr(self._controller, "trigger_motor"):
                self._controller.trigger_motor(
                    motor_id=0 if trigger == "left_trigger" else 1,
                    strength=strength * self.config.vibration_strength,
                    duration=int(duration * 1000),
                )
                return True
        except pg.error:
            pass

        return False

    def get_state(self) -> ControllerState:
        """Get current controller state."""
        return self._state

    def close(self) -> None:
        """Close controller."""
        if self._controller:
            try:
                self._controller.quit()
            except AttributeError:
                pass
            self._controller = None
            self._initialized = False
            self._state.connected = False


class ControllerManager:
    """
    Manager for multiple game controllers.

    Features:
    - Hot-plugging detection
    - Per-controller configuration
    - Event-based input
    """

    def __init__(self) -> None:
        """Initialize controller manager."""
        self.controllers: Dict[int, GameController] = {}
        self.configs: Dict[str, ControllerConfig] = {}
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "controllers.json",
        )
        self._load_configs()

        # Callbacks
        self._connect_callbacks: List[Callable[[int], None]] = []
        self._disconnect_callbacks: List[Callable[[int], None]] = []

    def _load_configs(self) -> None:
        """Load controller configurations."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for guid, config_data in data.items():
                    self.configs[guid] = ControllerConfig.from_dict(config_data)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_configs(self) -> None:
        """Save controller configurations."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(
                    {guid: config.to_dict() for guid, config in self.configs.items()},
                    f,
                    indent=2,
                )
        except (IOError, OSError):
            pass

    def scan_controllers(self) -> List[int]:
        """
        Scan for connected controllers.

        Returns:
            List of connected controller IDs
        """
        pg.joystick.init()
        count = pg.joystick.get_count()

        # Check for new controllers
        for i in range(count):
            if i not in self.controllers:
                config = self._get_config_for_controller(i)
                self.controllers[i] = GameController(i, config)
                if self.controllers[i].is_connected:
                    self._notify_connect(i)

        # Check for disconnected controllers
        disconnected = []
        for controller_id, controller in self.controllers.items():
            if controller_id >= count or not controller.is_connected:
                controller.close()
                disconnected.append(controller_id)

        for controller_id in disconnected:
            del self.controllers[controller_id]
            self._notify_disconnect(controller_id)

        return list(self.controllers.keys())

    def _get_config_for_controller(self, joystick_id: int) -> ControllerConfig:
        """Get configuration for controller."""
        try:
            controller = pg.joystick.Joystick(joystick_id)
            controller.init()
            guid = controller.get_guid()
            controller.quit()

            if guid in self.configs:
                return self.configs[guid]
        except (pg.error, AttributeError):
            pass

        return ControllerConfig()

    def get_controller(self, index: int = 0) -> Optional[GameController]:
        """
        Get controller by index.

        Args:
            index: Controller index

        Returns:
            GameController or None
        """
        if index in self.controllers:
            return self.controllers[index]

        # Return first available
        if self.controllers:
            return next(iter(self.controllers.values()))

        return None

    def get_all_controllers(self) -> List[GameController]:
        """Get all connected controllers."""
        return list(self.controllers.values())

    def update(self) -> Dict[int, ControllerState]:
        """
        Update all controllers.

        Returns:
            Dictionary of controller states
        """
        self.scan_controllers()

        states = {}
        for controller_id, controller in self.controllers.items():
            states[controller_id] = controller.update()

        return states

    def vibrate_all(self, duration: float = 0.5, strength: float = 1.0) -> None:
        """Vibrate all controllers."""
        for controller in self.controllers.values():
            controller.vibrate(duration, strength)

    def on_connect(self, callback: Callable[[int], None]) -> None:
        """Register connect callback."""
        self._connect_callbacks.append(callback)

    def on_disconnect(self, callback: Callable[[int], None]) -> None:
        """Register disconnect callback."""
        self._disconnect_callbacks.append(callback)

    def _notify_connect(self, controller_id: int) -> None:
        """Notify about controller connection."""
        for callback in self._connect_callbacks:
            callback(controller_id)

    def _notify_disconnect(self, controller_id: int) -> None:
        """Notify about controller disconnection."""
        for callback in self._disconnect_callbacks:
            callback(controller_id)

    def save_config(self, controller_id: int, config: ControllerConfig) -> None:
        """
        Save controller configuration.

        Args:
            controller_id: Controller ID
            config: Configuration to save
        """
        controller = self.controllers.get(controller_id)
        if controller:
            try:
                guid = controller._controller.get_guid()  # type: ignore
                self.configs[guid] = config
                self._save_configs()
            except (pg.error, AttributeError):
                pass

    def get_button_mapping_help(self) -> str:
        """Get help string for button mappings."""
        return """
Controller Button Mapping Guide:
--------------------------------
Xbox Controller:
  A=0, B=1, X=2, Y=3
  LB=4, RB=5
  Back=6, Start=7
  Left Stick=8, Right Stick=9

PlayStation Controller:
  Cross=0, Circle=1, Square=2, Triangle=3
  L1=4, R1=5
  Select=6, Start=7
  L3=9, R3=10

D-Pad: Use hat(0) or buttons 10-13
Triggers: Use axes 2 and 5
"""


# Global controller manager
_controller_manager: Optional[ControllerManager] = None


def get_controller_manager() -> ControllerManager:
    """Get global controller manager."""
    global _controller_manager
    if _controller_manager is None:
        _controller_manager = ControllerManager()
    return _controller_manager


def init_controllers() -> ControllerManager:
    """Initialize controller system."""
    pg.joystick.init()
    return get_controller_manager()
