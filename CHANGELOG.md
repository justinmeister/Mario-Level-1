# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-02-24

### Added (Wave 6 - Latest)

#### Minimap System (`data/minimap_system.py`)
- Real-time minimap rendering
- Entity tracking with 10 entity types
- 6 marker shapes (Circle, Square, Triangle, Diamond, Arrow, Star)
- Waypoint system with labels
- Fog of war (optional)
- Zoom levels (0.05x - 0.5x)
- Interactive marker clicks
- Camera tracking

#### Melee Combat System (`data/melee_combat.py`)
- Combo attack system
- 4 attack types (Light, Heavy, Aerial, Charged)
- Hit box detection
- Damage calculation with modifiers
- Knockback and hit stun
- Attack state machine (Windup, Active, Recovery)
- 4 predefined combo chains
- Combat statistics tracking

### Added (Wave 5)

#### Achievements System v2 (`data/achievements_v2.py`)
- **Rarity System**: 6 tiers (Common, Uncommon, Rare, Very Rare, Legendary, Mythic)
- **Categories**: 9 categories (Combat, Collection, Exploration, Platforming, Speedrun, Survival, Combo, Boss, Special)
- **Achievement Tiers**: Bronze, Silver, Gold, Platinum, Diamond
- **Achievement Chains**: Prerequisites and chain IDs for progression
- **Milestones**: Partial progress tracking with milestone callbacks
- **Hidden Achievements**: Secret achievements with hidden descriptions
- **Points System**: Achievement points with total tracking
- **Visual Notifications**: Unlock notifications with rarity colors
- **17 Default Achievements**: Pre-configured achievements across all categories

#### Enhanced Particle System v2 (`data/enhanced_particles_v2.py`)
- **Particle Shapes**: Circle, Square, Triangle, Star, Ring, Spark
- **Behaviors**: Normal, Gravity, Float, Orbit, Spiral, Homing, Explode, Fade Out, Pulse, Wave
- **Color Gradients**: Smooth color transitions over lifetime
- **Size Animation**: Dynamic size changes
- **Rotation**: Rotating particles with configurable speed
- **Alpha Fading**: Fade in/out effects
- **Object Pooling**: Efficient particle reuse
- **Continuous Emitters**: Rate-controlled particle emission
- **10 Presets**: Fire, Smoke, Spark, Magic, Explosion, Debris, Energy Orb, Rain, Snow, Coin Burst
- **Effect Presets**: Jump, Land, Coin, Powerup, Explosion, Fireball, Death, Victory

### Added (Wave 4)
- **Effect System**: Complete buff/debuff system with stacking, durations, and modifiers
  - `EffectType`: BUFF, DEBUFF, POWERUP, STATUS, SPECIAL
  - `EffectCategory`: MOVEMENT, COMBAT, DEFENSE, UTILITY, SPECIAL
  - `EffectStackType`: NONE, STACK, EXTEND
  - `EffectManager`: Apply, remove, update effects with callbacks
  - `ActiveEffect`: Timed and permanent effects with progress tracking
  - 7 preset effects: Speed Boost, Slow, Invincibility, Poison, Mushroom/Fire/Ice Power
  - Visual effect indicators with progress bars

- **Quest System**: Full quest management with chains and prerequisites
  - `QuestType`: MAIN, SIDE, DAILY, WEEKLY, ACHIEVEMENT, HIDDEN
  - `QuestCategory`: COMBAT, COLLECTION, EXPLORATION, PLATFORMING, BOSS, NPC, SPECIAL
  - `QuestState`: LOCKED, AVAILABLE, ACTIVE, COMPLETED, CLAIMED, FAILED, EXPIRED
  - Multiple objectives per quest with progress tracking
  - Reward system: coins, XP, items, unlockables, stat bonuses
  - Quest chains with prerequisite checking
  - Repeatable quests (daily/weekly)
  - 5 default quests included

- **Enhanced Main Menu**: Animated menu with visual effects
  - `EnhancedMenu`: Smooth animations and transitions
  - `AnimatedButton`: Hover effects, scaling, pulse animations
  - `ParticleBackground`: Animated particle system
  - Player stats display (level, rank, coins)
  - Keyboard navigation support

### Changed
- Fixed `ChallengeStatus.from_dict()` to use proper enum indexing
- Fixed `QuestState.from_dict()` to use proper enum indexing
- Fixed `AchievementTier.from_dict()` to use proper enum indexing
- Added `EffectType.SPECIAL` for custom effects
- Added `__post_init__` to `ActiveEffect` for proper initialization

### Tests
- **67 new tests** for Achievements v2 and Enhanced Particles v2
- Full coverage for achievement tracking, rarity, categories, and prerequisites
- Full coverage for particle behaviors, shapes, and effects
- Integration tests for event-based progress tracking

### Technical
- All new code follows project conventions (type hints, docstrings)
- Formatted with black and isort
- 85%+ coverage on new modules

## [2.7.0] - 2026-02-23

### Added
- **Player Progression System**: XP, levels, 7 rank tiers (Novice → Legend)
- **Character Customization**: 14+ unlockable skins with unique bonuses
- **Daily & Weekly Challenges**: Auto-generated challenges with 6 categories
- **Advanced AI System**: State machines, group coordination, AI director
- **Lazy Image Loading**: `ImageCache` and `LazyImageLoader` for optimized resource loading
- **KeyBindings Class**: Configurable key bindings with runtime reconfiguration
- **Integration Tests**: Comprehensive test suite for component interactions
- **Makefile**: Build automation for common development tasks
- **.editorconfig**: Editor consistency across different IDEs

### Changed
- **Refactored constants**: Split into submodules (`colors`, `physics`, `states`, `items`, `screen`)
- **Refactored tools**: Split into submodules (`controllers`, `states`, `resources`, `keybindings`)
- **Enhanced error handling**: Improved `main.py` with detailed error messages and logging
- **Enhanced setup**: Modular initialization with factory functions for states
- **CI improvements**: Removed `|| true` from mypy, added stricter type checking

### Fixed
- Version synchronization between code and documentation
- Import warnings in refactored modules
- Resource loading error handling

### Technical
- Updated version to 2.7.0 in `Mario.py`
- Added comprehensive docstrings to new classes and functions
- Formatted all new code with black and isort

## [2.6.0] - 2026-02-XX

### Added
- Combo System 2.0 with multipliers up to 5x
- Boss System: Bowser, Mega Goomba, Giant Koopa Troopa
- 4 New Enemies: Piranha Plant, Bullet Bill, Hammer Bro, Buzzy Beetle
- Advanced Particles: Object pooling, 10+ new particle types
- Enhanced Hints: Smart tutorial system with progress tracking
- 100+ New Tests: Full test coverage for new systems

## [2.5.0] - 2026

### Added
- Python 3.10+ with type hints
- JSON level loader
- Save/load system
- Test suite (pytest)
- CI/CD pipeline
- Enhanced audio system
- Visual effects (particles, parallax)
- Performance optimizations

## [1.0.0] - 2023

### Added
- Original release by justinarmstrong
- Basic Mario Level 1 recreation
- Core gameplay mechanics

---

## Unreleased

### Planned
- More levels (1-2, 1-3, 1-4)
- Additional power-ups
- Time attack / speedrun mode
- Colorblind accessibility options
- Alternative control schemes
- API documentation (Sphinx)
