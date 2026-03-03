"""
Optimized Sprite Rendering System.

Features:
- Sprite batching for reduced draw calls
- Viewport culling (only render visible sprites)
- Layer-based rendering
- Dirty rectangle tracking
- Surface caching
- Texture atlas support
"""
from __future__ import annotations

import pygame as pg
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import IntEnum


class RenderLayer(IntEnum):
    """Rendering layers for proper z-ordering."""

    BACKGROUND = 0
    GROUND = 1
    BRICKS = 2
    ENEMIES = 3
    ITEMS = 4
    PLAYER = 5
    PARTICLES = 6
    UI = 7
    OVERLAY = 8


@dataclass
class AtlasRegion:
    """Region within a texture atlas."""

    x: int
    y: int
    width: int
    height: int
    name: str = ""

    def to_rect(self) -> pg.Rect:
        """Convert to pygame Rect."""
        return pg.Rect(self.x, self.y, self.width, self.height)


class TextureAtlas:
    """
    Texture atlas for efficient sprite rendering.

    Combines multiple small textures into one large texture
    to reduce texture switching overhead.
    """

    def __init__(self, width: int = 2048, height: int = 2048) -> None:
        """
        Initialize texture atlas.

        Args:
            width: Atlas width
            height: Atlas height
        """
        self.width = width
        self.height = height
        self.surface = pg.Surface((width, height), pg.SRCALPHA)
        self.regions: Dict[str, AtlasRegion] = {}
        self._current_x = 0
        self._current_y = 0
        self._row_height = 0

    def add_texture(self, name: str, texture: pg.Surface) -> Optional[AtlasRegion]:
        """
        Add texture to atlas.

        Args:
            name: Texture identifier
            texture: Texture surface

        Returns:
            Atlas region or None if doesn't fit
        """
        if name in self.regions:
            return self.regions[name]

        w, h = texture.get_size()

        # Check if fits in current row
        if self._current_x + w > self.width:
            # Move to next row
            self._current_x = 0
            self._current_y += self._row_height
            self._row_height = 0

        # Check if fits in atlas
        if self._current_y + h > self.height:
            return None

        # Blit texture to atlas
        self.surface.blit(texture, (self._current_x, self._current_y))

        # Create region
        region = AtlasRegion(
            x=self._current_x,
            y=self._current_y,
            width=w,
            height=h,
            name=name,
        )
        self.regions[name] = region

        # Update position
        self._current_x += w
        self._row_height = max(self._row_height, h)

        return region

    def get_region(self, name: str) -> Optional[AtlasRegion]:
        """Get atlas region by name."""
        return self.regions.get(name)

    def clear(self) -> None:
        """Clear atlas."""
        self.surface.fill((0, 0, 0, 0))
        self.regions.clear()
        self._current_x = 0
        self._current_y = 0
        self._row_height = 0


