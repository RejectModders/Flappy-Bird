import sys

import pygame
from pygame.locals import *

from src.constants import *
from src.objects import Base, Bird, Pipe
from src.ui import (
    GameOverScreen,
    LoadingScreen,
    MainMenu,
    ScoreDisplay,
    SettingsScreen,
    StatsScreen,
)


def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()

    # Set up display
    pygame.display.set_caption("Flappy Bird")
    icon = pygame.image.load("assets/favicon.ico")
    pygame.display.set_icon(icon)

    # Load sounds
    point_sound = load_audio("point.wav")
    hit_sound = load_audio("hit.wav")
    die_sound = load_audio("die.wav")

    # Game objects
    bird = Bird(50, SCREEN_HEIGHT // 2)
    base = Base()
    pipes = []
    score = 0
    last_pipe_time = pygame.time.get_ticks()

    # UI elements
    loading_screen = LoadingScreen()
    main_menu = MainMenu()
    settings_screen = SettingsScreen()
    score_display = ScoreDisplay()
    game_over_screen = GameOverScreen()
    stats_screen = StatsScreen()

    # Game state
    game_state = LOADING

    # Game loop
    running = True
    while running:
        # Handle click events for this frame
        mouse_clicked = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE and game_state == PLAYING:
                    bird.jump()
                elif event.key == K_ESCAPE:
                    if game_state == PLAYING:
                        # Return to main menu when Escape is pressed during gameplay
                        game_state = MAIN_MENU
                    elif game_state == SETTINGS:
                        # Return to main menu when Escape is pressed in settings
                        game_state = MAIN_MENU

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_clicked = True
                    # Allow jumping with mouse click during gameplay
                    if game_state == PLAYING:
                        bird.jump()

        # Update game based on current state
        if game_state == LOADING:
            loading_screen.update()
            if loading_screen.is_done:
                game_state = MAIN_MENU

        elif game_state == MAIN_MENU:
            new_state = main_menu.update(mouse_pos, mouse_clicked)
            if new_state != game_state:
                game_state = new_state
                # Reset game when transitioning from menu to game
                if new_state == PLAYING:
                    bird.reset(50, SCREEN_HEIGHT // 2)
                    pipes.clear()
                    score = 0
                    last_pipe_time = pygame.time.get_ticks()

        elif game_state == SETTINGS:
            new_state = settings_screen.update(mouse_pos, mouse_clicked)
            if new_state != game_state:
                game_state = new_state
                # Update bird in menu to match new settings
                main_menu = (
                    MainMenu()
                )  # Refresh menu to show correct bird color

        elif game_state == PLAYING:
            # Update bird
            bird.update()

            # Update base
            base.update()

            # Generate pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe_time > GAME_SETTINGS.get_pipe_frequency():
                pipes.append(Pipe(SCREEN_WIDTH))
                last_pipe_time = time_now

            # Update pipes
            for pipe in pipes[:]:
                pipe.update()

                # Check if bird passed a pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                    point_sound.play()

                # Remove pipes that went off screen
                if pipe.x < -pipe.top_pipe.get_width():
                    pipes.remove(pipe)

            # Check collisions with pipes
            for pipe in pipes:
                if bird.rect.colliderect(
                    pipe.top_rect
                ) or bird.rect.colliderect(pipe.bottom_rect):
                    hit_sound.play()
                    game_state = GAME_OVER
                    # Check for high score
                    game_over_screen.update_high_score(score)

            # Check collision with ground or ceiling
            if bird.y > SCREEN_HEIGHT - base.image.get_height() or bird.y < 0:
                die_sound.play()
                game_state = GAME_OVER
                # Check for high score
                game_over_screen.update_high_score(score)

        elif game_state == GAME_OVER:
            new_state = game_over_screen.update(mouse_pos, mouse_clicked)
            if new_state != game_state:
                # Reset game when leaving game over screen
                bird.reset(50, SCREEN_HEIGHT // 2)
                pipes.clear()
                score = 0
                last_pipe_time = pygame.time.get_ticks()
                game_state = new_state

        elif game_state == STATS:
            new_state = stats_screen.update(mouse_pos, mouse_clicked)
            if new_state != game_state:
                game_state = new_state

        # Drawing
        if game_state == LOADING:
            loading_screen.draw(SCREEN)

        elif game_state == MAIN_MENU:
            main_menu.draw(SCREEN)

        elif game_state == SETTINGS:
            settings_screen.draw(SCREEN)

        elif game_state == PLAYING:
            # Draw background
            SCREEN.blit(load_image("background-day.png"), (0, 0))

            # Draw pipes
            for pipe in pipes:
                pipe.draw(SCREEN)

            # Draw base
            base.draw(SCREEN)

            # Draw bird
            bird.draw(SCREEN)

            # Draw score
            score_display.draw(SCREEN, score)

        elif game_state == GAME_OVER:
            # Draw background
            SCREEN.blit(load_image("background-day.png"), (0, 0))

            # Draw pipes
            for pipe in pipes:
                pipe.draw(SCREEN)

            # Draw base
            base.draw(SCREEN)

            # Draw bird
            bird.draw(SCREEN)

            # Draw game over screen
            game_over_screen.draw(SCREEN, score)

        elif game_state == STATS:
            # Draw background
            SCREEN.blit(load_image("background-day.png"), (0, 0))

            # Draw stats screen
            stats_screen.draw(SCREEN)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
