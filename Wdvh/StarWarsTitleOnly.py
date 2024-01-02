from pathlib import Path
from typing import Literal, Optional

from pydantic import constr

from app.schemas.base import BetterColor
from app.schemas.card_type import BaseCardTypeCustomFontNoText
from modules.BaseCardType import BaseCardType, CardDescription
from modules.Debug import log
from modules.RemoteFile import RemoteFile


class StarWarsTitleOnly(BaseCardType):
    """
    This class describes a type of Card that produces a modified version
    of the Star Wars card.
    """

    API_DETAILS = CardDescription(
        name='Star Wars (Title Only)',
        identifier='Wdvh/StarWarsTitleOnly',
        example='https://user-images.githubusercontent.com/17693271/178131539-c7b55ced-b9ba-4564-8153-a998454e1742.jpg',
        creators=['Wdvh', 'CollinHeist'],
        source='remote',
        supports_custom_fonts=False,
        supports_custom_seasons=False,
        supported_extras=[],
        description=[
            'A variation of the standard Star Wars Card for Shows like '
            'Obi-Wan Kenobi that use Part/Chapter and similar as episode '
            'titles.', 'This card also uses a modified star gradient so that '
            'more of the left side of the image is visible.',
        ]
    )

    class CardModel(BaseCardTypeCustomFontNoText):
        title_text: constr(to_upper=True)
        font_color: BetterColor = '#DAC960'

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

    __slots__ = ('source_file', 'output_file', 'title')

    
    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            blur: bool = False,
            grayscale: bool = False,
            preferences: Optional['Preferences'] = None, # type: ignore
            **unused,
        ) -> None:
        """
        Initialize this CardType object.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        # Store source and output file
        self.source_file = source_file
        self.output_file = card_file

        # Store episode title
        self.title = self.image_magick.escape_chars(title_text)


    @staticmethod
    def is_custom_font(font: 'Font') -> Literal[False]: # type: ignore
        """
        Determines whether the given font characteristics constitute a
        default or custom font.
        
        Args:
            font: The Font being evaluated.
        
        Returns:
            False, as custom fonts are not used.
        """

        return False


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool,
            episode_text_format: str,
        ) -> Literal[False]:
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
            # Resize input and apply any style modifiers
            *self.resize_and_style,
            # Overlay the star gradient
            f'"{self.__STAR_GRADIENT_IMAGE.resolve()}"',
            f'-composite',
            # Add title text
            f'-font "{self.TITLE_FONT}"',
            f'-gravity northwest',
            f'-pointsize 124',
            f'-kerning 0.5',
            f'-interline-spacing 20',
            f'-fill "{self.TITLE_COLOR}"',
            f'-annotate +320+1529 "{self.title}"',
            # Resize and write output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
