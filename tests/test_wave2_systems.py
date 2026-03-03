"""
Tests for Wave 2 systems:
- Event System
- Render System
- Profiler
- Debug Utils
- Controller
- Dialog System
"""
from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEventSystem:
    """Tests for event system."""

    def test_event_creation(self):
        """Test event creation."""
        from data.event_system import Event, EventType

        event = Event(EventType.PLAYER_JUMP, {"height": 100})
        assert event.type == EventType.PLAYER_JUMP
        assert event.get("height") == 100
        assert not event.is_cancelled()

    def test_event_cancellation(self):
        """Test event cancellation."""
        from data.event_system import Event, EventType

        event = Event(EventType.PLAYER_JUMP)
        event.cancel()
        assert event.is_cancelled()

    def test_event_manager_emit(self):
        """Test event emission."""
        from data.event_system import EventManager, EventType

        manager = EventManager()
        received = []

        def handler(event):
            received.append(event)

        manager.on(EventType.PLAYER_JUMP, handler)
        manager.emit(EventType.PLAYER_JUMP, {"test": True})

        assert len(received) == 1
        assert received[0].get("test") is True

    def test_event_priority(self):
        """Test event handler priority."""
        from data.event_system import EventManager, EventType

        manager = EventManager()
        order = []

        def handler1(event):
            order.append(1)

        def handler2(event):
            order.append(2)

        manager.on(EventType.PLAYER_JUMP, handler1, priority=0)
        manager.on(EventType.PLAYER_JUMP, handler2, priority=10)
        manager.emit(EventType.PLAYER_JUMP)

        assert order == [2, 1]  # Higher priority first

    def test_event_once(self):
        """Test once handler."""
        from data.event_system import EventManager, EventType

        manager = EventManager()
        count = [0]

        def handler(event):
            count[0] += 1

        manager.on(EventType.PLAYER_JUMP, handler, once=True)
        manager.emit(EventType.PLAYER_JUMP)
        manager.emit(EventType.PLAYER_JUMP)

        assert count[0] == 1

    def test_global_handler(self):
        """Test global event handler."""
        from data.event_system import EventManager, EventType

        manager = EventManager()
        received = []

        def global_handler(event):
            received.append(event.type)

        manager.on_global(global_handler)
        manager.emit(EventType.PLAYER_JUMP)
        manager.emit(EventType.PLAYER_SCORE)

        assert EventType.PLAYER_JUMP in received
        assert EventType.PLAYER_SCORE in received

    def test_event_stats(self):
        """Test event statistics."""
        from data.event_system import EventManager, EventType

        manager = EventManager()
        manager.emit(EventType.PLAYER_JUMP)
        manager.emit(EventType.PLAYER_JUMP)
        manager.emit(EventType.PLAYER_SCORE)

        stats = manager.get_stats()
        assert stats["emitted"] == 3


class TestRenderSystem:
    """Tests for render system."""

    def test_sprite_renderer_creation(self, init_pygame):
        """Test sprite renderer initialization."""
        import pygame as pg
        from data.render_system import SpriteRenderer

        screen = pg.display.set_mode((800, 600))
        renderer = SpriteRenderer(screen)
        assert renderer is not None

    def test_sprite_batching(self, init_pygame):
        """Test sprite batching."""
        import pygame as pg
        from data.render_system import SpriteRenderer, RenderLayer

        screen = pg.display.set_mode((800, 600))
        renderer = SpriteRenderer(screen)

        # Add sprites with same image (should batch)
        image = pg.Surface((32, 32))
        for i in range(10):
            rect = pg.Rect(i * 32, 0, 32, 32)
            renderer.add_sprite(rect, image, RenderLayer.ITEMS)

        renderer.render()
        stats = renderer.get_stats()
        assert stats["visible_sprites"] == 10

    def test_viewport_culling(self, init_pygame):
        """Test viewport culling."""
        import pygame as pg
        from data.render_system import SpriteRenderer, RenderLayer

        screen = pg.display.set_mode((800, 600))
        renderer = SpriteRenderer(screen)

        viewport = pg.Rect(0, 0, 400, 400)
        renderer.set_viewport(viewport)

        # Add sprite inside viewport
        image = pg.Surface((32, 32))
        renderer.add_sprite(pg.Rect(100, 100, 32, 32), image, RenderLayer.ITEMS)

        # Add sprite outside viewport
        renderer.add_sprite(pg.Rect(500, 500, 32, 32), image, RenderLayer.ITEMS)

        renderer.render()
        stats = renderer.get_stats()
        assert stats["visible_sprites"] == 1
        assert stats["culled_sprites"] == 1

    def test_texture_atlas(self, init_pygame):
        """Test texture atlas functionality."""
        import pygame as pg
        from data.render_system import TextureAtlas

        atlas = TextureAtlas(512, 512)

        # Add textures
        tex1 = pg.Surface((64, 64))
        tex2 = pg.Surface((32, 32))

        region1 = atlas.add_texture("tex1", tex1)
        region2 = atlas.add_texture("tex2", tex2)

        assert region1 is not None
        assert region2 is not None
        assert len(atlas.regions) == 2

        # Get regions
        assert atlas.get_region("tex1") == region1
        assert atlas.get_region("tex2") == region2

    def test_renderer_with_atlas(self, init_pygame):
        """Test renderer with texture atlas."""
        import pygame as pg
        from data.render_system import SpriteRenderer

        screen = pg.display.set_mode((800, 600))
        renderer = SpriteRenderer(screen, use_atlas=True)

        atlas = renderer.get_atlas()
        assert atlas is not None

        # Add texture to atlas
        texture = pg.Surface((32, 32))
        success = renderer.add_to_atlas("test_tex", texture)
        assert success

        # Check atlas stats
        stats = renderer.get_atlas_stats()
        assert stats["enabled"]
        assert stats["regions"] == 1


