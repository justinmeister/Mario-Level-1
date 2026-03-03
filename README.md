# Super Mario Bros Level 1 - Enhanced Edition

![screenshot](screenshot.png)

An enhanced recreation of the first level of Super Mario Bros for the NES, built with Python and Pygame.

## 🎮 Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move left/right, crouch |
| `A` | Jump |
| `S` | Action (fireball, run) |
| `F5` | Toggle FPS display |
| `ESC` | Pause menu |

## ✨ New Features (v2.7)

### v2.7 - Latest Additions (Current)

#### Player Progression & RPG Elements
- **Player Level System**: XP, levels, and rank progression
  - 7 rank tiers: Novice → Apprentice → Warrior → Veteran → Elite → Master → Legend
  - Persistent stats tracking (coins, enemies, levels, deaths, etc.)
  - Skill tree with 8+ unlockable abilities
  - Level-based unlocks and rewards

- **Character Customization**: 14+ unlockable skins
  - **Classic**: Default, Fire, Ice, Gold Mario
  - **Modern**: Builder, Sport Mario
  - **Fantasy**: Knight, Wizard, Dragon Mario
  - **Retro**: 8-bit, Green Mario
  - **Event**: Birthday, Halloween, Christmas Mario
  - Skin bonuses (XP, coins multipliers)
  - Special visual effects per skin

- **Daily & Weekly Challenges**:
  - Auto-generated challenges (3 daily, 2 weekly)
  - 6 categories: Combat, Collection, Exploration, Skill, Speedrun, Special
  - Coin and XP rewards
  - Progress tracking and expiration

#### Advanced AI System
- **Enemy AI Controllers**:
  - State machine (Idle, Suspicious, Alerted, Combat, Retreating)
  - Target detection and tracking
  - Line of sight calculations
  - Memory system for lost targets

- **AI Behaviors**:
  - Passive, Aggressive, Defensive
  - Patrol with waypoints
  - Ambush tactics
  - Flee when low health
  - Guard positions

- **Group Coordination**:
  - Squad-based AI
  - Coordinated attacks
  - Flanking maneuvers
  - Role assignment (attackers, flankers)
  - Group strategies: Assault, Flank, Defensive, Patrol

- **AI Director**:
  - Dynamic difficulty adjustment
  - Player performance tracking
  - Tension level system
  - Adaptive spawn rates

### v2.6 Additions
- **Combo System 2.0**: Enhanced combo chains with multipliers up to 5x
- **Boss System**: Bowser, Mega Goomba, Giant Koopa Troopa
- **4 New Enemies**: Piranha Plant, Bullet Bill, Hammer Bro, Buzzy Beetle
- **Advanced Particles**: Object pooling, 10+ new particle types
- **Enhanced Hints**: Smart tutorial system with progress tracking
- **100+ New Tests**: Full test coverage for new systems

### v2.4 Additions
- **Weather System**: Dynamic rain, snow, clouds, storms + day/night cycle
- **Audio Manager**: Multi-channel audio, playlists, category-based volume
- **Hint System**: Context-sensitive hints, tutorial mode, 17+ built-in hints

### v2.3 Additions
- **Achievements System**: 20+ achievements with persistence and notifications
- **Combo System**: Score multipliers for consecutive actions
- **Advanced Animations**: Interpolated sprites with easing functions
- **Enhanced UI**: Animated menus, buttons with hover effects, pause menu
- **Difficulty Settings**: Easy, Normal, Hard, Extreme modes
- **Settings Manager**: Persistent video, audio, and control settings

### Developer Tools
- **Testing**: Full pytest test suite (320+ tests)
- **CI/CD**: GitHub Actions for automated testing and builds
- **Code Quality**: pre-commit hooks, mypy, flake8, black
- **Documentation**: Comprehensive docstrings throughout

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Type checking
mypy data/

