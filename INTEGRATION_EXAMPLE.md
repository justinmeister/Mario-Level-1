# Пример интеграции новой музыки и звуков

## Как добавить музыку в уровень

### Шаг 1: Импорт в файл уровня

```python
from ..level_music_manager import get_level_music_manager
from ..level_sound_effects import get_level_sound_effects
```

### Шаг 2: Инициализация в startup()

```python
def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
    """Called when the State object is created"""
    # ... существующий код ...
    
    # Инициализация музыки и звуков
    self.music_manager = get_level_music_manager()
    self.sound_effects = get_level_sound_effects()
    
    # Запуск музыки для уровня
    # Для level1.py используйте 'level1', для level2.py - 'level2' и т.д.
    self.music_manager.play_level_music('level1', fade_ms=1000)
    
    # ... остальной код ...
```

### Шаг 3: Обновление музыки в update()

```python
def update(self, surface: pg.Surface, keys: tuple, current_time: float) -> None:
    """Update level state"""
    self.current_time = current_time
    
    # Обновление музыки на основе оставшегося времени
    if hasattr(self, 'music_manager'):
        time_remaining = self.game_info.get(c.LEVEL_TIME, 400)
        self.music_manager.update(time_remaining)
    
    # ... остальной код ...
```

### Шаг 4: Остановка музыки при выходе

```python
def cleanup(self) -> Dict[str, Any]:
    """Clean up when leaving the state"""
    # Остановка музыки
    if hasattr(self, 'music_manager'):
        self.music_manager.stop(fade_ms=500)
    
    return self.persist
```

## Как использовать звуковые эффекты

### Сбор монеты

```python
# В методе, где обрабатывается сбор монеты
if coin_collected:
    self.sound_effects.play_coin()
    self.game_info[c.COIN_TOTAL] += 1
```

### Завершение уровня

```python
# Когда Марио достигает флага
if level_complete:
    self.sound_effects.play_level_complete()
    # Остановить музыку уровня
    self.music_manager.stop(fade_ms=500)
```

### Победа над боссом

```python
# Когда побежден босс в замке
if boss_defeated:
    self.sound_effects.play_boss_defeat()
    # Затем воспроизвести звук завершения замка
    pg.time.wait(1000)  # Подождать 1 секунду
    self.sound_effects.play_castle_complete()
```

### Game Over

```python
# Когда Марио умирает
if mario_dead:
    self.music_manager.stop(fade_ms=200)
    self.sound_effects.play_game_over()
```

### Предупреждение о времени

```python
# Когда время заканчивается (автоматически при переключении музыки)
if time_remaining == 100 and not self.time_warning_played:
    self.sound_effects.play_time_warning()
    self.time_warning_played = True
```

## Полный пример для level1.py

```python
from __future__ import annotations

from typing import Any, Dict

import pygame as pg

from .. import constants as c
from ..level_music_manager import get_level_music_manager
from ..level_sound_effects import get_level_sound_effects

class Level1(tools._State):
    """Level 1 state"""
    
    def __init__(self) -> None:
        tools._State.__init__(self)
        self.level_file = "data/levels/level_1_1.json"
    
    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called when the State object is created"""
        # Существующий код инициализации
        self.game_info = persist
        self.persist = self.game_info
        
        # Инициализация музыки и звуков
        self.music_manager = get_level_music_manager()
        self.sound_effects = get_level_sound_effects()
        self.time_warning_played = False
        
        # Загрузка уровня и настройка
        # ... существующий код ...
        
        # Запуск музыки
        self.music_manager.play_level_music('level1', fade_ms=1000)
    
    def update(self, surface: pg.Surface, keys: tuple, current_time: float) -> None:
        """Update level state"""
        self.current_time = current_time
        
        # Получить оставшееся время
        time_remaining = self.game_info.get(c.LEVEL_TIME, 400)
        
        # Обновить музыку (автоматически переключится на ускоренную при time < 100)
        self.music_manager.update(time_remaining)
        
        # Воспроизвести предупреждение о времени
        if time_remaining == 100 and not self.time_warning_played:
            self.sound_effects.play_time_warning()
            self.time_warning_played = True
        
        # Проверка сбора монет
        if coin_collected:
            self.sound_effects.play_coin()
        
        # Проверка завершения уровня
        if level_complete:
            self.music_manager.stop(fade_ms=500)
            self.sound_effects.play_level_complete()
        
        # Проверка смерти
        if mario_dead:
            self.music_manager.stop(fade_ms=200)
            self.sound_effects.play_game_over()
        
        # ... остальной код обновления ...
    
    def cleanup(self) -> Dict[str, Any]:
        """Clean up when leaving the state"""
        # Остановить музыку
        if hasattr(self, 'music_manager'):
            self.music_manager.stop(fade_ms=500)
        
        return self.persist
```

## Карта музыки для уровней

- **Level 1 (1-1)**: main_theme → main_theme_sped_up
- **Level 2 (1-2)**: underground → underground_sped_up
- **Level 3 (1-3)**: main_theme → main_theme_sped_up
- **Level 4 (1-4)**: castle → castle_sped_up
- **Level 5 (2-1)**: main_theme → main_theme_sped_up
- **Level 6 (2-2)**: underwater → underwater_sped_up
- **Level 7 (2-3)**: main_theme → main_theme_sped_up
- **Level 8 (2-4)**: castle → castle_sped_up

## Настройка громкости

```python
# Установить громкость музыки (0.0 - 1.0)
music_manager.set_volume(0.7)

# Установить громкость звуковых эффектов (0.0 - 1.0)
sound_effects.set_volume(0.8)
```

## Примечания

1. Музыка автоматически переключается на ускоренную версию при времени < 100 секунд
2. Все звуковые эффекты загружаются один раз при первом использовании
3. Используйте fade_ms для плавных переходов между треками
4. Не забудьте остановить музыку в методе cleanup()
