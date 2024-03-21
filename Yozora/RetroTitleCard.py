from pathlib import Path
from typing import Literal, Optional

from pydantic import root_validator

from app.schemas.card_type import BaseCardTypeCustomFontNoText
from modules.BaseCardType import (
    BaseCardType, ImageMagickCommands, CardDescription
)
from modules.RemoteFile import RemoteFile
from modules.Title import SplitCharacteristics

if TYPE_CHECKING:
    from app.models.preferences import Preferences
    from modules.Font import Font

OverrideBw = Literal['bw', 'color']
OverrideStyle = Literal['rewind', 'play']

class RetroTitleCard(BaseCardType):
    """
    This class describes a CardType designed by Yozora. This card type
    is retro-themed, and features either a Rewind/Play overlay.
    """

    API_DETAILS = CardDescription(
        name='Retro',
        identifier='Yozora/RetroTitleCard',
        example=(
            'https://camo.githubusercontent.com/bb6308801194ee20a369080'
            'a2d1830c19a63685fab304aa814f0faa1dded2caf/68747470733a2f2f'
            '692e6962622e636f2f30746e4a4a36502f537472616e6765722d546869'
            '6e67732d323031362d5330332d4530322e6a7067'
        ),
        creators=['Yozora', 'CollinHeist'],
        source='remote',
        supports_custom_fonts=True,
        supports_custom_seasons=False,
        supported_extras=[],
        description=[
            'Card type featuring a VHS/Camcorder inspired overlay.',
            "The 'Play' button can be set to 'Rewind' and the image "
            'greyscaled when the item has been played.',
        ]
    )

    class CardModel(BaseCardTypeCustomFontNoText):
        title_text: str
        episode_text: str
        hide_episode_text: bool = False
        watched: bool = True
        override_bw: Optional[OverrideBw] = None
        override_style: Optional[OverrideStyle] = None

        @root_validator
        def toggle_text_hiding(cls, values):
            values['hide_episode_text'] |= (len(values['episode_text']) == 0)

            return values

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref' / 'retro'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS: SplitCharacteristics = {
        'max_line_width': 32,
        'max_line_count': 3,
        'style': 'bottom',
    }

    """Default font characteristics for the title text"""
    TITLE_FONT = str(RemoteFile('Yozora', 'ref/retro/retro.ttf'))
    TITLE_COLOR = '#FFFFFF'
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

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

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'episode_text',
        'hide_episode_text', 'font_color', 'font_file','font_interline_spacing',
        'font_kerning', 'font_size', 'font_stroke_width', 'font_vertical_shift',
        'override_bw', 'override_style', 'watched', 
    )


    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            episode_text: str,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            watched: bool = True,
            blur: bool = False,
            grayscale: bool = False,
            override_bw: Optional[OverrideBw] = None,
            override_style: Optional[OverrideStyle] = None,
            preferences: Optional['Preferences'] = None,
            **unused,
        ) -> None:
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        self.source_file = source_file
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        self.hide_episode_text = hide_episode_text

        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift
        
        # Store extras
        self.watched = watched
        self.override_bw = override_bw
        self.override_style = override_style


    @property
    def add_gradient_commands(self) -> ImageMagickCommands:
        """Add the static gradient to this object's source image."""
        
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

        return [
            f'"{gradient_image.resolve()}"',
            f'-composite',
            f'{colorspace}',
        ]


    @property
    def title_text_commands(self) -> ImageMagickCommands:
        """Adds episode title text to the provide image."""

        font_size = 150 * self.font_size
        interline_spacing = -17 + self.font_interline_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 170 + self.font_vertical_shift

        return [
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth {stroke_width}',
            f'-annotate +229+{vertical_shift} "{self.title_text}"',
            f'-fill "{self.font_color}"',
            f'-annotate +229+{vertical_shift} "{self.title_text}"',
        ]


    @property
    def index_text_commands(self) -> ImageMagickCommands:
        """Adds the series count text."""

        if self.hide_episode_text:
            return []

        return [
            f'-kerning 5.42',
            f'-pointsize 100',
            f'+interword-spacing',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity northeast',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
            f'-annotate +200+229 "{self.episode_text}"',
            f'-fill white',
            f'-stroke black',
            f'-strokewidth 0.75',
            f'-annotate +200+229 "{self.episode_text}"',
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

        return ((font.color != RetroTitleCard.TITLE_COLOR)
            or (font.file != RetroTitleCard.TITLE_FONT)
            or (font.interline_spacing != 0)
            or (font.kerning != 1.0)
            or (font.size != 1.0)
            or (font.stroke_width != 1.0)
            or (font.vertical_shift != 0)
        )


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool,
            episode_text_format: str,
        ) -> bool:
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

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            *self.resize_and_style,
            *self.add_gradient_commands,
            *self.title_text_commands,
            *self.index_text_commands,
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