@dataclass
class RenderStats:
    """Rendering statistics."""

    total_sprites: int = 0
    visible_sprites: int = 0
    culled_sprites: int = 0
    batches: int = 0
    draw_calls: int = 0
    dirty_rects: int = 0

    def reset(self) -> None:
        """Reset statistics."""
        self.total_sprites = 0
        self.visible_sprites = 0
        self.culled_sprites = 0
        self.batches = 0
        self.draw_calls = 0
        self.dirty_rects = 0

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access for tests."""
        return getattr(self, key)


@dataclass
class SpriteBatch:
    """
    Batch of sprites to render together.

    Groups sprites by texture for efficient rendering.
    """

    texture: pg.Surface
    sprites: List[Tuple[pg.Rect, Optional[pg.Rect]]] = field(default_factory=list)

    def add(self, rect: pg.Rect, src_rect: Optional[pg.Rect] = None) -> None:
        """Add sprite to batch."""
        self.sprites.append((rect, src_rect))

    def clear(self) -> None:
        """Clear batch."""
        self.sprites.clear()

    def render(self, surface: pg.Surface, offset: Tuple[int, int] = (0, 0)) -> int:
        """
        Render batch to surface.

        Args:
            surface: Target surface
            offset: Camera offset (x, y)

        Returns:
            Number of draw calls made
        """
        if not self.sprites:
            return 0

        ox, oy = offset
        draw_calls = 0

        for rect, src_rect in self.sprites:
            # Apply offset
            dest_rect = pg.Rect(rect.x - ox, rect.y - oy, rect.width, rect.height)

            # Cull off-screen sprites
            if dest_rect.right < 0 or dest_rect.left > surface.get_width():
                continue
            if dest_rect.bottom < 0 or dest_rect.top > surface.get_height():
                continue

            # Blit
            if src_rect:
                surface.blit(self.texture, dest_rect, src_rect)
            else:
                surface.blit(self.texture, dest_rect)
            draw_calls += 1

        return draw_calls


class SpriteRenderer:
    """
    Optimized sprite rendering system.

    Features:
    - Batch rendering by texture
    - Viewport culling
    - Layer-based rendering
    - Statistics tracking
    - Texture atlas support

    Usage:
        renderer = SpriteRenderer(screen)
        renderer.add_sprite(mario, RenderLayer.PLAYER)
        renderer.render(viewport_rect)
    """

    def __init__(self, surface: pg.Surface, use_atlas: bool = False) -> None:
        """
        Initialize sprite renderer.

        Args:
            surface: Target surface for rendering
            use_atlas: Enable texture atlas optimization
        """
        self.surface = surface
        self.stats = RenderStats()

        # Batches per layer
        self._batches: Dict[RenderLayer, Dict[int, SpriteBatch]] = {layer: {} for layer in RenderLayer}

        # Sprite data
        self._sprites: List[RenderSprite] = []

        # Viewport for culling
        self._viewport: Optional[pg.Rect] = None

        # Dirty rect tracking
        self._dirty_rects: Set[pg.Rect] = set()
        self._use_dirty: bool = False

        # Texture atlas
        self._use_atlas = use_atlas
        self._atlas: Optional[TextureAtlas] = None
        if use_atlas:
            self._atlas = TextureAtlas()

    def get_atlas(self) -> Optional[TextureAtlas]:
        """Get texture atlas."""
        return self._atlas

    def add_to_atlas(self, name: str, texture: pg.Surface) -> bool:
        """
        Add texture to atlas.

        Args:
            name: Texture identifier
            texture: Texture surface

        Returns:
            True if added successfully
        """
        if not self._use_atlas or self._atlas is None:
            return False

        region = self._atlas.add_texture(name, texture)
        return region is not None

    def add_sprite(
        self,
        rect: Optional[pg.Rect],
        image: Optional[pg.Surface],
        layer: RenderLayer = RenderLayer.ITEMS,
        src_rect: Optional[pg.Rect] = None,
    ) -> None:
        """
        Add sprite to render queue.

        Args:
            rect: Destination rectangle
            image: Sprite image/texture
            layer: Rendering layer
            src_rect: Source rectangle (for sprite sheets)
        """
        if rect is None or image is None:
            return
        self._sprites.append(
            RenderSprite(
                rect=rect,
                image=image,
                layer=layer,
                src_rect=src_rect,
            )
        )

    def add_sprite_object(self, sprite: pg.sprite.Sprite, layer: RenderLayer) -> None:
        """
        Add pygame sprite to render queue.

        Args:
            sprite: Pygame sprite object
            layer: Rendering layer
        """
        if hasattr(sprite, "image") and hasattr(sprite, "rect"):
            rect = sprite.rect
            if rect is not None:
                self.add_sprite(pg.Rect(rect), sprite.image, layer)

    def add_sprite_group(
        self,
        group: pg.sprite.Group,
        layer: RenderLayer,
    ) -> None:
        """
        Add sprite group to render queue.

        Args:
            group: Pygame sprite group
            layer: Rendering layer
        """
        for sprite in group.sprites():
            self.add_sprite_object(sprite, layer)

    def set_viewport(self, viewport: pg.Rect) -> None:
        """
        Set viewport for culling.

        Args:
            viewport: Visible area rectangle
        """
        self._viewport = viewport

    def _should_cull(self, rect: pg.Rect) -> bool:
        """Check if sprite should be culled."""
        if self._viewport is None:
            return False

        # Expand viewport slightly for safety margin
        margin = 50
        viewport = self._viewport.inflate(margin * 2, margin * 2)

        return (
            rect.right < viewport.left
            or rect.left > viewport.right
            or rect.bottom < viewport.top
            or rect.top > viewport.bottom
        )

    def _build_batches(self) -> None:
        """Build sprite batches from sprite list."""
        # Clear existing batches
        for layer_batches in self._batches.values():
            layer_batches.clear()

        for sprite in self._sprites:
            # Cull check
            if self._should_cull(sprite.rect):
                self.stats.culled_sprites += 1
                continue

            self.stats.visible_sprites += 1

            # Get texture ID
            texture_id = id(sprite.image)

            # Get or create batch
            layer_batches = self._batches[sprite.layer]
            if texture_id not in layer_batches:
                layer_batches[texture_id] = SpriteBatch(texture=sprite.image)

            # Add to batch
            layer_batches[texture_id].add(sprite.rect, sprite.src_rect)

    def render(
        self,
        offset: Tuple[int, int] = (0, 0),
        clear: bool = True,
    ) -> None:
        """
        Render all sprites.

        Args:
            offset: Camera offset (x, y)
            clear: Clear surface before rendering
        """
        self.stats.reset()
        self.stats.total_sprites = len(self._sprites)

        if clear:
            self.surface.fill((0, 0, 0))

        # Build batches
        self._build_batches()
        self.stats.batches = sum(len(batches) for batches in self._batches.values())

        # Render by layer
        for layer in RenderLayer:
            layer_batches = self._batches[layer]
            for batch in layer_batches.values():
                draw_calls = batch.render(self.surface, offset)
                self.stats.draw_calls += draw_calls

        # Clear sprite list for next frame
        self._sprites.clear()

    def render_group(
        self,
        group: pg.sprite.Group,
        offset: Tuple[int, int] = (0, 0),
    ) -> int:
        """
        Render sprite group directly (without batching).

        For simple cases where batching overhead isn't worth it.

        Args:
            group: Sprite group to render
            offset: Camera offset

        Returns:
            Number of sprites rendered
        """
        count = 0
        ox, oy = offset

        for sprite in group.sprites():
            if not hasattr(sprite, "image") or not hasattr(sprite, "rect"):
                continue

            # Cull check
            if self._should_cull(sprite.rect):
                continue

            # Blit
            dest_rect = pg.Rect(
                sprite.rect.x - ox,
                sprite.rect.y - oy,
                sprite.rect.width,
                sprite.rect.height,
            )
            self.surface.blit(sprite.image, dest_rect)
            count += 1

        return count

    def mark_dirty(self, rect: pg.Rect) -> None:
        """Mark rectangle as dirty (needs redraw)."""
        if self._use_dirty:
            self._dirty_rects.add(rect.copy())

    def enable_dirty_tracking(self, enable: bool = True) -> None:
        """Enable or disable dirty rectangle tracking."""
        self._use_dirty = enable
        if not enable:
            self._dirty_rects.clear()

    def get_stats(self) -> RenderStats:
        """Get rendering statistics."""
        return self.stats

    def get_atlas_stats(self) -> Dict[str, Any]:
        """Get texture atlas statistics."""
        if not self._use_atlas or self._atlas is None:
            return {"enabled": False}

        return {
            "enabled": True,
            "size": (self._atlas.width, self._atlas.height),
            "regions": len(self._atlas.regions),
            "usage": f"{self._atlas._current_y / self._atlas.height * 100:.1f}%",
        }


@dataclass
class RenderSprite:
    """Data class for sprite rendering."""

    rect: pg.Rect
    image: pg.Surface
    layer: RenderLayer = RenderLayer.ITEMS
    src_rect: Optional[pg.Rect] = None


class RenderManager:
    """
    High-level render manager.

    Combines SpriteRenderer with additional features:
    - Multiple render targets
    - Post-processing hooks
    - Automatic viewport management
    """

    def __init__(self, surface: pg.Surface) -> None:
        """
        Initialize render manager.

        Args:
            surface: Main rendering surface
        """
        self.surface = surface
        self.renderer = SpriteRenderer(surface)
        self._viewport = pg.Rect(0, 0, surface.get_width(), surface.get_height())

        # Render targets
        self._targets: Dict[str, pg.Surface] = {}

    def set_viewport(self, x: int, y: int, width: int, height: int) -> None:
        """Set rendering viewport."""
        self._viewport.x = x
        self._viewport.y = y
        self._viewport.width = width
        self._viewport.height = height
        self.renderer.set_viewport(self._viewport)

    def create_target(self, name: str, width: int, height: int) -> pg.Surface:
        """
        Create render target (off-screen surface).

        Args:
            name: Target name
            width: Target width
            height: Target height

        Returns:
            Created surface
        """
        surface = pg.Surface((width, height), pg.SRCALPHA)
        self._targets[name] = surface
        return surface

    def get_target(self, name: str) -> Optional[pg.Surface]:
        """Get render target by name."""
        return self._targets.get(name)

    def begin_frame(self) -> None:
        """Begin rendering frame."""
        pass  # Hook for future expansion

    def end_frame(self) -> None:
        """End rendering frame."""
        pg.display.flip()

    def render(self, offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Render current frame.

        Args:
            offset: Camera offset
        """
        self.begin_frame()
        self.renderer.render(offset)
        self.end_frame()

    def get_stats(self) -> Dict[str, int]:
        """Get render statistics."""
        stats = self.renderer.get_stats()
        return {
            "total_sprites": stats.total_sprites,
            "visible_sprites": stats.visible_sprites,
            "culled_sprites": stats.culled_sprites,
            "batches": stats.batches,
            "draw_calls": stats.draw_calls,
        }
