import json
import os
from typing import cast

import appdirs

from src.constants import EASY, HARD, MEDIUM, resource_path


class Settings:
    """
    Manages game settings and high scores, including difficulty, bird type, and pipe color.

    Attributes
    ----------
    settings_file : str
        The filename for saving and loading settings.
    difficulty : int
        The current difficulty level.
    high_scores : dict of int to int
        High scores for each difficulty level.
    bird_type : str
        The current bird type.
    pipe_color : str
        The current pipe color.
    volume : float
        The game volume level (0.0 to 1.0).
    """

    def __init__(self) -> None:
        """
        Initialize the Settings object, loading settings from file if available.
        """
        app_name = "FlappyBird"

        user_data_dir = cast(str, appdirs.user_data_dir(app_name))

        os.makedirs(user_data_dir, exist_ok=True)

        self.settings_file: str = os.path.join(user_data_dir, "game_data.json")

        self.difficulty: int = EASY

        self.high_scores: dict[int, int] = {EASY: 0, MEDIUM: 0, HARD: 0}

        self.bird_type: str = "yellow"
        self.pipe_color: str = "green"
        self.volume: float = 1.0  # Default to full volume

        # For tracking changes in the settings screen
        self.has_changes: bool = False

        # Load settings from file
        self.load_settings()

    def load_settings(self) -> None:
        """
        Load settings from the settings file.
        """
        # Use resource_path to ensure it works when packaged as an executable
        settings_path = resource_path(self.settings_file)
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as file:
                    data = json.load(file)
                    self.difficulty = data.get("difficulty", EASY)
                    self.high_scores = data.get(
                        "high_scores",
                        {str(k): v for k, v in self.high_scores.items()},
                    )
                    # Convert string keys back to integers
                    self.high_scores = {
                        int(k): v for k, v in self.high_scores.items()
                    }
                    self.bird_type = data.get("bird_type", "yellow")
                    self.pipe_color = data.get("pipe_color", "green")
                    self.volume = data.get("volume", 1.0)

                # Apply loaded volume setting
                self.apply_volume()
            except (json.JSONDecodeError, IOError):
                # If there's an error reading the file, use default settings
                pass

    def save_settings(self) -> None:
        """
        Save settings to the settings file and apply them.
        """
        data = {
            "difficulty": self.difficulty,
            "high_scores": {str(k): v for k, v in self.high_scores.items()},
            "bird_type": self.bird_type,
            "pipe_color": self.pipe_color,
            "volume": self.volume,
        }
        try:
            # Use resource_path to ensure it works when packaged as an executable
            settings_path = resource_path(self.settings_file)
            # Make sure the directory exists
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, "w") as file:
                json.dump(data, file, indent=4)

            # Apply the volume settings immediately
            self.apply_volume()
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def apply_volume(self) -> None:
        """
        Apply the current volume setting to pygame mixer.
        """
        import pygame

        from src.constants import update_all_sounds_volume

        # Set the volume for all channels
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(self.volume)

        # Set music volume
        pygame.mixer.music.set_volume(self.volume)

        # Update all cached sound effects
        update_all_sounds_volume(self.volume)

    def update_high_score(self, score: int) -> bool:
        """
        Update the high score for the current difficulty if the new score is higher.

        Parameters
        ----------
        score : int
            The new score to check against the high score.

        Returns
        -------
        bool
            True if the high score was updated, False otherwise.
        """
        if score > self.high_scores[self.difficulty]:
            self.high_scores[self.difficulty] = score
            self.save_settings()
            return True
        return False

    def get_gravity(self) -> float:
        """
        Get the gravity value based on the current difficulty.

        Returns
        -------
        float
            The gravity value.
        """
        from src.constants import GRAVITY

        # Adjust gravity based on difficulty
        if self.difficulty == EASY:
            return GRAVITY * 0.8  # Easier: lower gravity
        elif self.difficulty == MEDIUM:
            return GRAVITY  # Normal gravity
        else:  # HARD
            return GRAVITY * 1.2  # Harder: higher gravity

    def get_pipe_frequency(self) -> int:
        """
        Get the pipe frequency based on the current difficulty.

        Returns
        -------
        int
            The pipe frequency in milliseconds.
        """
        from src.constants import PIPE_FREQUENCY

        # Adjust pipe frequency based on difficulty
        if self.difficulty == EASY:
            return int(PIPE_FREQUENCY * 1.2)  # Easier: less frequent pipes
        elif self.difficulty == MEDIUM:
            return PIPE_FREQUENCY  # Normal frequency
        else:  # HARD
            return int(PIPE_FREQUENCY * 0.8)  # Harder: more frequent pipes

    def set_volume(self, volume: float) -> None:
        """
        Set the game volume and apply it to pygame mixer.

        Parameters
        ----------
        volume : float
            Volume level between 0.0 (mute) and 1.0 (full volume)
        """
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        self.apply_volume()
        self.has_changes = True


# Create a global settings instance
GAME_SETTINGS = Settings()
