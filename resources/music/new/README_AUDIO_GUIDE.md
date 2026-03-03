# Аудио файлы для Super Mario Bros

## 📁 Структура файлов

Все новые аудио файлы находятся в `resources/music/new/`

## 🎵 Музыкальные треки

### Основные уровни
- **Главная тема** (0:15) - Классическая музыка первого уровня
- **Подземный уровень** (1:08) - Музыка для подземелий
- **Подводный мир** (0:55) - Музыка для подводных уровней
- **Замок с драконом** (0:07) - Музыка для замков/боссов

### Ускоренные версии (когда заканчивается время)
- **Ускоренная музыка первого уровня** (0:55)
- **Ускоренная подземная** (0:11)
- **Ускоренная подводная** (0:20)
- **Ускоренная замок** (1:11)

### Специальные треки
- **Звезда непобедимости** (0:11) - Когда Марио подобрал звезду
- **Быстрая музыка со звездой** (0:05) - Звезда + мало времени
- **Музыка титров** (0:04) - После прохождения игры
- **Марио на пианино** (0:01) - Альтернативная версия

## 🔊 Звуковые эффекты

### События уровня
- **Время истекает** (0:01) - Короткий предупреждающий звук
- **Переход по трубе** (0:01) - Спуск в подземелье
- **Переход на следующую сцену** (0:01) - Смена экрана
- **Сбор монеты** (0:02) - Подбор монеты

### Победа
- **Звук победы** (0:02) - Прохождение уровня с фанфарами
- **Мир очищен** (0:03) - Фанфары победы
- **Замок пройден** (0:05) - Дракон побежден
- **Победа над боссом** (0:01) - Короткий звук победы

### Game Over
- **Game Over** (0:00) - Смерть/потеря жизни
- **Последняя жизнь** (0:01) - Потрачена последняя жизнь
- **Альтернативный Game Over** (0:00) - Другая версия

## 🎮 Как использовать в игре

### 1. Переименование файлов
Рекомендуемые имена для интеграции:
```
main_theme.mp3              -> Главная тема
main_theme_sped_up.mp3      -> Ускоренная главная
underground.mp3             -> Подземелье
underground_sped_up.mp3     -> Ускоренное подземелье
underwater.mp3              -> Подводный мир
underwater_sped_up.mp3      -> Ускоренный подводный
castle.mp3                  -> Замок
castle_sped_up.mp3          -> Ускоренный замок
star_power.mp3              -> Звезда непобедимости
star_power_sped_up.mp3      -> Звезда + мало времени
ending.mp3                  -> Титры
```

### 2. Звуковые эффекты
```
time_warning.mp3            -> Предупреждение о времени
pipe.mp3                    -> Переход по трубе
stage_clear.mp3             -> Переход на следующую сцену
coin.mp3                    -> Сбор монеты
level_complete.mp3          -> Прохождение уровня
world_clear.mp3             -> Мир очищен
castle_complete.mp3         -> Замок пройден
boss_defeat.mp3             -> Победа над боссом
game_over.mp3               -> Game Over
game_over_last_life.mp3     -> Последняя жизнь
game_over_alt.mp3           -> Альтернативный Game Over
```

### 3. Интеграция в код

#### Загрузка музыки (в setup.py или audio_manager.py)
```python
# Основные треки
MUSIC = {
    'main_theme': 'resources/music/new/main_theme.mp3',
    'underground': 'resources/music/new/underground.mp3',
    'underwater': 'resources/music/new/underwater.mp3',
    'castle': 'resources/music/new/castle.mp3',
    'star_power': 'resources/music/new/star_power.mp3',
}

# Ускоренные версии (для таймера)
MUSIC_SPED_UP = {
    'main_theme': 'resources/music/new/main_theme_sped_up.mp3',
    'underground': 'resources/music/new/underground_sped_up.mp3',
    'underwater': 'resources/music/new/underwater_sped_up.mp3',
    'castle': 'resources/music/new/castle_sped_up.mp3',
}
```

#### Воспроизведение музыки
```python
# Обычная музыка
pg.mixer.music.load(MUSIC['main_theme'])
pg.mixer.music.play(-1)  # -1 = бесконечный цикл

# Переключение на ускоренную при малом времени
if time_remaining < 100:
    pg.mixer.music.load(MUSIC_SPED_UP['main_theme'])
    pg.mixer.music.play(-1)
```

#### Звуковые эффекты
```python
# Загрузка
coin_sound = pg.mixer.Sound('resources/music/new/coin.mp3')
pipe_sound = pg.mixer.Sound('resources/music/new/pipe.mp3')

# Воспроизведение
coin_sound.play()
pipe_sound.play()
```

## 📝 Примечания

