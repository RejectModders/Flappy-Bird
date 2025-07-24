from typing import Any, override

import pygame
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
from src.screens.base_screen import BaseScreen
from src.settings import GAME_SETTINGS
from src.ui import Button, time_based_background
from src.ui_constants import (
    BUTTON_SECONDARY_COLOR,
    BUTTON_TEXT_COLOR,
    FONT_LARGE,
    FONT_SMALL,
)


class StatsScreen(BaseScreen, state_name="stats"):
    """
    Statistics screen for displaying high scores and achievements.

    Shows high scores for each difficulty and achievement status.
    """

    @override
    def on_setup(self) -> None:
        """
        Perform initial setup when the state is first loaded into the StateManager.

        Initializes background, base, panel properties, fonts, back button, and sound.

        Returns
        -------
        None
        """
        self.background: pygame.Surface = time_based_background()
        self.base: pygame.Surface = load_image(("base.png")).convert_alpha()

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        self.panel_width: int = 250
        self.panel_height: int = 300
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            70,
        )

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

        self.title_font: pygame.font.Font = FONT_LARGE
        self.font: pygame.font.Font = FONT_SMALL
        self.small_font: pygame.font.Font = pygame.font.Font(None, 20)

        self.swoosh_sound: pygame.mixer.Sound = load_audio("swoosh.wav")

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the stats screen.

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
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            self.manager.change_state("main_menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(mouse_pos, True):
                self.swoosh_sound.play()
                self.manager.change_state("main_menu")

    @override
    def process_update(self, dt: float, args: tuple[Any, ...]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the stats screen state and render.

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

        panel_surf = pygame.Surface(
            (self.panel_width, self.panel_height), pygame.SRCALPHA
        )
        panel_surf.fill((0, 0, 0, 220))
        pygame.draw.rect(
            panel_surf, WHITE, (0, 0, self.panel_width, self.panel_height), 2
        )
        self.window.blit(panel_surf, self.panel_position)

        title = self.title_font.render("High Scores", True, WHITE)
        title_rect = title.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 25)
        )
        self.window.blit(title, title_rect)

        y_pos = self.panel_position[1] + 70
        spacing = 70

        self.draw_difficulty_stats("Easy", EASY, YELLOW, y_pos)
        self.draw_difficulty_stats("Medium", MEDIUM, BLUE, y_pos + spacing)
        self.draw_difficulty_stats("Hard", HARD, RED, y_pos + spacing * 2)

        self.back_button.draw(self.window)

        pygame.display.update()

    def draw_difficulty_stats(
        self,
        name: str,
        difficulty: int,
        color: tuple[int, int, int],
        y_pos: int,
    ) -> None:
        """
        Draw stats and achievement for a specific difficulty level.

        Parameters
        ----------
        name : str
            Name of the difficulty level.
        difficulty : int
            Difficulty constant (EASY, MEDIUM, or HARD).
        color : tuple[int, int, int]
            RGB color for the difficulty name.
        y_pos : int
            Vertical position to start drawing.

        Returns
        -------
        None
        """
        diff_text = self.font.render(name, True, color)
        self.window.blit(diff_text, (self.panel_position[0] + 20, y_pos))

        score = GAME_SETTINGS.high_scores[difficulty]
        score_text = self.font.render(f"High Score: {score}", True, WHITE)
        self.window.blit(score_text, (self.panel_position[0] + 20, y_pos + 25))

        if score > 100:
            achievement_status = "Master"
            achievement_color = (255, 215, 0)  # Gold
        elif score > 50:
            achievement_status = "Expert"
            achievement_color = (255, 215, 0)  # Gold
        elif score > 20:
            achievement_status = "Skilled"
            achievement_color = (192, 192, 192)  # Silver
        elif score > 0:
            achievement_status = "Beginner"
            achievement_color = (184, 115, 51)  # Bronze
        else:
            achievement_status = "No Record"
            achievement_color = (150, 150, 150)  # Gray

        if achievement_status:
            achievement_text = self.small_font.render(
                achievement_status, True, achievement_color
            )
            achievement_x = (
                self.panel_position[0]
                + self.panel_width
                - achievement_text.get_width()
                - 20
            )
            achievement_y = y_pos + 25
            self.window.blit(achievement_text, (achievement_x, achievement_y))
