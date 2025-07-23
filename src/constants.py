import json
import os

import pygame

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
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (240, 210, 0)

# Game states
LOADING = 0
MAIN_MENU = 1
PLAYING = 2
GAME_OVER = 3
SETTINGS = 4
STATS = 5

# Difficulty levels
EASY = 0
MEDIUM = 1
HARD = 2

# Set up the game window
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
CLOCK = pygame.time.Clock()


# Load assets
def load_image(name):
    return pygame.image.load(
        os.path.join("assets", "sprites", name)
    ).convert_alpha()


def load_audio(name):
    return pygame.mixer.Sound(os.path.join("assets", "audio", name))


# Game settings and high score manager
class Settings:
    def __init__(self):
        self.settings_file = "game_data.json"
        self.difficulty = EASY

        # Store separate high scores for each difficulty level
        self.high_scores = {EASY: 0, MEDIUM: 0, HARD: 0}

        self.bird_type = "yellow"
        self.pipe_color = "green"
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.difficulty = data.get("difficulty", EASY)

                    # Load high scores with backwards compatibility
                    if "high_scores" in data:
                        # Convert string keys to integers if needed
                        self.high_scores = {
                            int(k) if isinstance(k, str) else k: v
                            for k, v in data["high_scores"].items()
                        }
                    else:
                        # Support old save format with single high score
                        old_high_score = data.get("high_score", 0)
                        self.high_scores = {
                            EASY: old_high_score,
                            MEDIUM: 0,
                            HARD: 0,
                        }

                    # Make sure all difficulty levels exist in high_scores
                    for diff in [EASY, MEDIUM, HARD]:
                        if diff not in self.high_scores:
                            self.high_scores[diff] = 0

                    self.bird_type = data.get("bird_type", "yellow")
                    self.pipe_color = data.get("pipe_color", "green")
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Use defaults if file can't be loaded

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                data = {
                    "difficulty": self.difficulty,
                    "high_scores": self.high_scores,
                    "bird_type": self.bird_type,
                    "pipe_color": self.pipe_color,
                }
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

        # Update bird and pipe colors based on difficulty
        if difficulty == EASY:
            self.bird_type = "yellow"
            self.pipe_color = "green"
        elif difficulty == MEDIUM:
            self.bird_type = "blue"
            self.pipe_color = "green"
        elif difficulty == HARD:
            self.bird_type = "red"
            self.pipe_color = "red"

        self.save_settings()

    def update_high_score(self, score):
        current_difficulty = self.difficulty
        if score > self.high_scores[current_difficulty]:
            self.high_scores[current_difficulty] = score
            self.save_settings()
            return True
        return False

    def get_high_score(self, difficulty=None):
        """Get high score for specified difficulty or current difficulty if None"""
        if difficulty is None:
            difficulty = self.difficulty
        return self.high_scores[difficulty]

    def get_difficulty_name(self):
        if self.difficulty == EASY:
            return "Easy"
        elif self.difficulty == MEDIUM:
            return "Medium"
        else:
            return "Hard"

    def get_difficulty_color(self):
        if self.difficulty == EASY:
            return YELLOW
        elif self.difficulty == MEDIUM:
            return BLUE
        else:
            return RED

    def get_pipe_gap(self):
        # Adjust pipe gap based on difficulty
        if self.difficulty == EASY:
            return 120
        elif self.difficulty == MEDIUM:
            return 100
        else:
            return 85

    def get_pipe_frequency(self):
        # Adjust pipe frequency based on difficulty
        if self.difficulty == EASY:
            return 1800
        elif self.difficulty == MEDIUM:
            return 1500
        else:
            return 1200

    def get_gravity(self):
        # Adjust gravity based on difficulty
        if self.difficulty == EASY:
            return 0.2
        elif self.difficulty == MEDIUM:
            return 0.25
        else:
            return 0.3


# Create global settings instance
GAME_SETTINGS = Settings()
