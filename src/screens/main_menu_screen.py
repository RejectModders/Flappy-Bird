from __future__ import annotations

import math
from typing import TYPE_CHECKING, override

import pygame
from game_state import State
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH, load_audio, load_image
from src.screens.base_screen import BaseScreen
from src.settings import GAME_SETTINGS
from src.ui import Button, time_based_background
from src.ui_constants import BUTTON_PRIMARY_COLOR, BUTTON_SECONDARY_COLOR

if TYPE_CHECKING:
    from typing import Any


class MainMenuScreen(BaseScreen, state_name="main_menu"):
    """
    Main menu screen for the game.

    Provides options to play, access settings, and view stats.

    Attributes
    ----------
    background : pygame.Surface
        The background surface for the main menu.
    logo : pygame.Surface
        The logo image displayed on the main menu.
    base : pygame.Surface
        The base image for the main menu.
    bird_frames : dict of str to list of pygame.Surface
        Animation frames for each bird type.
    current_frame : int
        Current animation frame index.
    animation_speed : float
        Speed of bird animation.
    animation_time : float
        Time accumulator for animation.
    bird_y : float
        Vertical position of the bird.
    bird_oscillation : float
        Oscillation value for bird movement.
    oscillation_speed : float
        Speed of bird oscillation.
    oscillation_range : float
        Range of bird oscillation.
    base_width : int
        Width of the base image.
    base_height : int
        Height of the base image.
    base_y : int
        Vertical position of the base.
    base_x : int
        Horizontal position of the base.
    base_scroll_speed : int
        Speed at which the base scrolls.
    play_button : Button
        Button to start the game.
    stats_button : Button
        Button to view stats.
    settings_button : Button
        Button to access settings.
    swoosh_sound : pygame.mixer.Sound
        Sound effect for button clicks.
    point_sound : pygame.mixer.Sound
        Sound effect for points.
    """

    @override
    def on_setup(self) -> None:
        """
        Perform initial setup when the state is first loaded into the StateManager.

        Initializes background, logo, base, bird animation frames, animation properties,
        base properties, button setup, and loads sounds.

        Returns
        -------
        None
        """
        self.background: pygame.Surface = time_based_background()
        self.logo: pygame.Surface = load_image(("message.png")).convert_alpha()
        self.base: pygame.Surface = load_image(("base.png")).convert_alpha()

        self.bird_frames: dict[str, list[pygame.Surface]] = {
            "yellow": [
                load_image((f"yellowbird-{frame}flap.png")).convert_alpha()
                for frame in ["down", "mid", "up"]
            ],
            "blue": [
                load_image((f"bluebird-{frame}flap.png")).convert_alpha()
                for frame in ["down", "mid", "up"]
            ],
            "red": [
                load_image((f"redbird-{frame}flap.png")).convert_alpha()
                for frame in ["down", "mid", "up"]
            ],
        }

        self.current_frame: int = 0
        self.animation_speed: float = 0.2
        self.animation_time: float = 0.0
        self.bird_y: float = 285

        self.bird_oscillation: float = 0.0
        self.oscillation_speed: float = 2.0
        self.oscillation_range: float = 20.0

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        button_width = 120
        button_height = 40
        button_spacing = 5
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y_start = 360

        self.play_button: Button = Button(
            center_x,
            button_y_start,
            button_width,
            button_height,
            "Play",
            bg_color=BUTTON_PRIMARY_COLOR,
        )

        self.stats_button: Button = Button(
            center_x,
            button_y_start + button_height + button_spacing,
            button_width,
            button_height,
            "Stats",
            bg_color=BUTTON_SECONDARY_COLOR,
        )

        self.settings_button: Button = Button(
            center_x,
            button_y_start + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "Settings",
            bg_color=BUTTON_SECONDARY_COLOR,
        )

        # Load sounds
        self.swoosh_sound: pygame.mixer.Sound = load_audio("swoosh.wav")
        self.point_sound: pygame.mixer.Sound = load_audio("point.wav")

    @override
    def on_enter(self, prevous_state: State | None = None) -> None:
        """
        Called when the main menu becomes active.

        Parameters
        ----------
        prevous_state : State or None, optional
            The previous state before transitioning to this one.

        Returns
        -------
        None
        """
        self.animation_time = 0.0
        self.click_occurred: bool = False

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the main menu.

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
            self.manager.is_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

            # Handle button clicks only when mouse is actually clicked
            if self.play_button.is_clicked(mouse_pos, mouse_clicked):
                self.swoosh_sound.play()
                self.manager.change_state("playing")
            elif self.settings_button.is_clicked(mouse_pos, mouse_clicked):
                self.swoosh_sound.play()
                self.manager.change_state("settings")
            elif self.stats_button.is_clicked(mouse_pos, mouse_clicked):
                self.swoosh_sound.play()
                self.manager.change_state("stats")

    @override
    def process_update(self, dt: float, args: tuple[Any, ...]) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the main menu state and render.

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

        # Update buttons
        self.play_button.update(mouse_pos)
        self.settings_button.update(mouse_pos)
        self.stats_button.update(mouse_pos)

        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % 3

        self.bird_oscillation += dt * self.oscillation_speed
        bird_offset = int(
            abs(math.sin(self.bird_oscillation)) * self.oscillation_range
        )

        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width:
            self.base_x = 0

        self._render(bird_offset)

    def _render(self, bird_offset: int) -> None:
        """
        Render the main menu screen.

        Parameters
        ----------
        bird_offset : int
            Vertical offset for the bird's position.

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        logo_x = (self.window.get_width() - self.logo.get_width()) // 2
        logo_y = 50
        self.window.blit(self.logo, (logo_x, logo_y))

        bird_type = GAME_SETTINGS.bird_type

        bird_frame = self.bird_frames[bird_type][self.current_frame]
        bird_x = (self.window.get_width() - bird_frame.get_width()) // 2
        self.window.blit(bird_frame, (bird_x, self.bird_y - bird_offset))

        self.window.blit(self.base, (self.base_x, self.base_y))
        self.window.blit(
            self.base, (self.base_x + self.base_width, self.base_y)
        )

        self.play_button.draw(self.window)
        self.stats_button.draw(self.window)
        self.settings_button.draw(self.window)

        pygame.display.update()
