import random

import pygame

from src.constants import (
    BIRD_JUMP,
    PIPE_GAP,
    PIPE_VELOCITY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    load_audio,
    load_image,
)
from src.settings import GAME_SETTINGS


class Bird:
    """
    Represents the player-controlled bird in the game.
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

        self.update_bird_type()

        self.rect: pygame.Rect = pygame.Rect(
            int(x),
            int(y),
            self.frames[0].get_width(),
            self.frames[0].get_height(),
        )
        self.flap_sound: pygame.mixer.Sound = load_audio("wing.wav")

        self.mask: pygame.mask.Mask | None = None
        self.current_rotation: float = 0
        self.hitbox_reduction: int = 4

        self.rotated_image: pygame.Surface = self.frames[0]
        self.update_rotated_image()

    def update_bird_type(self) -> None:
        """
        Update the bird's animation frames based on the current bird type in settings.

        Returns
        -------
        None
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

        Returns
        -------
        None
        """
        self.velocity += GAME_SETTINGS.get_gravity()
        self.y += self.velocity

        self.rect.y = int(self.y)
        self.rect.x = int(self.x)

        self.frame_count += 1
        if self.frame_count > 5:
            self.frame_count = 0
            self.animation_index = (self.animation_index + 1) % 3

        self.update_rotated_image()

    def update_rotated_image(self) -> None:
        """
        Update the rotated image based on current velocity and animation frame.

        Ensures the rotated image is always available for collision detection.

        Returns
        -------
        None
        """
        max_rotation = 25
        min_rotation = -90
        self.current_rotation = min(
            max(self.velocity * -2, min_rotation), max_rotation
        )

        image = self.frames[self.animation_index]
        self.rotated_image = pygame.transform.rotate(
            image, self.current_rotation
        )

        self.mask = pygame.mask.from_surface(self.rotated_image)

        rotated_rect = self.rotated_image.get_rect(
            center=(int(self.x), int(self.y))
        )
        self.rect = rotated_rect.inflate(
            -self.hitbox_reduction, -self.hitbox_reduction
        )

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the bird on the given surface with rotation based on velocity.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the bird on.

        Returns
        -------
        None
        """
        rotated_rect = self.rotated_image.get_rect(
            center=(int(self.x), int(self.y))
        )
        surface.blit(self.rotated_image, rotated_rect)

    def get_mask(self) -> pygame.mask.Mask | None:
        """
        Get the current mask for pixel-perfect collision detection.

        Returns
        -------
        pygame.mask.Mask or None
            The mask representing the bird's current visual state, or None if not available.
        """
        if self.mask is None:
            self.mask = pygame.mask.from_surface(self.rotated_image)
        return self.mask

    def jump(self) -> None:
        """
        Make the bird jump by setting its velocity and playing the flap sound.

        Returns
        -------
        None
        """
        self.velocity = BIRD_JUMP
        self.flap_sound.play()

    def reset(self, x: float, y: float) -> None:
        """
        Reset the bird's position, velocity, and animation state.

        Parameters
        ----------
        x : float
            The x-coordinate to reset the bird to.
        y : float
            The y-coordinate to reset the bird to.

        Returns
        -------
        None
        """
        self.x = x
        self.y = y
        self.velocity = 0
        self.animation_index = 0
        self.frame_count = 0

        self.update_bird_type()

        self.rect.x = int(x)
        self.rect.y = int(y)


