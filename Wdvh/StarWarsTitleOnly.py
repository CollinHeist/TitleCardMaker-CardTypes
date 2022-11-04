from pathlib import Path
from re import match

from num2words import num2words

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class StarWarsTitleOnly (BaseCardType):
    """
    This class describes a type of ImageMaker that produces title cards in the
    theme of Star Wars cards as designed by reddit user /u/Olivier_286. These
    cards are not as customizable as the standard template.
    """

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref' / 'star_wars'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 16,   # Character count to begin splitting titles
        'max_line_count': 5,    # Maximum number of lines a title can take up
        'top_heavy': True,      # This class uses top heavy titling
    }

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Star Wars Title Only Style'

    """Path to the font to use for the episode title"""
    TITLE_FONT = str((REF_DIRECTORY/'Monstice-Base.ttf').resolve())

    """Color to use for the episode title"""
    TITLE_COLOR = '#DAC960'

    """Default episode text format string"""
    EPISODE_TEXT_FORMAT = ' '

    """Standard font replacements for the title font"""
    FONT_REPLACEMENTS = {'Ō': 'O', 'ō': 'o'}

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = False

    """Path to the reference star image to overlay on all source images"""
    __STAR_GRADIENT_IMAGE = RemoteFile('Wdvh', 'star_gradient_title_only.png')

    """Paths to intermediate files that are deleted after the card is created"""
    __SOURCE_WITH_STARS = BaseCardType.TEMP_DIR / 'source_gradient.png'

    __slots__ = ('source_file', 'output_file', 'title')

    
    def __init__(self, source: Path, output_file: Path, title: str,
                 blur: bool=False, grayscale: bool=False, **kwargs) -> None:
        """
        Initialize this CardType object.

        Args:
            source: Source image to base the card on.
            output_file: Output file where to create the card.
            title: Title text to add to created card.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            kwargs: Unused arguments.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Store source and output file
        self.source_file = source
        self.output_file = output_file

        # Store episode title
        self.title = self.image_magick.escape_chars(title.upper())


    def __add_star_gradient(self, source: Path) -> Path:
        """
        Add the static star gradient to the given source image.
        
        :param      source: The source image to modify.
        
        :returns:   Path to the created image.
        """

        command = ' '.join([
            f'convert "{source.resolve()}"',
            *self.resize_and_style,
            f'"{self.__STAR_GRADIENT_IMAGE.resolve()}"',
            f'-background None',
            f'-layers Flatten',
            f'"{self.__SOURCE_WITH_STARS.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__SOURCE_WITH_STARS


    def __add_title_text(self) -> list:
        """
        ImageMagick commands to add the episode title text to an image.
        
        :returns:   List of ImageMagick commands.
        """

        return [
            f'-font "{self.TITLE_FONT}"',
            f'-gravity northwest',
            f'-pointsize 124',
            f'-kerning 0.5',
            f'-interline-spacing 20',
            f'-fill "{self.TITLE_COLOR}"',
            f'-annotate +320+1529 "{self.title}"',
        ]


    def __add_only_title(self, gradient_source: Path) -> Path:
        """
        Add the title to the given image.
        
        :param      gradient_source:    Source image with starry gradient
                                        overlaid.
        
        :returns:   Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert "{gradient_source.resolve()}"',
            *self.__add_title_text(),
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.output_file


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given arguments represent a custom font for this
        card. This CardType does not use custom fonts, so this is always False.
        
        :param      font:   The Font being evaluated.
        
        :returns:   False, as fonts are not customizable with this card.
        """

        return False


    @staticmethod
    def is_custom_season_titles(episode_text_format: str,
                                *args, **kwargs) -> bool:
        """
        Determines whether the given attributes constitute custom or generic
        season titles.
        
        :param      episode_text_format:    The episode text format in use.
        :param      args and kwargs:        Generic arguments to permit 
                                            generalized function calls for any
                                            CardType.
        
        :returns:   False, as season titles are not utilized.
        """
        
        return False


    def create(self) -> None:
        """Create the title card as defined by this object."""

        # Add the starry gradient to the source image
        star_image = self.__add_star_gradient(self.source_file)

        # Add text to starry image, result is output
        self.__add_only_title(star_image)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(star_image)