# Code formatting
black data/ tests/
```

## 🚀 Running the Game

```bash
python Mario.py
```

Or on Windows:
```bash
python Mario.py
```

## 📁 Project Structure

```
Mario-Level-1/
├── Mario.py            # Main entry point
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
├── .pre-commit-config.yaml
├── data/
│   ├── __init__.py
│   ├── main.py          # Game initialization
│   ├── constants.py     # Game constants (typed)
│   ├── tools.py         # Base classes (Control, State)
│   ├── setup.py         # Resource loading
│   ├── level_loader.py  # JSON level loading
│   ├── save_system.py   # Game save/load
│   ├── optimization.py  # Object pooling, batching
│   ├── game_sound.py    # Enhanced audio system
│   ├── visual_effects.py # Particles, parallax
│   ├── advanced_particles.py # Advanced particle system
│   ├── combo_manager.py  # Combo system manager
│   ├── combo_system.py   # Combo & multipliers
│   ├── game_settings.py  # Settings & difficulty
│   ├── animation_system.py # Interpolated animations
│   ├── ui.py            # Enhanced UI menus
│   ├── dialogue_system.py # Dialogue management
│   ├── hint_system.py   # Basic hint system
│   ├── enhanced_hint_system.py # Enhanced hints
│   ├── debug.py         # Debug tools
│   ├── screenshot.py    # Screenshot system
│   ├── statistics.py    # Game statistics
│   ├── weather_system.py # Weather effects
│   ├── audio_manager.py # Audio management
│   ├── achievements.py   # Achievements system
│   ├── input_system.py   # Input handling
│   ├── resource_manager.py # Resource management
│   ├── components/      # Game objects
│   │   ├── mario.py
│   │   ├── enemies.py
│   │   ├── advanced_enemies.py # New enemies
│   │   ├── bosses.py     # Boss system
│   │   ├── bricks.py
│   │   └── ...
│   ├── states/          # Game states
│   │   ├── main_menu.py
│   │   ├── level1.py
│   │   └── ...
│   └── levels/          # JSON level files
│       └── level_1_1.json
├── tests/
│   ├── test_level_loader.py
│   ├── test_constants.py
│   ├── test_tools.py
│   ├── test_save_system.py
│   ├── test_new_features.py # Tests for new systems
│   └── ...
├── resources/
│   ├── graphics/
│   ├── sound/
│   └── fonts/
├── saves/               # Auto-created save directory
│   ├── game.sav
│   ├── hints.json
│   └── stats.json
└── screenshots/         # Auto-created screenshot dir
```

## 🛠️ Configuration

### Video Settings
Edit `data/constants.py`:
```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
```

### Audio Settings
The sound system supports volume control:
```python
from data.game_sound import SoundSettings

settings = SoundSettings()
settings.music_volume = 0.5  # 50%
settings.sfx_volume = 0.7    # 70%
```

### Key Bindings
Edit `data/tools.py`:
```python
keybinding = {
    'action': pg.K_s,
    'jump': pg.K_a,
    'left': pg.K_LEFT,
    'right': pg.K_RIGHT,
    'down': pg.K_DOWN
}
```

### YAML Configuration (v2.7+)

Edit `config/game.yaml` for comprehensive settings:

```yaml
display:
  screen_width: 800
  screen_height: 600
  fps: 60
  fullscreen: false

audio:
  enabled: true
  music_volume: 0.5
  sfx_volume: 0.7

gameplay:
  difficulty: normal  # easy, normal, hard, extreme
  starting_lives: 3
  enable_auto_save: true

graphics:
  quality_preset: high
  enable_particles: true
  max_particles: 1000
```

Load configuration in code:
```python
from data.config_manager import get_config

config = get_config()
print(f"Screen: {config.display.screen_width}x{config.display.screen_height}")
print(f"Difficulty: {config.gameplay.difficulty}")
```

## 📝 Creating Custom Levels

### JSON Format

Levels can be created in JSON format:

```json
{
  "name": "1-1",
  "width": 8550,
  "ground_height": 538,
  "bricks": [
    {"x": 858, "y": 365, "contents": null}
  ],
  "coin_boxes": [
    {"x": 685, "y": 365, "contents": "coin"}
  ],
  "enemies": [
    {"type": "goomba", "x": 0, "y": 538, "direction": "left"}
  ]
}
```

Save to `data/levels/` and load with:
```python
from data.level_loader import load_level_from_json
level = load_level_from_json("data/levels/my_level.json")
```

### Text-Based Level Builder (v2.7+)

Create levels using ASCII art:

```
# Save as my_level.txt
................................................................
................................................................
........................?.......................................
....................B?B?B.......................................
......................................##........................
....................G...........................................
====================================================............
```

Build with:
```bash
# Create sample layout
python scripts/build_level.py --sample

# Build level from layout
python scripts/build_level.py --name my_level --input my_level.txt
```

### Legend

| Symbol | Element |
|--------|---------|
| `.` | Empty space |
| `=` | Ground |
| `B` | Brick block |
| `?` | Coin box |
| `!` | Mushroom box |
| `#` | Pipe |
| `G` | Goomba |
| `K` | Koopa |
| `F` | Flag pole |
| `S` | Step block |

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=data --cov-report=html

