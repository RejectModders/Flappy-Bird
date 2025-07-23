import datetime

import pygame

from src.constants import (
    BLACK,
    BLUE,
    EASY,
    GAME_OVER,
    GAME_SETTINGS,
    GREEN,
    HARD,
    MAIN_MENU,
    MEDIUM,
    PLAYING,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SETTINGS,
    STATS,
    WHITE,
    YELLOW,
    load_audio,
    load_image,
)


def time_based_background() -> pygame.Surface:
    """Returns background based on local time (day or night)."""
    current_hour = datetime.datetime.now().hour
    # Day time is typically between 6 AM and 6 PM (6-18)
    is_daytime = 6 <= current_hour < 18
    return load_image(f"background-{'day' if is_daytime else 'night'}.png")


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        text_color: tuple[int, int, int] = WHITE,
        bg_color: tuple[int, int, int] = GREEN,
        hover_color: tuple[int, int, int] | None = None,
    ) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.text_color: tuple[int, int, int] = text_color
        self.bg_color: tuple[int, int, int] = bg_color
        self.hover_color: tuple[int, int, int] = hover_color or (
            min(bg_color[0] + 30, 255),
            min(bg_color[1] + 30, 255),
            min(bg_color[2] + 30, 255),
        )
        self.is_hovered: bool = False
        self.font: pygame.font.Font = pygame.font.Font(None, 32)

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw button background
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Button border

        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos: tuple[int, int], click: bool) -> bool:
        return self.rect.collidepoint(mouse_pos) and click


