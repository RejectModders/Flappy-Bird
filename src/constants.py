import os
import sys

import pygame

from src.settings import GAME_SETTINGS

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60
GRAVITY = 0.25
BIRD_JUMP = -5
PIPE_VELOCITY = -4
PIPE_GAP = 100
PIPE_FREQUENCY = 1500

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (76, 175, 80)
RED = (200, 0, 0)
BLUE = (66, 133, 244)
YELLOW = (240, 210, 0)

# Difficulty levels
EASY = 0
MEDIUM = 1
HARD = 2

# Set up the game window
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
CLOCK = pygame.time.Clock()


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for development and PyInstaller.

    Parameters
    ----------
    relative_path : str
        Relative path to the resource.

    Returns
    -------
    str
        Absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Use getattr to avoid attribute access error since _MEIPASS only exists when bundled
        base_path: str = getattr(sys, "_MEIPASS", os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_image(name: str) -> pygame.Surface:
    """
    Load an image from the assets/sprites directory.

    Parameters
    ----------
    name : str
        Filename of the image to load.

    Returns
    -------
    pygame.Surface
        Loaded image as a pygame Surface.
    """
    return pygame.image.load(
        resource_path(os.path.join("assets", "sprites", name))
    ).convert_alpha()


_sound_cache: dict[str, pygame.mixer.Sound] = {}


def load_audio(name: str) -> pygame.mixer.Sound:
    """
    Load an audio file and cache it for future use.

    Parameters
    ----------
    name : str
        Filename of the audio file to load.

    Returns
    -------
    pygame.mixer.Sound
        Loaded sound object.
    """
    global _sound_cache

    if name not in _sound_cache:
        sound: pygame.mixer.Sound = pygame.mixer.Sound(
            resource_path(os.path.join("assets", "audio", name))
        )
        _sound_cache[name] = sound

        sound.set_volume(GAME_SETTINGS.volume)
    return _sound_cache[name]


def update_all_sounds_volume(volume: float) -> None:
    """
    Update volume for all cached sounds.

    Parameters
    ----------
    volume : float
        Volume level to set for all sounds (0.0 to 1.0).

    Returns
    -------
    None
    """
    for sound in _sound_cache.values():
        sound.set_volume(volume)
