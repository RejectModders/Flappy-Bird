from __future__ import annotations

from typing import TYPE_CHECKING, override

import pygame
from game_state import State
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from src.constants import SCREEN_HEIGHT, load_audio
from src.objects import Base, Bird, Pipe
from src.settings import GAME_SETTINGS
from src.ui import ScoreDisplay, time_based_background

if TYPE_CHECKING:
    from typing import Any

    from src.screens.game_over_screen import GameOverScreen


class GameScreen(State, state_name="playing"):
    """
    Game screen for Flappy Bird gameplay.

    Manages the main gameplay loop, including rendering, event handling,
    collision detection, and score tracking.
    """

    def __init__(self) -> None:
        self.background: pygame.Surface = time_based_background()
        self.base: Base = Base()
        self.bird: Bird = Bird(50, SCREEN_HEIGHT // 2)
        self.pipes: list[Pipe] = []
        self.score: int = 0
        self.score_display: ScoreDisplay = ScoreDisplay()

        self.point_sound: pygame.mixer.Sound = load_audio("point.wav")
        self.hit_sound: pygame.mixer.Sound = load_audio("hit.wav")
        self.die_sound: pygame.mixer.Sound = load_audio("die.wav")

        self.game_over_screen: GameOverScreen = self.manager.state_map[
            "game_over"
        ]  # pyright:ignore[reportAttributeAccessIssue]

    @override
    def on_enter(self, prevous_state: State | None = None) -> None:
        """
        Called when the game screen becomes active.

        Parameters
        ----------
        prevous_state : State or None, optional
            The previous state before transitioning to this one.

        Returns
        -------
        None
        """
        self.bird.reset(50, SCREEN_HEIGHT // 2)
        self.pipes.clear()
        self.score = 0
        self.game_active: bool = True
        self.last_pipe_time: int = pygame.time.get_ticks()
        self.sound_played: bool = False

    @override
    def process_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for the game screen.

        Parameters
        ----------
        event : pygame.event.Event
            The pygame event to process.

        Returns
        -------
        None
        """
        if event.type == QUIT:
            self.manager.is_running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and self.game_active:
                self.bird.jump()
            elif event.key == K_ESCAPE:
                self.manager.change_state("main_menu")
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.game_active:
                self.bird.jump()

    @override
    def process_update(self, dt: float, *args: Any) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Update the game screen state and render.

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
        if not self.game_active:
            self._render()
            return

        self.bird.update()

        current_time = pygame.time.get_ticks()
        if (
            current_time - self.last_pipe_time
            > GAME_SETTINGS.get_pipe_frequency()
        ):
            self.pipes.append(Pipe())
            self.last_pipe_time = current_time

        pipes_to_remove: list[Pipe] = []
        for pipe in self.pipes:
            if not pipe.update():
                pipes_to_remove.append(pipe)

            if (
                not pipe.passed
                and pipe.x + pipe.pipe_top.get_width()
                < self.bird.x - self.bird.rect.width / 2
            ):
                pipe.passed = True
                self.score += 1
                self.point_sound.play()

        for pipe in pipes_to_remove:
            self.pipes.remove(pipe)

        self.base.update()

        if self.check_collision():
            self.game_active = False
            if not self.sound_played:
                self.hit_sound.play()
                pygame.time.delay(500)
                self.die_sound.play()
                self.sound_played = True

            GAME_SETTINGS.update_high_score(self.score)

            self.game_over_screen.set_score(self.score)

            pygame.time.delay(1000)
            self.manager.change_state("game_over")

        self._render()

    def check_collision(self) -> bool:
        """
        Check for collisions between the bird and obstacles.

        Returns
        -------
        bool
            True if a collision is detected, False otherwise.
        """
        if self.base.check_collision(self.bird):
            return True

        for pipe in self.pipes:
            if abs(pipe.x - self.bird.x) < 100:
                if pipe.check_collision(self.bird):
                    return True

        return False

    def _render(self) -> None:
        """
        Render the game screen.

        Draws the background, pipes, base, bird, score, and updates the display.

        Returns
        -------
        None
        """
        self.window.blit(self.background, (0, 0))

        for pipe in self.pipes:
            pipe.draw(self.window)

        self.base.draw(self.window)

        self.bird.draw(self.window)

        self.score_display.draw_score(self.window, self.score)

        pygame.display.update()
