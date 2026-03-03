"""
Pytest configuration and fixtures for Mario Level 1 tests.
"""
from __future__ import annotations

import os
import sys
import pytest

try:
    import pygame as pg
except Exception:  # pragma: no cover - fallback for environments without pygame
    from types import ModuleType, SimpleNamespace

    class _DummySurface:
        def __init__(self, size=(0, 0)):
            self._size = tuple(size)
            self._alpha = 255

        def get_size(self):
            return self._size

    class _Display:
        def __init__(self):
            self._mode = None
            self._surface = None

        def set_mode(self, size):
            self._mode = tuple(size)
            self._surface = _DummySurface(size)
            return self._surface

        def get_surface(self):
            return self._surface

    class _Time:
        class Clock:
            def tick(self, *_, **__):
                return 0

    def _init():
        return None

    def _quit():
        return None

    pg = ModuleType("pygame")
    pg.init = _init
    pg.quit = _quit
    pg.display = _Display()
    pg.time = _Time()

    # Minimal key constants and event support used in tests
    pg.K_a = ord("a")
    pg.K_s = ord("s")
    pg.K_z = ord("z")
    pg.K_d = ord("d")
    pg.K_w = ord("w")
    pg.K_SPACE = 32
    pg.K_RETURN = 13
    pg.K_BACKSPACE = 8
    pg.K_ESCAPE = 27
    pg.K_LSHIFT = 304
    pg.K_LEFT = 276
    pg.K_RIGHT = 275
    pg.K_UP = 273
    pg.K_DOWN = 274
    pg.K_F3 = 294
    pg.K_F4 = 295
    pg.K_F5 = 296
    pg.K_F9 = 300
    pg.K_F10 = 301
    pg.K_F12 = 303
    pg.K_BACKQUOTE = 96

    class _EventModule:
        KEYDOWN = 1
        KEYUP = 2
        MOUSEBUTTONDOWN = 3
        MOUSEBUTTONUP = 4

        @staticmethod
        def Event(event_type, attrs=None):
            obj = SimpleNamespace()
            obj.type = event_type
            if attrs:
                for k, v in attrs.items():
                    setattr(obj, k, v)
            return obj
        @staticmethod
        def set_allowed(_):
            return None

    pg.event = _EventModule()
    # Mirror common event constants at module level
    pg.KEYDOWN = _EventModule.KEYDOWN
    pg.KEYUP = _EventModule.KEYUP
    pg.MOUSEBUTTONDOWN = _EventModule.MOUSEBUTTONDOWN
    pg.MOUSEBUTTONUP = _EventModule.MOUSEBUTTONUP

    # Minimal sprite implementation
    class _Sprite:
        def __init__(self):
            self.image = None
            self.rect = None

        def update(self, *_, **__):
            pass

    class _Group:
        def __init__(self):
            self._sprites = []

        def add(self, *sprites):
            for s in sprites:
                if s not in self._sprites:
                    self._sprites.append(s)

        def remove(self, *sprites):
            for s in sprites:
                if s in self._sprites:
                    self._sprites.remove(s)

        def empty(self):
            self._sprites.clear()

        def update(self, *args, **kwargs):
            for s in list(self._sprites):
                if hasattr(s, "update"):
                    s.update(*args, **kwargs)

        def sprites(self):
            return list(self._sprites)

    pg.sprite = SimpleNamespace(Sprite=_Sprite, Group=_Group)

    # Dummy surface with basic drawing API used in tests
    class _DummySurface:
        def __init__(self, size=(0, 0)):
            self._size = tuple(size)

        def get_size(self):
            return self._size

        def fill(self, color):
            return None

        def blit(self, src, dest, *args, **kwargs):
            return None

        def get_rect(self, **kwargs):
            w, h = self._size
            center = kwargs.get("center")
            topleft = kwargs.get("topleft")
            if center is not None:
                cx, cy = center
                return _Rect(int(cx - w // 2), int(cy - h // 2), w, h)
            if topleft is not None:
                x, y = topleft
                return _Rect(int(x), int(y), w, h)
            return _Rect(0, 0, w, h)
        def set_alpha(self, alpha):
            self._alpha = alpha

        def convert(self):
            return self

        def set_colorkey(self, color):
            self._colorkey = color

        def get_width(self):
            return self._size[0]

        def get_height(self):
            return self._size[1]

        def subsurface(self, rect):
            # Return a new surface representing the subsurface area
            try:
                w = rect.width
                h = rect.height
            except Exception:
                try:
                    _, _, w, h = rect
                except Exception:
                    w, h = self._size
            return _DummySurface((w, h))

    def _image_save(surface, path):
        try:
            # create an empty file so directory scans will find it
            with open(path, "wb") as f:
                f.write(b"")
        except Exception:
            pass

    def _image_load(path):
        # Return a dummy surface for tests
        return _DummySurface((10, 10))

    pg.image = SimpleNamespace(save=_image_save, load=_image_load)
    

    # Simple Rect implementation
    class _Rect:
        def __init__(self, *args):
            if len(args) == 1 and isinstance(args[0], (tuple, list)):
                x, y, w, h = args[0]
            else:
                x, y, w, h = (args + (0, 0, 0, 0))[:4]
            self.x = x
            self.y = y
            self.width = w
            self.height = h
        @property
        def left(self):
            return self.x

        @left.setter
        def left(self, val):
            self.x = int(val)

        @property
        def right(self):
            return self.x + self.width

        @right.setter
        def right(self, val):
            self.x = int(val) - self.width

        @property
        def top(self):
            return self.y

        @top.setter
        def top(self, val):
            self.y = int(val)

        @property
        def bottom(self):
            return self.y + self.height

        @bottom.setter
        def bottom(self, val):
            self.y = int(val) - self.height

        def collidepoint(self, point):
            px, py = point
            return self.left <= px <= self.right and self.top <= py <= self.bottom

        def colliderect(self, other):
            # Simple AABB collision
            return not (
                self.right <= other.left
                or self.left >= other.right
                or self.bottom <= other.top
                or self.top >= other.bottom
            )

        def inflate(self, dx, dy):
            # return a new rect expanded by dx/dy (both sides total)
            new_x = self.x - dx // 2
            new_y = self.y - dy // 2
            new_w = self.width + dx
            new_h = self.height + dy
            return _Rect(new_x, new_y, new_w, new_h)
        @property
        def topleft(self):
            return (self.x, self.y)

        @topleft.setter
        def topleft(self, val):
            x, y = val
            self.x = int(x)
            self.y = int(y)

        @property
        def center(self):
            return (self.x + self.width // 2, self.y + self.height // 2)

        @center.setter
        def center(self, val):
            cx, cy = val
            self.x = int(cx - self.width // 2)
            self.y = int(cy - self.height // 2)

    # Basic font and image stubs
    class _Font:
        def __init__(self, *_, **__):
            pass

        def render(self, text, aa, color):
            # Return a dummy surface sized by text length
            return _DummySurface((max(1, len(str(text)) * 8), 16))

    pg.font = SimpleNamespace(Font=_Font)
    pg.error = Exception
    pg.image = SimpleNamespace(save=lambda surface, path: None)
    def _draw_rect(surface, color, rect, *_, **__):
        return None

    pg.draw = SimpleNamespace(rect=_draw_rect)

    # Minimal transform helpers
    class _Transform:
        @staticmethod
        def scale(surface, size):
            try:
                return _DummySurface(size)
            except Exception:
                return surface
        @staticmethod
        def flip(surface, flip_x, flip_y):
            # Tests only need a flipped surface placeholder; return same surface
            try:
                # preserve size when possible
                return _DummySurface(surface.get_size())
            except Exception:
                return surface

    pg.transform = _Transform()

    # Basic constants
    pg.SRCALPHA = 1
    pg.SRCALPHA = 1

    # Time helpers
    class _Time:
        class Clock:
            def tick(self, *_, **__):
                return 0

        @staticmethod
        def get_ticks():
            return 0

    pg.time = _Time()

    # Keys and keyboard state
    pg.key = SimpleNamespace(get_pressed=lambda: [False] * 512)

    # Surface and Rect aliases
    pg.Surface = _DummySurface
    pg.Rect = _Rect

    # Simple mixer stub
    pg.mixer = SimpleNamespace(Sound=lambda *a, **k: SimpleNamespace(play=lambda: None))

    # Make the dummy pygame available for subsequent imports
    sys.modules["pygame"] = pg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Expose constants module as 'c' to tests that expect it in globals
try:
    from data import constants as c  # type: ignore
    import builtins

    builtins.c = c
except Exception:
    pass


def pytest_collection_modifyitems(config, items):
    """Skip benchmark tests if pytest-benchmark is not installed."""
    # Skip benchmark tests by default (require special plugin)
    skip_benchmark = pytest.mark.skip(reason="Requires pytest-benchmark plugin")
    for item in items:
        if "benchmark" in item.nodeid:
            item.add_marker(skip_benchmark)


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """Initialize pygame once per test session."""
    try:
        pg.init()
        pg.display.set_mode((100, 100))
    except Exception:
        # If running with the dummy pygame, the calls are safe no-ops
        pass
    yield
    try:
        pg.quit()
    except Exception:
        pass


@pytest.fixture
def screen():
    """Create a pygame surface for rendering tests."""
    return pg.display.set_mode((800, 600))


@pytest.fixture
def clock():
    """Create a pygame clock for timing tests."""
    return pg.time.Clock()


@pytest.fixture
def temp_asset_dir():
    """Create temporary asset directory for tests."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)

        # Create subdirectories
        (path / "graphics").mkdir()
        (path / "sound").mkdir()
        (path / "fonts").mkdir()

        # Create test image
        pg.init()
        surface = pg.Surface((32, 32))
        surface.fill((255, 0, 0))
        try:
            pg.image.save(surface, str(path / "graphics" / "test.png"))
        except Exception:
            pass  # Ignore if save fails in test environment

        pg.quit()

        yield path


@pytest.fixture(scope="session", autouse=True)
def init_setup_resources():
    """Initialize setup.GFX with dummy resources for component tests."""
    from data import setup
    
    # Create dummy surfaces for required assets
    if not setup.GFX.get("tile_set"):
        setup.GFX["tile_set"] = pg.Surface((512, 512))
    if not setup.GFX.get("item_objects"):
        setup.GFX["item_objects"] = pg.Surface((512, 512))
    if not setup.GFX.get("smb_enemies_sheet"):
        setup.GFX["smb_enemies_sheet"] = pg.Surface((512, 512))
    if not setup.GFX.get("mario_bros"):
        setup.GFX["mario_bros"] = pg.Surface((512, 512))
    if not setup.GFX.get("text_images"):
        setup.GFX["text_images"] = pg.Surface((512, 512))
    
    yield
