from __future__ import annotations

import math
from typing import TYPE_CHECKING, override

import pygame
from game_state import State
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from src.constants import (
    BLUE,
    EASY,
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
from src.ui import Button, time_based_background
from src.ui_constants import (
    BUTTON_SECONDARY_COLOR,
    BUTTON_TEXT_COLOR,
    FONT_LARGE,
    FONT_SMALL,
)

if TYPE_CHECKING:
    from pygame import Surface
    from pygame.event import Event
    from pygame.font import Font
    from pygame.mixer import Sound


class StatsScreen(State, state_name="stats"):
    """
    Statistics screen for displaying high scores and achievements.

    Shows high scores for each difficulty and achievement status.
    """

    def __init__(self) -> None:
        self.background: Surface = time_based_background()
        self.base: Surface = load_image(("base.png")).convert_alpha()

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        self.panel_width: int = 300
        self.panel_height: int = 300
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            70,
        )

        self.panel_animation: float = 0.0
        self.score_animations: dict[str, float] = {
            "easy": 0.0,
            "medium": 0.0,
            "hard": 0.0,
        }
        self.achievement_colors: dict[str, tuple[int, int, int]] = {
            "Master": (255, 215, 0),  # Gold
            "Expert": (255, 215, 0),  # Gold
            "Skilled": (192, 192, 192),  # Silver
            "Beginner": (184, 115, 51),  # Bronze
            "No Record": (150, 150, 150),  # Gray
        }

        button_width = 120
        button_height = 40
        self.back_button: Button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT - self.base_height - 60,
            button_width,
            button_height,
            "Back",
            BUTTON_TEXT_COLOR,
            BUTTON_SECONDARY_COLOR,
        )

        self.title_font: Font = FONT_LARGE
        self.font: Font = FONT_SMALL
        self.small_font: Font = pygame.font.Font(None, 20)

        self.swoosh_sound: Sound = load_audio("swoosh.wav")

    @override
    def process_event(self, event: Event) -> None:
        """
        Handle pygame events for the stats screen.

        Parameters
        ----------
        event : Event
            Pygame event to process

        Returns
        -------
        None
        """
        mouse_pos = pygame.mouse.get_pos()

        if event.type == QUIT:
            self.manager.is_running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            self.manager.change_state("main_menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(mouse_pos, True):
                self.swoosh_sound.play()
                self.manager.change_state("main_menu")

    @override
    def process_update(self, dt: float) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the stats screen state and render.

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

        self.back_button.update(mouse_pos)

        self._render()

    def _render(self) -> None:
        """
        Render the stats screen.

        Draws the background, base, stats panel, high scores, achievements,
        and back button, then updates the display.

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

        title = self.title_font.render("High Scores", True, WHITE)
        glow = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
        glow_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        glow_size = int(2 + glow * 2)
        pygame.draw.rect(
            glow_surf,
            (255, 255, 255, 50),
            title.get_rect().inflate(glow_size * 2, glow_size * 2),
        )

        title_rect = title.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 25)
        )
        self.window.blit(
            glow_surf, glow_surf.get_rect(center=title_rect.center)
        )
        self.window.blit(title, title_rect)

        y_pos = self.panel_position[1] + 70
        spacing = 70

        self.draw_difficulty_stats("Easy", EASY, YELLOW, y_pos, "easy")
        self.draw_difficulty_stats(
            "Medium", MEDIUM, BLUE, y_pos + spacing, "medium"
        )
        self.draw_difficulty_stats(
            "Hard", HARD, RED, y_pos + spacing * 2, "hard"
        )

        self.back_button.draw(self.window)
        pygame.display.update()

    def draw_difficulty_stats(
        self,
        name: str,
        difficulty: int,
        color: tuple[int, int, int],
        y_pos: int,
        anim_key: str,
    ) -> None:
        """
        Draw stats and achievement for a specific difficulty level.

        Parameters
        ----------
        name : str
            Name of the difficulty level
        difficulty : int
            Difficulty constant (EASY, MEDIUM, or HARD)
        color : tuple[int, int, int]
            RGB color for the difficulty name
        y_pos : int
            Vertical position to start drawing
        anim_key : str
            Key for the score animation dictionary

        Returns
        -------
        None
        """
        self.score_animations[anim_key] = min(
            1.0, self.score_animations[anim_key] + 0.1
        )

        hover_factor = math.sin(pygame.time.get_ticks() * 0.003) * 0.1 + 0.9
        diff_color = tuple(int(c * hover_factor) for c in color)
        diff_text = self.font.render(name, True, diff_color)
        self.window.blit(diff_text, (self.panel_position[0] + 20, y_pos))

        score = GAME_SETTINGS.high_scores[difficulty]

        if score > 100:
            achievement_status = "Master"
        elif score > 50:
            achievement_status = "Expert"
        elif score > 20:
            achievement_status = "Skilled"
        elif score > 0:
            achievement_status = "Beginner"
        else:
            achievement_status = "No Record"

        displayed_score = int(score * self.score_animations[anim_key])
        score_text = self.font.render(
            f"High Score: {displayed_score}", True, WHITE
        )
        score_pos = (self.panel_position[0] + 20, y_pos + 25)
        self.window.blit(score_text, score_pos)

        achievement_color = self.achievement_colors[achievement_status]
        glow = (
            math.sin(pygame.time.get_ticks() * 0.003 + hash(name) * 0.5) + 1
        ) * 0.5
        achievement_text = self.small_font.render(
            achievement_status, True, achievement_color
        )

        glow_surf = pygame.Surface(
            achievement_text.get_size(), pygame.SRCALPHA
        )
        glow_color = (*achievement_color, int(50 * glow))
        pygame.draw.rect(
            glow_surf, glow_color, achievement_text.get_rect().inflate(4, 4)
        )

        achievement_x = (
            self.panel_position[0]
            + self.panel_width
            - achievement_text.get_width()
            - 20
        )
        achievement_y = y_pos + 25

        self.window.blit(glow_surf, (achievement_x - 2, achievement_y - 2))
        self.window.blit(achievement_text, (achievement_x, achievement_y))

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
            First RGB color to blend
        color2 : tuple[int, int, int]
            Second RGB color to blend
        factor : float
            Blend factor between 0.0 and 1.0

        Returns
        -------
        tuple[int, int, int]
            Resulting blended RGB color
        """
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)