class LoadingScreen:
    def __init__(self) -> None:
        self.background: pygame.Surface = time_based_background()
        self.logo: pygame.Surface = load_image("message.png")
        self.base: pygame.Surface = load_image("base.png")
        self.start_time: int = pygame.time.get_ticks()
        self.duration: int = 3000
        self.is_done: bool = False
        self.swoosh_sound: pygame.mixer.Sound = load_audio("swoosh.wav")
        self.played_sound: bool = False

        # Base animation properties
        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        # Create a bird for loading animation
        self.bird_frames: list[pygame.Surface] = [
            load_image("yellowbird-downflap.png"),
            load_image("yellowbird-midflap.png"),
            load_image("yellowbird-upflap.png"),
        ]
        self.bird_index: int = 0
        self.bird_frame_count: int = 0
        self.bird_position: list[int] = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
        self.bird_movement: int = 1  # Subtle up and down movement
        self.bird_direction: int = 1  # 1 for up, -1 for down

        # Loading progress dots
        self.dot_radius: int = 5
        self.dot_count: int = 3
        self.dot_spacing: int = 15
        self.dot_animation_timer: int = 0
        self.active_dots: int = 0

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.is_done = True

        # Play sound at appropriate time
        if (
            not self.played_sound
            and current_time - self.start_time > self.duration * 0.4
        ):
            self.swoosh_sound.play()
            self.played_sound = True

        # Animate base
        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width + SCREEN_WIDTH:
            self.base_x = 0

        # Animate bird
        self.bird_frame_count += 1
        if self.bird_frame_count > 5:
            self.bird_frame_count = 0
            self.bird_index = (self.bird_index + 1) % 3

        # Make bird bob up and down slightly
        self.bird_position[1] += self.bird_direction * self.bird_movement
        if self.bird_position[1] > SCREEN_HEIGHT // 2 + 10:
            self.bird_direction = -1
        elif self.bird_position[1] < SCREEN_HEIGHT // 2 - 10:
            self.bird_direction = 1

        # Animate loading dots
        self.dot_animation_timer += 1
        if self.dot_animation_timer > 15:  # Update dots every 15 frames
            self.dot_animation_timer = 0
            self.active_dots = (self.active_dots + 1) % (self.dot_count + 1)
            if (
                self.active_dots == 0
            ):  # If we've cycled through all dots, add a brief pause
                self.active_dots = 1

    def draw(self, surface: pygame.Surface) -> None:
        # Draw background
        surface.blit(self.background, (0, 0))

        # Calculate fade-in effect (0 to 255)
        current_time = pygame.time.get_ticks()
        progress = min(
            (current_time - self.start_time) / (self.duration * 0.6), 1.0
        )
        alpha = int(255 * progress)

        # Create a temporary surface for the logo with transparency
        logo_with_alpha = self.logo.copy()
        logo_with_alpha.set_alpha(alpha)

        # Draw logo centered with slight bounce effect
        offset = 0
        if (
            progress > 0.8
        ):  # Add slight bounce when logo is almost fully visible
            bounce_progress = (progress - 0.8) * 5  # Scale to 0-1 range
            bounce_amount = 5 * (1 - (bounce_progress * 2 - 1) ** 2)
            offset = max(0, int(bounce_amount))

        logo_rect = self.logo.get_rect(
            center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 3) - offset)
        )
        surface.blit(logo_with_alpha, logo_rect)

        # Draw animated bird if logo is visible enough
        if alpha > 100:
            bird_alpha = min(255, int((alpha - 100) * 1.5))
            bird_surf = self.bird_frames[self.bird_index].copy()
            bird_surf.set_alpha(bird_alpha)
            bird_rect = bird_surf.get_rect(center=self.bird_position)
            surface.blit(bird_surf, bird_rect)

        # Draw loading text and dots if logo is visible enough
        if alpha > 150:
            font = pygame.font.Font(None, 28)
            text_alpha = min(255, int((alpha - 150) * 2))

            # Draw "Loading" text
            loading_text = font.render("Loading", True, (255, 255, 255))
            loading_text.set_alpha(text_alpha)
            text_rect = loading_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            )
            surface.blit(loading_text, text_rect)

            # Draw animated dots
            dot_start_x = text_rect.right + 10
            dot_y = text_rect.centery

            for i in range(self.active_dots):
                dot_x = dot_start_x + i * self.dot_spacing
                dot_surf = pygame.Surface(
                    (self.dot_radius * 2, self.dot_radius * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    dot_surf,
                    (255, 255, 255, text_alpha),
                    (self.dot_radius, self.dot_radius),
                    self.dot_radius,
                )
                surface.blit(dot_surf, (dot_x, dot_y - self.dot_radius))

        # Draw base - first copy
        surface.blit(self.base, (self.base_x, self.base_y))

        # Draw base - second copy for continuous scrolling
        surface.blit(self.base, (self.base_x + self.base_width, self.base_y))


class MainMenu:
    def __init__(self) -> None:
        self.background: pygame.Surface = time_based_background()
        self.base: pygame.Surface = load_image("base.png")
        self.logo: pygame.Surface = load_image("message.png")

        # Base animation properties
        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        # Bird animation for menu screen
        self.bird_frames: list[pygame.Surface] = [
            load_image(f"{GAME_SETTINGS.bird_type}bird-downflap.png"),
            load_image(f"{GAME_SETTINGS.bird_type}bird-midflap.png"),
            load_image(f"{GAME_SETTINGS.bird_type}bird-upflap.png"),
        ]
        self.bird_index: int = 0
        self.bird_frame_count: int = 0
        self.bird_position: list[int] = [
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 30,
        ]
        self.bird_movement: float = 1.2  # Subtle up and down movement
        self.bird_direction: int = 1  # 1 for up, -1 for down

        # Create buttons
        button_width = 120
        button_height = 40
        button_spacing = 30
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y_offset = 60  # Move all buttons down by 60 pixels (was 40)

        self.play_button: Button = Button(
            button_x,
            SCREEN_HEIGHT // 2 + button_y_offset,
            button_width,
            button_height,
            "Play",
            WHITE,
            GREEN,
        )

        self.stats_button: Button = Button(
            button_x,
            SCREEN_HEIGHT // 2
            + button_spacing
            + button_height
            + button_y_offset,
            button_width,
            button_height,
            "Stats",
            WHITE,
            (100, 100, 200),  # Light purple
        )

        self.settings_button: Button = Button(
            button_x,
            SCREEN_HEIGHT // 2
            + (button_spacing + button_height) * 2
            + button_y_offset,
            button_width,
            button_height,
            "Settings",
            WHITE,
            BLUE,
        )

        # High score display
        self.score_display: ScoreDisplay = ScoreDisplay()

    def update(self, mouse_pos: tuple[int, int], click: bool) -> int:
        # Update base animation
        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width + SCREEN_WIDTH:
            self.base_x = 0

        # Animate bird
        self.bird_frame_count += 1
        if self.bird_frame_count > 5:
            self.bird_frame_count = 0
            self.bird_index = (self.bird_index + 1) % 3

        # Make bird bob up and down slightly
        self.bird_position[1] += int(self.bird_direction * self.bird_movement)
        if self.bird_position[1] > SCREEN_HEIGHT // 2 - 20:
            self.bird_direction = -1
        elif self.bird_position[1] < SCREEN_HEIGHT // 2 - 40:
            self.bird_direction = 1

        # Update buttons hover state
        self.play_button.update(mouse_pos)
        self.stats_button.update(mouse_pos)
        self.settings_button.update(mouse_pos)

        # Check for button clicks
        if self.play_button.is_clicked(mouse_pos, click):
            # Play sound when button is clicked
            load_audio("swoosh.wav").play()
            return PLAYING
        elif self.stats_button.is_clicked(mouse_pos, click):
            load_audio("swoosh.wav").play()
            return STATS
        elif self.settings_button.is_clicked(mouse_pos, click):
            load_audio("swoosh.wav").play()
            return SETTINGS

        return MAIN_MENU

    def draw(self, surface: pygame.Surface) -> None:
        # Draw background
        surface.blit(self.background, (0, 0))

        # Draw logo
        logo_rect = self.logo.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        )
        surface.blit(self.logo, logo_rect)

        # Draw animated bird
        bird_image = self.bird_frames[self.bird_index]
        bird_rect = bird_image.get_rect(center=self.bird_position)
        surface.blit(bird_image, bird_rect)

        # Draw base - first copy
        surface.blit(self.base, (self.base_x, self.base_y))

        # Draw base - second copy for continuous scrolling
        surface.blit(self.base, (self.base_x + self.base_width, self.base_y))

        # Draw buttons
        self.play_button.draw(surface)
        self.stats_button.draw(surface)
        self.settings_button.draw(surface)


