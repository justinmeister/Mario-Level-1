"""Sprite sheet utilities for extracting and scaling images."""

from __future__ import annotations

from typing import List

import pygame as pg

from .. import constants as c


def extract_image(
    sprite_sheet: pg.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    scale_multiplier: float = c.SIZE_MULTIPLIER,
    colorkey: tuple[int, int, int] = c.BLACK,
) -> pg.Surface:
    """
    Extract and scale an image from a sprite sheet.

    Args:
        sprite_sheet: Source sprite sheet surface
        x: X coordinate on sprite sheet
        y: Y coordinate on sprite sheet
        width: Width of region to extract
        height: Height of region to extract
        scale_multiplier: Scale factor (default: SIZE_MULTIPLIER)
        colorkey: Color to make transparent (default: BLACK)

    Returns:
        Scaled surface with transparency
    """
    image = pg.Surface([width, height])
    image.blit(sprite_sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pg.transform.scale(
        image,
        (int(width * scale_multiplier), int(height * scale_multiplier)),
    )
    return image


def extract_images(
    sprite_sheet: pg.Surface,
    frames: List[tuple[int, int, int, int]],
    scale_multiplier: float = c.SIZE_MULTIPLIER,
    colorkey: tuple[int, int, int] = c.BLACK,
) -> List[pg.Surface]:
    """
    Extract multiple images from a sprite sheet.

    Args:
        sprite_sheet: Source sprite sheet surface
        frames: List of (x, y, width, height) tuples
        scale_multiplier: Scale factor
        colorkey: Color to make transparent

    Returns:
        List of extracted and scaled surfaces
    """
    return [
        extract_image(sprite_sheet, x, y, w, h, scale_multiplier, colorkey)
        for x, y, w, h in frames
    ]


class SpriteSheetLoader:
    """Helper class for loading and extracting sprite sheet data."""

    def __init__(
        self,
        sprite_sheet: pg.Surface,
        scale_multiplier: float = c.SIZE_MULTIPLIER,
        colorkey: tuple[int, int, int] = c.BLACK,
    ) -> None:
        """
        Initialize loader with sprite sheet.

        Args:
            sprite_sheet: Source sprite sheet surface
            scale_multiplier: Default scale factor
            colorkey: Default transparent color
        """
        self.sprite_sheet = sprite_sheet
        self.scale_multiplier = scale_multiplier
        self.colorkey = colorkey

    def get_image(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        scale_multiplier: float | None = None,
    ) -> pg.Surface:
        """
        Extract a single image from sprite sheet.

        Args:
            x: X coordinate on sprite sheet
            y: Y coordinate on sprite sheet
            width: Width of region to extract
            height: Height of region to extract
            scale_multiplier: Override default scale factor

        Returns:
            Extracted and scaled surface
        """
        if scale_multiplier is None:
            scale_multiplier = self.scale_multiplier
        return extract_image(
            self.sprite_sheet, x, y, width, height, scale_multiplier, self.colorkey
        )

    def get_images(
        self,
        frames: List[tuple[int, int, int, int]],
        scale_multiplier: float | None = None,
    ) -> List[pg.Surface]:
        """
        Extract multiple images from sprite sheet.

        Args:
            frames: List of (x, y, width, height) tuples
            scale_multiplier: Override default scale factor

        Returns:
            List of extracted surfaces
        """
        if scale_multiplier is None:
            scale_multiplier = self.scale_multiplier
        return extract_images(
            self.sprite_sheet, frames, scale_multiplier, self.colorkey
        )
