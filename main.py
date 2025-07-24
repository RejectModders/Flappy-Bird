import sys

import pygame
from game_state import StateManager

from src.constants import FPS, resource_path
from src.screens.game_over_screen import GameOverScreen
from src.screens.game_screen import GameScreen
from src.screens.loading_screen import LoadingScreen
from src.screens.main_menu_screen import MainMenuScreen
from src.screens.settings_screen import SettingsScreen
from src.screens.stats_screen import StatsScreen


def main() -> None:
    """
    Main function to run the Flappy Bird game.

    Runs the main game loop, initializes pygame, sets up the display,
    loads game states, and handles event processing and state updates.

    Returns
    -------
    None
    """
    pygame.init()
    pygame.mixer.init()

    pygame.display.set_caption("Flappy Bird")
    icon = pygame.image.load(resource_path("assets/favicon.ico"))
    pygame.display.set_icon(icon)

    screen = pygame.display.set_mode((288, 512))

    state_manager = StateManager(screen)

    state_manager.load_states(
        LoadingScreen,
        MainMenuScreen,
        GameScreen,
        GameOverScreen,
        SettingsScreen,
        StatsScreen,
    )

    state_manager.change_state("loading")

    if state_manager.current_state is None:
        raise RuntimeError("State not set.")

    clock = pygame.time.Clock()

    while state_manager.is_running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            state_manager.current_state.process_event(event)

        state_manager.current_state.process_update(dt)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