class Pipe:
    """
    Represents a pair of pipes (top and bottom) in the game.
    """

    def __init__(self) -> None:
        """
        Initialize a pair of pipes with random heights.

        Returns
        -------
        None
        """
        self.pipe_color: str = GAME_SETTINGS.pipe_color
        self.pipe_img: pygame.Surface = load_image(
            f"pipe-{self.pipe_color}.png"
        )
        self.pipe_top: pygame.Surface = pygame.transform.flip(
            self.pipe_img, False, True
        )
        self.pipe_bottom: pygame.Surface = self.pipe_img

        self.gap: int = PIPE_GAP
        self.x: int = SCREEN_WIDTH

        self.height: int = random.randint(80, 280)

        self.top_rect: pygame.Rect = self.pipe_top.get_rect(
            topleft=(self.x, self.height - self.pipe_top.get_height())
        )
        self.bottom_rect: pygame.Rect = self.pipe_bottom.get_rect(
            topleft=(self.x, self.height + self.gap)
        )

        self.top_mask: pygame.mask.Mask = pygame.mask.from_surface(
            self.pipe_top
        )
        self.bottom_mask: pygame.mask.Mask = pygame.mask.from_surface(
            self.pipe_bottom
        )

        self.passed: bool = False
        self.center_passed: bool = False

    def update(self) -> bool:
        """
        Update pipe position and check if it's off-screen.

        Returns
        -------
        bool
            True if the pipe is still on screen, False otherwise.
        """
        self.x += PIPE_VELOCITY
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

        return self.x > -self.pipe_top.get_width()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw both top and bottom pipes on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the pipes on.

        Returns
        -------
        None
        """
        surface.blit(self.pipe_top, self.top_rect)
        surface.blit(self.pipe_bottom, self.bottom_rect)

    def check_collision(self, bird: Bird) -> bool:
        """
        Check if the bird collides with either the top or bottom pipe using mask-based collision.

        Parameters
        ----------
        bird : Bird
            The bird object to check collision with.

        Returns
        -------
        bool
            True if collision detected, False otherwise.
        """
        bird_mask = bird.get_mask()
        if bird_mask is None:
            return False

        bird_visual_rect = bird.rotated_image.get_rect(
            center=(int(bird.x), int(bird.y))
        )

        top_offset = (
            int(self.top_rect.x - bird_visual_rect.x),
            int(self.top_rect.y - bird_visual_rect.y),
        )
        bottom_offset = (
            int(self.bottom_rect.x - bird_visual_rect.x),
            int(self.bottom_rect.y - bird_visual_rect.y),
        )

        top_point = bird_mask.overlap(self.top_mask, top_offset)
        bottom_point = bird_mask.overlap(self.bottom_mask, bottom_offset)

        return top_point is not None or bottom_point is not None


class Base:
    """
    Represents the moving ground in the game.
    """

    def __init__(self) -> None:
        """
        Initialize the base object with animation properties.

        Returns
        -------
        None
        """
        self.image: pygame.Surface = load_image("base.png")
        self.width: int = self.image.get_width()
        self.height: int = self.image.get_height()
        self.y: int = SCREEN_HEIGHT - self.height
        self.x1: float = 0
        self.x2: float = self.width
        self.velocity: int = PIPE_VELOCITY

        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)

        self.rect1: pygame.Rect = self.image.get_rect(
            topleft=(self.x1, self.y)
        )
        self.rect2: pygame.Rect = self.image.get_rect(
            topleft=(self.x2, self.y)
        )

    def update(self) -> None:
        """
        Update the base position for scrolling animation.

        Returns
        -------
        None
        """
        self.x1 += self.velocity
        self.x2 += self.velocity

        self.rect1.x = int(self.x1)
        self.rect2.x = int(self.x2)

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
            self.rect1.x = int(self.x1)

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
            self.rect2.x = int(self.x2)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the base on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the base on.

        Returns
        -------
        None
        """
        surface.blit(self.image, (self.x1, self.y))
        surface.blit(self.image, (self.x2, self.y))

    def check_collision(self, bird: Bird) -> bool:
        """
        Check if the bird collides with the ground or ceiling.

        Parameters
        ----------
        bird : Bird
            The bird object to check collision with.

        Returns
        -------
        bool
            True if collision detected, False otherwise.
        """
        bird_visual_rect = bird.rotated_image.get_rect(
            center=(int(bird.x), int(bird.y))
        )
        if bird_visual_rect.top < 0:
            return True

        bird_mask = bird.get_mask()
        if bird_mask is None:
            return False

        if bird_visual_rect.colliderect(self.rect1):
            base_offset = (
                int(self.rect1.x - bird_visual_rect.x),
                int(self.rect1.y - bird_visual_rect.y),
            )
            if bird_mask.overlap(self.mask, base_offset):
                return True

        if bird_visual_rect.colliderect(self.rect2):
            base_offset = (
                int(self.rect2.x - bird_visual_rect.x),
                int(self.rect2.y - bird_visual_rect.y),
            )
            if bird_mask.overlap(self.mask, base_offset):
                return True

        return False
