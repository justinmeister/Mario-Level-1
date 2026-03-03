"""
Dialog and Narrative System for Super Mario Bros.

Features:
- Branching dialogues
- Character portraits
- Typewriter text effect
- Dialog conditions and triggers
- Quest/narrative tracking
- Localization support
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg

logger = logging.getLogger(__name__)


class DialogPosition(Enum):
    """Dialog box positions."""

    TOP = auto()
    CENTER = auto()
    BOTTOM = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class DialogSpeed(Enum):
    """Text display speeds."""

    INSTANT = 0
    FAST = 30  # chars per second
    NORMAL = 60
    SLOW = 90


@dataclass
class DialogChoice:
    """Dialog choice option."""

    text: str
    next_dialog: str
    condition: Optional[str] = None  # Condition ID to show choice
    on_select: Optional[str] = None  # Action to trigger

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "next_dialog": self.next_dialog,
            "condition": self.condition,
            "on_select": self.on_select,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogChoice":
        return cls(
            text=data.get("text", ""),
            next_dialog=data.get("next_dialog", ""),
            condition=data.get("condition"),
            on_select=data.get("on_select"),
        )


@dataclass
class DialogEntry:
    """Single dialog entry."""

    id: str
    speaker: str
    text: str
    portrait: Optional[str] = None
    choices: List[DialogChoice] = field(default_factory=list)
    next_dialog: Optional[str] = None
    conditions: List[str] = field(default_factory=list)  # Must all be true
    actions: List[str] = field(default_factory=list)  # Actions to trigger
    sound: Optional[str] = None
    music: Optional[str] = None
    position: DialogPosition = DialogPosition.BOTTOM
    speed: DialogSpeed = DialogSpeed.NORMAL
    background: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "speaker": self.speaker,
            "text": self.text,
            "portrait": self.portrait,
            "choices": [c.to_dict() for c in self.choices],
            "next_dialog": self.next_dialog,
            "conditions": self.conditions,
            "actions": self.actions,
            "sound": self.sound,
            "music": self.music,
            "position": self.position.name,
            "speed": self.speed.name,
            "background": self.background,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogEntry":
        choices = [DialogChoice.from_dict(c) for c in data.get("choices", [])]
        position = DialogPosition[data.get("position", "BOTTOM")]
        speed = DialogSpeed[data.get("speed", "NORMAL")]

        return cls(
            id=data.get("id", ""),
            speaker=data.get("speaker", ""),
            text=data.get("text", ""),
            portrait=data.get("portrait"),
            choices=choices,
            next_dialog=data.get("next_dialog"),
            conditions=data.get("conditions", []),
            actions=data.get("actions", []),
            sound=data.get("sound"),
            music=data.get("music"),
            position=position,
            speed=speed,
            background=data.get("background"),
        )


@dataclass
class DialogState:
    """Current dialog state."""

    active: bool = False
    current_dialog: Optional[str] = None
    displayed_text: str = ""
    full_text: str = ""
    char_index: int = 0
    choice_index: int = 0
    waiting_for_input: bool = False
    waiting_for_choice: bool = False
    timer: float = 0.0

    def reset(self) -> None:
        self.active = False
        self.current_dialog = None
        self.displayed_text = ""
        self.full_text = ""
        self.char_index = 0
        self.choice_index = 0
        self.waiting_for_input = False
        self.waiting_for_choice = False
        self.timer = 0.0


class DialogCondition:
    """Dialog condition checker."""

    def __init__(self) -> None:
        self.conditions: Dict[str, Callable[[], bool]] = {}

    def register(self, name: str, func: Callable[[], bool]) -> None:
        """Register condition function."""
        self.conditions[name] = func

    def check(self, condition_id: str) -> bool:
        """Check if condition is met."""
        if condition_id in self.conditions:
            return self.conditions[condition_id]()
        return True  # Unknown conditions pass by default

    def check_all(self, condition_ids: List[str]) -> bool:
        """Check if all conditions are met."""
        return all(self.check(cid) for cid in condition_ids)


class DialogManager:
    """
    Dialog system manager.

    Features:
    - Load dialogs from JSON
    - Typewriter text effect
    - Branching choices
    - Conditions and actions
    - Character portraits
    - Localization

    Usage:
        dialog_mgr = DialogManager()
        dialog_mgr.load('dialogs.json')

        dialog_mgr.start('intro')

        while dialog_mgr.active:
            dialog_mgr.update(dt)
            dialog_mgr.render(screen)
    """

    def __init__(self, font_size: int = 24) -> None:
        """
        Initialize dialog manager.

        Args:
            font_size: Font size for dialog text
        """
        self.dialogs: Dict[str, DialogEntry] = {}
        self.state = DialogState()
        self.conditions = DialogCondition()
        self.actions: Dict[str, Callable[[str], None]] = {}

        # Visual settings
        self.box_color: Tuple[int, int, int] = (0, 0, 0)
        self.text_color: Tuple[int, int, int] = (255, 255, 255)
        self.border_color: Tuple[int, int, int] = (255, 215, 0)
        self.box_alpha: int = 200
        self.padding: int = 20
        self.line_height: int = 32

        # Fonts
        self.font: Optional[pg.font.Font] = None
        self.name_font: Optional[pg.font.Font] = None
        self._init_fonts(font_size)

        # Portraits
        self.portraits: Dict[str, pg.Surface] = {}
        self.current_portrait: Optional[pg.Surface] = None

        # Callbacks
        self.on_dialog_start: Optional[Callable[[str], None]] = None
        self.on_dialog_end: Optional[Callable[[], None]] = None
        self.on_choice_made: Optional[Callable[[str, str], None]] = None

        # Localization
        self.language: str = "en"
        self.translations: Dict[str, Dict[str, Any]] = {}

    def _init_fonts(self, font_size: int) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, font_size)
            self.name_font = pg.font.Font(None, font_size - 4)
        except pg.error:
            self.font = None
            self.name_font = None

    def load(self, filepath: str) -> bool:
        """
        Load dialogs from JSON file.

        Args:
            filepath: Path to dialog JSON file

        Returns:
            True if loaded successfully
        """
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for entry_data in data.get("dialogs", []):
                entry = DialogEntry.from_dict(entry_data)
                self.dialogs[entry.id] = entry

            # Load translations if present
            if "translations" in data:
                self.translations = data["translations"]

            return True

        except (json.JSONDecodeError, IOError) as e:
            logger.error("Dialog load error: %s", e)
            return False

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Load dialogs from dictionary."""
        for entry_data in data.get("dialogs", []):
            entry = DialogEntry.from_dict(entry_data)
            self.dialogs[entry.id] = entry

    def get_text(self, dialog_id: str) -> str:
        """Get localized text for dialog."""
        lang_translations = self.translations.get(self.language)
        if lang_translations and dialog_id in lang_translations:
            text = lang_translations[dialog_id]
            return text if isinstance(text, str) else str(text)
        return dialog_id

    def start(self, dialog_id: str) -> bool:
        """
        Start a dialog.

        Args:
            dialog_id: ID of dialog to start

        Returns:
            True if dialog started
        """
        if dialog_id not in self.dialogs:
            return False

        dialog = self.dialogs[dialog_id]

        # Check conditions
        if not self.conditions.check_all(dialog.conditions):
            return False

        # Trigger actions
        for action in dialog.actions:
            self._trigger_action(action)

        # Play sound/music
        if dialog.sound:
            self._play_sound(dialog.sound)
        if dialog.music:
            self._play_music(dialog.music)

        # Set state
        self.state.reset()
        self.state.active = True
        self.state.current_dialog = dialog_id
        self.state.full_text = dialog.text

        # Load portrait
        self.current_portrait = None
        if dialog.portrait and dialog.portrait in self.portraits:
            self.current_portrait = self.portraits[dialog.portrait]

        if self.on_dialog_start:
            self.on_dialog_start(dialog_id)

        return True

    def _trigger_action(self, action_id: str) -> None:
        """Trigger dialog action."""
        if action_id in self.actions:
            self.actions[action_id](action_id)

    def _play_sound(self, sound_id: str) -> None:
        """Play dialog sound."""
        # Placeholder - integrate with audio system
        pass

    def _play_music(self, music_id: str) -> None:
        """Play dialog music."""
        # Placeholder - integrate with audio system
        pass

    def update(self, dt: float) -> None:
        """
        Update dialog state.

        Args:
            dt: Delta time in seconds
        """
        if not self.state.active:
            return

        current_id = self.state.current_dialog
        if not current_id:
            return

        dialog = self.dialogs.get(current_id)
        if not dialog:
            return

        # Typewriter effect
        if not self.state.waiting_for_input and not self.state.waiting_for_choice:
            chars_to_add = int(dialog.speed.value * dt)
            if chars_to_add > 0:
                self.state.char_index += chars_to_add
                if self.state.char_index >= len(self.state.full_text):
                    self.state.char_index = len(self.state.full_text)
                    self.state.waiting_for_input = True

            self.state.displayed_text = self.state.full_text[: self.state.char_index]

    def advance(self) -> bool:
        """
        Advance dialog.

        Returns:
            True if dialog continues, False if ended
        """
        if not self.state.active:
            return False

        current_id = self.state.current_dialog
        if not current_id:
            return False

        dialog = self.dialogs.get(current_id)
        if not dialog:
            return False

        # Show full text if typing
        if not self.state.waiting_for_input:
            self.state.displayed_text = self.state.full_text
            self.state.char_index = len(self.state.full_text)
            self.state.waiting_for_input = True
            return True

        # Handle choices
        if dialog.choices and not self.state.waiting_for_choice:
            self.state.waiting_for_choice = True
            self.state.waiting_for_input = False
            return True

        # Next dialog or end
        if dialog.next_dialog:
            return self.start(dialog.next_dialog)

        self.end()
        return False

    def select_choice(self, index: int) -> bool:
        """
        Select dialog choice.

        Args:
            index: Choice index

        Returns:
            True if choice was valid
        """
        if not self.state.active or not self.state.waiting_for_choice:
            return False

        current_id = self.state.current_dialog
        if not current_id:
            return False

        dialog = self.dialogs.get(current_id)
        if not dialog or index >= len(dialog.choices):
            return False

        choice = dialog.choices[index]

        # Check condition
        if choice.condition and not self.conditions.check(choice.condition):
            return False

        # Trigger action
        if choice.on_select:
            self._trigger_action(choice.on_select)

        if self.on_choice_made:
            self.on_choice_made(dialog.id, choice.text)

        return self.start(choice.next_dialog)

    def end(self) -> None:
        """End current dialog."""
        if self.on_dialog_end:
            self.on_dialog_end()
        self.state.reset()

    def render(self, surface: pg.Surface) -> None:
        """
        Render dialog.

        Args:
            surface: Surface to render to
        """
        if not self.state.active:
            return

        current_id = self.state.current_dialog
        if not current_id:
            return

        dialog = self.dialogs.get(current_id)
        if not dialog:
            return

        # Calculate box position
        box_rect = self._get_box_rect(surface.get_size())

        # Draw background
        box = pg.Surface((box_rect.width, box_rect.height), pg.SRCALPHA)
        box.fill((*self.box_color, self.box_alpha))
        surface.blit(box, box_rect)

        # Draw border
        pg.draw.rect(surface, self.border_color, box_rect, 2)

        # Draw portrait
        portrait_x = box_rect.x + self.padding
        portrait_y = box_rect.y + self.padding
        if self.current_portrait:
            surface.blit(self.current_portrait, (portrait_x, portrait_y))
            text_x = portrait_x + self.current_portrait.get_width() + self.padding
        else:
            text_x = portrait_x

        # Draw speaker name
        name_y = box_rect.y + self.padding
        if dialog.speaker and self.name_font:
            name_text = self.name_font.render(dialog.speaker, True, self.border_color)
            surface.blit(name_text, (text_x, name_y))
            text_y = name_y + self.line_height
        else:
            text_y = name_y

        # Draw dialog text
        if self.font:
            lines = self._wrap_text(self.state.displayed_text, box_rect.width - 2 * self.padding)
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, self.text_color)
                surface.blit(text_surface, (text_x, text_y + i * self.line_height))

        # Draw choices
        if self.state.waiting_for_choice and dialog.choices:
            choice_y = box_rect.bottom - self.padding - len(dialog.choices) * self.line_height
            for i, choice in enumerate(dialog.choices):
                # Check if choice is available
                available = not choice.condition or self.conditions.check(choice.condition)
                color = self.text_color if available else (128, 128, 128)

                prefix = "> " if i == self.state.choice_index else "  "
                if self.font:
                    choice_text = self.font.render(prefix + choice.text, True, color)
                    surface.blit(choice_text, (text_x, choice_y + i * self.line_height))

        # Draw continue indicator
        if self.state.waiting_for_input and not dialog.choices and self.font:
            indicator = self.font.render("▼", True, self.border_color)
            surface.blit(indicator, (box_rect.right - 40, box_rect.bottom - 30))

    def _get_box_rect(self, screen_size: Tuple[int, int]) -> pg.Rect:
        """Get dialog box rectangle based on position."""
        width = screen_size[0] - 2 * self.padding
        height = 150

        position = DialogPosition.BOTTOM
        if self.state.current_dialog:
            dialog = self.dialogs.get(self.state.current_dialog)
            if dialog:
                position = dialog.position

        if position == DialogPosition.TOP:
            x = self.padding
            y = self.padding
        elif position == DialogPosition.CENTER:
            x = (screen_size[0] - width) // 2
            y = (screen_size[1] - height) // 2
        elif position == DialogPosition.BOTTOM:
            x = self.padding
            y = screen_size[1] - height - self.padding
        elif position == DialogPosition.TOP_LEFT:
            x = self.padding
            y = self.padding
            width = 400
        elif position == DialogPosition.TOP_RIGHT:
            x = screen_size[0] - 400 - self.padding
            y = self.padding
            width = 400
        elif position == DialogPosition.BOTTOM_LEFT:
            x = self.padding
            y = screen_size[1] - height - self.padding
            width = 400
        elif position == DialogPosition.BOTTOM_RIGHT:
            x = screen_size[0] - 400 - self.padding
            y = screen_size[1] - height - self.padding
            width = 400
        else:
            x = self.padding
            y = screen_size[1] - height - self.padding

        return pg.Rect(x, y, width, height)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within width."""
        if not self.font:
            return [text]

        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines

    def add_portrait(self, name: str, surface: pg.Surface) -> None:
        """Add character portrait."""
        self.portraits[name] = surface

    def register_action(self, name: str, func: Callable[[str], None]) -> None:
        """Register dialog action handler."""
        self.actions[name] = func

    def register_condition(self, name: str, func: Callable[[], bool]) -> None:
        """Register dialog condition."""
        self.conditions.register(name, func)

    @property
    def active(self) -> bool:
        """Check if dialog is active."""
        return self.state.active

    @property
    def current_id(self) -> Optional[str]:
        """Get current dialog ID."""
        return self.state.current_dialog


# Global dialog manager
_dialog_manager: Optional[DialogManager] = None


def get_dialog_manager() -> DialogManager:
    """Get global dialog manager."""
    global _dialog_manager
    if _dialog_manager is None:
        _dialog_manager = DialogManager()
    return _dialog_manager
