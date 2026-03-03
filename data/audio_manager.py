"""
Advanced Audio Manager for Super Mario Bros.

Provides:
- Multi-channel audio playback
- Sound effect pooling
- Music playlist system
- Dynamic audio mixing
- Audio fade effects
- Sound categories (SFX, Music, Voice, Ambient)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable

import pygame as pg

logger = logging.getLogger(__name__)


class AudioCategory(Enum):
    """Audio channel categories."""

    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    AMBIENT = "ambient"
    UI = "ui"


class AudioState(Enum):
    """Audio playback state."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"


@dataclass
class SoundConfig:
    """Configuration for a sound effect."""

    volume: float = 1.0
    pitch: float = 1.0
    loops: int = 0
    fade_ms: int = 0
    category: AudioCategory = AudioCategory.SFX
    priority: int = 5  # 1-10, higher = more important


@dataclass
class MusicTrack:
    """Music track information."""

    name: str
    file_path: str
    duration_ms: int = 0
    volume: float = 0.7
    fade_ms: int = 1000
    loops: int = -1  # -1 = infinite


@dataclass
class AudioStats:
    """Audio system statistics."""

    total_sounds_played: int = 0
    total_music_tracks: int = 0
    sounds_active: int = 0
    memory_used_mb: float = 0.0
    channels_used: int = 0


class SoundPool:
    """
    Pool for managing sound effect instances.
    """

    def __init__(self, max_channels: int = 16) -> None:
        """
        Initialize sound pool.

        Args:
            max_channels: Maximum number of simultaneous sounds
        """
        self.max_channels = max_channels
        self.channels: List[Optional[pg.mixer.Channel]] = []
        self.sounds: Dict[str, pg.mixer.Sound] = {}
        self.channel_usage: List[bool] = [False] * max_channels

        self._init_channels()

    def _init_channels(self) -> None:
        """Initialize mixer channels."""
        for i in range(self.max_channels):
            channel = pg.mixer.Channel(i)
            self.channels.append(channel)

    def load_sound(self, name: str, file_path: str) -> bool:
        """
        Load sound effect.

        Args:
            name: Sound name/ID
            file_path: Path to sound file

        Returns:
            True if loaded successfully
        """
        try:
            sound = pg.mixer.Sound(file_path)
            self.sounds[name] = sound
            return True
        except (pg.error, FileNotFoundError) as e:
            logger.warning(f"Could not load sound {name}: {e}")
            return False

    def play(self, name: str, volume: float = 1.0, loops: int = 0, priority: int = 5) -> bool:
        """
        Play sound effect.

        Args:
            name: Sound name
            volume: Volume (0-1)
            loops: Number of loops (-1 = infinite)
            priority: Priority level (1-10)

        Returns:
            True if sound started playing
        """
        if name not in self.sounds:
            return False

        sound = self.sounds[name]
        sound.set_volume(volume)

        # Find available channel
        channel = self._find_channel(priority)
        if channel is None:
            return False

        channel.play(sound, loops)
        return True

    def _find_channel(self, priority: int) -> Optional[pg.mixer.Channel]:
        """
        Find available channel.

        Args:
            priority: Priority level

        Returns:
            Available channel or None
        """
        # First, try to find inactive channel
        for i, channel in enumerate(self.channels):
            if channel and not channel.get_busy():
                self.channel_usage[i] = False
                return channel

        # If all busy, steal lowest priority channel
        _ = 10  # lowest_priority reserved for future use
        lowest_idx = -1

        for i, channel in enumerate(self.channels):
            if channel and channel.get_busy():
                # Could track priority per channel
                if lowest_idx == -1:
                    lowest_idx = i

        if lowest_idx >= 0:
            return self.channels[lowest_idx]

        return None

    def stop(self, name: Optional[str] = None) -> None:
        """
        Stop sound(s).

        Args:
            name: Sound name to stop (None = stop all)
        """
        if name is None:
            pg.mixer.stop()
        elif name in self.sounds:
            # Stop all channels playing this sound
            for channel in self.channels:
                if channel and channel.get_sound() == self.sounds[name]:
                    channel.stop()

    def stop_all(self) -> None:
        """Stop all sounds."""
        pg.mixer.stop()

    def pause(self) -> None:
        """Pause all sounds."""
        pg.mixer.pause()

    def unpause(self) -> None:
        """Unpause all sounds."""
        pg.mixer.unpause()

    def get_active_count(self) -> int:
        """Get number of active sounds."""
        return sum(1 for ch in self.channels if ch and ch.get_busy())

    def unload(self, name: str) -> None:
        """
        Unload sound from memory.

        Args:
            name: Sound name
        """
        if name in self.sounds:
            del self.sounds[name]

    def clear(self) -> None:
        """Clear all sounds."""
        self.sounds.clear()
        self.stop_all()


