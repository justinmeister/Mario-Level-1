"""
Tests for UI system.
"""
import pytest
import pygame as pg

from data.ui import (
    UIState,
    MenuAction,
    ButtonStyle,
    MenuItem,
    UIButton,
    UILabel,
    AnimatedMenu,
    MainMenu,
    PauseMenu,
    HUD,
    UIManager,
)


class TestButtonStyle:
    """Tests for ButtonStyle."""

    def test_default_style(self) -> None:
        """Test default button style."""
        style = ButtonStyle()

        assert style.bg_color == c.SKY_BLUE
        assert style.bg_hover_color == c.BLUE
        assert style.text_color == c.WHITE
        assert style.border_width == 2
        assert style.font_size == 36
        assert style.corner_radius == 8

    def test_custom_style(self) -> None:
        """Test custom button style."""
        style = ButtonStyle(
            bg_color=c.RED,
            bg_hover_color=c.ORANGE,
            font_size=48,
            corner_radius=16,
        )

        assert style.bg_color == c.RED
        assert style.bg_hover_color == c.ORANGE
        assert style.font_size == 48
        assert style.corner_radius == 16


class TestMenuItem:
    """Tests for MenuItem."""

    def test_menu_item_creation(self) -> None:
        """Test creating menu item."""
        item = MenuItem(text="Test", action=MenuAction.START_GAME)

        assert item.text == "Test"
        assert item.action == MenuAction.START_GAME
        assert item.callback is None
        assert item.enabled is True

    def test_menu_item_with_callback(self) -> None:
        """Test menu item with callback."""
        called = []

        def callback() -> None:
            called.append(True)

        item = MenuItem(text="Test", action=MenuAction.SELECT, callback=callback)

        assert item.enabled is True
        item.callback()
        assert len(called) == 1


class TestUIButton:
    """Tests for UIButton."""

    @pytest.fixture
    def button(self) -> UIButton:
        """Create test button."""
        return UIButton(x=100, y=100, width=200, height=50, text="Click Me")

    def test_button_creation(self, button: UIButton) -> None:
        """Test button creation."""
        assert button.x == 100
        assert button.y == 100
        assert button.width == 200
        assert button.height == 50
        assert button.text == "Click Me"
        assert button.is_enabled is True
        assert button.is_hovered is False

    def test_button_position(self, button: UIButton) -> None:
        """Test button rect position."""
        assert button.rect.x == 100
        assert button.rect.y == 100
        assert button.rect.width == 200
        assert button.rect.height == 50

    def test_button_hover(self, button: UIButton) -> None:
        """Test button hover detection."""
        # Mouse over button
        button.update(16, (150, 120))
        assert button.is_hovered is True

        # Mouse outside button
        button.update(16, (50, 50))
        assert button.is_hovered is False

    def test_button_callback(self) -> None:
        """Test button callback."""
        called = []

        def callback() -> None:
            called.append(True)

        button = UIButton(x=100, y=100, width=200, height=50, text="Click", callback=callback)

        pg.init()
        # Simulate click
        event = pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": (150, 120), "button": 1})
        button.handle_event(event)

        event = pg.event.Event(pg.MOUSEBUTTONUP, {"pos": (150, 120), "button": 1})
        button.handle_event(event)

        assert len(called) == 1

        pg.quit()

    def test_button_disable(self, button: UIButton) -> None:
        """Test disabling button."""
        button.set_enabled(False)
        assert button.is_enabled is False

        # Hover should not work when disabled
        button.update(16, (150, 120))
        assert button.is_hovered is False

    def test_button_set_position(self, button: UIButton) -> None:
        """Test setting button position."""
        button.set_position(200, 200)

        assert button.x == 200
        assert button.y == 200
        assert button.rect.x == 200
        assert button.rect.y == 200

    def test_button_draw_no_crash(self, button: UIButton) -> None:
        """Test button draw doesn't crash."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        button.draw(surface)

        pg.quit()


class TestUILabel:
    """Tests for UILabel."""

    @pytest.fixture
    def label(self) -> UILabel:
        """Create test label."""
        return UILabel(x=100, y=50, text="Test Label", font_size=36, color=c.WHITE)

    def test_label_creation(self, label: UILabel) -> None:
        """Test label creation."""
        assert label.x == 100
        assert label.y == 50
        assert label.text == "Test Label"
        assert label.color == c.WHITE
        assert label.visible is True

    def test_label_set_text(self, label: UILabel) -> None:
        """Test changing label text."""
        label.set_text("New Text")
        assert label.text == "New Text"

    def test_label_visibility(self, label: UILabel) -> None:
        """Test label visibility."""
        label.visible = False
        assert label.visible is False

    def test_label_draw_no_crash(self, label: UILabel) -> None:
        """Test label draw doesn't crash."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        label.draw(surface)

        pg.quit()