# Run specific test file
pytest tests/test_level_loader.py -v

# Run benchmarks
pytest tests/test_benchmark.py --benchmark-only

# Run integration tests
pytest tests/test_integration.py -v
```

## 👨‍💻 Developer Examples

### Save/Load System

```python
from data.save_system import SaveManager, GameData

# Get save manager
manager = SaveManager()

# Create game data
game_data = GameData(
    score=10000,
    coin_total=50,
    lives=3,
    current_level='level1',
    unlocked_skins=['fire', 'ice'],
)

# Save to slot 1
manager.save_game(1, game_data)

# Load from slot 1
loaded_data = manager.load_game(1)
print(f"Score: {loaded_data.score}")

# Check if save exists
if manager.save_exists(1):
    print(f"Save info: {manager.get_save_summary(1)}")
```

### Particle System

```python
from data.advanced_particles import AdvancedParticleSystem

# Create particle system
particles = AdvancedParticleSystem(max_particles=500)

# Emit particles at position
particles.emit(400, 300, "jump_dust")
particles.emit(200, 400, "coin_burst")

# Update in game loop
while running:
    particles.update(16)  # 16ms delta time
    
    # Render
    screen.fill((0, 0, 0))
    particles.draw_batch(screen)
    pygame.display.flip()

# Get statistics
stats = particles.get_stats()
print(f"Active particles: {stats['active']}")
```

### Configuration

```python
from data.config_manager import get_config, reload_config

# Get configuration (auto-loads)
config = get_config()

# Access settings
print(config.display.screen_width)
print(config.gameplay.difficulty)
print(config.graphics.max_particles)

# Modify settings
config.set('gameplay', 'starting_lives', 5)
config.save()

# Reload from file
reload_config()
```

### Key Bindings

```python
from data.tools.keybindings import KeyBindings
import pygame as pg

# Create key bindings
bindings = KeyBindings()

# Get key for action
jump_key = bindings.get('jump')

# Check if key matches action
if bindings.is_action(pg.K_SPACE, 'jump'):
    print("Space is jump!")

# Rebind
bindings.set('jump', pg.K_SPACE)

# Reset to defaults
bindings.reset()
```

### Image Caching

```python
from data.tools.resources import ImageCache, LazyImageLoader

# Use global cache
sprite = ImageCache.get("resources/graphics/mario.png")

# Or use lazy loader for directories
loader = LazyImageLoader("resources/graphics/enemies")
goomba_sprite = loader.get("goomba_walk_1")

# Get all images from directory
all_sprites = loader.get_all()

# Clear cache to free memory
ImageCache.clear()
```

## 📊 Performance

The enhanced version includes several optimizations:

| Feature | Improvement |
|---------|-------------|
| Object Pooling | Reduced GC overhead |
| Sprite Batching | Fewer draw calls |
| Type Hints | Better IDE support |
| Lazy Loading | Faster startup |

## 🐛 Known Issues

- Some animations may stutter on low-end hardware
- Audio latency on some Windows configurations

## 📄 License

This project is intended for **non-commercial educational purposes only**.

Super Mario Bros is a trademark of Nintendo.

## 🙏 Credits

**Original Author:** justinarmstrong  
**Enhanced Version:** Community contributions  
**Based on:** Super Mario Bros (Nintendo, 1985)

## 🔗 Links

- [Original YouTube Demo](http://www.youtube.com/watch?v=HBbzYKMfx5Y)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## Version History

### v2.6.0 (2026) - Bosses & Enhanced Combat
- ✅ **Combo System 2.0**: Enhanced chains, 5x multiplier, visual feedback
- ✅ **Boss System**: Bowser, Mega Goomba, Giant Koopa Troopa
- ✅ **4 New Enemies**: Piranha Plant, Bullet Bill, Hammer Bro, Buzzy Beetle
- ✅ **Advanced Particles**: Object pooling, 10+ new particle types
- ✅ **Enhanced Hints**: Smart tutorial system with progress tracking
- ✅ **100+ New Tests**: Full test coverage for new systems

### v2.5.0 (2026) - Enhanced Edition
- ✅ Python 3.10+ with type hints
- ✅ JSON level loader
- ✅ Save/load system
- ✅ Test suite (pytest)
- ✅ CI/CD pipeline
- ✅ Enhanced audio system
- ✅ Visual effects (particles, parallax)
- ✅ Performance optimizations

### v1.0.0 (2023)
- Original release

---

*Last updated: February 2026*
