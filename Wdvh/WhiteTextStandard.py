from pathlib import Path
from typing import Optional

from pydantic import FilePath
from app.schemas.base import BetterColor
from app.schemas.card_type import BaseCardTypeCustomFontAllText

from modules.BaseCardType import BaseCardType, ImageMagickCommands
from modules.RemoteFile import RemoteFile


class WhiteTextStandard(BaseCardType):
    """
    WDVH's WhiteTextStandard card type.
    """

    class CardModel(BaseCardTypeCustomFontAllText):
        font_color: BetterColor = '#FFFFFF'
        font_file: FilePath
        separator: str = '-'

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 32,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,     # This class uses bottom heavy titling
    }

    """Default font and text color for episode title text"""
    TITLE_FONT = str(RemoteFile('Wdvh', 'TerminalDosis-Bold.ttf'))
    TITLE_COLOR = '#FFFFFF'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {}

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'White Text Standard Style'

    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = REF_DIRECTORY / 'GRADIENT.png'

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    __slots__ = (
        'source_file', 'output_file', 'title', 'season_text', 'episode_text',
        'font', 'font_size', 'title_color', 'hide_season', 'separator',
        'vertical_shift', 'interline_spacing', 'kerning', 'stroke_width',
        'hide_episode',
    )


    def __init__(self,
            source_file: Path,
            card_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool,
            hide_episode_text: bool,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            separator: str = '-',
            preferences: Optional['Preferences'] = None, # type: ignore
            **unused,
        ) -> None:
        """Initialize this CardType object."""
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        self.source_file = source_file
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text)
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_season = hide_season_text
        self.hide_episode = hide_episode_text

        self.font = font_file
        self.interline_spacing = font_interline_spacing
        self.kerning = font_kerning
        self.font_size = font_size
        self.stroke_width = font_stroke_width
        self.title_color = font_color
        self.vertical_shift = font_vertical_shift

        # Extras
        self.separator = separator


    @property
    def title_text_commands(self) -> list[ImageMagickCommands]:
        """
        ImageMagick commands to add title text.

        Returns:
            List of ImageMagick commands.
        """

        font_size = 180 * self.font_size
        interline_spacing = -70 + self.interline_spacing
        kerning = -1.25 * self.kerning
        stroke_width = 4.0 * self.stroke_width
        vertical_shift = 145 + self.vertical_shift

        return [
            # Global effects
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity south',
            # Black stroke
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth {stroke_width}',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            # Normal text
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
        ]


    @property
    def index_text_commands(self) -> list[ImageMagickCommands]:
        """
        Get the ImageMagick commands required to add the index (season
        and episode) text to the image.

        Returns:
            List of ImageMagick commands.
        """

        # All text is hidden, return empty commands
        if self.hide_season and self.hide_episode:
            return []

        # Determine which text to add
        if self.hide_season:
            index_text = self.episode_text
        elif self.hide_episode:
            index_text = self.season_text
        else:
            index_text = (
                f'{self.season_text} {self.separator} {self.episode_text}'
            )

        return [
            f'-kerning 5.42',
            f'-pointsize 85',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity center',
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
            f'-annotate +0+800 "{index_text}"',
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
            f'-annotate +0+800 "{index_text}"',
        ]


    @staticmethod
    def is_custom_font(font: 'Font') -> bool: # type: ignore
        """
        Determines whether the given font characteristics constitute a
        default or custom font.
        
        Args:
            font: The Font being evaluated.
        
        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.color != WhiteTextStandard.TITLE_COLOR)
            or (font.file != WhiteTextStandard.TITLE_FONT)
            or (font.kerning != 1.0)
            or (font.interline_spacing != 0)
            or (font.size != 1.0)
            or (font.stroke_width != 1.0)
            or (font.vertical_shift != 0)
        )


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool,
            episode_text_format: str,
        ) -> bool:
        """
        Determines whether the given attributes constitute custom or
        generic season titles.
        
        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.
        
        Returns:
            True if custom season title are indicated. False otherwise.
        """

        standard_etf = WhiteTextStandard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map
                or episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
        """

        command = ' '.join([
            f'convert',
            # Resize and style source image
            f'"{self.source_file.resolve()}"',
            *self.resize_and_style,
            # Overlay gradient
            f'"{self.__GRADIENT_IMAGE.resolve()}"',
            f'-composite',
            # Add title text
            *self.title_text_commands,
            # Add index text
            *self.index_text_commands,
            # Create and resize output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
