from pathlib import Path
from re import findall
from typing import Optional

from modules.BaseCardType import BaseCardType, ImageMagickCommands
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class GradientLogoTitleCard(BaseCardType):
    """
    This class describes a type of CardType created by Beedman, and is 
    a modification of the StandardTitleCard class with a different
    gradient  overlay, featuring a logo and left-aligned title text
    """
    
    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 32,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,     # This class uses bottom heavy titling
    }

    """Default font and text color for episode title text"""
    TITLE_FONT = str((REF_DIRECTORY / 'Sequel-Neue.otf').resolve())
    TITLE_COLOR = '#EBEBEB'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Archive name for this card type"""
    ARCHIVE_NAME = 'Gradient Logo Style'

    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = str(RemoteFile('Beedman', 'leftgradient.png'))

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Proxima Nova Semibold.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Proxima Nova Regular.otf'
    SERIES_COUNT_TEXT_COLOR = '#CFCFCF'

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'season_text',
        'episode_text', 'hide_season_text', 'font_color', 'font_file',
        'font_interline_spacing', 'font_kerning', 'font_size',
        'font_stroke_width', 'font_vertical_shift', 'logo', 
    )


    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            logo: Optional[str] = None,
            **unused) -> None:
        """
        Construct a new instance of this card.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source_file
        self.output_file = card_file
        self.logo = Path(logo) if logo is not None else None

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text.upper())
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        self.hide_season_text = hide_season_text or len(season_text) == 0

        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift


    @property
    def logo_command(self) -> ImageMagickCommands:
        """
        Get the ImageMagick commands to add the resized logo to the
        source image.

        Returns:
            List of ImageMagick commands.
        """

        return [
            # Resize logo
            f'\( "{self.logo.resolve()}"',
            f'-trim',
            f'+repage',
            f'-resize x650',
            f'-resize 1155x650\> \)',
            # Overlay resized logo
            f'-gravity northwest',
            f'-define colorspace:auto-grayscale=false',
            f'-type TrueColorAlpha',  
            f'-geometry "+50+50"',
            f'-composite',
        ]


    @property
    def title_text_command(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        center gravity.

        Returns:
            List of ImageMagick commands.
        """

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.font_interline_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 125 + self.font_vertical_shift

        return [
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +50+{vertical_shift} "{self.title_text}"',
            f'-fill "{self.font_color}"',
            f'-annotate +50+{vertical_shift} "{self.title_text}"',
        ]


    @property
    def index_text_command(self) -> ImageMagickCommands:
        """
        Get the ImageMagick commands required to add the index (season
        and episode) text to the image.

        Returns:
            List of ImageMagick commands.
        """

        # Season hiding, just add episode text
        if self.hide_season_text:
            return [
                f'-kerning 5.42',
                f'-pointsize 67.75',
                f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
                f'-gravity southwest',
                f'-fill black',
                f'-stroke black',
                f'-strokewidth 6',
                f'-annotate +50+50 "{self.episode_text}"',
                f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-strokewidth 0.75',
                f'-annotate +50+50 "{self.episode_text}"',
            ]

        return [
            f'-background transparent',
            f'+interword-spacing',
            f'-kerning 5.42',
            f'-pointsize 67.75',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
            f'\( -gravity center',
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'label:"{self.season_text} •"',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'label:"{self.episode_text}"',
            f'+smush 30 \)',
            f'-gravity southwest',
            f'-geometry +50+50',
            f'-composite',
            f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-strokewidth 0.75',
            f'\( -gravity center',
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'label:"{self.season_text} •"',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'label:"{self.episode_text}"',
            f'+smush 30 \)',
            f'-gravity southwest',
            f'-geometry +50+50',
            f'-composite',
        ]


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given arguments represent a custom font
        for this card.

        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.color != GradientLogoTitleCard.TITLE_COLOR)
            or (font.file != GradientLogoTitleCard.TITLE_FONT)
            or (font.interline_spacing != 0)
            or (font.kerning != 1.0)
            or (font.size != 1.0)
            or (font.stroke_width != 1.0)
            or (font.vertical_shift != 0)
        )


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool, episode_text_format: str) -> bool:
        """
        Determines whether the given attributes constitute custom or
        generic season titles.

        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.

        Returns:
            True if custom season titles are indicated, False otherwise.
        """

        standard_etf = GradientLogoTitleCard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map
                or episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """
        
        # Skip card if logo doesn't exist
        if self.logo is None:
            log.error(f'Logo file not specified')
            return None
        elif not self.logo.exists():
            log.error(f'Logo file "{self.logo.resolve()}" does not exist')
            return None

        command = ' '.join([
            f'convert',
            # Resize source image
            f'"{self.source_file.resolve()}"',
            *self.resize_and_style,
            # Overlay gradient
            f'"{self.__GRADIENT_IMAGE}"',
            f'-composite',
            # Overlay resized logo
            *self.logo_command,
            # Put title text
            *self.title_text_command,
            # Put season/episode text
            *self.index_text_command,
            # Create and resize output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)