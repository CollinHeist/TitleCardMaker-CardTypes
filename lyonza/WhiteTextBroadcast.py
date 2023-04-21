from pathlib import Path

from modules.BaseCardType import BaseCardType, ImageMagickCommands
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
        'source_file', 'output_file', 'title_text', 'episode_text',
        'hide_season_text', 'font_file', 'font_size', 'font_color',
        'font_vertical_shift', 'font_interline_spacing', 'font_kerning',
        'font_stroke_width', 'episode_text_color', 'omit_gradient',
    )


    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            episode_text: str,
            font_color: str,
            font_file: str,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            episode_text_color: str = SERIES_COUNT_TEXT_COLOR,
            omit_gradient: bool = False,
            **unused) -> None:
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source_file
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())

        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift

        self.episode_text_color = episode_text_color
        self.omit_gradient = omit_gradient


    @property
    def title_text_command(self) -> ImageMagickCommands:
        """
        Add episode title text to the provide image.
        """

        font_size = 180 * self.font_size
        interline_spacing = -17 + self.font_interline_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 50 + self.font_vertical_shift

        return [
            # Global text effects
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity south',
            # Black stroke
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +0+{vertical_shift} "{self.title_text}"',
            # Actual title text
            f'-fill "{self.font_color}"',
            f'-annotate +0+{vertical_shift} "{self.title_text}"',
        ]


    @property
    def index_text_command(self) -> ImageMagickCommands:
        """
        Adds the series count text without season title/number.
        """

        return [
            # Global text effects
            f'+interword-spacing',
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

        return ((font.color != WhiteTextBroadcast.TITLE_COLOR)
            or (font.file != WhiteTextBroadcast.TITLE_FONT)
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
            False. Custom season titles are not used.
        """

        return False


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        if self.omit_gradient:
            gradient_command = []
        else:
            gradient_command = [
                f'"{self.__GRADIENT_IMAGE.resolve()}"',
                f'-composite',
            ]

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            # Overlay gradient
            *self.resize_and_style,
            *gradient_command,
            *self.title_text_command,
            *self.index_text_command,
            # Resize and write output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])
        
        self.image_magick.run(command)