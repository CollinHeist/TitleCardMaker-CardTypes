from pathlib import Path
from typing import Optional

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class WhiteTextTitleOnlyLogo(BaseCardType):
    """
    This class describes Wdvh's title only title CardType.
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
    TITLE_FONT = str(RemoteFile('Wdvh', 'TerminalDosis-Bold.ttf'))
    TITLE_COLOR = '#FFFFFF'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {}

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = False

    """Whether this CardType uses unique source images"""
    USES_UNIQUE_SOURCES = False

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'White Text Title Only Logo Style'

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    """Paths to intermediate files that are deleted after the card is created"""
    __RESIZED_LOGO = BaseCardType.TEMP_DIR / 'resized_logo.png'
    __BACKDROP_WITH_LOGO = BaseCardType.TEMP_DIR / 'backdrop_logo.png'

    __slots__ = (
        'logo', 'output_file', 'title', 'font', 'font_size', 'title_color',
        'vertical_shift', 'interline_spacing', 'kerning', 'stroke_width',
        'background',
    )


    def __init__(self, *,
            card_file: Path,
            title_text: str,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_kerning: float = 1.0,
            font_interline_spacing: int = 0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            logo: Optional[str] = None, 
            background: str = '#000000',
            **unused) -> None:
        """
        Initialize this CardType object.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Convert logo to Path
        if isinstance(logo, str):
            self.logo = Path(logo)
        else:
            self.logo = None

        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title_text)

        self.font = font_file
        self.title_color = font_color
        self.interline_spacing = font_interline_spacing
        self.kerning = font_kerning
        self.font_size = font_size
        self.stroke_width = font_stroke_width
        self.vertical_shift = font_vertical_shift

        self.background = background


    def __title_text_global_effects(self) -> list[str]:
        """
        ImageMagick commands to implement the title text's global effects.
        Specifically the the font, kerning, fontsize, and center gravity.
        
        Returns:
            List of ImageMagick commands.
        """

        font_size = 180 * self.font_size
        interline_spacing = -17 + self.interline_spacing
        kerning = -1.25 * self.kerning

        return [
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity south',
        ]   


    def __title_text_black_stroke(self) -> list[str]:
        """
        ImageMagick commands to implement the title text's black stroke.
        
        Returns:
            List of ImageMagick commands.
        """

        stroke_width = 4.0 * self.stroke_width

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth {stroke_width}',
        ]


    def _resize_logo(self) -> Path:
        """
        Resize the logo into at most a 1875x1030 bounding box.
        
        Returns:
            Path to the created image.
        """

        command = ' '.join([
            f'convert',
            f'"{self.logo.resolve()}"',
            f'-resize x1030',
            f'-resize 1875x1030\>',
            f'"{self.__RESIZED_LOGO.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__RESIZED_LOGO


    def _add_logo_to_backdrop(self, resized_logo: Path) -> Path:
        """
        Add the resized logo to a fixed color backdrop.
        
        Returns:
            Path to the created image.
        """

        # Get height of the resized logo to determine offset
        height_command = ' '.join([
            f'identify',
            f'-format "%h"',
            f'"{resized_logo.resolve()}"',
        ])

        height = int(self.image_magick.run_get_output(height_command))

        # Get offset of where to place logo onto card
        offset = 60 + ((1030 - height) // 2)

        command = ' '.join([
            f'convert',
            f'-size "{self.TITLE_CARD_SIZE}"',  # Create backdrop
            f'xc:"{self.background}"',          # Fill canvas with color
            f'"{resized_logo.resolve()}"',
            f'-set colorspace sRGB',
            f'-gravity north',
            f'-geometry "+0+{offset}"',         # Put logo on backdrop
            f'-composite "{self.__BACKDROP_WITH_LOGO.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__BACKDROP_WITH_LOGO


    def _add_title_text(self, backdrop_logo: Path) -> Path:
        """
        Adds episode title text to the provide image.

        :param      backdrop_logo:  The backdrop and logo image.
        
        :returns:   Path to the created image that has the title text added.
        """

        vertical_shift = 245 + self.vertical_shift

        command = ' '.join([
            f'convert "{backdrop_logo.resolve()}"',
            *self.resize_and_style,
            *self.__title_text_global_effects(),
            *self.__title_text_black_stroke(),
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.output_file

    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given font characteristics constitute a
        default or custom font.
        
        Args:
            font: The Font being evaluated.
        
        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.file != WhiteTextTitleOnlyLogo.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != WhiteTextTitleOnlyLogo.TITLE_COLOR)
            or (font.replacements != WhiteTextTitleOnlyLogo.FONT_REPLACEMENTS)
            or (font.vertical_shift != 0)
            or (font.interline_spacing != 0)
            or (font.kerning != 1.0)
            or (font.stroke_width != 1.0))


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
            False, as custom season titles are not used.
        """

        return False


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

        # Resize logo
        resized_logo = self._resize_logo()
        
        # Create backdrop+logo image
        backdrop_logo = self._add_logo_to_backdrop(resized_logo)

        # Add either one or two lines of episode text 
        self._add_title_text(backdrop_logo)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(resized_logo,backdrop_logo)