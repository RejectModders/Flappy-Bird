import datetime

import pygame

from src.constants import BLACK, SCREEN_WIDTH, load_image
from src.ui_constants import (
    BUTTON_PRIMARY_COLOR,
    BUTTON_TEXT_COLOR,
    FONT_LARGE,
    FONT_SMALL,
    HIGH_SCORE_COLOR,
)


def time_based_background() -> pygame.Surface:
    """
    Return the background image based on the local time (day or night).

    Returns
    -------
    pygame.Surface
        The loaded background image as a pygame Surface. Daytime background is used between 6 AM and 6 PM, otherwise night background is used.
    """
    current_hour = datetime.datetime.now().hour
    is_daytime = 6 <= current_hour < 18
    return load_image(f"background-{'day' if is_daytime else 'night'}.png")


class Button:
    """
    A clickable button UI element with hover effects.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        text_color: tuple[int, int, int] = BUTTON_TEXT_COLOR,
        bg_color: tuple[int, int, int] = BUTTON_PRIMARY_COLOR,
        hover_color: tuple[int, int, int] | None = None,
    ) -> None:
        """
        Initialize a Button instance.

        Parameters
        ----------
        x : int
            X coordinate of the button.
        y : int
            Y coordinate of the button.
        width : int
            Width of the button.
        height : int
            Height of the button.
        text : str
            Text to display on the button.
        text_color : tuple[int, int, int], optional
            RGB color for the text, by default BUTTON_TEXT_COLOR.
        bg_color : tuple[int, int, int], optional
            RGB color for the button background, by default BUTTON_PRIMARY_COLOR.
        hover_color : tuple[int, int, int], optional
            RGB color for the button when hovered, by default computed from bg_color.
        """
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
        self.font: pygame.font.Font = FONT_SMALL

    def update(self, mouse_pos: tuple[int, int]) -> None:
        """
        Update the button's hover state based on mouse position.

        Parameters
        ----------
        mouse_pos : tuple[int, int]
            Current mouse position (x, y).
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the button on.
        """
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos: tuple[int, int], click: bool) -> bool:
        """
        Determine if the button is clicked.

        Parameters
        ----------
        mouse_pos : tuple[int, int]
            Current mouse position (x, y).
        click : bool
            Whether a mouse click occurred.

        Returns
        -------
        bool
            True if button is clicked, False otherwise.
        """
        return self.rect.collidepoint(mouse_pos) and click


class ScoreDisplay:
    """
    Displays the current score during gameplay and final score in game over.
    """

    def __init__(self) -> None:
        """
        Initialize a ScoreDisplay instance.
        """
        self.font: pygame.font.Font = FONT_LARGE
        self.digit_images: list[pygame.Surface] = [
            load_image(f"{i}.png") for i in range(10)
        ]
        self.digit_width: int = self.digit_images[0].get_width()

    def draw_score(
        self,
        surface: pygame.Surface,
        score: int,
        x: int | None = None,
        y: int = 50,
    ) -> None:
        """
        Draw the score using digit sprites.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the score on.
        score : int
            The score to display.
        x : int, optional
            X coordinate for the score, centered if None.
        y : int, optional
            Y coordinate for the score, default is 50px from top.
        """
        score_str = str(score)
        total_width = len(score_str) * self.digit_width

        if x is None:
            x = (SCREEN_WIDTH - total_width) // 2

        for i, digit in enumerate(score_str):
            digit_img = self.digit_images[int(digit)]
            surface.blit(digit_img, (x + i * self.digit_width, y))

    def draw_text_score(
        self, surface: pygame.Surface, text: str, score: int, x: int, y: int
    ) -> None:
        """
        Draw a text label and score.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw on.
        text : str
            The label text to display.
        score : int
            The score value to display.
        x : int
            X coordinate.
        y : int
            Y coordinate.
        """
        text_surf = self.font.render(
            f"{text}: {score}", True, HIGH_SCORE_COLOR
        )
        surface.blit(text_surf, (x, y))


class Slider:
    """
    A horizontal slider UI element for adjusting numeric values.

    Attributes
    ----------
    x : int
        X coordinate of the slider.
    y : int
        Y coordinate of the slider.
    width : int
        Width of the slider track.
    height : int
        Height of the slider track.
    min_value : float
        Minimum value the slider can represent.
    max_value : float
        Maximum value the slider can represent.
    value : float
        Current value of the slider.
    handle_radius : int
        Radius of the slider handle in pixels.
    track_color : tuple[int, int, int]
        RGB color of the slider track.
    handle_color : tuple[int, int, int]
        RGB color of the slider handle.
    active_color : tuple[int, int, int]
        RGB color of the active portion of the track.
    is_dragging : bool
        Whether the slider is currently being dragged.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_value: float = 0.0,
        max_value: float = 1.0,
        initial_value: float = 0.5,
        track_color: tuple[int, int, int] = (100, 100, 100),
        handle_color: tuple[int, int, int] = BUTTON_TEXT_COLOR,
        active_color: tuple[int, int, int] = BUTTON_PRIMARY_COLOR,
    ) -> None:
        """
        Initialize a Slider instance.

        Parameters
        ----------
        x : int
            X coordinate of the slider.
        y : int
            Y coordinate of the slider.
        width : int
            Width of the slider track.
        height : int
            Height of the slider track.
        min_value : float, optional
            Minimum value the slider can represent. Default is 0.0.
        max_value : float, optional
            Maximum value the slider can represent. Default is 1.0.
        initial_value : float, optional
            Initial value of the slider. Default is 0.5.
        track_color : tuple[int, int, int], optional
            RGB color of the slider track. Default is gray.
        handle_color : tuple[int, int, int], optional
            RGB color of the slider handle. Default is white.
        active_color : tuple[int, int, int], optional
            RGB color of the active portion of the track. Default is green.
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.value: float = max(min_value, min(max_value, initial_value))
        self.handle_radius: float = height * 1.2
        self.track_color: tuple[int, int, int] = track_color
        self.handle_color: tuple[int, int, int] = handle_color
        self.active_color: tuple[int, int, int] = active_color
        self.is_dragging: bool = False

    def get_handle_position(self) -> int:
        """
        Calculate the handle's x-position based on the current value.

        Returns
        -------
        int
            X-coordinate of the handle's center.
        """
        value_range = self.max_value - self.min_value
        if value_range == 0:
            return self.x
        value_ratio = (self.value - self.min_value) / value_range
        return int(self.x + value_ratio * self.width)

    def set_value_from_position(self, x_pos: int) -> None:
        """
        Set the slider value based on a given x-position.

        Parameters
        ----------
        x_pos : int
            X-coordinate to calculate value from.
        """
        x_pos = max(self.x, min(self.x + self.width, x_pos))
        value_ratio = (x_pos - self.x) / self.width
        self.value = self.min_value + value_ratio * (
            self.max_value - self.min_value
        )

    def handle_event(
        self, event: pygame.event.Event, mouse_pos: tuple[int, int]
    ) -> bool:
        """
        Handle pygame events for the slider.

        Parameters
        ----------
        event : pygame.event.Event
            Pygame event to process.
        mouse_pos : tuple[int, int]
            Current mouse position.

        Returns
        -------
        bool
            True if the slider value was changed, False otherwise.
        """
        handle_x = self.get_handle_position()
        handle_rect = pygame.Rect(
            handle_x - self.handle_radius,
            self.y - self.handle_radius // 2,
            self.handle_radius * 2,
            self.handle_radius * 2,
        )

        value_changed = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                value_changed = True
            elif (
                self.x <= mouse_pos[0] <= self.x + self.width
                and self.y - self.height
                <= mouse_pos[1]
                <= self.y + self.height * 2
            ):
                self.set_value_from_position(mouse_pos[0])
                self.is_dragging = True
                value_changed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                value_changed = True

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.set_value_from_position(mouse_pos[0])
            value_changed = True

        return value_changed

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the slider on the given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw the slider on.
        """
        track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(
            surface,
            self.track_color,
            track_rect,
            border_radius=self.height // 2,
        )

        handle_x = self.get_handle_position()
        active_width = handle_x - self.x
        if active_width > 0:
            active_rect = pygame.Rect(
                self.x, self.y, active_width, self.height
            )
            pygame.draw.rect(
                surface,
                self.active_color,
                active_rect,
                border_radius=self.height // 2,
            )

        pygame.draw.circle(
            surface,
            self.handle_color,
            (handle_x, self.y + self.height // 2),
            self.handle_radius // 2,
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (handle_x, self.y + self.height // 2),
            self.handle_radius // 2,
            1,
        )
