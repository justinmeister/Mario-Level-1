"""Resource loading utilities."""

from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import pygame as pg

__all__ = [
    "load_all_gfx",
    "load_all_music",
    "load_all_fonts",
    "load_all_sfx",
    "LazyImageLoader",
    "ImageCache",
]

# Global image cache for lazy loading
_image_cache: Dict[str, pg.Surface] = {}


class ImageCache:
    """
    Global image cache with lazy loading support.

    Provides a centralized cache for loaded images to avoid
    duplicate loading and improve performance.

    Usage:
        # Get cached image or load if not present
        surface = ImageCache.get("path/to/image.png")

        # Clear cache to free memory
        ImageCache.clear()

        # Get cache statistics
        count = ImageCache.size()
    """

    _cache: Dict[str, pg.Surface] = {}

    @classmethod
    def get(
        cls,
        path: str,
        colorkey: Tuple[int, int, int] = (255, 0, 255),
    ) -> Optional[pg.Surface]:
        """
        Get image from cache or load it.

        Args:
            path: Path to image file
            colorkey: Color to use as transparent key

        Returns:
            Loaded pygame Surface or None if file not found
        """
        if path not in cls._cache:
            if not os.path.exists(path):
                return None

            img = pg.image.load(path)
            if img.get_alpha():
                try:
                    img = img.convert_alpha()
                except pg.error:
                    pass
            else:
                try:
                    img = img.convert()
                    img.set_colorkey(colorkey)
                except pg.error:
                    pass

            cls._cache[path] = img

        return cls._cache[path]

    @classmethod
    def clear(cls) -> None:
        """Clear all cached images."""
        cls._cache.clear()

    @classmethod
    def size(cls) -> int:
        """Get number of cached images."""
        return len(cls._cache)

    @classmethod
    def remove(cls, path: str) -> bool:
        """
        Remove specific image from cache.

        Args:
            path: Path to image file

        Returns:
            True if image was in cache and removed
        """
        if path in cls._cache:
            del cls._cache[path]
            return True
        return False


class LazyImageLoader:
    """
    Lazy image loader with directory-based caching.

    Loads images on-demand and caches them for reuse.
    Useful for large sprite sheets where not all images
    are needed immediately.

    Attributes:
        directory: Base directory for image files
        colorkey: Default colorkey for transparency
        cache: Internal cache of loaded images
    """

    def __init__(
        self,
        directory: str,
        colorkey: Tuple[int, int, int] = (255, 0, 255),
        accept: Tuple[str, ...] = (".png", ".jpg", ".bmp"),
    ) -> None:
        """
        Initialize lazy loader.

        Args:
            directory: Base directory for image files
            colorkey: Default colorkey for transparency
            accept: Tuple of acceptable file extensions
        """
        self.directory = directory
        self.colorkey = colorkey
        self.accept = accept
        self.cache: Dict[str, pg.Surface] = {}
        self._available_images: Optional[Dict[str, str]] = None

    def _scan_directory(self) -> Dict[str, str]:
        """Scan directory for available images."""
        if self._available_images is None:
            self._available_images = {}
            if os.path.exists(self.directory):
                for pic in os.listdir(self.directory):
                    name, ext = os.path.splitext(pic)
                    if ext.lower() in self.accept:
                        self._available_images[name] = os.path.join(self.directory, pic)
        return self._available_images

    def get(self, name: str) -> Optional[pg.Surface]:
        """
        Load and cache image by name.

        Args:
            name: Image name (without extension)

        Returns:
            Loaded pygame Surface or None if not found
        """
        if name in self.cache:
            return self.cache[name]

        available = self._scan_directory()
        if name not in available:
            # Fallback: try constructing a path using accepted extensions
            for ext in self.accept:
                candidate = os.path.join(self.directory, name + ext)
                if os.path.exists(candidate):
                    img = pg.image.load(candidate)
                    break
            else:
                return None
        else:
            img = pg.image.load(available[name])
        if img.get_alpha():
            try:
                img = img.convert_alpha()
            except pg.error:
                pass
        else:
            try:
                img = img.convert()
                img.set_colorkey(self.colorkey)
            except pg.error:
                pass

        self.cache[name] = img
        return img

    def get_all(self) -> Dict[str, pg.Surface]:
        """
        Load all available images.

        Returns:
            Dictionary mapping names to Surfaces
        """
        available = self._scan_directory()
        result = {}
        for name, path in available.items():
            if name not in self.cache:
                self.get(name)
            result[name] = self.cache[name]
        return result

    def clear(self) -> None:
        """Clear loaded images from cache."""
        self.cache.clear()
        self._available_images = None


def load_all_gfx(
    directory: str,
    colorkey: Tuple[int, int, int] = (255, 0, 255),
    accept: Tuple[str, ...] = (".png", ".jpg", ".bmp"),
) -> Dict[str, pg.Surface]:
    """
    Load all graphics from a directory.

    Args:
        directory: Path to directory containing image files
        colorkey: Color to use as transparent key
        accept: Tuple of acceptable file extensions

    Returns:
        Dictionary mapping filename (without extension) to pygame Surface
    """
    graphics: Dict[str, pg.Surface] = {}
    if not os.path.exists(directory):
        return graphics

    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                try:
                    img = img.convert_alpha()
                except pg.error:
                    pass
            else:
                try:
                    img = img.convert()
                    img.set_colorkey(colorkey)
                except pg.error:
                    pass
            graphics[name] = img
    return graphics


def load_all_music(directory: str, accept: Tuple[str, ...] = (".wav", ".mp3", ".ogg", ".mdi")) -> Dict[str, str]:
    """
    Load all music file paths from a directory.

    Args:
        directory: Path to directory containing music files
        accept: Tuple of acceptable file extensions

    Returns:
        Dictionary mapping filename (without extension) to file path
    """
    songs: Dict[str, str] = {}
    for song in os.listdir(directory):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs


def load_all_fonts(directory: str, accept: Tuple[str, ...] = (".ttf",)) -> Dict[str, str]:
    """
    Load all font file paths from a directory.

    Args:
        directory: Path to directory containing font files
        accept: Tuple of acceptable file extensions

    Returns:
        Dictionary mapping filename (without extension) to file path
    """
    return load_all_music(directory, accept)


def load_all_sfx(
    directory: str, accept: Tuple[str, ...] = (".wav", ".mpe", ".ogg", ".mdi")
) -> Dict[str, pg.mixer.Sound]:
    """
    Load all sound effects from a directory.

    Args:
        directory: Path to directory containing sound effect files
        accept: Tuple of acceptable file extensions

    Returns:
        Dictionary mapping filename (without extension) to pygame Sound
    """
    effects: Dict[str, pg.mixer.Sound] = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects
