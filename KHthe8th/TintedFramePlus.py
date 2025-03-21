from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

from pydantic import FilePath, PositiveFloat, PositiveInt, root_validator

from app.schemas.card_type import BaseCardTypeAllText
from modules.Debug import log
from modules.BaseCardType import (
    BaseCardType,
    CardDescription,
    Coordinate,
    Extra,
    ImageMagickCommands,
    Rectangle,
)
from modules.Title import SplitCharacteristics

if TYPE_CHECKING:
    from app.models.preferences import Preferences
    from modules.Font import Font


class TintedFramePlus(BaseCardType):
    """
    CardType that produces title cards featuring a rectangular frame
    with blurred content on the edges of the frame, and unblurred
    content within. The frame itself can be intersected by title text,
    index text, or a logo at the top and bottom.
    """

    API_DETAILS = CardDescription(
        name='Tinted Frame+',
        identifier='KHthe8th/TintedFramePlus',
        example=(
            'https://github.com/khthe8th/TitleCardMaker-CardTypes/assets/'
            '5308389/d089a1b1-7458-4eaf-ad8d-59c7f332a7c1'
        ),
        creators=['CollinHeist', 'KHthe8th'],
        source='remote',
        supports_custom_fonts=True,
        supports_custom_seasons=True,
        supported_extras=[],
        description=[
            'A combination of the TintedFrameTitleCard and the Standard for '
            'the best of both worlds.', 'It has many of the same extras you '
            'can pass to tinted frame, but it adds the episode title text '
            'above the bottom frame element (this is not modifiable). The top '
            'element will default to logo now, and title is no longer an '
            'option (as it is always shown above the bottom element).',
        ]
    )

    class CardModel(BaseCardTypeAllText):
        logo_file: Path
        font_color: str = 'white'
        font_file: FilePath
        font_interline_spacing: int = 0
        font_interword_spacing: int = 0
        font_kerning: float = 1.0
        font_size: PositiveFloat = 1.0
        font_vertical_shift: int = 0
        separator: str = '-'
        episode_text_color: Optional[str] = None
        episode_text_font: Path = BaseCardType.BASE_REF_DIRECTORY / 'tinted_frame' / 'Galey Semi Bold.ttf'
        episode_text_font_size: PositiveFloat = 1.0
        episode_text_vertical_shift: int = 0
        frame_color: Optional[str] = None
        frame_width: PositiveInt = 3
        top_element: Literal['index', 'logo', 'omit'] = 'logo'
        middle_element: Literal['logo', 'omit'] = 'omit'
        bottom_element: Literal['index', 'logo', 'omit'] = 'index'
        logo_size: PositiveFloat = 1.0
        blur_edges: bool = True

        @root_validator(skip_on_failure=True)
        def validate_episode_text_font_file(cls, values: dict) -> dict:
            etf = Path(values['episode_text_font'])
            # Episode text font does not exist, search alongside source image
            if not Path(etf).exists():
                if (new_etf := values['source_file'].parent / etf.name).exists():
                    values['episode_text_font'] = new_etf
            if not Path(values['episode_text_font']).exists():
                raise ValueError(f'Specified Episode Text Font does not exist')

            return values

        @root_validator(skip_on_failure=True)
        def validate_extras(cls, values: dict) -> dict:
            # Logo indicated, verify it exists
            top = values['top_element']
            middle = values['middle_element']
            bottom = values['bottom_element']
            if ((top == 'logo' or middle == 'logo' or bottom == 'logo')
                and not values['logo_file'].exists()):
                raise ValueError('Logo file indicated and does not exist')

            # Verify no two elements are the same
            if ((top != 'omit' and top in (middle, bottom))
                or (middle != 'omit' and (middle == bottom))):
                raise ValueError('Top/middle/bottom elements cannot be the same')

            # Convert None colors to the default font color
            if values['episode_text_color'] is None:
                values['episode_text_color'] = values['font_color']
            if values['frame_color'] is None:
                values['frame_color'] = values['font_color']

            return values

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = BaseCardType.BASE_REF_DIRECTORY / 'tinted_frame'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS: SplitCharacteristics = {
        'max_line_width': 35,
        'max_line_count': 2,
        'style': 'top',
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str((REF_DIRECTORY / 'Galey Semi Bold.ttf').resolve())
    TITLE_COLOR = 'white'
    DEFAULT_FONT_CASE = 'upper'
    FONT_REPLACEMENTS = {}

    """Characteristics of the episode text"""
    EPISODE_TEXT_COLOR = TITLE_COLOR
    EPISODE_TEXT_FONT = REF_DIRECTORY / 'Galey Semi Bold.ttf'

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'Tinted Frame (Plus) Style'

    """How many pixels from the image edge the box is placed; and box width"""
    BOX_OFFSET = 185
    BOX_WIDTH = 3

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'season_text',
        'episode_text', 'hide_season_text', 'hide_episode_text', 'font_file',
        'font_size', 'font_color', 'font_interline_spacing',
        'font_interword_spacing', 'font_kerning', 'font_stroke_width',
        'font_vertical_shift', 'episode_text_color', 'stroke_color','separator',
        'frame_color', 'logo', 'top_element', 'middle_element',
        'bottom_element', 'logo_size', 'blur_edges', 'episode_text_font',
        'frame_width', 'episode_text_font_size', 'episode_text_vertical_shift',
    )


    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            logo_file: Optional[Path],
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_interword_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
			font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            separator: str = '-',
            stroke_color: str = 'black',
            episode_text_color: str = None,
            episode_text_font: Path = EPISODE_TEXT_FONT,
            episode_text_font_size: float = 1.0,
            episode_text_vertical_shift: int = 0,
            frame_color: str = None,
            frame_width: int = BOX_WIDTH,
            top_element: Literal['index', 'logo', 'omit'] = 'logo',
            middle_element: Literal['logo', 'omit'] = 'omit',
            bottom_element: Literal['index', 'logo', 'omit'] = 'index',
            logo_size: float = 1.0,
            blur_edges: bool = True,
            preferences: Optional['Preferences'] = None,
            **unused,
        ) -> None:
        """Construct a new instance of this Card."""

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        self.source_file = source_file
        self.output_file = card_file
        self.logo = logo_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text)
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_season_text = hide_season_text
        self.hide_episode_text = hide_episode_text

        # Font/card customizations
        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_interword_spacing = font_interword_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift

        # Optional extras
        self.blur_edges = blur_edges
        self.bottom_element = bottom_element
        self.episode_text_color = episode_text_color
        self.episode_text_font = episode_text_font
        self.episode_text_font_size = episode_text_font_size
        self.episode_text_vertical_shift = episode_text_vertical_shift
        self.frame_color = frame_color
        self.frame_width = frame_width
        self.middle_element = middle_element
        self.logo_size = logo_size
        self.stroke_color = stroke_color
        self.top_element = top_element
        self.separator = separator


    @property
    def blur_commands(self) -> ImageMagickCommands:
        """Subcommand to blur the outer frame of the source image."""

        # Blurring is disabled (or being applied globally), return empty command
        if not self.blur_edges or self.blur:
            return []

        crop_width = self.WIDTH - (2 * self.BOX_OFFSET) - 6 # 6px margin
        crop_height = self.HEIGHT - (2 * self.BOX_OFFSET) - 4 # 4px margin

        return [
            # Blur entire image
            f'-blur 0x20',
            # Crop out center area of the source image
            f'-gravity center',
            fr'\(',
            f'"{self.source_file.resolve()}"',
            *self.resize_and_style,
            f'-crop {crop_width}x{crop_height}+0+0',
            f'+repage',
            fr'\)',
            # Overlay unblurred center area
            f'-composite',
        ]


    @property
    def index_text_commands(self) -> ImageMagickCommands:
        """Subcommand for adding index text to the source image."""

        # If not showing index text, or all text is hidden, return
        if ((self.top_element != 'index' and self.bottom_element != 'index')
            or (self.hide_season_text and self.hide_episode_text)):
            return []

        # Set index text based on which text is hidden/not
        if self.hide_season_text:
            index_text = self.episode_text
        elif self.hide_episode_text:
            index_text = self.season_text
        else:
            index_text = f'{self.season_text} {self.separator} {self.episode_text}'

        # Determine vertical position based on which element this text is
        if self.top_element == 'index':
            vertical_shift = -708
        else:
            vertical_shift = 722
        vertical_shift += self.episode_text_vertical_shift

        return [
            f'-background transparent',
            fr'\(',
            f'-font "{self.episode_text_font.resolve()}"',
            f'+kerning',
            f'+interline-spacing',
            f'+interword-spacing',
            f'-pointsize {60 * self.episode_text_font_size}',
            f'-fill "{self.episode_text_color}"',
            f'label:"{index_text}"',
            # Create drop shadow
            fr'\(',
            f'+clone',
            f'-shadow 80x3+6+6',
            fr'\)',
            # Position shadow below text
            f'+swap',
            f'-layers merge',
            f'+repage',
            fr'\)',
            # Overlay text and shadow onto source image
            f'-gravity center',
            f'-geometry +0{vertical_shift:+}',
            f'-composite',
        ]


    @property
    def logo_commands(self) -> ImageMagickCommands:
        """Subcommands for adding the logo to the image."""

        # Logo not indicated or not available, return empty commands
        if ((self.top_element != 'logo'
             and self.middle_element != 'logo'
             and self.bottom_element != 'logo')
            or self.logo is None or not self.logo.exists()):
            return []

        # Determine vertical position based on which element the logo is
        if self.top_element == 'logo':
            vertical_shift = -720
        elif self.middle_element == 'logo':
            vertical_shift = 0
        elif self.bottom_element == 'logo':
            vertical_shift = 700
        else:
            vertical_shift = 0

        # Determine logo height
        if self.middle_element == 'logo':
            logo_height = 350 * self.logo_size
        else:
            logo_height = 150 * self.logo_size

        # Determine resizing for the logo
        if self.middle_element == 'logo':
            # Constrain by width and height
            resize_command = [
                f'-resize x{logo_height}',
                fr'-resize {2500 * self.logo_size}x{logo_height}\>',
            ]
        else:
            resize_command = [f'-resize x{logo_height}']

        return [
            fr'\(',
            f'"{self.logo.resolve()}"',
            *resize_command,
            fr'\)',
            f'-gravity center',
            f'-geometry +0{vertical_shift:+}',
            f'-composite',
        ]


    @property
    def _frame_top_commands(self) -> ImageMagickCommands:
        """
        Subcommand to add the top of the frame, intersected by the
        selected element.
        """

        # Coordinates used by multiple rectangles
        INSET = self.BOX_OFFSET
        BOX_WIDTH = self.frame_width
        TopLeft = Coordinate(INSET, INSET)
        TopRight = Coordinate(self.WIDTH - INSET, INSET + BOX_WIDTH)

        # This frame is uninterrupted, draw single rectangle
        if (self.top_element == 'omit'
            or (self.top_element == 'index'
                and self.hide_season_text and self.hide_episode_text)
            or (self.top_element == 'logo'
                and (self.logo is None or not self.logo.exists()))):

            return [Rectangle(TopLeft, TopRight).draw()]

        # Element is index text
        if self.top_element == 'index':
            element_width, _ = self.image_magick.get_text_dimensions(
                self.index_text_commands,
            )
            margin = 25
        # Element is logo
        elif self.top_element == 'logo':
            element_width, logo_height = self.image_magick.get_image_dimensions(
                self.logo
            )
            element_width /= logo_height / 150
            element_width *= self.logo_size
            margin = 25

        # Determine bounds based on element width
        left_box_x = (self.WIDTH - element_width) / 2 - margin
        right_box_x = (self.WIDTH + element_width) / 2 + margin

        # If the boundaries are wider than the start of the frame, draw nothing
        if left_box_x < INSET or right_box_x > (self.WIDTH - INSET):
            return []

        # Create Rectangles for these two frame sections
        top_left_rectangle = Rectangle(
            TopLeft,
            Coordinate(left_box_x, INSET + BOX_WIDTH)
        )
        top_right_rectangle = Rectangle(
            Coordinate(right_box_x, INSET),
            TopRight,
        )

        return [
            top_left_rectangle.draw(),
            top_right_rectangle.draw()
        ]


    @property
    def _frame_bottom_commands(self) -> ImageMagickCommands:
        """
        Subcommand to add the bottom of the frame, intersected by the
        selected element.
        """

        # Coordinates used by multiple rectangles
        INSET = self.BOX_OFFSET
        BOX_WIDTH = self.frame_width
        # BottomLeft = Coordinate(INSET + BOX_WIDTH, self.HEIGHT - INSET)
        BottomRight = Coordinate(self.WIDTH - INSET, self.HEIGHT - INSET)

        # This frame is uninterrupted, draw single rectangle
        if (self.bottom_element == 'omit'
            or (self.bottom_element == 'index'
                and self.hide_season_text and self.hide_episode_text)
            or (self.bottom_element == 'logo'
                and (self.logo is None or not self.logo.exists()))):

            return [
                Rectangle(
                    Coordinate(INSET, self.HEIGHT - INSET - BOX_WIDTH),
                    BottomRight
                ).draw()
            ]

        # Element is index text
        if self.bottom_element == 'index':
            element_width, _ = self.image_magick.get_text_dimensions(
                self.index_text_commands,
            )
            margin = 25
        # Element is logo
        elif self.bottom_element == 'logo':
            element_width, logo_height = self.image_magick.get_image_dimensions(
                self.logo
            )
            element_width /= logo_height / 150
            element_width *= self.logo_size
            margin = 25

        # Determine bounds based on element width
        left_box_x = (self.WIDTH / 2) - (element_width / 2) - margin
        right_box_x = (self.WIDTH / 2) + (element_width / 2) + margin

        # If the boundaries are wider than the start of the frame, draw nothing
        if left_box_x < INSET or right_box_x > (self.WIDTH - INSET):
            return []

        # Create Rectangles for these two frame sections
        bottom_left_rectangle = Rectangle(
            Coordinate(INSET, self.HEIGHT - INSET - BOX_WIDTH),
            Coordinate(left_box_x, self.HEIGHT - INSET)
        )
        bottom_right_rectangle = Rectangle(
            Coordinate(right_box_x, self.HEIGHT - INSET - BOX_WIDTH),
            BottomRight,
        )

        return [
            bottom_left_rectangle.draw(),
            bottom_right_rectangle.draw(),
        ]


    @property
    def frame_commands(self) -> ImageMagickCommands:
        """
        Subcommands to add the box that separates the outer (blurred)
        image and the interior (unblurred) image. This box features a
        drop shadow. The top and bottom parts of the frame are
        optionally intersected by a index text, title text, or a logo.
        """

        # Coordinates used by multiple rectangles
        INSET = self.BOX_OFFSET
        BOX_WIDTH = self.frame_width
        TopLeft = Coordinate(INSET, INSET)
        # TopRight = Coordinate(self.WIDTH - INSET, INSET + BOX_WIDTH)
        BottomLeft = Coordinate(INSET + BOX_WIDTH, self.HEIGHT - INSET)
        BottomRight = Coordinate(self.WIDTH - INSET, self.HEIGHT - INSET)

        # Determine frame draw commands
        top = self._frame_top_commands
        left = [Rectangle(TopLeft, BottomLeft).draw()]
        right = [
            Rectangle(
                Coordinate(self.WIDTH - INSET - BOX_WIDTH, INSET),
                BottomRight,
            ).draw()
        ]
        bottom = self._frame_bottom_commands

        return [
            # Create blank canvas
            fr'\(',
            f'-size {self.TITLE_CARD_SIZE}',
            f'xc:transparent',
            # Draw all sets of rectangles
            f'+stroke',
            f'-fill "{self.frame_color}"',
            *top, *left, *right, *bottom,
            fr'\(',
            f'+clone',
            f'-shadow 80x3+4+4',
            fr'\)',
            # Position drop shadow below rectangles
            f'+swap',
            f'-layers merge',
            f'+repage',
            fr'\)',
            # Overlay box and shadow onto source image
            f'-geometry +0+0',
            f'-composite',
        ]


    @staticmethod
    def modify_extras(
            extras: dict,
            custom_font: bool,
            custom_season_titles: bool,
        ) -> None:
        """
        Modify the given extras based on whether font or season titles
        are custom.

        Args:
            extras: Dictionary to modify.
            custom_font: Whether the font are custom.
            custom_season_titles: Whether the season titles are custom.
        """

        # Generic font, reset episode text and box colors
        if not custom_font:
            for extra in (
                'episode_text_color',
                'episode_text_font',
                'episode_text_font_size',
                'episode_text_vertical_shift',
                'frame_color',
            ):
                if extra in extras:
                    del extras[extra]


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determine whether the given font characteristics constitute a
        default or custom font.

        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return TintedFramePlus._is_custom_font(font)


    @property
    def black_title_commands(self) -> ImageMagickCommands:
        """
        Subcommands for adding the black stroke behind the title text.
        """

        # Stroke disabled, return empty command
        if self.font_stroke_width == 0:
            return []

        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 245 + self.font_vertical_shift

        return [
            f'-fill "{self.stroke_color}"',
            f'-stroke "{self.stroke_color}"',
            f'-strokewidth {stroke_width}',
            f'-annotate +0+{vertical_shift} "{self.title_text}"',
        ]


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool,
            episode_text_format: str,
        ) -> bool:
        """
        Determine whether the given attributes constitute custom or
        generic season titles.

        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.

        Returns:
            True if custom season titles are indicated, False otherwise.
        """

        return (
            custom_episode_map
            or episode_text_format != TintedFramePlus.EPISODE_TEXT_FORMAT
        )


    def create(self) -> None:
        """Create this object's defined title card."""

        # Font customizations
        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.font_interline_spacing
        interword_spacing = 50 + self.font_interword_spacing
        kerning = -1.25 * self.font_kerning
        vertical_shift = 245 + self.font_vertical_shift
 
        self.image_magick.run([
            f'convert "{self.source_file.resolve()}"',
            # Resize and apply styles to source image
            *self.resize_and_style,
            # Add blurred edges (if indicated)
            *self.blur_commands,
			# Global title text options
            f'-gravity south',
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing {interword_spacing}',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
			# Black stroke behind title text
            *self.black_title_commands,
			# Title text
            f'-fill "{self.font_color}"',
            f'-annotate +0+{vertical_shift} "{self.title_text}"',
            *self.index_text_commands,
            *self.logo_commands,
            *self.frame_commands,
            # Attempt to overlay mask
            *self.add_overlay_mask(self.source_file),
            # Create card
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])