### Типы уровней и их музыка
- **Level 1-1, 2-1** → main_theme.mp3
- **Level 1-2** → underground.mp3(подземелье)
- **Level 1-3, 2-3** → main_theme.mp3(мосты/деревья)
- **Level 1-4, 2-4** → castle.mp3(замки с боссами)
- **Level 2-2** → underwater.mp3(подводный)

### Когда использовать ускоренную музыку
- Когда таймер < 100 секунд
- Автоматически переключаться с обычной на ускоренную
- Воспроизводить предупреждающий звук (time_warning.mp3) при переключении

### Звуковые события
- **Сбор монеты** → coin.mp3
- **Вход в трубу** → pipe.mp3
- **Завершение уровня** → level_complete.mp3
- **Смерть** → game_over.mp3
- **Победа над боссом** → boss_defeat.mp3+ castle_complete.mp3

## 🔧 Конвертация (если нужно)

Если файлы в формате MP3 не работают, конвертируйте в OGG:
```bash
ffmpeg -i input.mp3 -acodec libvorbis output.ogg
```

## 📊 Приоритеты интеграции

1. **Высокий приоритет**:
   - Главная тема (main_theme.mp3)
   - Подземная музыка (underground.mp3)
   - Музыка замка (castle.mp3)
   - Звук монеты (coin.mp3)
   - Game Over (game_over.mp3)

2. **Средний приоритет**:
   - Подводная музыка (underwater.mp3)
   - Ускоренные версии
   - Звуки победы
   - Переход по трубе

3. **Низкий приоритет**:
   - Звезда непобедимости
   - Титры
   - Альтернативные версии

## 🎯 TODO для интеграции

- [x] Переименовать файлы согласно рекомендациям ✅
- [x] Конвертировать MP3 в OGG (если нужно) - Пропускаем, pygame поддерживает MP3 ✅
- [x] Добавить в audio_manager.py - Создан new_audio_loader.py ✅
- [x] Настроить переключение музыки по типу уровня ✅
- [x] Реализовать систему ускоренной музыки при малом времени ✅
- [x] Добавить звуковые эффекты для событий ✅
- [ ] Протестировать громкость всех треков
- [ ] Настроить плавные переходы между треками - Реализовано с fade_ms ✅

## 📝 Статус интеграции

### ✅ Выполнено
1. Все файлы переименованы с понятными именами
2. Создан модуль `data/new_audio_loader.py` для загрузки новой музыки
3. Добавлена карта соответствия уровней и музыки (LEVEL_MUSIC_MAP)
4. Реализована функция `get_level_music()` для автоматического выбора трека
5. Создан `data/level_music_manager.py` - полная система управления музыкой
6. Создан `data/level_sound_effects.py` - менеджер звуковых эффектов
7. Автоматическое переключение на ускоренную музыку при времени < 100 сек
8. Плавные переходы между треками (fade in/out)
9. Создан `INTEGRATION_EXAMPLE.md` с примерами использования

### � Готово к интеграции
Все модули созданы и готовы к использованию в уровнях!

### 📋 Как использовать

См. файл `INTEGRATION_EXAMPLE.md` в корне проекта для подробных примеров.

Краткий пример:
```python
from ..level_music_manager import get_level_music_manager
from ..level_sound_effects import get_level_sound_effects

# В startup()
self.music_manager = get_level_music_manager()
self.sound_effects = get_level_sound_effects()
self.music_manager.play_level_music('level1')

# В update()
self.music_manager.update(time_remaining)

# Звуковые эффекты
self.sound_effects.play_coin()
self.sound_effects.play_level_complete()
```

## 📚 Источник
Все файлы скачаны с: https://zvukipro.com/dendy/213-zvuki-iz-igry-mario-na-dendi.html


---

## 🎉 ОБНОВЛЕНИЕ: Интеграция завершена!

**Дата:** 1 марта 2026

Новая музыкальная система полностью интегрирована во все уровни игры!

### Что сделано:
✅ Музыкальные менеджеры добавлены во все уровни (level1-level8)
✅ Автоматическое переключение на ускоренную музыку при времени < 100 сек
✅ Предупреждающий звук при малом времени
✅ Плавные переходы между треками (fade in/out)

### Карта музыки по уровням:
- **Level 1 (1-1)**: main_theme → main_theme_sped_up
- **Level 2 (1-2)**: underground → underground_sped_up  
- **Level 3 (1-3)**: main_theme → main_theme_sped_up
- **Level 4 (1-4)**: castle → castle_sped_up
- **Level 5 (2-1)**: main_theme → main_theme_sped_up
- **Level 6 (2-2)**: underwater → underwater_sped_up
- **Level 7 (2-3)**: main_theme → main_theme_sped_up
- **Level 8 (2-4)**: castle → castle_sped_up

### Готово к тестированию!
Запустите игру и проверьте работу новой музыкальной системы.
