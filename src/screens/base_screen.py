from typing import Any, override

import pygame
from game_state import State


class BaseScreen(State):
    """
    Base class for all game screens using the game-state package.

    Parameters
    ----------
    manager : Any
        The manager object that handles this screen.
    window : pygame.Surface
        The pygame surface to render on.
    """

    def __init__(self, manager: Any, window: pygame.Surface) -> None:
        """
        Initialize the base screen.

        Parameters
        ----------
        manager : Any
            The manager object that handles this screen.
        window : pygame.Surface
            The pygame surface to render on.
        """
        super().__init__()
        self.manager: Any = manager
        self.window: pygame.Surface = window

    @override
    def on_setup(self) -> None:
        """
        Called when this state is first loaded into the StateManager.
        """

        pass

    @override
    def on_enter(self, prevous_state: State | None = None) -> None:
        """
        Called when this state becomes active.

        Parameters
        ----------
        prevous_state : State or None, optional
            The previous state before transitioning to this one.
        """

        pass

    def on_exit(self) -> None:
        """
        Called when this state is no longer active.
        """

        pass

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the screen.

        Parameters
        ----------
        event : pygame.event.Event
            Pygame event to process.
        """

        pass

    @override
    def process_update(self, *args: Any) -> None:
        """
        Update the screen state and render.

        Parameters
        ----------
        *args : Any
            Arguments passed from the State base class (typically dt: float).
        """

        pass