class ScoreDisplay:
    def __init__(self) -> None:
        self.number_images: list[pygame.Surface] = [
            load_image(f"{i}.png") for i in range(10)
        ]

    def draw(
        self,
        surface: pygame.Surface,
        score: int,
        x: int | None = None,
        y: int = 50,
    ) -> None:
        score_str = str(score)
        width = 0

        # Calculate total width to center the score
        for digit in score_str:
            width += self.number_images[int(digit)].get_width() + 2

        # Center score horizontally if x is not provided
        if x is None:
            x = (SCREEN_WIDTH - width) // 2

        # Draw each digit
        for digit in score_str:
            digit_image = self.number_images[int(digit)]
            surface.blit(digit_image, (x, y))
            x += digit_image.get_width() + 2


class GameOverScreen:
    def __init__(self) -> None:
        self.game_over_image: pygame.Surface = load_image("gameover.png")
        self.score_display: ScoreDisplay = ScoreDisplay()
        self.new_high_score: bool = False
        self.flash_timer: int = 0

        # Create buttons
        button_width = 120
        button_height = 40
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        self.retry_button: Button = Button(
            button_x,
            SCREEN_HEIGHT // 2 + 30,
            button_width,
            button_height,
            "Retry",
            WHITE,
            GREEN,
        )

        self.menu_button: Button = Button(
            button_x,
            SCREEN_HEIGHT // 2 + 80,
            button_width,
            button_height,
            "Menu",
            WHITE,
            BLUE,
        )

    def update_high_score(self, score: int) -> None:
        # Check if this score beats the high score for the current difficulty
        self.new_high_score = GAME_SETTINGS.update_high_score(score)

    def update(self, mouse_pos: tuple[int, int], click: bool) -> int:
        # Flash effect for new high score
        if self.new_high_score:
            self.flash_timer += 1
            if self.flash_timer > 60:  # Reset every second (assuming 60 FPS)
                self.flash_timer = 0

        # Update buttons hover state
        self.retry_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)

        # Check for button clicks
        if self.retry_button.is_clicked(mouse_pos, click):
            load_audio("swoosh.wav").play()
            return PLAYING
        elif self.menu_button.is_clicked(mouse_pos, click):
            load_audio("swoosh.wav").play()
            return MAIN_MENU

        return GAME_OVER

    def draw(self, surface: pygame.Surface, score: int) -> None:
        # Draw game over image
        game_over_rect = self.game_over_image.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20)
        )
        surface.blit(self.game_over_image, game_over_rect)

        # Draw score
        self.score_display.draw(surface, score, y=SCREEN_HEIGHT // 3 - 30)

        # Draw high score
        font = pygame.font.Font(None, 26)
        high_score = GAME_SETTINGS.get_high_score()

        # Draw "NEW HIGH SCORE!" with flash effect if applicable - moved down
        if self.new_high_score:
            flash_color = WHITE if self.flash_timer < 30 else YELLOW
            high_score_text = font.render("NEW HIGH SCORE!", True, flash_color)
            high_score_rect = high_score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 30)
            )
            surface.blit(high_score_text, high_score_rect)

        # Always draw the high score - moved down
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60)
        )
        surface.blit(high_score_text, high_score_rect)

        # Draw buttons
        self.retry_button.draw(surface)
        self.menu_button.draw(surface)


