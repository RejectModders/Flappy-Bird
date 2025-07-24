from __future__ import annotations

from typing import TYPE_CHECKING, override

import pygame
from game_state import State

from src.constants import SCREEN_HEIGHT, load_audio, load_image
from src.ui import time_based_background

if TYPE_CHECKING:
    from typing import Any

    from pygame import Surface
    from pygame.mixer import Sound


class LoadingScreen(State, state_name="loading"):
    """
    Loading screen shown when the game first starts.

    This screen displays a logo and a moving base while assets are loaded.
    """

    def __init__(self) -> None:
        self.background: Surface = time_based_background()
        self.logo: Surface = load_image("message.png")

        self.base: Surface = load_image(("base.png")).convert_alpha()
        self.swoosh_sound: Sound = load_audio("swoosh.wav")

        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

    @override
    def on_enter(self, prevous_state: State | None = None) -> None:
        """
        Called when the loading screen becomes active.

        Parameters
        ----------
        prevous_state : State or None, optional
            The previous state before transitioning to this one.

        Returns
        -------
        None
        """
        self.start_time: int = pygame.time.get_ticks()
        self.duration: int = 2000
        self.played_sound: bool = False

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the loading screen.

        Parameters
        ----------
        event : pygame.event.Event
            Pygame event to process.

        Returns
        -------
        None
        """
        if event.type == pygame.QUIT:
            self.manager.is_running = False

    @override
    def process_update(self, dt: float, *args: Any) -> None:
        """
        Update the loading screen state and render.

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
        current_time = pygame.time.get_ticks()

        if not self.played_sound and current_time - self.start_time > 500:
            self.swoosh_sound.play()
            self.played_sound = True

        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width:
            self.base_x = 0

        if current_time - self.start_time > self.duration:
            self.manager.change_state("main_menu")

        self._render()

    def _render(self) -> None:
        """
        Render the loading screen.

        Draws the background, logo, moving base, and updates the display.

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        logo_x = (self.window.get_width() - self.logo.get_width()) // 2
        logo_y = (
            self.window.get_height()
            - self.logo.get_height()
            - self.base_height
        ) // 2
        self.window.blit(self.logo, (logo_x, logo_y))

        self.window.blit(self.base, (self.base_x, self.base_y))
        self.window.blit(
            self.base, (self.base_x + self.base_width, self.base_y)
        )

        pygame.display.update()