class MusicManager:
    """
    Manager for background music.
    """

    def __init__(self) -> None:
        """Initialize music manager."""
        self.playlist: List[MusicTrack] = []
        self.current_track: Optional[MusicTrack] = None
        self.current_index = 0
        self.state = AudioState.STOPPED
        self.volume = 0.7
        self.shuffle = False
        self.repeat = True

        self._on_track_end: Optional[Callable[[], None]] = None

    def add_track(self, track: MusicTrack) -> None:
        """
        Add track to playlist.

        Args:
            track: Music track to add
        """
        self.playlist.append(track)

    def add_tracks(self, tracks: List[MusicTrack]) -> None:
        """Add multiple tracks to playlist."""
        self.playlist.extend(tracks)

    def load_track(self, name: str, file_path: str, volume: float = 0.7, loops: int = -1) -> bool:
        """
        Load and add track to playlist.

        Args:
            name: Track name
            file_path: Path to music file
            volume: Track volume
            loops: Number of loops

        Returns:
            True if loaded successfully
        """
        try:
            if not os.path.exists(file_path):
                return False

            track = MusicTrack(name=name, file_path=file_path, volume=volume, loops=loops)
            self.add_track(track)
            return True
        except Exception as e:
            logger.warning(f"Could not load music {name}: {e}")
            return False

    def play(self, track_name: Optional[str] = None, fade_ms: int = 1000) -> bool:
        """
        Play music.

        Args:
            track_name: Specific track to play (None = current)
            fade_ms: Fade in duration

        Returns:
            True if playback started
        """
        if not self.playlist:
            return False

        # Find track
        if track_name:
            for i, track in enumerate(self.playlist):
                if track.name == track_name:
                    self.current_index = i
                    self.current_track = track
                    break
        elif not self.current_track:
            self.current_track = self.playlist[0]
            self.current_index = 0

        if not self.current_track:
            return False

        try:
            pg.mixer.music.load(self.current_track.file_path)
            pg.mixer.music.set_volume(self.current_track.volume * self.volume)
            pg.mixer.music.play(self.current_track.loops, 0.0, fade_ms)
            self.state = AudioState.PLAYING
            return True
        except pg.error as e:
            logger.warning(f"Could not play music: {e}")
            return False

    def play_next(self, fade_ms: int = 1000) -> bool:
        """
        Play next track in playlist.

        Args:
            fade_ms: Fade duration

        Returns:
            True if next track started
        """
        if not self.playlist:
            return False

        if self.shuffle:
            import random

            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self.current_track = self.playlist[self.current_index]
        return self.play(fade_ms=fade_ms)

    def play_previous(self, fade_ms: int = 1000) -> bool:
        """Play previous track."""
        if not self.playlist:
            return False

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.current_track = self.playlist[self.current_index]
        return self.play(fade_ms=fade_ms)

    def stop(self, fade_ms: int = 1000) -> None:
        """Stop music with fade."""
        pg.mixer.music.fadeout(fade_ms)
        self.state = AudioState.STOPPED

    def pause(self) -> None:
        """Pause music."""
        pg.mixer.music.pause()
        self.state = AudioState.PAUSED

    def unpause(self) -> None:
        """Unpause music."""
        pg.mixer.music.unpause()
        self.state = AudioState.PLAYING

    def set_volume(self, volume: float) -> None:
        """
        Set music volume.

        Args:
            volume: Volume (0-1)
        """
        self.volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.volume)

    def fade_out(self, duration_ms: int = 1000) -> None:
        """Fade out music."""
        pg.mixer.music.fadeout(duration_ms)
        self.state = AudioState.FADE_OUT

    def fade_in(self, duration_ms: int = 1000, start_volume: float = 0.0) -> None:
        """
        Fade in music.

        Args:
            duration_ms: Fade duration
            start_volume: Starting volume
        """
        self.volume = start_volume
        pg.mixer.music.set_volume(0.0)
        self.state = AudioState.FADE_IN

        # Would need timer to complete fade

    def is_playing(self) -> bool:
        """Check if music is playing."""
        return pg.mixer.music.get_busy() and self.state == AudioState.PLAYING

    def is_paused(self) -> bool:
        """Check if music is paused."""
        return self.state == AudioState.PAUSED

    def get_current_track(self) -> Optional[MusicTrack]:
        """Get current track info."""
        return self.current_track

    def get_playlist(self) -> List[MusicTrack]:
        """Get playlist."""
        return self.playlist.copy()

    def clear_playlist(self) -> None:
        """Clear playlist."""
        self.playlist.clear()
        self.current_track = None
        self.current_index = 0
        self.stop()

    def set_on_track_end(self, callback: Callable[[], None]) -> None:
        """Set callback for track end."""
        self._on_track_end = callback