class TestAnimatedMenu:
    """Tests for AnimatedMenu."""

    @pytest.fixture
    def menu(self) -> AnimatedMenu:
        """Create test menu."""
        return AnimatedMenu(800, 600, title="TEST MENU")

    def test_menu_creation(self, menu: AnimatedMenu) -> None:
        """Test menu creation."""
        assert menu.screen_width == 800
        assert menu.screen_height == 600
        assert menu.title == "TEST MENU"
        assert menu.state == UIState.HIDDEN
        assert len(menu.buttons) == 0

    def test_add_button(self, menu: AnimatedMenu) -> None:
        """Test adding button to menu."""
        button = menu.add_button("Start", MenuAction.START_GAME)

        assert len(menu.buttons) == 1
        assert button.text == "Start"

    def test_add_label(self, menu: AnimatedMenu) -> None:
        """Test adding label to menu."""
        label = menu.add_label("Info text")

        assert len(menu.labels) == 1
        assert label.text == "Info text"

    def test_show_hide(self, menu: AnimatedMenu) -> None:
        """Test showing and hiding menu."""
        assert menu.state == UIState.HIDDEN

        menu.show()
        assert menu.state == UIState.VISIBLE

        menu.hide()
        assert menu.state == UIState.HIDDEN

    def test_menu_clear(self, menu: AnimatedMenu) -> None:
        """Test clearing menu."""
        menu.add_button("Button 1", MenuAction.SELECT)
        menu.add_button("Button 2", MenuAction.SELECT)
        menu.add_label("Label")

        menu.clear()

        assert len(menu.buttons) == 0
        assert len(menu.labels) == 0

    def test_menu_update(self, menu: AnimatedMenu) -> None:
        """Test menu update."""
        menu.show()
        menu.add_button("Test", MenuAction.SELECT)

        # Should not crash
        menu.update(16, (400, 300))

    def test_menu_draw(self, menu: AnimatedMenu) -> None:
        """Test menu draw."""
        pg.init()
        surface = pg.Surface((800, 600))

        menu.show()
        menu.add_button("Test", MenuAction.SELECT)

        # Should not crash
        menu.draw(surface)

        pg.quit()


class TestMainMenu:
    """Tests for MainMenu."""

    @pytest.fixture
    def main_menu(self) -> MainMenu:
        """Create main menu."""
        return MainMenu(800, 600)

    def test_main_menu_creation(self, main_menu: MainMenu) -> None:
        """Test main menu creation."""
        assert main_menu.title == "SUPER MARIO BROS"
        assert len(main_menu.buttons) >= 3  # Start, Options, Quit

    def test_main_menu_buttons(self, main_menu: MainMenu) -> None:
        """Test main menu buttons exist."""
        button_texts = [btn.text for btn in main_menu.buttons]

        assert "НАЧАТЬ ИГРУ" in button_texts or "Start" in button_texts
        assert "ВЫХОД" in button_texts or "Quit" in button_texts


class TestPauseMenu:
    """Tests for PauseMenu."""

    @pytest.fixture
    def pause_menu(self) -> PauseMenu:
        """Create pause menu."""
        return PauseMenu(800, 600)

    def test_pause_menu_creation(self, pause_menu: PauseMenu) -> None:
        """Test pause menu creation."""
        assert pause_menu.title == "ПАУЗА"
        assert len(pause_menu.buttons) >= 3

    def test_pause_menu_buttons(self, pause_menu: PauseMenu) -> None:
        """Test pause menu buttons."""
        button_texts = [btn.text for btn in pause_menu.buttons]

        assert "ПРОДОЛЖИТЬ" in button_texts or any("Continue" in t for t in button_texts)


