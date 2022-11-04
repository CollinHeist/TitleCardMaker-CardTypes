from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class RetroTitleCard(BaseCardType):
    """
    This class describes a CardType designed by Yozora. This card type is retro-
    themed, and features either a Rewind/Play overlay.
    """

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref' / 'retro'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 32,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,     # This class uses bottom heavy titling
    }

    """Default font characteristics for the title text"""
    TITLE_FONT = str(RemoteFile('Yozora', 'ref/retro/retro.ttf'))
    TITLE_COLOR = '#FFFFFF'
    FONT_REPLACEMENTS = {'[': '(', ']': ')', '(': '[', ')': ']', '―': '-',
                         '…': '...'}

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'Retro Style'
    
    EPISODE_TEXT_FORMAT = "S{season_number:02}E{episode_number:02}"
    
    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE_PLAY = RemoteFile('Yozora', 'ref/retro/gradient_play.png')
    __GRADIENT_IMAGE_REWIND = RemoteFile('Yozora', 'ref/retro/gradient_rewind.png')

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = RemoteFile('Yozora', 'ref/retro/retro.ttf')
    EPISODE_COUNT_FONT = RemoteFile('Yozora', 'ref/retro/retro.ttf')
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    """Paths to intermediate files that are deleted after the card is created"""
    __SOURCE_WITH_GRADIENT = BaseCardType.TEMP_DIR / 'source_gradient.png'
    __GRADIENT_WITH_TITLE = BaseCardType.TEMP_DIR / 'gradient_title.png'

    __slots__ = (
        'source_file', 'output_file', 'title', 'episode_text', 'font',
        'font_size', 'title_color', 'watched', 'vertical_shift',
        'interline_spacing', 'kerning', 'stroke_width', 'override_bw',
        'override_style'
    )


    def __init__(self, source: Path, output_file: Path, title: str,
                 episode_text: str, font: str, font_size: float,
                 title_color: str, watched: bool=True, blur: bool=False,
                 grayscale: bool=False, vertical_shift: int=0,
                 interline_spacing: int=0, kerning: float=1.0,
                 stroke_width: float=1.0, override_bw: str='',
                 override_style: str='', **kwargs) -> None:
        """
        Initialize this CardType object.

        Args:
            source: Source image to base the card on.
            output_file: Output file where to create the card.
            title: Title text to add to created card.
            season_text: Season text to add to created card.
            episode_text: Episode text to add to created card.
            font: Font name or path (as string) to use for episode title.
            font_size: Scalar to apply to title font size.
            title_color: Color to use for title text.
            watched: Whether this episode has been watched.
            hide_season: Whether to ignore season_text.
            separator: Character to use to separate season and episode text.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            vertical_shift: Pixel count to adjust the title vertical offset by.
            interline_spacing: Pixel count to adjust title interline spacing by.
            kerning: Scalar to apply to kerning of the title text.
            stroke_width: Scalar to apply to black stroke of the title text.
            override_bw: Override B/W modification based on watch status.
            override_style: Override the play/rewind style basd on watch status.
                Should be 'rewind' or 'play'.
            kwargs: Unused arguments.
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
        self.watched = watched
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width
        
        # Store extras
        self.override_bw = override_bw.lower()
        self.override_style = override_style.lower()


    def __title_text_global_effects(self) -> list:
        """
        ImageMagick commands to implement the title text's global effects.
        Specifically the the font, kerning, fontsize, and center gravity.
        
        :returns:   List of ImageMagick commands.
        """

        font_size = 150 * self.font_size
        interline_spacing = -17 + self.interline_spacing
        kerning = -1.25 * self.kerning

        return [
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
        ]   


    def __title_text_black_stroke(self) -> list:
        """
        ImageMagick commands to implement the title text's black stroke.
        
        :returns:   List of ImageMagick commands.
        """

        stroke_width = 3.0 * self.stroke_width

        return [
            f'-fill black',
            f'-stroke black',
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
            f'-pointsize 100',
        ]


    def __series_count_text_black_stroke(self) -> list:
        """
        ImageMagick commands for adding the necessary black stroke effects to
        series count text.
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
        ]


    def __series_count_text_effects(self) -> list:
        """
        ImageMagick commands for adding the necessary text effects to the series
        count text.
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-fill white',
            f'-stroke black',
            f'-strokewidth 0.75',
        ]


    def _add_gradient(self) -> Path:
        """
        Add the static gradient to this object's source image.
        
        :returns:   Path to the created image.
        """
        
        # Select gradient overlay based on override/watch status
        if self.override_style == 'rewind':
            gradient_image = self.__GRADIENT_IMAGE_REWIND
        elif self.override_style == 'play':
            gradient_image = self.__GRADIENT_IMAGE_PLAY
        elif self.watched:
            gradient_image = self.__GRADIENT_IMAGE_REWIND
        else:
            gradient_image = self.__GRADIENT_IMAGE_PLAY
            
        # Determine colorspace (B+W/color) on override/watch status
        if self.override_bw == 'bw':
            colorspace = '-colorspace gray'
        elif self.override_bw == 'color':
            colorspace = ''
        elif self.watched:
            colorspace = '-colorspace gray'
        else:
            colorspace = ''

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            *self.resize_and_style,
            f'"{gradient_image.resolve()}"',
            f'-background None',
            f'-layers Flatten',
            f'{colorspace}',
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

        vertical_shift = 170 + self.vertical_shift

        command = ' '.join([
            f'convert "{gradient_image.resolve()}"',
            *self.__title_text_global_effects(),
            *self.__title_text_black_stroke(),
            f'-annotate +229+{vertical_shift} "{self.title}"',
            f'-fill "{self.title_color}"',
            f'-annotate +229+{vertical_shift} "{self.title}"',
            f'"{self.__GRADIENT_WITH_TITLE.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__GRADIENT_WITH_TITLE


    def _add_series_count_text(self, titled_image: Path) -> Path:
        """
        Adds the series count text.
        
        :param      titled_image:  The titled image to add text to.

        :returns:   Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert "{titled_image.resolve()}"',
            *self.__series_count_text_global_effects(),
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity northeast',
            *self.__series_count_text_black_stroke(),
            f'-annotate +200+229 "{self.episode_text}"',
            *self.__series_count_text_effects(),
            f'-annotate +200+229 "{self.episode_text}"',
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

        return ((font.file != RetroTitleCard.TITLE_FONT)
            or (font.size != 1.0)
            or (font.color != RetroTitleCard.TITLE_COLOR)
            or (font.replacements != RetroTitleCard.FONT_REPLACEMENTS)
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

        return False


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
        """
        
        # Add the gradient to the source image (always)
        gradient_image = self._add_gradient()

        # Add either one or two lines of episode text 
        titled_image = self._add_title_text(gradient_image)

        # Create the output directory and any necessary parents 
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Add episode text 
        self._add_series_count_text(titled_image)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(gradient_image, titled_image)