class AudioManager:
    """
    Central audio management system.
    """

    def __init__(self, sound_channels: int = 16, frequency: int = 44100) -> None:
        """
        Initialize audio manager.

        Args:
            sound_channels: Number of sound channels
            frequency: Audio frequency
        """
        self.sound_channels = sound_channels
        self.frequency = frequency

        self.sound_pool: Optional[SoundPool] = None
        self.music_manager: Optional[MusicManager] = None

        self.master_volume = 0.7
        self.category_volumes: Dict[AudioCategory, float] = {
            AudioCategory.MUSIC: 0.7,
            AudioCategory.SFX: 0.8,
            AudioCategory.VOICE: 0.9,
            AudioCategory.AMBIENT: 0.5,
            AudioCategory.UI: 0.8,
        }

        self.enabled = True
        self.muted = False

        self.stats = AudioStats()

        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize audio system.

        Returns:
            True if initialization successful
        """
        try:
            pg.mixer.init(frequency=self.frequency, size=-16, channels=2, buffer=512)

            self.sound_pool = SoundPool(self.sound_channels)
            self.music_manager = MusicManager()
            self._initialized = True
            return True

        except pg.error as e:
            logger.warning(f"Audio initialization failed: {e}")
            return False

    def shutdown(self) -> None:
        """Shutdown audio system."""
        if self.sound_pool:
            self.sound_pool.clear()
        if self.music_manager:
            self.music_manager.stop()
        pg.mixer.quit()
        self._initialized = False

    def load_sound(self, name: str, file_path: str, category: AudioCategory = AudioCategory.SFX) -> bool:
        """
        Load sound effect.

        Args:
            name: Sound name
            file_path: Path to sound file
            category: Sound category

        Returns:
            True if loaded successfully
        """
        if not self._initialized or not self.sound_pool:
            return False

        return self.sound_pool.load_sound(name, file_path)

    def load_sounds_from_directory(self, directory: str, category: AudioCategory = AudioCategory.SFX) -> int:
        """
        Load all sounds from directory.

        Args:
            directory: Directory path
            category: Sound category

        Returns:
            Number of sounds loaded
        """
        count = 0
        dir_path = Path(directory)

        if not dir_path.exists():
            return 0

        for file_path in dir_path.glob("*.wav"):
            name = file_path.stem
            if self.load_sound(name, str(file_path), category):
                count += 1

        for file_path in dir_path.glob("*.ogg"):
            name = file_path.stem
            if self.load_sound(name, str(file_path), category):
                count += 1

        return count

    def play_sound(
        self, name: str, volume: float = 1.0, category: AudioCategory = AudioCategory.SFX, priority: int = 5
    ) -> bool:
        """
        Play sound effect.

        Args:
            name: Sound name
            volume: Volume (0-1)
            category: Sound category
            priority: Priority (1-10)

        Returns:
            True if sound started
        """
        if not self.enabled or self.muted:
            return False

        if not self._initialized or not self.sound_pool:
            return False

        # Apply category volume
        category_vol = self.category_volumes.get(category, 1.0)
        final_volume = volume * category_vol * self.master_volume

        return self.sound_pool.play(name, volume=final_volume, priority=priority)

    def play_music(self, track_name: Optional[str] = None, fade_ms: int = 1000) -> bool:
        """
        Play background music.

        Args:
            track_name: Specific track name
            fade_ms: Fade in duration

        Returns:
            True if music started
        """
        if not self.enabled or self.muted:
            return False

        if not self._initialized or not self.music_manager:
            return False

        return self.music_manager.play(track_name, fade_ms)

    def stop_sound(self, name: Optional[str] = None) -> None:
        """Stop sound effect(s)."""
        if self.sound_pool:
            self.sound_pool.stop(name)

    def stop_music(self, fade_ms: int = 1000) -> None:
        """Stop background music."""
        if self.music_manager:
            self.music_manager.stop(fade_ms)

    def pause_all(self) -> None:
        """Pause all audio."""
        if self.sound_pool:
            self.sound_pool.pause()
        if self.music_manager:
            self.music_manager.pause()

    def unpause_all(self) -> None:
        """Unpause all audio."""
        if self.sound_pool:
            self.sound_pool.unpause()
        if self.music_manager:
            self.music_manager.unpause()

    def set_master_volume(self, volume: float) -> None:
        """
        Set master volume.

        Args:
            volume: Volume (0-1)
        """
        self.master_volume = max(0.0, min(1.0, volume))

    def set_category_volume(self, category: AudioCategory, volume: float) -> None:
        """
        Set category volume.

        Args:
            category: Audio category
            volume: Volume (0-1)
        """
        self.category_volumes[category] = max(0.0, min(1.0, volume))

    def mute(self) -> None:
        """Mute all audio."""
        self.muted = True
        self.stop_music(500)

    def unmute(self) -> None:
        """Unmute audio."""
        self.muted = False

    def toggle_mute(self) -> bool:
        """
        Toggle mute state.

        Returns:
            New mute state
        """
        self.muted = not self.muted
        if self.muted:
            self.mute()
        return self.muted

    def get_stats(self) -> AudioStats:
        """Get audio statistics."""
        if self.sound_pool:
            self.stats.sounds_active = self.sound_pool.get_active_count()
            self.stats.channels_used = self.sound_channels
        return self.stats

    def is_initialized(self) -> bool:
        """Check if audio system is initialized."""
        return self._initialized

    def is_enabled(self) -> bool:
        """Check if audio is enabled."""
        return self.enabled and not self.muted


# Preset sound names for Mario game
SOUND_NAMES = {
    # Mario sounds
    "jump": "jump",
    "big_jump": "big_jump",
    "fireball": "fireball",
    "powerup_appears": "powerup_appears",
    "powerup": "powerup",
    "stomp": "stomp",
    "kick": "kick",
    "pipe": "pipe",
    "break_block": "break_block",
    "coin": "coin",
    "flagpole": "flagpole",
    "game_over": "game_over",
    "die": "die",
    "stage_clear": "stage_clear",
    "boss_fireball": "boss_fireball",
    "explosion": "explosion",
    "bump": "bump",
    # Enemy sounds
    "goomba_appears": "goomba_appears",
    "koopa_appears": "koopa_appears",
    # UI sounds
    "button_click": "button_click",
    "menu_move": "menu_move",
    "pause": "pause",
}


class GameAudioPreset:
    """
    Pre-configured audio setup for Mario game.
    """

    def __init__(self, audio_manager: AudioManager) -> None:
        """
        Initialize game audio preset.

        Args:
            audio_manager: Audio manager instance
        """
        self.audio = audio_manager

    def load_default_sounds(self, sound_dir: str = "resources/sound") -> int:
        """
        Load default game sounds.

        Args:
            sound_dir: Sound directory path

        Returns:
            Number of sounds loaded
        """
        count = 0

        for sound_name in SOUND_NAMES.values():
            file_path = Path(sound_dir) / f"{sound_name}.wav"
            if file_path.exists():
                if self.audio.load_sound(sound_name, str(file_path)):
                    count += 1

        return count

    def play_jump(self, is_big: bool = False) -> bool:
        """Play jump sound."""
        name = SOUND_NAMES["big_jump"] if is_big else SOUND_NAMES["jump"]
        return self.audio.play_sound(name, category=AudioCategory.SFX)

    def play_coin(self) -> bool:
        """Play coin collection sound."""
        return self.audio.play_sound(SOUND_NAMES["coin"], category=AudioCategory.SFX, priority=7)

    def play_stomp(self) -> bool:
        """Play enemy stomp sound."""
        return self.audio.play_sound(SOUND_NAMES["stomp"], category=AudioCategory.SFX)

    def play_powerup(self) -> bool:
        """Play powerup collection sound."""
        return self.audio.play_sound(SOUND_NAMES["powerup"], category=AudioCategory.SFX, priority=8)

    def play_game_over(self) -> bool:
        """Play game over sound."""
        return self.audio.play_sound(SOUND_NAMES["game_over"], category=AudioCategory.SFX, priority=10)

    def play_stage_clear(self) -> bool:
        """Play stage clear sound."""
        return self.audio.play_sound(SOUND_NAMES["stage_clear"], category=AudioCategory.SFX, priority=10)

    def play_ui_click(self) -> bool:
        """Play UI click sound."""
        return self.audio.play_sound(SOUND_NAMES["button_click"], category=AudioCategory.UI)

    def play_menu_move(self) -> bool:
        """Play menu navigation sound."""
        return self.audio.play_sound(SOUND_NAMES["menu_move"], category=AudioCategory.UI)


class AudioEffect(Enum):
    """Audio effect types."""

    NONE = "none"
    REVERB = "reverb"
    ECHO = "echo"
    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    DISTORTION = "distortion"


@dataclass
class EffectConfig:
    """Audio effect configuration."""

    effect_type: AudioEffect = AudioEffect.NONE
    intensity: float = 0.5  # 0.0 - 1.0
    mix: float = 0.3  # Dry/wet mix
    enabled: bool = True


class AudioEffectProcessor:
    """
    Audio effects processor.

    Applies real-time audio effects to sounds.
    Note: This is a simplified implementation. For production,
    consider using external audio libraries like pydub or sounddevice.
    """

    def __init__(self) -> None:
        """Initialize audio effect processor."""
        self.effects: Dict[str, EffectConfig] = {}
        self.enabled = True

    def add_effect(self, name: str, config: EffectConfig) -> None:
        """
        Add audio effect.

        Args:
            name: Effect identifier
            config: Effect configuration
        """
        self.effects[name] = config

    def remove_effect(self, name: str) -> None:
        """
        Remove audio effect.

        Args:
            name: Effect identifier
        """
        if name in self.effects:
            del self.effects[name]

    def set_effect_intensity(self, name: str, intensity: float) -> None:
        """
        Set effect intensity.

        Args:
            name: Effect identifier
            intensity: Intensity value (0.0 - 1.0)
        """
        if name in self.effects:
            self.effects[name].intensity = max(0.0, min(1.0, intensity))

    def set_effect_mix(self, name: str, mix: float) -> None:
        """
        Set effect dry/wet mix.

        Args:
            name: Effect identifier
            mix: Mix value (0.0 = dry, 1.0 = wet)
        """
        if name in self.effects:
            self.effects[name].mix = max(0.0, min(1.0, mix))

    def enable_effect(self, name: str, enable: bool = True) -> None:
        """
        Enable or disable effect.

        Args:
            name: Effect identifier
            enable: Enable state
        """
        if name in self.effects:
            self.effects[name].enabled = enable

    def get_active_effects(self) -> List[str]:
        """
        Get list of active effects.

        Returns:
            List of active effect names
        """
        return [name for name, config in self.effects.items() if config.enabled]

    def clear_effects(self) -> None:
        """Clear all effects."""
        self.effects.clear()

    def get_effect_config(self, name: str) -> Optional[EffectConfig]:
        """
        Get effect configuration.

        Args:
            name: Effect identifier

        Returns:
            Effect config or None
        """
        return self.effects.get(name)


class AudioMixer:
    """
    Advanced audio mixer with ducking and crossfading.
    """

    def __init__(self) -> None:
        """Initialize audio mixer."""
        self.ducking_enabled = False
        self.ducking_amount = 0.5  # How much to reduce volume
        self.ducking_duration_ms = 500
        self.crossfade_duration_ms = 1000

        # Track volumes for ducking
        self._original_volumes: Dict[AudioCategory, float] = {}
        self._ducked = False

    def enable_ducking(self, enable: bool = True, amount: float = 0.5, duration_ms: int = 500) -> None:
        """
        Enable audio ducking (reduce music when SFX plays).

        Args:
            enable: Enable ducking
            amount: Amount to reduce volume (0.0 - 1.0)
            duration_ms: Fade duration
        """
        self.ducking_enabled = enable
        self.ducking_amount = max(0.0, min(1.0, amount))
        self.ducking_duration_ms = duration_ms

    def duck_audio(self, category: AudioCategory, volume: float) -> None:
        """
        Duck audio for category.

        Args:
            category: Audio category to duck
            volume: Original volume
        """
        if not self.ducking_enabled:
            return

        if category not in self._original_volumes:
            self._original_volumes[category] = volume

        self._ducked = True

    def restore_audio(self, category: AudioCategory) -> float:
        """
        Restore ducked audio.

        Args:
            category: Audio category to restore

        Returns:
            Original volume
        """
        if category in self._original_volumes:
            volume = self._original_volumes[category]
            del self._original_volumes[category]
            self._ducked = False
            return volume
        return 1.0

    def is_ducked(self) -> bool:
        """Check if audio is currently ducked."""
        return self._ducked

    def set_crossfade_duration(self, duration_ms: int) -> None:
        """
        Set crossfade duration.

        Args:
            duration_ms: Duration in milliseconds
        """
        self.crossfade_duration_ms = max(0, duration_ms)

    def get_ducked_volume(self, original_volume: float) -> float:
        """
        Calculate ducked volume.

        Args:
            original_volume: Original volume

        Returns:
            Ducked volume
        """
        if self._ducked:
            return original_volume * (1.0 - self.ducking_amount)
        return original_volume
