from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class StandardAllBoldCard(BaseCardType):
    """
    This class describes a type of CardType is identical to the
    StandardTitleCard, except season and episode text is bolded
    """
    
    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 32,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,     # This class uses bottom heavy titling
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str((REF_DIRECTORY / 'Sequel-Neue.otf').resolve())
    TITLE_COLOR = '#EBEBEB'
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'All Bold Style'

    """Default fonts and color for series count text"""
    COUNT_FONT = REF_DIRECTORY / 'Proxima Nova Semibold.otf'
    SERIES_COUNT_TEXT_COLOR = '#CFCFCF'

    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = REF_DIRECTORY / 'GRADIENT.png'

    __slots__ = (
        'source_file', 'output_file', 'title', 'season_text', 'episode_text',
        'font', 'font_size', 'title_color', 'hide_season', 'separator', 'blur',
        'vertical_shift', 'interline_spacing', 'kerning', 'stroke_width'
    )


    def __init__(self, *,
            source: Path,
            output_file: Path,
            title: str,
            season_text: str,
            episode_text: str,
            font: str,
            font_size: float,
            title_color: str,
            hide_season: bool = False,
            blur: bool = False,
            grayscale: bool = False,
            vertical_shift: int = 0,
            interline_spacing: int = 0,
            kerning: float = 1.0,
            stroke_width: float = 1.0,
            separator: str = '•',
            **unused) -> None:
        """
        Construct a new instance of this card.

        Args:
            source: Source image to base the card on.
            output_file: Output file where to create the card.
            title: Title text to add to created card.
            season_text: Season text to add to created card.
            episode_text: Episode text to add to created card.
            font: Font name or path (as string) to use for episode title.
            font_size: Scalar to apply to title font size.
            title_color: Color to use for title text.
            hide_season: Whether to ignore season_text.
            separator: Character to use to separate season and episode text.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            vertical_shift: Pixel count to adjust the title vertical offset by.
            interline_spacing: Pixel count to adjust title interline spacing by.
            kerning: Scalar to apply to kerning of the title text.
            stroke_width: Scalar to apply to black stroke of the title text.
            kwargs: Unused arguments.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source
        self.output_file = output_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title)
        self.season_text = self.image_magick.escape_chars(season_text.upper())
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())

        self.font = font
        self.font_size = font_size
        self.title_color = title_color
        self.hide_season = hide_season
        self.separator = separator
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given arguments represent a custom font
        for this card. This CardType only uses custom font cases.

        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.file != StandardAllBoldCard.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != StandardAllBoldCard.TITLE_COLOR)
            or (font.vertical_shift != 0)
            or (font.interline_spacing != 0)
            or (font.kerning != 1.0)
            or (font.stroke_width != 1.0))


    @staticmethod
    def is_custom_season_titles(custom_episode_map: bool, 
                                episode_text_format: str) -> bool:
        """
        Determines whether the given attributes constitute custom or
        generic season titles.

        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.

        Returns:
            True if custom season titles are indicated, False otherwise.
        """

        standard_etf = StandardAllBoldCard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map or
                episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        font_size = 157.41 * self.font_size
        vertical_shift = 245 + self.vertical_shift
        interline_spacing = -22 + self.interline_spacing
        kerning = -1.25 * self.kerning
        stroke_width = 3.0 * self.stroke_width

        if self.hide_season:
            series_count_text = self.episode_text
        else:
            series_count_text = (f'{self.season_text} {self.separator} '
                                 f'{self.episode_text}')

        command = ' '.join([
            # Resize source image
            f'convert "{self.source_file.resolve()}"',
            f'+profile "*"',
            f'-gravity center',
            f'-resize "{self.TITLE_CARD_SIZE}^"',
            f'-extent "{self.TITLE_CARD_SIZE}"',
            # Blur source
            f'-blur {self.BLUR_PROFILE}' if self.blur else '',
            # Add gradient overlay
            f'"{self.__GRADIENT_IMAGE.resolve()}"',
            # Combine source + gradient
            f'-composite',
            # Add title
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            ## Black stroke
            f'-gravity south',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            # Add series count text
            f'-font "{self.COUNT_FONT.resolve()}"',
            f'-kerning 5.42',
            f'-pointsize 67.75',
            f'-gravity center',
            f'+interword-spacing',  # Reset interword spacing
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
            f'-annotate +0+697.2 "{series_count_text}"',
            f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-strokewidth 0.75',
            f'-annotate +0+697.2 "{series_count_text}"',
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)