class TestProfiler:
    """Tests for profiler."""

    def test_profiler_creation(self):
        """Test profiler initialization."""
        from data.profiler import Profiler

        profiler = Profiler()
        assert profiler is not None

    def test_profiler_start_stop(self):
        """Test profiler start/stop."""
        from data.profiler import Profiler

        profiler = Profiler()
        profiler.start()
        assert profiler._running

        profiler.stop()
        assert not profiler._running

    def test_profiler_frame_timing(self):
        """Test frame timing."""
        from data.profiler import Profiler

        profiler = Profiler()
        profiler.start()

        time.sleep(0.016)  # ~60fps
        stats = profiler.end_frame()

        assert stats.frame_time > 0
        assert stats.fps > 0

    def test_profiler_section(self):
        """Test section profiling."""
        from data.profiler import Profiler

        profiler = Profiler()
        profiler.start()

        with profiler.profile("test_section"):
            time.sleep(0.01)

        profiler.end_frame()
        stats = profiler.get_stats()
        assert stats.total_frames == 1

    def test_profiler_stats(self):
        """Test profiler statistics."""
        from data.profiler import Profiler

        profiler = Profiler(history_size=10)
        profiler.start()

        for _ in range(5):
            profiler.end_frame()

        stats = profiler.get_stats()
        assert stats.total_frames == 5
        assert stats.fps_avg > 0


class TestDebugUtils:
    """Tests for debug utilities."""

    def test_debug_overlay_creation(self, init_pygame):
        """Test debug overlay initialization."""
        import pygame as pg
        from data.debug_utils import DebugOverlay

        screen = pg.display.set_mode((800, 600))
        overlay = DebugOverlay(screen)
        assert overlay is not None
        assert not overlay.enabled

    def test_debug_overlay_toggle(self, init_pygame):
        """Test debug overlay toggle."""
        import pygame as pg
        from data.debug_utils import DebugOverlay

        screen = pg.display.set_mode((800, 600))
        overlay = DebugOverlay(screen)

        overlay.toggle()
        assert overlay.enabled

        overlay.toggle()
        assert not overlay.enabled

    def test_debug_console_creation(self):
        """Test debug console initialization."""
        from data.debug_utils import DebugConsole

        console = DebugConsole()
        assert console is not None
        assert not console.enabled

    def test_debug_console_commands(self):
        """Test debug console commands."""
        from data.debug_utils import DebugConsole

        console = DebugConsole()

        # Test help command
        assert "help" in console.commands
        assert "fps" in console.commands

    def test_hitbox_visualizer(self):
        """Test hitbox visualizer."""
        from data.debug_utils import HitboxVisualizer

        visualizer = HitboxVisualizer()
        assert not visualizer.enabled

        visualizer.toggle()
        assert visualizer.enabled


