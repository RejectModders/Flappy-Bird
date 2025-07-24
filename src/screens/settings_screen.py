from __future__ import annotations

import math
import random
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
    FONT_MEDIUM,
    FONT_SMALL,
)

if TYPE_CHECKING:
    from typing import Literal

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

        self.panel_width: int = 280
        self.panel_height: int = 350
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            40,
        )

        self.tab_width: int = self.panel_width // 3
        self.tab_height: int = 30

        self.title_font: Font = FONT_MEDIUM
        self.font: Font = FONT_SMALL
        self.active_tab: Literal["introduction", "gameplay", "audio"] = (
            "introduction"
        )

        self.panel_animation: float = 0.0
        self.tab_hover_effects: dict[str, float] = {
            "introduction": 0.0,
            "gameplay": 0.0,
            "audio": 0.0,
        }
        self.bird_animations: dict[str, dict[str, float]] = {
            "yellow": {"y": 0.0, "phase": 0.0},
            "blue": {"y": 0.0, "phase": 2.0},
            "red": {"y": 0.0, "phase": 4.0},
        }
        self.pipe_shine_effect: float = 0.0
        self.preview_fade: float = 0.0
        self.volume_particles: list[dict[str, float]] = []

        self.bird_frames: dict[str, list[Surface]] = {
            "yellow": [
                load_image("yellowbird-upflap.png").convert_alpha(),
                load_image("yellowbird-midflap.png").convert_alpha(),
                load_image("yellowbird-downflap.png").convert_alpha(),
            ],
            "blue": [
                load_image("bluebird-upflap.png").convert_alpha(),
                load_image("bluebird-midflap.png").convert_alpha(),
                load_image("bluebird-downflap.png").convert_alpha(),
            ],
            "red": [
                load_image("redbird-upflap.png").convert_alpha(),
                load_image("redbird-midflap.png").convert_alpha(),
                load_image("redbird-downflap.png").convert_alpha(),
            ],
        }

        intro_color = (50, 50, 50)
        gameplay_color = (50, 50, 50)
        audio_color = (50, 50, 50)

        if self.active_tab == "introduction":
            intro_color = BUTTON_PRIMARY_COLOR
        elif self.active_tab == "gameplay":
            gameplay_color = BUTTON_PRIMARY_COLOR
        elif self.active_tab == "audio":
            audio_color = BUTTON_PRIMARY_COLOR

        self.intro_tab: Button = Button(
            self.panel_position[0],
            self.panel_position[1],
            self.tab_width,
            self.tab_height,
            "Intro",
            bg_color=intro_color,
        )

        self.gameplay_tab: Button = Button(
            self.panel_position[0] + self.tab_width,
            self.panel_position[1],
            self.tab_width,
            self.tab_height,
            "Gameplay",
            bg_color=gameplay_color,
        )

        self.audio_tab: Button = Button(
            self.panel_position[0] + self.tab_width * 2,
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
        self.initial_difficulty: int = GAME_SETTINGS.difficulty
        self.initial_bird_type: str = GAME_SETTINGS.bird_type
        self.initial_pipe_color: str = GAME_SETTINGS.pipe_color
        self.has_changes: bool = False

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

    @override
    def process_event(self, event: Event) -> None:
        """
        Handle pygame events for the settings screen.

        Parameters
        ----------
        event : Event
            The pygame event to process

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

            if self.intro_tab.is_clicked(mouse_pos, mouse_clicked):
                self.active_tab = "introduction"
                self.click_sound.play()

            elif self.gameplay_tab.is_clicked(mouse_pos, mouse_clicked):
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
                    self._update_has_changes()

                elif self.medium_button.is_clicked(mouse_pos, mouse_clicked):
                    GAME_SETTINGS.difficulty = MEDIUM
                    GAME_SETTINGS.bird_type = "blue"
                    GAME_SETTINGS.pipe_color = "green"

                    self.easy_button.bg_color = (70, 70, 70)
                    self.medium_button.bg_color = BLUE
                    self.hard_button.bg_color = (70, 70, 70)

                    self.click_sound.play()
                    self._update_has_changes()

                elif self.hard_button.is_clicked(mouse_pos, mouse_clicked):
                    GAME_SETTINGS.difficulty = HARD
                    GAME_SETTINGS.bird_type = "red"
                    GAME_SETTINGS.pipe_color = "red"

                    self.easy_button.bg_color = (70, 70, 70)
                    self.medium_button.bg_color = (70, 70, 70)
                    self.hard_button.bg_color = RED

                    self.click_sound.play()
                    self._update_has_changes()

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
                self.initial_bird_type = GAME_SETTINGS.bird_type
                self.initial_pipe_color = GAME_SETTINGS.pipe_color
                self.has_changes = False
                self.point_sound.play()

            elif self.back_button.is_clicked(mouse_pos, mouse_clicked):
                if self.has_changes:
                    GAME_SETTINGS.difficulty = self.initial_difficulty
                    GAME_SETTINGS.bird_type = self.initial_bird_type
                    GAME_SETTINGS.pipe_color = self.initial_pipe_color
                    GAME_SETTINGS.set_volume(self.initial_volume)

                    self.easy_button.bg_color = (
                        YELLOW
                        if self.initial_difficulty == EASY
                        else (70, 70, 70)
                    )
                    self.medium_button.bg_color = (
                        BLUE
                        if self.initial_difficulty == MEDIUM
                        else (70, 70, 70)
                    )
                    self.hard_button.bg_color = (
                        RED
                        if self.initial_difficulty == HARD
                        else (70, 70, 70)
                    )

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

    def _update_has_changes(self) -> None:
        """
        Update the has_changes flag based on all settings.

        Checks if any settings have been modified from their initial values.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.has_changes = (
            self.initial_difficulty != GAME_SETTINGS.difficulty
            or self.initial_bird_type != GAME_SETTINGS.bird_type
            or self.initial_pipe_color != GAME_SETTINGS.pipe_color
            or abs(self.initial_volume - GAME_SETTINGS.volume) > 0.001
        )

    def _update_bird_and_pipe_for_difficulty(self) -> None:
        """
        Update bird type and pipe color based on the current difficulty setting.

        Sets appropriate bird type and pipe color combinations for each difficulty level.

        Parameters
        ----------
        None

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
    def process_update(self, dt: float) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the settings screen state and render.

        Parameters
        ----------
        dt : float
            Time delta since last update in seconds

        Returns
        -------
        None
        """
        mouse_pos = pygame.mouse.get_pos()

        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width:
            self.base_x = 0

        if self.active_tab == "gameplay":
            self.gameplay_tab.hover_color = (
                min(BUTTON_PRIMARY_COLOR[0] + 30, 255),
                min(BUTTON_PRIMARY_COLOR[1] + 30, 255),
                min(BUTTON_PRIMARY_COLOR[2] + 30, 255),
            )
            self.audio_tab.hover_color = (
                80,
                80,
                80,
            )
        else:
            self.gameplay_tab.hover_color = (
                80,
                80,
                80,
            )
            self.audio_tab.hover_color = (
                min(BUTTON_PRIMARY_COLOR[0] + 30, 255),
                min(BUTTON_PRIMARY_COLOR[1] + 30, 255),
                min(BUTTON_PRIMARY_COLOR[2] + 30, 255),
            )

        self.intro_tab.update(mouse_pos)
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

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        self.window.blit(self.base, (self.base_x, self.base_y))
        self.window.blit(
            self.base, (self.base_x + self.base_width, self.base_y)
        )

        self.panel_animation = min(1.0, self.panel_animation + 0.1)
        panel_height = int(self.panel_height * self.panel_animation)
        panel_y = (
            self.panel_position[1] + (self.panel_height - panel_height) // 2
        )

        panel_surf = pygame.Surface(
            (self.panel_width, panel_height), pygame.SRCALPHA
        )
        for i in range(panel_height):
            alpha = min(220, int(180 + i * 0.2))
            pygame.draw.line(
                panel_surf, (0, 0, 0, alpha), (0, i), (self.panel_width, i)
            )

        self.window.blit(panel_surf, (self.panel_position[0], panel_y))

        active_tab = self.active_tab
        for tab_name in ["introduction", "gameplay", "audio"]:
            if tab_name == active_tab:
                self.tab_hover_effects[tab_name] = min(
                    1.0, self.tab_hover_effects[tab_name] + 0.1
                )
            else:
                self.tab_hover_effects[tab_name] = max(
                    0.0, self.tab_hover_effects[tab_name] - 0.1
                )

        self.intro_tab.bg_color = self._blend_colors(
            (50, 50, 50),
            BUTTON_PRIMARY_COLOR,
            self.tab_hover_effects["introduction"],
        )
        self.gameplay_tab.bg_color = self._blend_colors(
            (50, 50, 50),
            BUTTON_PRIMARY_COLOR,
            self.tab_hover_effects["gameplay"],
        )
        self.audio_tab.bg_color = self._blend_colors(
            (50, 50, 50), BUTTON_PRIMARY_COLOR, self.tab_hover_effects["audio"]
        )

        self.intro_tab.draw(self.window)
        self.gameplay_tab.draw(self.window)
        self.audio_tab.draw(self.window)

        match self.active_tab:
            case "gameplay":
                self._render_gameplay_tab()
            case "audio":
                self._render_audio_tab()
            case _:
                self._render_introduction_tab()

        if self.has_changes:
            glow = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
            self.save_button.bg_color = self._blend_colors(
                BUTTON_PRIMARY_COLOR,
                (
                    min(BUTTON_PRIMARY_COLOR[0] + 50, 255),
                    min(BUTTON_PRIMARY_COLOR[1] + 50, 255),
                    min(BUTTON_PRIMARY_COLOR[2] + 50, 255),
                ),
                glow,
            )
        else:
            self.save_button.bg_color = (70, 70, 70)

        self.save_button.draw(self.window)
        self.back_button.draw(self.window)

        pygame.display.update()

    def _render_gameplay_tab(self) -> None:
        """
        Render the gameplay settings tab with animations.

        Displays difficulty selection, bird preview animations, and pipe type options.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        time = pygame.time.get_ticks() * 0.001

        shared_y = math.sin(time * 2) * 5

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
        base_bird_y = self.panel_position[1] + 200
        pipe_y = base_bird_y + 50
        bird_spacing = 60

        frame_idx = int((time * 10) % 3)
        for idx, frames in enumerate(self.bird_frames.values()):
            bird = frames[frame_idx]
            offset_x = [-bird_spacing, 0, bird_spacing][idx]
            bird_x = center_x + offset_x - bird.get_width() // 2
            bird_y = base_bird_y + shared_y

            bird_surf = bird.copy()
            self.window.blit(bird_surf, (bird_x, bird_y))

        label_y = base_bird_y + 35
        labels = [("Easy", YELLOW), ("Medium", BLUE), ("Hard", RED)]

        for idx, (text, color) in enumerate(labels):
            offset_x = (idx - 1) * bird_spacing
            label = self.font.render(text, True, color)
            label_rect = label.get_rect(center=(center_x + offset_x, label_y))
            self.window.blit(label, label_rect)

        pipe_width = self.green_pipe.get_width() // 5
        pipe_height = self.green_pipe.get_height() // 5

        for pipe_info in [
            (self.green_pipe, -60, GREEN, "Easy/Med"),
            (self.red_pipe, 60, RED, "Hard"),
        ]:
            pipe_img, offset_x, color, label = pipe_info
            pipe_small = pygame.transform.scale(
                pipe_img, (pipe_width, pipe_height)
            )
            pipe_pos = (center_x + offset_x - pipe_width // 2, pipe_y)
            self.window.blit(pipe_small, pipe_pos)

            label_surf = self.font.render(label, True, color)
            label_rect = label_surf.get_rect(
                center=(center_x + offset_x, pipe_y + pipe_height + 15)
            )
            self.window.blit(label_surf, label_rect)

        self._draw_selection_highlights(
            center_x,
            base_bird_y,
            bird_spacing,
            pipe_width,
            pipe_height,
            pipe_y,
        )

    def _render_audio_tab(self) -> None:
        """
        Render the audio tab with enhanced visual effects.

        Shows volume slider with particle effects and volume indicators.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        time = pygame.time.get_ticks() * 0.001
        title_wave = math.sin(time * 2) * 3

        audio_title = self.font.render("Audio Settings", True, WHITE)
        audio_rect = audio_title.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                self.panel_position[1] + 80 + title_wave,
            )
        )
        self.window.blit(audio_title, audio_rect)

        volume_label = self.font.render("Volume:", True, WHITE)
        volume_label_rect = volume_label.get_rect(
            topleft=(self.panel_position[0] + 15, self.panel_position[1] + 120)
        )
        self.window.blit(volume_label, volume_label_rect)

        volume_percent = int(GAME_SETTINGS.volume * 100)
        color_intensity = (math.sin(time * 4) + 1) * 0.5
        volume_color = self._blend_colors(
            WHITE,
            (100, 255, 100),
            color_intensity if volume_percent > 0 else 0,
        )

        volume_text = self.font.render(
            f"{volume_percent}%", True, volume_color
        )
        volume_text_rect = volume_text.get_rect(
            topright=(
                self.panel_position[0] + self.panel_width - 15,
                self.panel_position[1] + 120,
            )
        )
        self.window.blit(volume_text, volume_text_rect)

        self.volume_slider.y = volume_label_rect.bottom + 10
        self.volume_slider.draw(self.window)

        if GAME_SETTINGS.volume > 0 and len(self.volume_particles) < 20:
            particle_chance = GAME_SETTINGS.volume * 0.3
            if random.random() < particle_chance:
                self.volume_particles.append(
                    {
                        "x": self.volume_slider.x
                        + self.volume_slider.value * self.volume_slider.width,
                        "y": self.volume_slider.y,
                        "vel_y": random.uniform(-2, -1),
                        "alpha": 255,
                        "size": random.randint(2, 4),
                    }
                )

        new_particles = []
        for particle in self.volume_particles:
            particle["y"] += particle["vel_y"]
            particle["alpha"] -= 5

            if particle["alpha"] > 0:
                pygame.draw.circle(
                    self.window,
                    (
                        BUTTON_PRIMARY_COLOR[0],
                        BUTTON_PRIMARY_COLOR[1],
                        BUTTON_PRIMARY_COLOR[2],
                        int(particle["alpha"]),
                    ),
                    (int(particle["x"]), int(particle["y"])),
                    int(particle["size"]),
                )
                new_particles.append(particle)

        self.volume_particles = new_particles

        label_alpha = int(127 + 127 * math.sin(time * 2))

        mute_text = self.font.render("Mute", True, (150, 150, 150))
        mute_rect = mute_text.get_rect(
            topleft=(self.volume_slider.x, self.volume_slider.y + 15)
        )
        mute_text.set_alpha(label_alpha if GAME_SETTINGS.volume == 0 else 150)
        self.window.blit(mute_text, mute_rect)

        max_text = self.font.render("Max", True, (150, 150, 150))
        max_rect = max_text.get_rect(
            topright=(
                self.volume_slider.x + self.volume_slider.width,
                self.volume_slider.y + 15,
            )
        )
        max_text.set_alpha(label_alpha if GAME_SETTINGS.volume == 1 else 150)
        self.window.blit(max_text, max_rect)

    def _draw_selection_highlights(
        self,
        center_x: int,
        bird_y: int,
        bird_spacing: int,
        pipe_width: int,
        pipe_height: int,
        pipe_y: int,
    ) -> None:
        """
        Draw animated selection highlights for current difficulty.

        Parameters
        ----------
        center_x : int
            Center x coordinate for drawing
        bird_y : int
            Y position for bird
        bird_spacing : int
            Spacing between birds
        pipe_width : int
            Width of pipe sprites
        pipe_height : int
            Height of pipe sprites
        pipe_y : int
            Y position for pipes

        Returns
        -------
        None
        """
        time = pygame.time.get_ticks() * 0.001
        glow = (math.sin(time * 4) + 1) * 0.5
        border_width = 2 + int(glow * 2)

        if GAME_SETTINGS.difficulty == EASY:
            color = (YELLOW[0], YELLOW[1], YELLOW[2], int(200 + 55 * glow))
            self._draw_highlight_rect(
                (
                    center_x
                    - bird_spacing
                    - self.yellow_bird.get_width() // 2
                    - 2,
                    bird_y - 2,
                    self.yellow_bird.get_width() + 4,
                    self.yellow_bird.get_height() + 4,
                ),
                color,
                border_width,
            )
            self._draw_highlight_rect(
                (
                    center_x - 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                (GREEN[0], GREEN[1], GREEN[2], int(200 + 55 * glow)),
                border_width,
            )
        elif GAME_SETTINGS.difficulty == MEDIUM:
            color = (BLUE[0], BLUE[1], BLUE[2], int(200 + 55 * glow))
            self._draw_highlight_rect(
                (
                    center_x - self.blue_bird.get_width() // 2 - 2,
                    bird_y - 2,
                    self.blue_bird.get_width() + 4,
                    self.blue_bird.get_height() + 4,
                ),
                color,
                border_width,
            )
            self._draw_highlight_rect(
                (
                    center_x - 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                (GREEN[0], GREEN[1], GREEN[2], int(200 + 55 * glow)),
                border_width,
            )
        else:  # HARD
            color = (RED[0], RED[1], RED[2], int(200 + 55 * glow))
            self._draw_highlight_rect(
                (
                    center_x
                    + bird_spacing
                    - self.red_bird.get_width() // 2
                    - 2,
                    bird_y - 2,
                    self.red_bird.get_width() + 4,
                    self.red_bird.get_height() + 4,
                ),
                color,
                border_width,
            )
            self._draw_highlight_rect(
                (
                    center_x + 60 - pipe_width // 2 - 2,
                    pipe_y - 2,
                    pipe_width + 4,
                    pipe_height + 4,
                ),
                (RED[0], RED[1], RED[2], int(200 + 55 * glow)),
                border_width,
            )

    def _draw_highlight_rect(
        self,
        rect: tuple[int, int, int, int],
        color: tuple[int, int, int, int],
        width: int,
    ) -> None:
        """
        Draw a rectangle with a glowing effect.

        Parameters
        ----------
        rect : tuple[int, int, int, int]
            Rectangle coordinates (x, y, width, height)
        color : tuple[int, int, int, int]
            RGBA color values
        width : int
            Border width

        Returns
        -------
        None
        """
        x, y, w, h = rect
        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            pygame.draw.line(self.window, color, start, end, width)

    def _blend_colors(
        self,
        color1: tuple[int, int, int],
        color2: tuple[int, int, int],
        factor: float,
    ) -> tuple[int, int, int]:
        """
        Blend between two colors based on a factor.

        Parameters
        ----------
        color1 : tuple[int, int, int]
            First RGB color tuple
        color2 : tuple[int, int, int]
            Second RGB color tuple
        factor : float
            Blending factor between 0.0 and 1.0

        Returns
        -------
        tuple[int, int, int]
            The blended RGB color
        """
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)

    def _render_introduction_tab(self) -> None:
        """
        Render the introduction tab content.

        Displays instructions on how to play Flappy Bird.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        title_text = "How to Play"
        title_surface = self.title_font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(
            centerx=self.panel_position[0] + self.panel_width // 2,
            top=self.panel_position[1] + 45,
        )
        self.window.blit(title_surface, title_rect)

        instructions = [
            ("Tap SPACE to flap", BLUE),
            ("Keep the bird flying!", WHITE),
            ("", WHITE),
            ("Avoid Pipes:", GREEN),
            ("• Green pipes - Normal", GREEN),
            ("• Red pipes - Extra challenge", RED),
        ]

        y_offset = title_rect.bottom + 15
        line_spacing = 28

        for line, color in instructions:
            text_surface = (
                self.font.render(line, True, color) if line else None
            )
            if text_surface:
                text_rect = text_surface.get_rect(
                    x=self.panel_position[0] + 25, y=y_offset
                )
                self.window.blit(text_surface, text_rect)
            y_offset += line_spacing

        good_luck = self.font.render("Good Luck!", True, BLUE)
        luck_rect = good_luck.get_rect(
            centerx=self.panel_position[0] + self.panel_width // 2,
            bottom=self.panel_position[1] + self.panel_height - 60,
        )
        self.window.blit(good_luck, luck_rect)

        self.save_button.draw(self.window)
        self.back_button.draw(self.window)

    def _get_difficulty_name(self) -> str:
        """
        Get the current difficulty level name.

        Returns
        -------
        str
            Name of current difficulty level ('Easy', 'Medium', or 'Hard')
        """
        if GAME_SETTINGS.difficulty == EASY:
            return "Easy"
        elif GAME_SETTINGS.difficulty == MEDIUM:
            return "Medium"
        else:
            return "Hard"

    def _get_difficulty_color(self) -> tuple[int, int, int]:
        """
        Get the color associated with current difficulty level.

        Returns
        -------
        tuple[int, int, int]
            RGB color tuple for current difficulty
        """
        if GAME_SETTINGS.difficulty == EASY:
            return YELLOW
        elif GAME_SETTINGS.difficulty == MEDIUM:
            return BLUE
        else:
            return RED
