from typing import Any, override

import pygame
from game_state import State
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, QUIT

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH, load_audio, load_image
from src.screens.base_screen import BaseScreen
from src.settings import GAME_SETTINGS
from src.ui import Button, ScoreDisplay, time_based_background


class GameOverScreen(BaseScreen, state_name="game_over"):
    """
    Game over screen shown after the player loses.

    This screen displays the final score, high score, and provides options
    to retry or return to the main menu.
    """

    @override
    def on_setup(self) -> None:
        """
        Perform initial setup when the state is first loaded into the StateManager.

        Initializes background, base, game over image, score display, buttons,
        sound, and score attributes.

        Returns
        -------
        None
        """
        self.background: pygame.Surface = time_based_background()
        self.base: pygame.Surface = load_image(("base.png")).convert_alpha()
        self.game_over_img: pygame.Surface = load_image("gameover.png")
        self.score_display: ScoreDisplay = ScoreDisplay()

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height

        button_width = 120
        button_height = 40
        button_spacing = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y_start = SCREEN_HEIGHT - self.base_height - 150

        self.green_color = (76, 175, 80)
        self.blue_color = (66, 133, 244)

        self.play_again_button: Button = Button(
            center_x,
            button_y_start,
            button_width,
            button_height,
            "Retry",
            bg_color=self.green_color,
        )
        self.menu_button: Button = Button(
            center_x,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "Main Menu",
            bg_color=self.blue_color,
        )

        self.swoosh_sound: pygame.mixer.Sound = load_audio("swoosh.wav")

        self.score: int = 0
        # Initialize high score in on_setup to ensure it exists before set_score is called
        self.high_score: int = GAME_SETTINGS.high_scores[
            GAME_SETTINGS.difficulty
        ]
        self.is_new_high_score: bool = False
        self.high_score_flash_timer: float = 0
        self.high_score_visible: bool = True
        self.high_score_flash_speed: float = 0.5  # Flash every 0.5 seconds

    @override
    def on_enter(self, prevous_state: State | None = None) -> None:
        """
        Called when the game over screen becomes active.

        Parameters
        ----------
        prevous_state : State or None, optional
            The previous state before transitioning to this one.

        Returns
        -------
        None
        """
        # Get the current high score for the current difficulty
        self.high_score: int = GAME_SETTINGS.high_scores[
            GAME_SETTINGS.difficulty
        ]

    def set_score(self, score: int) -> None:
        """
        Set the score from the completed game.

        Parameters
        ----------
        score : int
            The final score from the game.

        Returns
        -------
        None
        """
        self.score = score

        # Check if this is a new high score
        if score > self.high_score:
            self.is_new_high_score = True
            self.high_score = score
            # Update the high score in game settings
            GAME_SETTINGS.high_scores[GAME_SETTINGS.difficulty] = score
            GAME_SETTINGS.save_settings()  # Save the new high score
        else:
            self.is_new_high_score = False

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the game over screen.

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
            if event.key == K_SPACE:
                self.swoosh_sound.play()
                self.manager.change_state("playing")
            elif event.key == K_ESCAPE:
                self.swoosh_sound.play()
                self.manager.change_state("main_menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

            if self.play_again_button.is_clicked(mouse_pos, mouse_clicked):
                self.swoosh_sound.play()
                self.manager.change_state("playing")
            elif self.menu_button.is_clicked(mouse_pos, mouse_clicked):
                self.swoosh_sound.play()
                self.manager.change_state("main_menu")

    @override
    def process_update(self, dt: float, args: tuple[Any, ...]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the game over screen state and render.

        Parameters
        ----------
        dt : float
            Time delta since last update in seconds.
        args : tuple of Any
            Additional arguments passed from the state manager.

        Returns
        -------
        None
        """
        mouse_pos = pygame.mouse.get_pos()

        self.play_again_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)

        if self.is_new_high_score:
            self.high_score_flash_timer += dt
            if self.high_score_flash_timer >= self.high_score_flash_speed:
                self.high_score_visible = not self.high_score_visible
                self.high_score_flash_timer = 0

        self._render()

    def _render(self) -> None:
        """
        Render the game over screen.

        Draws the background, base, game over image, score, high score,
        and buttons, then updates the display.

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        self.window.blit(self.base, (0, self.base_y))

        game_over_x = (SCREEN_WIDTH - self.game_over_img.get_width()) // 2
        game_over_y = 100
        self.window.blit(self.game_over_img, (game_over_x, game_over_y))

        score_y = game_over_y + self.game_over_img.get_height() + 30
        self.score_display.draw_score(self.window, self.score, y=score_y)

        high_score_y = score_y + 50
        high_score_font = pygame.font.Font(None, 26)

        high_score_text = high_score_font.render(
            f"High Score: {self.high_score}", True, (255, 255, 255)
        )
        high_score_x = (SCREEN_WIDTH - high_score_text.get_width()) // 2
        self.window.blit(high_score_text, (high_score_x, high_score_y))

        if self.is_new_high_score:
            if self.high_score_visible:
                new_high_score_font = pygame.font.Font(None, 36)
                new_high_score_text = new_high_score_font.render(
                    "New High Score!", True, (255, 255, 0)
                )
                new_high_score_x = (
                    SCREEN_WIDTH - new_high_score_text.get_width()
                ) // 2
                new_high_score_y = high_score_y + 40
                self.window.blit(
                    new_high_score_text, (new_high_score_x, new_high_score_y)
                )

        self.play_again_button.draw(self.window)
        self.menu_button.draw(self.window)

        pygame.display.update()
