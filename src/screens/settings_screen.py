from __future__ import annotations

from typing import TYPE_CHECKING, override

import pygame
from game_state import State
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from src.constants import (
    BLUE,
    EASY,
    GREEN,
    HARD,
    MEDIUM,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
    YELLOW,
    load_audio,
    load_image,
)
from src.settings import GAME_SETTINGS
from src.ui import Button, Slider, time_based_background
from src.ui_constants import (
    BUTTON_PRIMARY_COLOR,
    BUTTON_SECONDARY_COLOR,
    FONT_LARGE,
    FONT_SMALL,
)

if TYPE_CHECKING:
    from typing import Any, Literal

    from pygame import Surface
    from pygame.event import Event
    from pygame.font import Font
    from pygame.mixer import Sound


class SettingsScreen(State, state_name="settings"):
    """
    Settings screen for adjusting game preferences.

    Provides UI for changing difficulty, bird and pipe types, and audio settings.
    """

    def __init__(self) -> None:
        self.background: Surface = time_based_background()
        self.base: Surface = load_image(("base.png")).convert_alpha()

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        self.panel_width: int = 250
        self.panel_height: int = 400
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            50,
        )

        self.title_font: Font = FONT_LARGE
        self.font: Font = FONT_SMALL
        self.active_tab: Literal["gameplay", "audio"] = "gameplay"

        self.tab_width: int = self.panel_width // 2
        self.tab_height: int = 40

        gameplay_color = (
            BUTTON_PRIMARY_COLOR
            if self.active_tab == "gameplay"
            else (50, 50, 50)
        )
        audio_color = (50, 50, 50)

        self.gameplay_tab: Button = Button(
            self.panel_position[0],
            self.panel_position[1],
            self.tab_width,
            self.tab_height,
            "Gameplay",
            bg_color=gameplay_color,
        )

        self.audio_tab: Button = Button(
            self.panel_position[0] + self.tab_width,
            self.panel_position[1],
            self.tab_width,
            self.tab_height,
            "Audio",
            bg_color=audio_color,
        )

        # Bird sprites
        self.yellow_bird: Surface = load_image(
            "yellowbird-midflap.png"
        ).convert_alpha()
        self.blue_bird: Surface = load_image(
            "bluebird-midflap.png"
        ).convert_alpha()
        self.red_bird: Surface = load_image(
            "redbird-midflap.png"
        ).convert_alpha()

        # Pipe sprites
        self.green_pipe: Surface = load_image("pipe-green.png").convert_alpha()
        self.red_pipe: Surface = load_image("pipe-red.png").convert_alpha()

        self.selection_width: int = (self.panel_width - 40) // 3
        self.medium_width: int = self.selection_width
        self.selection_height: int = 35

        button_y = self.panel_position[1] + 75
        button_spacing = 10

        first_button_x = self.panel_position[0] + 10
        self.easy_button: Button = Button(
            first_button_x,
            button_y,
            self.selection_width,
            self.selection_height,
            "Easy",
            bg_color=YELLOW
            if GAME_SETTINGS.difficulty == EASY
            else (70, 70, 70),
        )

        self.medium_button: Button = Button(
            first_button_x + self.selection_width + button_spacing,
            button_y,
            self.medium_width,
            self.selection_height,
            "Medium",
            bg_color=BLUE
            if GAME_SETTINGS.difficulty == MEDIUM
            else (70, 70, 70),
        )

        self.hard_button: Button = Button(
            first_button_x + (self.selection_width + button_spacing) * 2,
            button_y,
            self.selection_width,
            self.selection_height,
            "Hard",
            bg_color=RED if GAME_SETTINGS.difficulty == HARD else (70, 70, 70),
        )

        nav_button_width = self.panel_width // 2 - 15
        nav_button_y = self.panel_position[1] + self.panel_height - 50

        self.save_button: Button = Button(
            self.panel_position[0] + 10,
            nav_button_y,
            nav_button_width,
            40,
            "Save",
            bg_color=BUTTON_PRIMARY_COLOR,
        )

        self.back_button: Button = Button(
            self.panel_position[0] + self.panel_width // 2 + 5,
            nav_button_y,
            nav_button_width,
            40,
            "Back",
            bg_color=BUTTON_SECONDARY_COLOR,
        )

        self.initial_volume: float = GAME_SETTINGS.volume

        self.click_sound: Sound = load_audio("swoosh.wav")
        self.point_sound: Sound = load_audio("point.wav")

        self.volume_slider: Slider = Slider(
            self.panel_position[0] + 20,
            self.panel_position[1] + 180,
            self.panel_width - 40,
            10,
            0.0,
            1.0,
            GAME_SETTINGS.volume,
        )

        self.initial_difficulty: int = GAME_SETTINGS.difficulty
        self.has_changes: bool = False

    @override
    def process_event(self, event: Event) -> None:
        """
        Handle pygame events for the settings screen.

        Parameters
        ----------
        event : pygame.event.Event
            Pygame event to process.

        Returns
        -------
        None
        """
        mouse_pos = pygame.mouse.get_pos()

        if event.type == QUIT:
            self.manager.is_running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.manager.change_state("main_menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

            if self.gameplay_tab.is_clicked(mouse_pos, mouse_clicked):
                self.active_tab = "gameplay"
                self.click_sound.play()

            elif self.audio_tab.is_clicked(mouse_pos, mouse_clicked):
                self.active_tab = "audio"
                self.click_sound.play()

            if self.active_tab == "gameplay":
                if self.easy_button.is_clicked(mouse_pos, mouse_clicked):
                    GAME_SETTINGS.difficulty = EASY
                    GAME_SETTINGS.bird_type = "yellow"
                    GAME_SETTINGS.pipe_color = "green"

                    self.easy_button.bg_color = YELLOW
                    self.medium_button.bg_color = (70, 70, 70)
                    self.hard_button.bg_color = (70, 70, 70)

                    self.click_sound.play()
                    self.has_changes = True

                elif self.medium_button.is_clicked(mouse_pos, mouse_clicked):
                    GAME_SETTINGS.difficulty = MEDIUM
                    GAME_SETTINGS.bird_type = "blue"
                    GAME_SETTINGS.pipe_color = "green"

                    self.easy_button.bg_color = (70, 70, 70)
                    self.medium_button.bg_color = BLUE
                    self.hard_button.bg_color = (70, 70, 70)

                    self.click_sound.play()
                    self.has_changes = True

                elif self.hard_button.is_clicked(mouse_pos, mouse_clicked):
                    GAME_SETTINGS.difficulty = HARD
                    GAME_SETTINGS.bird_type = "red"
                    GAME_SETTINGS.pipe_color = "red"

                    self.easy_button.bg_color = (70, 70, 70)
                    self.medium_button.bg_color = (70, 70, 70)
                    self.hard_button.bg_color = RED

                    self.click_sound.play()
                    self.has_changes = True

            elif self.active_tab == "audio":
                if self.volume_slider.handle_event(event, mouse_pos):
                    GAME_SETTINGS.set_volume(self.volume_slider.value)
                    if abs(GAME_SETTINGS.volume - self.initial_volume) > 0.001:
                        self.has_changes = True
                    else:
                        self.has_changes = False

            if self.save_button.is_clicked(mouse_pos, mouse_clicked):
                GAME_SETTINGS.save_settings()
                self.initial_difficulty = GAME_SETTINGS.difficulty
                self.initial_volume = GAME_SETTINGS.volume
                self.has_changes = False
                self.point_sound.play()

            elif self.back_button.is_clicked(mouse_pos, mouse_clicked):
                if self.has_changes:
                    GAME_SETTINGS.difficulty = self.initial_difficulty
                    GAME_SETTINGS.set_volume(self.initial_volume)
                    self._update_bird_and_pipe_for_difficulty()
                self.click_sound.play()
                self.manager.change_state("main_menu")

        elif (
            event.type == pygame.MOUSEMOTION
            or event.type == pygame.MOUSEBUTTONUP
        ) and self.active_tab == "audio":
            if self.volume_slider.handle_event(event, mouse_pos):
                GAME_SETTINGS.set_volume(self.volume_slider.value)
                if abs(GAME_SETTINGS.volume - self.initial_volume) > 0.001:
                    self.has_changes = True
                else:
                    self.has_changes = False

    def _update_bird_and_pipe_for_difficulty(self) -> None:
        """
        Update bird type and pipe color based on the current difficulty setting.

        Returns
        -------
        None
        """
        if GAME_SETTINGS.difficulty == EASY:
            GAME_SETTINGS.bird_type = "yellow"
            GAME_SETTINGS.pipe_color = "green"
        elif GAME_SETTINGS.difficulty == MEDIUM:
            GAME_SETTINGS.bird_type = "blue"
            GAME_SETTINGS.pipe_color = "green"
        else:  # HARD
            GAME_SETTINGS.bird_type = "red"
            GAME_SETTINGS.pipe_color = "red"

    @override
    def process_update(self, dt: float, *args: Any) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the settings screen state and render.

        Parameters
        ----------
        dt : float
            Time delta since last update in seconds.
        args : tuple[Any, ...]
            Additional arguments passed from the state manager.

        Returns
        -------
        None
        """
        mouse_pos = pygame.mouse.get_pos()

        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width:
            self.base_x = 0

        self.gameplay_tab.update(mouse_pos)
        self.audio_tab.update(mouse_pos)

        if self.active_tab == "gameplay":
            easy_original_color = self.easy_button.bg_color
            medium_original_color = self.medium_button.bg_color
            hard_original_color = self.hard_button.bg_color

            self.easy_button.update(mouse_pos)
            self.medium_button.update(mouse_pos)
            self.hard_button.update(mouse_pos)

            if (
                self.easy_button.is_hovered
                and self.easy_button.bg_color != YELLOW
            ):
                self.easy_button.hover_color = YELLOW
            elif easy_original_color == YELLOW:
                self.easy_button.hover_color = (
                    min(YELLOW[0] + 30, 255),
                    min(YELLOW[1] + 30, 255),
                    min(YELLOW[2] + 30, 255),
                )
            else:
                self.easy_button.hover_color = (100, 100, 100)

            if (
                self.medium_button.is_hovered
                and self.medium_button.bg_color != BLUE
            ):
                self.medium_button.hover_color = BLUE
            elif medium_original_color == BLUE:
                self.medium_button.hover_color = (
                    min(BLUE[0] + 30, 255),
                    min(BLUE[1] + 30, 255),
                    min(BLUE[2] + 30, 255),
                )
            else:
                self.medium_button.hover_color = (100, 100, 100)

            if (
                self.hard_button.is_hovered
                and self.hard_button.bg_color != RED
            ):
                self.hard_button.hover_color = RED
            elif hard_original_color == RED:
                self.hard_button.hover_color = (
                    min(RED[0] + 30, 255),
                    min(RED[1] + 30, 255),
                    min(RED[2] + 30, 255),
                )
            else:
                self.hard_button.hover_color = (100, 100, 100)

        self.save_button.update(mouse_pos)
        self.back_button.update(mouse_pos)

        self.has_changes = self.initial_difficulty != GAME_SETTINGS.difficulty

        self._render()

    def _render(self) -> None:
        """
        Render the settings screen.

        Draws the background, base, settings panel, tabs, title, content based on
        active tab, and navigation buttons, then updates the display.

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        self.window.blit(self.base, (self.base_x, self.base_y))
        self.window.blit(
            self.base, (self.base_x + self.base_width, self.base_y)
        )

        panel_surf = pygame.Surface(
            (self.panel_width, self.panel_height), pygame.SRCALPHA
        )
        panel_surf.fill((0, 0, 0, 220))
        pygame.draw.rect(
            panel_surf, WHITE, (0, 0, self.panel_width, self.panel_height), 2
        )
        self.window.blit(panel_surf, self.panel_position)

        if self.active_tab == "gameplay":
            self.gameplay_tab.bg_color = BUTTON_PRIMARY_COLOR
            self.audio_tab.bg_color = (50, 50, 50)
        else:
            self.gameplay_tab.bg_color = (50, 50, 50)
            self.audio_tab.bg_color = BUTTON_PRIMARY_COLOR

        self.gameplay_tab.draw(self.window)
        self.audio_tab.draw(self.window)

        # Draw title
        title_text = self.title_font.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] - 20)
        )
        self.window.blit(title_text, title_rect)

        if self.active_tab == "gameplay":
            self._render_gameplay_tab()
        else:
            self._render_audio_tab()

        if self.has_changes:
            self.save_button.bg_color = BUTTON_PRIMARY_COLOR
        else:
            self.save_button.bg_color = (70, 70, 70)

        self.save_button.draw(self.window)
        self.back_button.draw(self.window)

        pygame.display.update()

    def _render_gameplay_tab(self) -> None:
        """
        Render the gameplay settings tab content.

        Draws difficulty selection, preview of birds and pipes, and highlights
        the current selection.

        Returns
        -------
        None
        """
        diff_header = self.font.render("Select Difficulty:", True, WHITE)
        diff_header_rect = diff_header.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 60)
        )
        self.window.blit(diff_header, diff_header_rect)

        self.easy_button.draw(self.window)
        self.medium_button.draw(self.window)
        self.hard_button.draw(self.window)

        curr_text = self.font.render(
            f"Current: {self._get_difficulty_name()}",
            True,
            self._get_difficulty_color(),
        )
        curr_rect = curr_text.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 135)
        )
        self.window.blit(curr_text, curr_rect)

        preview_title = self.font.render("Preview:", True, WHITE)
        preview_rect = preview_title.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 160)
        )
        self.window.blit(preview_title, preview_rect)

        center_x = SCREEN_WIDTH // 2
        bird_y = self.panel_position[1] + 200
        pipe_y = bird_y + 50

        bird_spacing = 60

        self.window.blit(
            self.yellow_bird,
            (
                center_x - bird_spacing - self.yellow_bird.get_width() // 2,
                bird_y,
            ),
        )
        self.window.blit(
            self.blue_bird,
            (center_x - self.blue_bird.get_width() // 2, bird_y),
        )
        self.window.blit(
            self.red_bird,
            (center_x + bird_spacing - self.red_bird.get_width() // 2, bird_y),
        )

        label_y = bird_y + 25
        easy_label = self.font.render("Easy", True, YELLOW)
        medium_label = self.font.render("Medium", True, BLUE)
        hard_label = self.font.render("Hard", True, RED)

        self.window.blit(
            easy_label,
            (center_x - bird_spacing - easy_label.get_width() // 2, label_y),
        )
        self.window.blit(
            medium_label, (center_x - medium_label.get_width() // 2, label_y)
        )
        self.window.blit(
            hard_label,
            (center_x + bird_spacing - hard_label.get_width() // 2, label_y),
        )

        pipe_width = self.green_pipe.get_width() // 5
        pipe_height = self.green_pipe.get_height() // 5

        green_pipe_small = pygame.transform.scale(
            self.green_pipe, (pipe_width, pipe_height)
        )
        red_pipe_small = pygame.transform.scale(
            self.red_pipe, (pipe_width, pipe_height)
        )

        self.window.blit(
            green_pipe_small, (center_x - 60 - pipe_width // 2, pipe_y)
        )
        self.window.blit(
            red_pipe_small, (center_x + 60 - pipe_width // 2, pipe_y)
        )

        pipe_label_y = pipe_y + pipe_height + 5
        green_pipe_label = self.font.render("Easy/Med", True, GREEN)
        red_pipe_label = self.font.render("Hard", True, RED)

        self.window.blit(
            green_pipe_label,
            (center_x - 60 - green_pipe_label.get_width() // 2, pipe_label_y),
        )
        self.window.blit(
            red_pipe_label,
            (center_x + 60 - red_pipe_label.get_width() // 2, pipe_label_y),
        )

        if GAME_SETTINGS.difficulty == EASY:
            pygame.draw.rect(
                self.window,
                YELLOW,
                (
                    center_x
                    - bird_spacing
                    - self.yellow_bird.get_width() // 2
                    - 2,
                    bird_y - 2,
                    self.yellow_bird.get_width() + 4,
                    self.yellow_bird.get_height() + 4,
                ),
                2,
            )
            pygame.draw.rect(
                self.window,
                GREEN,
                (
                    center_x - 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                2,
            )
        elif GAME_SETTINGS.difficulty == MEDIUM:
            pygame.draw.rect(
                self.window,
                BLUE,
                (
                    center_x - self.blue_bird.get_width() // 2 - 2,
                    bird_y - 2,
                    self.blue_bird.get_width() + 4,
                    self.blue_bird.get_height() + 4,
                ),
                2,
            )
            pygame.draw.rect(
                self.window,
                GREEN,
                (
                    center_x - 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                2,
            )
        else:  # HARD
            pygame.draw.rect(
                self.window,
                RED,
                (
                    center_x
                    + bird_spacing
                    - self.red_bird.get_width() // 2
                    - 2,
                    bird_y - 2,
                    self.red_bird.get_width() + 4,
                    self.red_bird.get_height() + 4,
                ),
                2,
            )
            pygame.draw.rect(
                self.window,
                RED,
                (
                    center_x + 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                2,
            )

    def _render_audio_tab(self) -> None:
        """
        Render the audio settings tab content.

        Draws audio settings title, volume label, volume percentage, slider,
        and mute/max indicators.

        Returns
        -------
        None
        """
        audio_title = self.font.render("Audio Settings", True, WHITE)
        audio_rect = audio_title.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 80)
        )
        self.window.blit(audio_title, audio_rect)

        volume_label = self.font.render("Volume:", True, WHITE)
        volume_label_rect = volume_label.get_rect(
            topleft=(self.panel_position[0] + 15, self.panel_position[1] + 120)
        )
        self.window.blit(volume_label, volume_label_rect)

        volume_percent = int(GAME_SETTINGS.volume * 100)
        volume_text = self.font.render(f"{volume_percent}%", True, WHITE)
        volume_text_rect = volume_text.get_rect(
            topright=(
                self.panel_position[0] + self.panel_width - 15,
                self.panel_position[1] + 120,
            )
        )
        self.window.blit(volume_text, volume_text_rect)

        self.volume_slider.y = volume_label_rect.bottom + 10

        self.volume_slider.draw(self.window)

        mute_text = self.font.render("Mute", True, (150, 150, 150))
        mute_rect = mute_text.get_rect(
            topleft=(self.volume_slider.x, self.volume_slider.y + 15)
        )
        self.window.blit(mute_text, mute_rect)

        max_text = self.font.render("Max", True, (150, 150, 150))
        max_rect = max_text.get_rect(
            topright=(
                self.volume_slider.x + self.volume_slider.width,
                self.volume_slider.y + 15,
            )
        )
        self.window.blit(max_text, max_rect)

    def _get_difficulty_name(self) -> str:
        """
        Get the name of the current difficulty setting.

        Returns
        -------
        str
            Name of the current difficulty.
        """
        if GAME_SETTINGS.difficulty == EASY:
            return "Easy"
        elif GAME_SETTINGS.difficulty == MEDIUM:
            return "Medium"
        return "Hard"

    def _get_difficulty_color(self) -> tuple[int, int, int]:
        """
        Get the color associated with the current difficulty.

        Returns
        -------
        tuple of int
            RGB color tuple for the current difficulty.
        """
        if GAME_SETTINGS.difficulty == EASY:
            return YELLOW
        elif GAME_SETTINGS.difficulty == MEDIUM:
            return BLUE
        return RED
