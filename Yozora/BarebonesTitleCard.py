from pathlib import Path
from re import match

from num2words import num2words

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class BarebonesTitleCard(BaseCardType):
    """
    Yozora's barebones card type that is inspired by the Olivier and
    StarWars card types.
    """

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref' / 'barebones'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 16,   # Character count to begin splitting titles
        'max_line_count': 5,    # Maximum number of lines a title can take up
        'top_heavy': True,      # This class uses top heavy titling
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str(RemoteFile('Yozora', 'ref/barebones/Montserrat-Bold.ttf'))
    TITLE_COLOR = '#FFFFFF'
    FONT_REPLACEMENTS = {}

    """Characteristics of the episode text"""
    EPISODE_TEXT_FORMAT = 'EPISODE {episode_number}'
    EPISODE_TEXT_COLOR = '#FFFFFF'
    EPISODE_TEXT_FONT = RemoteFile('Yozora', 'ref/barebones/Montserrat-SemiBold.ttf')

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = False

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Barebones Style'

    """Paths to intermediate files that are deleted after the card is created"""
    __RESIZED_SOURCE = BaseCardType.TEMP_DIR / 'resized_source.png'

    __slots__ = (
        'source_file', 'output_file', 'title', 'hide_episode_text', 
        'episode_text', 'font', 'font_size', 'title_color',
        'episode_text_color', 'stroke_width'
    )

    
    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            episode_text: str,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            blur: bool = False,
            grayscale: bool = False,
            episode_text_color: str = EPISODE_TEXT_COLOR,
            **unused) -> None:
        """
        Initialize this CardType object.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Store source and output file
        self.source_file = source_file
        self.output_file = card_file

        # Store episode title and text
        self.title = self.image_magick.escape_chars(title_text.upper())
        self.hide_episode_text = hide_episode_text or len(episode_text) == 0

        # Attempt to convert episode text number to numeric text
        if (not self.hide_episode_text
            and (groups := match(r'^(.*?)(\d+)$', episode_text)) is not None):
            pre, number = groups.groups()
            episode_text = f'{pre}{num2words(int(number))}'.upper()
        else:
            episode_text = episode_text.upper()
        self.episode_text = self.image_magick.escape_chars(episode_text)

        # Font customizations
        self.title_color = font_color
        self.font = font_file
        self.font_size = font_size
        self.stroke_width = font_stroke_width

        self.episode_text_color = episode_text_color


    def __resize_source(self, source: Path) -> Path:
        """
        Resize the source image.
        
        Args:
            source: The source image to modify.
        
        Returns:
            Path to the resized image.
        """

        command = ' '.join([
            f'convert "{source.resolve()}"',
            *self.resize_and_style,
            f'"{self.__RESIZED_SOURCE.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__RESIZED_SOURCE

    def __add_title_text(self) -> list[str]:
        """
        ImageMagick commands to add the episode title text to an image.
        
        Returns:
            List of ImageMagick commands.
        """

        stroke_width = 6.0 * self.stroke_width
        font_size = 124 * self.font_size

        return [
            f'\( -font "{self.font}"',
            f'-gravity northwest',
            f'-pointsize {font_size}',
            f'-kerning 0.5',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +320+829 "{self.title}" \)',
            f'\( -fill "{self.title_color}"',
            f'-stroke "{self.title_color}"',
            f'-strokewidth 0',
            f'-annotate +320+829 "{self.title}" \)',
        ]


    def __add_episode_text(self) -> list[str]:
        """
        ImageMagick commands to add the episode text to an image.
        
        Returns:
            List of ImageMagick commands.
        """

        return [
            f'-gravity west',
            f'-font "{self.EPISODE_TEXT_FONT.resolve()}"',
            f'-pointsize 53',
            f'-kerning 19',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 4.5',
            f'-annotate +325-140 "{self.episode_text}"',
            f'-fill "{self.episode_text_color}"',
            f'-stroke "{self.episode_text_color}"',
            f'-strokewidth 0',
            f'-annotate +325-140 "{self.episode_text}"',
        ]


    def __add_only_title(self, resized_source: Path) -> Path:
        """
        Add the title to the given image.
        
        Args:
            resized_source: Resized source image.
        
        Returns:
            Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert "{resized_source.resolve()}"',
            *self.__add_title_text(),
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.output_file


    def __add_all_text(self, resized_source: Path) -> Path:
        """
        Add the title and episode text to the given image.
        
        Args:
            resized_source: Resized source image.
        
        Returns:
            Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert "{resized_source.resolve()}"',
            *self.__add_title_text(),
            *self.__add_episode_text(),
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

        return ((font.color != BarebonesTitleCard.TITLE_COLOR)
            or (font.file != BarebonesTitleCard.TITLE_FONT)
            or (font.size != 1.0)
            or (font.stroke_width != 1.0)
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

        standard_etf = BarebonesTitleCard.EPISODE_TEXT_FORMAT.upper()

        return episode_text_format.upper() != standard_etf


    def create(self) -> None:
        """Create the title card as defined by this object."""

        # Add the starry gradient to the source image
        resized_image = self.__resize_source(self.source_file)

        # Add text to starry image, result is output
        if self.hide_episode_text:
            self.__add_only_title(resized_image)
        else:
            self.__add_all_text(resized_image)

        # Delete all intermediate images
        self.image_magick.delete_intermediate_images(resized_image)