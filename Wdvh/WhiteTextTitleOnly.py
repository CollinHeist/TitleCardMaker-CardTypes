from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class WhiteTextTitleOnly(BaseCardType):
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

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'White Text Title Only Style'
    
    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = REF_DIRECTORY / 'GRADIENT.png'

    """Paths to intermediate files that are deleted after the card is created"""
    __SOURCE_WITH_GRADIENT = BaseCardType.TEMP_DIR / 'source_gradient.png'

    __slots__ = (
        'source_file', 'output_file', 'title', 'font', 'font_size',
        'title_color', 'vertical_shift', 'interline_spacing', 'kerning',
        'stroke_width'
    )


    def __init__(self,
            source: Path,
            card_file: Path,
            title: str,
            font: str,
            font_size: float,
            title_color: str,
            blur: bool = False,
            grayscale: bool = False,
            vertical_shift: int = 0,
            interline_spacing: int = 0,
            kerning: float = 1.0,
            stroke_width: float = 1.0,
            **unused) -> None:
        """
        Initialize this CardType object.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title)

        self.font = font
        self.font_size = font_size
        self.title_color = title_color
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width


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


    def _add_gradient(self) -> Path:
        """
        Add the static gradient to this object's source image.
        
        Returns:
            Path to the created image.
        """

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            *self.resize_and_style,
            f'"{self.__GRADIENT_IMAGE.resolve()}"',
            f'-background None',
            f'-layers Flatten',
            f'"{self.__SOURCE_WITH_GRADIENT.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__SOURCE_WITH_GRADIENT


    def _add_title_text(self, gradient_image: Path) -> Path:
        """
        Adds episode title text to the provide image.

        :param      gradient_image: The image with gradient added.
        
        :returns:   Path to the created image that has a gradient and the title
                    text added.
        """

        vertical_shift = 50 + self.vertical_shift

        command = ' '.join([
            f'convert "{gradient_image.resolve()}"',
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

        return ((font.file != WhiteTextTitleOnly.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != WhiteTextTitleOnly.TITLE_COLOR)
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
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
        """

        # Add the gradient to the source image (always)
        gradient_image = self._add_gradient()

        # Add either one or two lines of episode text 
        self._add_title_text(gradient_image)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(gradient_image)