class TestHUD:
    """Tests for HUD."""

    @pytest.fixture
    def hud(self) -> HUD:
        """Create HUD."""
        return HUD(800, 600)

    def test_hud_creation(self, hud: HUD) -> None:
        """Test HUD creation."""
        assert hud.screen_width == 800
        assert hud.screen_height == 600
        assert hud.score == 0
        assert hud.coins == 0
        assert hud.lives == 3

    def test_hud_set_values(self, hud: HUD) -> None:
        """Test setting HUD values."""
        hud.set_score(1000)
        hud.set_coins(5)
        hud.set_lives(2)
        hud.set_world("1-2")
        hud.set_time(300)

        assert hud.score == 1000
        assert hud.coins == 5
        assert hud.lives == 2
        assert hud.world == "1-2"
        assert hud.time == 300

    def test_hud_set_combo(self, hud: HUD) -> None:
        """Test setting combo display."""
        hud.set_combo("5x COMBO!")
        assert hud.combo_text == "5x COMBO!"

    def test_hud_draw_no_crash(self, hud: HUD) -> None:
        """Test HUD draw doesn't crash."""
        pg.init()
        surface = pg.Surface((800, 600))

        hud.set_score(12345)
        hud.set_coins(10)

        # Should not crash
        hud.draw(surface)

        pg.quit()


class TestUIManager:
    """Tests for UIManager."""

    @pytest.fixture
    def ui_manager(self) -> UIManager:
        """Create UI manager."""
        return UIManager(800, 600)

    def test_ui_manager_creation(self, ui_manager: UIManager) -> None:
        """Test UI manager creation."""
        assert ui_manager.screen_width == 800
        assert ui_manager.screen_height == 600
        assert ui_manager.main_menu is not None
        assert ui_manager.pause_menu is not None
        assert ui_manager.hud is not None

    def test_show_main_menu(self, ui_manager: UIManager) -> None:
        """Test showing main menu."""
        ui_manager.show_main_menu()
        assert ui_manager.current_menu == ui_manager.main_menu

    def test_show_pause_menu(self, ui_manager: UIManager) -> None:
        """Test showing pause menu."""
        ui_manager.show_pause_menu()
        assert ui_manager.current_menu == ui_manager.pause_menu

    def test_hide_menu(self, ui_manager: UIManager) -> None:
        """Test hiding menu."""
        ui_manager.show_main_menu()
        ui_manager.hide_menu()
        assert ui_manager.current_menu is None

    def test_show_hide_hud(self, ui_manager: UIManager) -> None:
        """Test showing and hiding HUD."""
        ui_manager.show_hud()
        # HUD should be visible

        ui_manager.hide_hud()
        # HUD should be hidden

    def test_ui_manager_update(self, ui_manager: UIManager) -> None:
        """Test UI manager update."""
        ui_manager.show_main_menu()

        # Should not crash
        ui_manager.update(16, (400, 300))

    def test_ui_manager_draw(self, ui_manager: UIManager) -> None:
        """Test UI manager draw."""
        pg.init()
        surface = pg.Surface((800, 600))

        ui_manager.show_main_menu()

        # Should not crash
        ui_manager.draw(surface)

        pg.quit()


class TestUIIntegration:
    """Integration tests for UI system."""

    def test_full_menu_flow(self) -> None:
        """Test complete menu flow."""
        pg.init()

        ui_manager = UIManager(800, 600)

        # Show main menu
        ui_manager.show_main_menu()
        assert ui_manager.current_menu == ui_manager.main_menu

        # Hide menu
        ui_manager.hide_menu()
        assert ui_manager.current_menu is None

        # Show pause menu
        ui_manager.show_pause_menu()
        assert ui_manager.current_menu == ui_manager.pause_menu

        pg.quit()

    def test_hud_with_game_state(self) -> None:
        """Test HUD reflecting game state."""
        hud = HUD(800, 600)

        # Simulate game progress
        hud.set_score(5000)
        hud.set_coins(25)
        hud.set_lives(2)
        hud.set_time(150)
        hud.set_combo("3x COMBO!")

        assert hud.score == 5000
        assert hud.coins == 25

    def test_button_interaction_sequence(self) -> None:
        """Test button interaction sequence."""
        pg.init()

        click_count = [0]

        def on_click() -> None:
            click_count[0] += 1

        button = UIButton(x=100, y=100, width=200, height=50, text="Test", callback=on_click)

        surface = pg.Surface((800, 600))

        # Hover
        button.update(16, (150, 120))
        assert button.is_hovered

        # Click
        event = pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": (150, 120), "button": 1})
        button.handle_event(event)

        event = pg.event.Event(pg.MOUSEBUTTONUP, {"pos": (150, 120), "button": 1})
        button.handle_event(event)

        assert click_count[0] == 1

        pg.quit()
