from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.RemoteFile import RemoteFile
from modules.Debug import log

class WhiteTextStandard(BaseCardType):
    """
    This class describes a type of CardType that produces the 'generic' title
    cards based on Reddit user /u/UniversalPolymath. This card supports 
    customization of every aspect of the card, but does not use any arbitrary
    data.
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
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'White Text Standard Style'

    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = REF_DIRECTORY / 'GRADIENT.png'

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    """Paths to intermediate files that are deleted after the card is created"""
    __SOURCE_WITH_GRADIENT = BaseCardType.TEMP_DIR / 'source_gradient.png'
    __GRADIENT_WITH_TITLE = BaseCardType.TEMP_DIR / 'gradient_title.png'

    __slots__ = ('source_file', 'output_file', 'title', 'season_text',
                 'episode_text', 'font', 'font_size', 'title_color',
                 'hide_season', 'separator', 'blur', 'vertical_shift', 
                 'interline_spacing', 'kerning', 'stroke_width')


    def __init__(self, source: Path, output_file: Path, title: str,
                 season_text: str, episode_text: str, font: str,
                 font_size: float, title_color: str, hide_season: bool,
                 separator: str='-', blur: bool=False, vertical_shift: int=0,
                 interline_spacing: int=0, kerning: float=1.0,
                 stroke_width: float=1.0, **kwargs) -> None:
        """
        Initialize the TitleCardMaker object. This primarily just stores
        instance variables for later use in `create()`. If the provided font
        does not have a character in the title text, a space is used instead.

        :param  source:             Source image.
        :param  output_file:        Output file.
        :param  title_top_line:     Episode title.
        :param  season_text:        Text to use as season count text. Ignored if
                                    hide_season is True.
        :param  episode_text:       Text to use as episode count text.
        :param  separator:          Character to use to separate season and
                                    episode text.
        :param  font:               Font to use for the episode title. MUST be a
                                    a valid ImageMagick font, or filepath to a
                                    font.
        :param  font_size:          Scalar to apply to the title font size.
        :param  title_color:        Color to use for the episode title.
        :param  hide_season:        Whether to omit the season text (and joining
                                    character) from the title card completely.
        :param  blur:               Whether to blur the source image.
        :param  vertical_shift:     Pixels to adjust title vertical shift by.
        :param  interline_spacing:  Pixels to adjust title interline spacing by.
        :param  kerning:            Scalar to apply to kerning of the title text.
        :param  stroke_width:       Scalar to apply to black stroke of the title
                                    text.
        :param  args and kwargs:    Unused arguments to permit generalized calls
                                    for any CardType.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__()

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
        self.blur = blur
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width


    def __title_text_global_effects(self) -> list:
        """
        ImageMagick commands to implement the title text's global effects.
        Specifically the the font, kerning, fontsize, and center gravity.
        
        :returns:   List of ImageMagick commands.
        """

        font_size = 180 * self.font_size
        interline_spacing = -70 + self.interline_spacing
        kerning = -1.25 * self.kerning

        return [
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity south',
        ]   


    def __title_text_black_stroke(self) -> list:
        """
        ImageMagick commands to implement the title text's black stroke.
        
        :returns:   List of ImageMagick commands.
        """

        stroke_width = 4.0 * self.stroke_width

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth {stroke_width}',
        ]


    def __series_count_text_global_effects(self) -> list:
        """
        ImageMagick commands for global text effects applied to all series count
        text (season/episode count and dot).
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-kerning 5.42',
            f'-pointsize 85',
        ]


    def __series_count_text_black_stroke(self) -> list:
        """
        ImageMagick commands for adding the necessary black stroke effects to
        series count text.
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
        ]


    def __series_count_text_effects(self) -> list:
        """
        ImageMagick commands for adding the necessary text effects to the series
        count text.
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
        ]


    def _add_gradient(self) -> Path:
        """
        Add the static gradient to this object's source image.
        
        :returns:   Path to the created image.
        """

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            f'+profile "*"',
            f'-gravity center',
            f'-resize "{self.TITLE_CARD_SIZE}^"',
            f'-extent "{self.TITLE_CARD_SIZE}"',
            f'-blur {self.BLUR_PROFILE}' if self.blur else '',
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

        vertical_shift = 145 + self.vertical_shift

        command = ' '.join([
            f'convert "{gradient_image.resolve()}"',
            *self.__title_text_global_effects(),
            *self.__title_text_black_stroke(),
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'"{self.__GRADIENT_WITH_TITLE.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__GRADIENT_WITH_TITLE


    def _add_series_count_text(self, titled_image: Path) -> Path:
        """
        Adds the (optional) season and episode text.
        
        :param      titled_image:  The titled image to add text to.

        :returns:   Path to the created image (the output file).
        """
        
        if self.hide_season:
            series_count_text = self.episode_text
        else:
            series_count_text = (f'{self.season_text} {self.separator} '
                                 f'{self.episode_text}')

        command = ' '.join([
            f'convert "{titled_image.resolve()}"',
            *self.__series_count_text_global_effects(),
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity center',
            *self.__series_count_text_black_stroke(),
            f'-annotate +0+800 "{series_count_text}"',
            *self.__series_count_text_effects(),
            f'-annotate +0+800 "{series_count_text}"',
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.output_file


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given font characteristics constitute a default
        or custom font.
        
        :param      font:   The Font being evaluated.
        
        :returns:   True if a custom font is indicated, False otherwise.
        """

        return ((font.file != WhiteTextStandard.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != WhiteTextStandard.TITLE_COLOR)
            or (font.replacements != WhiteTextStandard.FONT_REPLACEMENTS)
            or (font.vertical_shift != 0)
            or (font.interline_spacing != 0)
            or (font.kerning != 1.0)
            or (font.stroke_width != 1.0))


    @staticmethod
    def is_custom_season_titles(custom_episode_map: bool, 
                                episode_text_format: str) -> bool:
        """
        Determines whether the given attributes constitute custom or generic
        season titles.
        
        :param      custom_episode_map:     Whether the EpisodeMap was
                                            customized.
        :param      episode_text_format:    The episode text format in use.
        
        :returns:   True if custom season titles are indicated, False otherwise.
        """

        standard_etf = WhiteTextStandard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map or
                episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
        """
        
        # Add the gradient to the source image (always)
        gradient_image = self._add_gradient()

        # Add either one or two lines of episode text 
        titled_image = self._add_title_text(gradient_image)

        # Add season/episode text
        self._add_series_count_text(titled_image)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(gradient_image, titled_image)