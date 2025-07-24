"""
UI constants for Flappy Bird.

This module defines common UI elements like fonts, colors, and styling to ensure
consistency across the entire game.
"""

import pygame

from src.constants import BLUE, GREEN, RED, WHITE, YELLOW

# Initialize pygame font system
pygame.font.init()

# Font definitions
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_LARGE = pygame.font.Font(None, 48)
FONT_XL = pygame.font.Font(None, 64)


# Button styling
BUTTON_TEXT_COLOR = WHITE
BUTTON_PRIMARY_COLOR = GREEN
BUTTON_SECONDARY_COLOR = BLUE
BUTTON_DANGER_COLOR = RED
BUTTON_PADDING = 10

# UI Spacing
MARGIN_SMALL = 10
MARGIN_MEDIUM = 20
MARGIN_LARGE = 40

# Animation timings (in seconds)
FLASH_SPEED_SLOW = 0.8
FLASH_SPEED_MEDIUM = 0.5
FLASH_SPEED_FAST = 0.3

# Z-order for layering UI elements
Z_BACKGROUND = 0
Z_GAME_ELEMENTS = 10
Z_UI_BASE = 20
Z_UI_ELEMENTS = 30
Z_OVERLAY = 40
Z_POPUP = 50

# High score styling
HIGH_SCORE_COLOR = YELLOW
HIGH_SCORE_FLASH_SPEED = FLASH_SPEED_MEDIUM
