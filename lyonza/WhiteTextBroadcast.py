from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class WhiteTextBroadcast(BaseCardType):
    """
    This class describes lyonza's CardType based on Wvdh's
    "WhiteTextBroadcast" card to show SxxExx format instead of absolute
    numbering
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
    TITLE_FONT = str(RemoteFile('lyonza', 'TerminalDosis-Bold.ttf'))
    TITLE_COLOR = '#FFFFFF'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'Broadcast Ordering Style'
    
    EPISODE_TEXT_FORMAT = "S{season_number:02}E{episode_number:02}"
    
    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = RemoteFile('lyonza', 'GRADIENTABS.png')

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = RemoteFile('lyonza', 'TerminalDosis-Bold.ttf')
    EPISODE_COUNT_FONT = RemoteFile('lyonza', 'TerminalDosis-Bold.ttf')
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    __slots__ = (
        'source_file', 'output_file', 'title', 'episode_text', 'font',
        'font_size', 'title_color', 'hide_season', 'blur', 'vertical_shift',
        'interline_spacing', 'kerning', 'stroke_width', 'episode_text_color',
    )


    def __init__(self, *,
            source: Path,
            output_file: Path,
            title: str,
            episode_text: str,
            font: str,
            font_size: float,
            title_color: str,
            blur: bool = False,
            grayscale: bool = False,
            vertical_shift: int = 0,
            interline_spacing: int = 0,
            kerning: float = 1.0,
            stroke_width: float = 1.0,
            episode_text_color: str = SERIES_COUNT_TEXT_COLOR,
            **unused) -> None:
        """
        Initialize this CardType object.

        Args:
            source: Source image to base the card on.
            output_file: Output file where to create the card.
            title: Title text to add to created card.
            episode_text: Episode text to add to created card.
            font: Font name or path (as string) to use for episode title.
            font_size: Scalar to apply to title font size.
            title_color: Color to use for title text.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            vertical_shift: Pixel count to adjust the title vertical offset by.
            interline_spacing: Pixel count to adjust title interline spacing by.
            kerning: Scalar to apply to kerning of the title text.
            stroke_width: Scalar to apply to black stroke of the title text.
            unused: Unused arguments.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source
        self.output_file = output_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title)
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())

        self.font = font
        self.font_size = font_size
        self.title_color = title_color
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width

        self.episode_text_color = episode_text_color


    @property
    def title_text_command(self) -> list[str]:
        """
        Add episode title text to the provide image.
        """

        font_size = 180 * self.font_size
        interline_spacing = -17 + self.interline_spacing
        kerning = -1.25 * self.kerning
        stroke_width = 3.0 * self.stroke_width
        vertical_shift = 50 + self.vertical_shift

        return [
            # Global text effects
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity south',
            # Black stroke
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            # Actual title text
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
        ]


    @property
    def index_text_command(self) -> list[str]:
        """
        Adds the series count text without season title/number.
        """

        return [
            # Global text effects
            f'-kerning 5.42',
            f'-pointsize 120',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity west',
            # Add black stroke
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
            f'-annotate +100-750 "{self.episode_text}"',
            # Add actual episode text
            f'-fill "{self.episode_text_color}"',
            f'-stroke black',
            f'-strokewidth 0.75',
            f'-annotate +100-750 "{self.episode_text}"',
        ]


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

        return ((font.file != WhiteTextBroadcast.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != WhiteTextBroadcast.TITLE_COLOR)
            or (font.replacements != WhiteTextBroadcast.FONT_REPLACEMENTS)
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
            False. Custom season titles are not used.
        """

        return False


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            # Overlay gradient
            *self.resize_and_style,
            f'"{self.__GRADIENT_IMAGE.resolve()}"',
            f'-composite',
            *self.title_text_command,
            *self.index_text_command,
            # Resize and write output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])
        
        self.image_magick.run(command)