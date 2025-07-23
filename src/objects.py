import random

import pygame

from src.constants import (
    BIRD_JUMP,
    EASY,
    GAME_SETTINGS,
    HARD,
    PIPE_VELOCITY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    load_audio,
    load_image,
)


class Bird:
    """
    Represents the player-controlled bird in the game.

    Methods
    -------
    __init__(x, y)
        Initializes the Bird object at the given coordinates.
    update_bird_type()
        Updates the bird's animation frames based on the current bird type in settings.
    update()
        Updates the bird's position, velocity, and animation state.
    draw(surface)
        Draws the bird on the given surface with rotation based on velocity.
    jump()
        Makes the bird jump by setting its velocity and playing the flap sound.
    reset(x, y)
        Resets the bird's position, velocity, and animation state.
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialize the Bird object at the specified coordinates.

        Parameters
        ----------
        x : float
            The initial x-coordinate of the bird.
        y : float
            The initial y-coordinate of the bird.
        """
        self.x: float = x
        self.y: float = y
        self.velocity: float = 0
        self.animation_index: int = 0
        self.frame_count: int = 0

        # Load frames based on bird type from settings
        self.update_bird_type()

        self.rect: pygame.Rect = pygame.Rect(
            int(x),
            int(y),
            self.frames[0].get_width(),
            self.frames[0].get_height(),
        )
        self.flap_sound: pygame.mixer.Sound = load_audio("wing.wav")

    def update_bird_type(self) -> None:
        """
        Update the bird's animation frames based on the current bird type in settings.
        """
        bird_type = GAME_SETTINGS.bird_type
        self.frames: list[pygame.Surface] = [
            load_image(f"{bird_type}bird-downflap.png"),
            load_image(f"{bird_type}bird-midflap.png"),
            load_image(f"{bird_type}bird-upflap.png"),
        ]

    def update(self) -> None:
        """
        Update the bird's position, velocity, and animation state.
        """
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

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the bird on the given surface with rotation based on velocity.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the bird on.
        """
        # Rotate bird based on velocity (diving angle)
        rotated_bird = pygame.transform.rotate(
            self.frames[self.animation_index], -self.velocity * 3
        )
        surface.blit(rotated_bird, (self.x, self.y))

    def jump(self) -> None:
        """
        Make the bird jump by setting its velocity and playing the flap sound.
        """
        self.velocity = BIRD_JUMP
        self.flap_sound.play()

    def reset(self, x: float, y: float) -> None:
        """
        Reset the bird's position, velocity, and animation state.

        Parameters
        ----------
        x : float
            The new x-coordinate for the bird.
        y : float
            The new y-coordinate for the bird.
        """
        self.x = x
        self.y = y
        self.velocity = 0
        self.animation_index = 0
        self.frame_count = 0
        self.rect.x = int(x)
        self.rect.y = int(y)
        # Update bird type in case settings changed
        self.update_bird_type()


class Pipe:
    """
    Represents a pair of pipes (top and bottom) in the game.

    Methods
    -------
    __init__(x)
        Initializes the Pipe object at the given x-coordinate.
    update()
        Updates the pipe's position based on the current difficulty.
    draw(surface)
        Draws the top and bottom pipes on the given surface.
    """

    def __init__(self, x: float) -> None:
        """
        Initialize the Pipe object at the specified x-coordinate.

        Parameters
        ----------
        x : float
            The initial x-coordinate of the pipe.
        """
        self.x: float = x
        self.pipe_color: str = GAME_SETTINGS.pipe_color
        self.pipe_img: pygame.Surface = load_image(
            f"pipe-{self.pipe_color}.png"
        )
        self.top_pipe: pygame.Surface = pygame.transform.flip(
            self.pipe_img, False, True
        )
        self.bottom_pipe: pygame.Surface = self.pipe_img
        self.passed: bool = False

        # Get appropriate pipe gap based on difficulty
        self.pipe_gap: int = GAME_SETTINGS.get_pipe_gap()

        # Calculate the base height to account for ground height
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

        self.height: int = random.randint(min_height, max_height)

        # Create rects for collision detection
        self.top_rect: pygame.Rect = pygame.Rect(
            int(x),
            self.height - self.top_pipe.get_height(),
            self.top_pipe.get_width(),
            self.top_pipe.get_height(),
        )
        self.bottom_rect: pygame.Rect = pygame.Rect(
            int(x),
            self.height + self.pipe_gap,
            self.bottom_pipe.get_width(),
            self.bottom_pipe.get_height(),
        )

    def update(self) -> None:
        """
        Update the pipe's position based on the current difficulty.
        """
        # Make pipe speed dependent on difficulty
        velocity = PIPE_VELOCITY
        if GAME_SETTINGS.difficulty == HARD:
            velocity -= 1  # Faster for hard mode
        elif GAME_SETTINGS.difficulty == EASY:
            velocity += 1  # Slower for easy mode

        self.x += velocity
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the top and bottom pipes on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the pipes on.
        """
        # Draw top pipe
        surface.blit(
            self.top_pipe, (self.x, self.height - self.top_pipe.get_height())
        )
        # Draw bottom pipe
        surface.blit(self.bottom_pipe, (self.x, self.height + self.pipe_gap))


class Base:
    """
    Represents the scrolling ground base in the game.

    Methods
    -------
    __init__()
        Initializes the Base object.
    update()
        Updates the base's position to create a scrolling effect.
    draw(surface)
        Draws the base on the given surface, creating a seamless loop.
    """

    def __init__(self) -> None:
        """
        Initialize the Base object.
        """
        self.image: pygame.Surface = load_image("base.png")
        self.width: int = self.image.get_width()
        self.x: float = 0
        self.y: int = SCREEN_HEIGHT - self.image.get_height()
        self.rect: pygame.Rect = pygame.Rect(
            int(self.x), self.y, self.width, self.image.get_height()
        )
        self.scroll_speed: float = 2  # Base scroll speed

    def update(self) -> None:
        """
        Update the base's position to create a scrolling effect.
        """
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
        self.rect.x = int(self.x)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the base on the given surface, creating a seamless loop.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the base on.
        """
        # Draw first copy of the base
        surface.blit(self.image, (self.x, self.y))

        # Draw second copy to create seamless scrolling
        surface.blit(self.image, (self.x + self.width, self.y))
