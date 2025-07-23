import random

from src.constants import *


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.animation_index = 0
        self.frame_count = 0

        # Load frames based on bird type from settings
        self.update_bird_type()

        self.rect = pygame.Rect(
            x, y, self.frames[0].get_width(), self.frames[0].get_height()
        )
        self.flap_sound = load_audio("wing.wav")

    def update_bird_type(self):
        bird_type = GAME_SETTINGS.bird_type
        self.frames = [
            load_image(f"{bird_type}bird-downflap.png"),
            load_image(f"{bird_type}bird-midflap.png"),
            load_image(f"{bird_type}bird-upflap.png"),
        ]

    def update(self):
        # Apply gravity based on difficulty
        self.velocity += GAME_SETTINGS.get_gravity()
        self.y += self.velocity

        # Update rectangle position for collision detection
        self.rect.y = int(self.y)
        self.rect.x = int(self.x)

        # Animation
        self.frame_count += 1
        if self.frame_count > 5:  # Change animation every 5 frames
            self.frame_count = 0
            self.animation_index = (self.animation_index + 1) % 3

    def draw(self, surface):
        # Rotate bird based on velocity (diving angle)
        rotated_bird = pygame.transform.rotate(
            self.frames[self.animation_index], -self.velocity * 3
        )
        surface.blit(rotated_bird, (self.x, self.y))

    def jump(self):
        self.velocity = BIRD_JUMP
        self.flap_sound.play()

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.animation_index = 0
        self.frame_count = 0
        self.rect.x = x
        self.rect.y = y
        # Update bird type in case settings changed
        self.update_bird_type()


class Pipe:
    def __init__(self, x):
        self.x = x
        self.pipe_color = GAME_SETTINGS.pipe_color
        self.pipe_img = load_image(f"pipe-{self.pipe_color}.png")
        self.top_pipe = pygame.transform.flip(self.pipe_img, False, True)
        self.bottom_pipe = self.pipe_img
        self.passed = False

        # Get appropriate pipe gap based on difficulty
        self.pipe_gap = GAME_SETTINGS.get_pipe_gap()

        # Calculate the base height to account for ground height
        base_height = self.pipe_img.get_height()
        ground_y = SCREEN_HEIGHT - load_image("base.png").get_height()

        # Improved height range to prevent pipes from appearing too close to ground or ceiling
        # Min height ensures top pipe isn't too short
        # Max height ensures bottom pipe doesn't clip into ground
        min_height = 80  # Minimum height for top pipe
        max_height = (
            ground_y - self.pipe_gap - 80
        )  # Maximum height ensuring bottom pipe has space

        # Make height range more challenging based on difficulty
        if GAME_SETTINGS.difficulty == HARD:
            # For hard difficulty, allow more extreme pipe placements
            min_height = 60
            max_height = ground_y - self.pipe_gap - 60

        self.height = random.randint(min_height, max_height)

        # Create rects for collision detection
        self.top_rect = pygame.Rect(
            x,
            self.height - self.top_pipe.get_height(),
            self.top_pipe.get_width(),
            self.top_pipe.get_height(),
        )
        self.bottom_rect = pygame.Rect(
            x,
            self.height + self.pipe_gap,
            self.bottom_pipe.get_width(),
            self.bottom_pipe.get_height(),
        )

    def update(self):
        # Make pipe speed dependent on difficulty
        velocity = PIPE_VELOCITY
        if GAME_SETTINGS.difficulty == HARD:
            velocity -= 1  # Faster for hard mode
        elif GAME_SETTINGS.difficulty == EASY:
            velocity += 1  # Slower for easy mode

        self.x += velocity
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        # Draw top pipe
        surface.blit(
            self.top_pipe, (self.x, self.height - self.top_pipe.get_height())
        )
        # Draw bottom pipe
        surface.blit(self.bottom_pipe, (self.x, self.height + self.pipe_gap))


class Base:
    def __init__(self):
        self.image = load_image("base.png")
        self.width = self.image.get_width()
        self.x = 0
        self.y = SCREEN_HEIGHT - self.image.get_height()
        self.rect = pygame.Rect(
            self.x, self.y, self.width, self.image.get_height()
        )
        self.scroll_speed = 2  # Base scroll speed

    def update(self):
        # Adjust speed based on difficulty
        speed_modifier = 1.0
        if GAME_SETTINGS.difficulty == HARD:
            speed_modifier = 1.5
        elif GAME_SETTINGS.difficulty == EASY:
            speed_modifier = 0.8

        # Move base to the left
        self.x -= self.scroll_speed * speed_modifier

        # Reset position when enough of the image has scrolled to create a seamless loop
        if self.x <= -self.width + SCREEN_WIDTH:
            self.x = 0

        # Update collision rectangle
        self.rect.x = self.x

    def draw(self, surface):
        # Draw first copy of the base
        surface.blit(self.image, (self.x, self.y))

        # Draw second copy to create seamless scrolling
        surface.blit(self.image, (self.x + self.width, self.y))