class SettingsScreen:
    def __init__(self) -> None:
        self.background: pygame.Surface = time_based_background()
        self.base: pygame.Surface = load_image("base.png")

        # Base animation properties
        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        # Create preview birds for each difficulty
        self.yellow_bird: pygame.Surface = load_image("yellowbird-midflap.png")
        self.blue_bird: pygame.Surface = load_image("bluebird-midflap.png")
        self.red_bird: pygame.Surface = load_image("redbird-midflap.png")

        # Create preview pipes
        self.green_pipe: pygame.Surface = load_image("pipe-green.png")
        self.red_pipe: pygame.Surface = load_image("pipe-red.png")

        # Create font
        self.title_font: pygame.font.Font = pygame.font.Font(None, 36)
        self.font: pygame.font.Font = pygame.font.Font(None, 24)

        # Settings panel background - moved up slightly for better positioning
        self.panel_width: int = 250
        self.panel_height: int = 320
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            50,
        )  # Moved up from 70 to 50

        # Difficulty selection section
        self.selection_width: int = 60  # Width for Easy and Hard buttons
        self.medium_width: int = 80  # Wider width for Medium button
        self.selection_height: int = 30
        selection_y = self.panel_position[1] + 65  # Moved up slightly

        # Better spaced buttons with Medium button being wider
        button_spacing = 18  # Reduced spacing for better fit

        self.easy_button: Button = Button(
            self.panel_position[0] + 15,
            selection_y,
            self.selection_width,
            self.selection_height,
            "Easy",
            WHITE,
            YELLOW,
        )

        self.medium_button: Button = Button(
            self.panel_position[0]
            + (self.panel_width - self.medium_width) // 2,
            selection_y,
            self.medium_width,  # Wider button for "Medium" text
            self.selection_height,
            "Medium",
            WHITE,
            BLUE,
        )

        self.hard_button: Button = Button(
            self.panel_position[0]
            + self.panel_width
            - self.selection_width
            - 15,
            selection_y,
            self.selection_width,
            self.selection_height,
            "Hard",
            WHITE,
            RED,
        )

        # Navigation buttons - made wider and more prominent
        button_width = 90
        button_height = 40
        button_spacing = 20

        # Save and Back buttons positioned at bottom of panel
        self.save_button: Button = Button(
            self.panel_position[0]
            + self.panel_width // 2
            - button_width
            - button_spacing // 2,
            self.panel_position[1] + self.panel_height - 60,
            button_width,
            button_height,
            "Save",
            WHITE,
            GREEN,
        )

        self.back_button: Button = Button(
            self.panel_position[0]
            + self.panel_width // 2
            + button_spacing // 2,
            self.panel_position[1] + self.panel_height - 60,
            button_width,
            button_height,
            "Back",
            WHITE,
            (100, 100, 100),  # Gray
        )

        # To track if settings were changed and need saving
        self.initial_difficulty: int = GAME_SETTINGS.difficulty
        self.has_changes: bool = False

    def update(self, mouse_pos: tuple[int, int], click: bool) -> int:
        # Update base animation
        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width + SCREEN_WIDTH:
            self.base_x = 0

        # Update buttons
        self.easy_button.update(mouse_pos)
        self.medium_button.update(mouse_pos)
        self.hard_button.update(mouse_pos)
        self.save_button.update(mouse_pos)
        self.back_button.update(mouse_pos)

        # Check for any changes to enable/disable save button
        self.has_changes = self.initial_difficulty != GAME_SETTINGS.difficulty

        # Check button clicks
        if click:
            if self.easy_button.is_clicked(mouse_pos, click):
                GAME_SETTINGS.set_difficulty(EASY)
                load_audio("point.wav").play()
            elif self.medium_button.is_clicked(mouse_pos, click):
                GAME_SETTINGS.set_difficulty(MEDIUM)
                load_audio("point.wav").play()
            elif self.hard_button.is_clicked(mouse_pos, click):
                GAME_SETTINGS.set_difficulty(HARD)
                load_audio("point.wav").play()
            elif (
                self.save_button.is_clicked(mouse_pos, click)
                and self.has_changes
            ):
                GAME_SETTINGS.save_settings()
                self.initial_difficulty = GAME_SETTINGS.difficulty
                self.has_changes = False
                load_audio("swoosh.wav").play()
                return MAIN_MENU
            elif self.back_button.is_clicked(mouse_pos, click):
                # If there are unsaved changes, revert to initial settings
                if self.has_changes:
                    GAME_SETTINGS.set_difficulty(self.initial_difficulty)
                load_audio("swoosh.wav").play()
                return MAIN_MENU

        return SETTINGS

    def draw(self, surface: pygame.Surface) -> None:
        # Draw background first
        surface.blit(self.background, (0, 0))

        # Draw base BEFORE settings panel to ensure it's behind
        surface.blit(self.base, (self.base_x, self.base_y))
        surface.blit(self.base, (self.base_x + self.base_width, self.base_y))

        # Draw settings panel with semi-transparency - AFTER the base
        panel_surf = pygame.Surface(
            (self.panel_width, self.panel_height), pygame.SRCALPHA
        )
        panel_surf.fill((0, 0, 0, 220))  # More opaque for better contrast
        pygame.draw.rect(
            panel_surf, WHITE, (0, 0, self.panel_width, self.panel_height), 2
        )
        surface.blit(panel_surf, self.panel_position)

        # Draw title
        title_text = self.title_font.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 25)
        )
        surface.blit(title_text, title_rect)

        # Draw difficulty section title
        diff_header = self.font.render("Select Difficulty:", True, WHITE)
        diff_header_rect = diff_header.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 50)
        )
        surface.blit(diff_header, diff_header_rect)

        # Draw current selection indicator
        curr_text = self.font.render(
            f"Current: {GAME_SETTINGS.get_difficulty_name()}",
            True,
            GAME_SETTINGS.get_difficulty_color(),
        )
        curr_rect = curr_text.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 105)
        )
        surface.blit(curr_text, curr_rect)

        # Draw difficulty buttons
        self.easy_button.draw(surface)
        self.medium_button.draw(surface)
        self.hard_button.draw(surface)

        # Draw bird and pipe previews section title - moved up
        preview_title = self.font.render("Preview:", True, WHITE)
        preview_rect = preview_title.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 140)
        )
        surface.blit(preview_title, preview_rect)

        # Draw birds row - moved up
        bird_y = self.panel_position[1] + 165
        bird_spacing = 60
        center_x = SCREEN_WIDTH // 2

        # Position birds properly in a row
        surface.blit(
            self.yellow_bird,
            (
                center_x - bird_spacing - self.yellow_bird.get_width() // 2,
                bird_y,
            ),
        )
        surface.blit(
            self.blue_bird,
            (center_x - self.blue_bird.get_width() // 2, bird_y),
        )
        surface.blit(
            self.red_bird,
            (center_x + bird_spacing - self.red_bird.get_width() // 2, bird_y),
        )

        # Draw bird labels - now positioned properly below birds
        label_y = bird_y + 25
        easy_label = self.font.render("Easy", True, YELLOW)
        medium_label = self.font.render("Medium", True, BLUE)
        hard_label = self.font.render("Hard", True, RED)

        surface.blit(
            easy_label,
            (center_x - bird_spacing - easy_label.get_width() // 2, label_y),
        )
        surface.blit(
            medium_label, (center_x - medium_label.get_width() // 2, label_y)
        )
        surface.blit(
            hard_label,
            (center_x + bird_spacing - hard_label.get_width() // 2, label_y),
        )

        # Draw pipes preview - moved higher to avoid collisions
        pipe_y = bird_y + 50  # Reduced vertical gap
        pipe_width = (
            self.green_pipe.get_width() // 5
        )  # Even smaller scale for display
        pipe_height = self.green_pipe.get_height() // 5

        # Scale pipes for preview - smaller scale
        green_pipe_small = pygame.transform.scale(
            self.green_pipe, (pipe_width, pipe_height)
        )
        red_pipe_small = pygame.transform.scale(
            self.red_pipe, (pipe_width, pipe_height)
        )

        # Draw pipes with more horizontal spacing
        surface.blit(
            green_pipe_small, (center_x - 60 - pipe_width // 2, pipe_y)
        )
        surface.blit(red_pipe_small, (center_x + 60 - pipe_width // 2, pipe_y))

        # Draw pipe labels with better positioning
        pipe_label_y = pipe_y + pipe_height + 5
        green_pipe_label = self.font.render(
            "Easy/Med", True, GREEN
        )  # Shortened text
        red_pipe_label = self.font.render("Hard", True, RED)

        surface.blit(
            green_pipe_label,
            (center_x - 60 - green_pipe_label.get_width() // 2, pipe_label_y),
        )
        surface.blit(
            red_pipe_label,
            (center_x + 60 - red_pipe_label.get_width() // 2, pipe_label_y),
        )

        # Draw buttons
        self.save_button.draw(surface)
        self.back_button.draw(surface)


class StatsScreen:
    def __init__(self) -> None:
        self.background: pygame.Surface = time_based_background()
        self.base: pygame.Surface = load_image("base.png")

        # Base animation properties
        self.base_width: int = self.base.get_width()
        self.base_height: int = self.base.get_height()
        self.base_y: int = SCREEN_HEIGHT - self.base_height
        self.base_x: int = 0
        self.base_scroll_speed: int = 2

        # Medal images for high scores
        if GAME_SETTINGS.get_high_score(EASY) > 10:
            self.easy_medal: pygame.Surface | None = load_image(
                "9.png"
            )  # Gold medal
        elif GAME_SETTINGS.get_high_score(EASY) > 0:
            self.easy_medal: pygame.Surface | None = load_image(
                "1.png"
            )  # Silver medal
        else:
            self.easy_medal: pygame.Surface | None = None

        if GAME_SETTINGS.get_high_score(MEDIUM) > 10:
            self.medium_medal: pygame.Surface | None = load_image(
                "9.png"
            )  # Gold medal
        elif GAME_SETTINGS.get_high_score(MEDIUM) > 0:
            self.medium_medal: pygame.Surface | None = load_image(
                "1.png"
            )  # Silver medal
        else:
            self.medium_medal: pygame.Surface | None = None

        if GAME_SETTINGS.get_high_score(HARD) > 10:
            self.hard_medal: pygame.Surface | None = load_image(
                "9.png"
            )  # Gold medal
        elif GAME_SETTINGS.get_high_score(HARD) > 0:
            self.hard_medal: pygame.Surface | None = load_image(
                "1.png"
            )  # Silver medal
        else:
            self.hard_medal: pygame.Surface | None = None

        # Stats panel
        self.panel_width: int = 250
        self.panel_height: int = 300
        self.panel_position: tuple[int, int] = (
            SCREEN_WIDTH // 2 - self.panel_width // 2,
            70,
        )

        # Create font
        self.title_font: pygame.font.Font = pygame.font.Font(None, 36)
        self.font: pygame.font.Font = pygame.font.Font(None, 24)

        # Back button
        self.back_button: Button = Button(
            SCREEN_WIDTH // 2 - 60,
            SCREEN_HEIGHT - self.base_height - 60,
            120,
            40,
            "Back",
            WHITE,
            (100, 100, 100),  # Gray
        )

    def update(self, mouse_pos: tuple[int, int], click: bool) -> int:
        # Update base animation
        self.base_x -= self.base_scroll_speed
        if self.base_x <= -self.base_width + SCREEN_WIDTH:
            self.base_x = 0

        # Update button hover state
        self.back_button.update(mouse_pos)

        # Check for button clicks
        if self.back_button.is_clicked(mouse_pos, click):
            load_audio("swoosh.wav").play()
            return MAIN_MENU

        return STATS

    def draw(self, surface: pygame.Surface) -> None:
        # Draw background
        surface.blit(self.background, (0, 0))

        # Draw base - first copy
        surface.blit(self.base, (self.base_x, self.base_y))
        # Draw base - second copy for continuous scrolling
        surface.blit(self.base, (self.base_x + self.base_width, self.base_y))

        # Draw stats panel with semi-transparency
        panel_surf = pygame.Surface(
            (self.panel_width, self.panel_height), pygame.SRCALPHA
        )
        panel_surf.fill((0, 0, 0, 220))  # Semi-transparent black
        pygame.draw.rect(
            panel_surf, WHITE, (0, 0, self.panel_width, self.panel_height), 2
        )
        surface.blit(panel_surf, self.panel_position)

        # Draw title
        title_text = self.title_font.render("High Scores", True, WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, self.panel_position[1] + 25)
        )
        surface.blit(title_text, title_rect)

        # Draw difficulty high scores
        y_pos = self.panel_position[1] + 70
        spacing = 70

        # Easy difficulty
        self.draw_difficulty_stats(
            surface, "Easy", EASY, YELLOW, y_pos, self.easy_medal
        )

        # Medium difficulty
        self.draw_difficulty_stats(
            surface, "Medium", MEDIUM, BLUE, y_pos + spacing, self.medium_medal
        )

        # Hard difficulty
        self.draw_difficulty_stats(
            surface, "Hard", HARD, RED, y_pos + spacing * 2, self.hard_medal
        )

        # Draw back button
        self.back_button.draw(surface)

    def draw_difficulty_stats(
        self,
        surface: pygame.Surface,
        name: str,
        difficulty: int,
        color: tuple[int, int, int],
        y_pos: int,
        medal: pygame.Surface | None,
    ) -> None:
        # Draw difficulty name with color
        diff_text = self.font.render(name, True, color)
        surface.blit(diff_text, (self.panel_position[0] + 20, y_pos))

        # Draw high score
        score = GAME_SETTINGS.get_high_score(difficulty)
        score_text = self.font.render(f"High Score: {score}", True, WHITE)
        surface.blit(score_text, (self.panel_position[0] + 20, y_pos + 25))

        # Draw medal if applicable
        if medal:
            medal_x = self.panel_position[0] + self.panel_width - 50
            medal_y = y_pos + 10
            surface.blit(medal, (medal_x, medal_y))