class TestDialogSystem:
    """Tests for dialog system."""

    def test_dialog_manager_creation(self, init_pygame):
        """Test dialog manager initialization."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        assert manager is not None
        assert not manager.active

    def test_dialog_load_from_dict(self, init_pygame):
        """Test dialog loading from dictionary."""
        from data.dialog_system import DialogManager

        manager = DialogManager()

        data = {
            "dialogs": [
                {
                    "id": "test_dialog",
                    "speaker": "Mario",
                    "text": "Hello, World!",
                }
            ]
        }

        manager.load_from_dict(data)
        assert "test_dialog" in manager.dialogs

    def test_dialog_start(self, init_pygame):
        """Test starting dialog."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        manager.load_from_dict({"dialogs": [{"id": "test", "speaker": "Mario", "text": "Hello!"}]})

        result = manager.start("test")
        assert result is True
        assert manager.active
        assert manager.current_id == "test"

    def test_dialog_start_invalid(self, init_pygame):
        """Test starting invalid dialog."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        result = manager.start("nonexistent")
        assert result is False
        assert not manager.active

    def test_dialog_update(self, init_pygame):
        """Test dialog update with typewriter effect."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        manager.load_from_dict(
            {
                "dialogs": [
                    {
                        "id": "test",
                        "speaker": "Mario",
                        "text": "Hello World!",
                        "speed": "FAST",
                    }
                ]
            }
        )

        manager.start("test")
        initial_text = manager.state.displayed_text

        manager.update(0.1)  # 100ms
        later_text = manager.state.displayed_text

        assert len(later_text) >= len(initial_text)

    def test_dialog_advance(self, init_pygame):
        """Test dialog advancement."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        manager.load_from_dict(
            {
                "dialogs": [
                    {"id": "test1", "speaker": "Mario", "text": "First", "next_dialog": "test2"},
                    {"id": "test2", "speaker": "Luigi", "text": "Second"},
                ]
            }
        )

        manager.start("test1")
        manager.state.waiting_for_input = True  # Simulate typing complete

        result = manager.advance()
        assert result is True
        assert manager.current_id == "test2"

    def test_dialog_end(self, init_pygame):
        """Test dialog ending."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        manager.load_from_dict({"dialogs": [{"id": "test", "speaker": "Mario", "text": "Hello!"}]})

        manager.start("test")
        manager.end()

        assert not manager.active
        assert manager.current_id is None

    def test_dialog_choices(self, init_pygame):
        """Test dialog choices."""
        from data.dialog_system import DialogManager

        manager = DialogManager()
        manager.load_from_dict(
            {
                "dialogs": [
                    {
                        "id": "start",
                        "speaker": "NPC",
                        "text": "Choose wisely!",
                        "choices": [
                            {"text": "Option 1", "next_dialog": "ending1"},
                            {"text": "Option 2", "next_dialog": "ending2"},
                        ],
                    },
                    {"id": "ending1", "speaker": "NPC", "text": "You chose 1!"},
                    {"id": "ending2", "speaker": "NPC", "text": "You chose 2!"},
                ]
            }
        )

        manager.start("start")
        manager.state.waiting_for_input = True
        manager.advance()  # Now waiting for choice

        manager.select_choice(0)
        assert manager.current_id == "ending1"


class TestController:
    """Tests for controller system."""

    def test_controller_manager_creation(self, init_pygame):
        """Test controller manager initialization."""
        from data.controller import ControllerManager

        manager = ControllerManager()
        assert manager is not None

    def test_controller_config(self):
        """Test controller configuration."""
        from data.controller import ControllerConfig

        config = ControllerConfig()
        assert "jump" in config.button_mappings
        assert config.vibration_enabled is True

    def test_controller_config_to_dict(self):
        """Test controller config serialization."""
        from data.controller import ControllerConfig

        config = ControllerConfig()
        data = config.to_dict()

        assert "button_mappings" in data
        assert "vibration_enabled" in data

    def test_controller_config_from_dict(self):
        """Test controller config deserialization."""
        from data.controller import ControllerConfig

        data = {
            "button_mappings": {"jump": 5},
            "vibration_enabled": False,
            "deadzone": 0.2,
        }

        config = ControllerConfig.from_dict(data)
        assert config.button_mappings["jump"] == 5
        assert config.vibration_enabled is False
        assert config.deadzone == 0.2


@pytest.fixture
def init_pygame():
    """Initialize pygame for tests."""
    import pygame as pg

    pg.init()
    pg.display.set_mode((100, 100))
    yield
    pg.quit()
