from pathlib import Path
from re import compile as re_compile, findall
from typing import Literal, Optional, TYPE_CHECKING, Union

from pydantic import FilePath

from app.schemas.base import BetterColor
from app.schemas.card_type import BaseCardTypeCustomFontAllText
from modules.BaseCardType import (
    BaseCardType, ImageMagickCommands, CardDescription
)
from modules.Debug import log
from modules.RemoteFile import RemoteFile
from modules.Title import SplitCharacteristics

if TYPE_CHECKING:
    from app.models.preferences import Preferences
    from modules.Font import Font


class TitleColorMatch(BaseCardType):
    """
    This class describes a type of CardType created by azuravian, and is 
    a modification of Beedman's GradientLogoTitleCard class with a few
    changes,  specifically the ability to autoselect a font color that
    matches the logo, as well as trimming the logo of any extra
    transparent space that makes its  location incorrect.
    """

    API_DETAILS =  CardDescription(
        name='Title Color Match',
        identifier='azuravian/TitleColorMatch',
        example=(
            'https://user-images.githubusercontent.com/7379812/'
            '187586521-353ba09f-30a8-424b-bbf3-ee9036c9e638.jpg'
        ),
        creators=['Azuravian', 'Beedman', 'CollinHeist'],
        source='remote',
        supports_custom_fonts=True,
        supports_custom_seasons=True,
        supported_extras=[],
        description=[
            'A modification of GradientLogoTitleCard that includes the option '
            'to auto-select font color based on logo color.', 'This card will '
            'also automatically crop off extraneous transparent space from '
            'around the logo.',
        ]
    )

    class CardModel(BaseCardTypeCustomFontAllText):
        logo_file: FilePath
        font_color: Union[BetterColor, Literal['auto']] = '#EBEBEB'
        font_file: FilePath

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'ref'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS: SplitCharacteristics = {
        'max_line_width': 32,
        'max_line_count': 3,
        'style': 'bottom',
    }

    """Default font and text color for episode title text"""
    TITLE_FONT = str((REF_DIRECTORY / 'Sequel-Neue.otf').resolve())
    TITLE_COLOR = '#EBEBEB'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Archive name for this card type"""
    ARCHIVE_NAME = 'Title Color Match Style'

    """Source path for the gradient image overlayed over all title cards"""
    __GRADIENT_IMAGE = str(RemoteFile('azuravian', 'leftgradient.png'))

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Proxima Nova Semibold.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Proxima Nova Regular.otf'
    SERIES_COUNT_TEXT_COLOR = '#CFCFCF'

    """Regex to match colors/counts in ImageMagick histograms"""
    __COLORDATA_REGEX = re_compile(r'[\s]*(\d*)?:\s.*\s(#\w{8}).*\n?')

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'season_text',
        'episode_text', 'hide_season_text', 'hide_episode_text', 'font_color',
        'font_file', 'font_interline_spacing', 'font_kerning', 'font_size',
        'font_stroke_width', 'font_vertical_shift', 'logo', 
    )

    def __init__(self,
            source_file: Path,
            card_file: Path,
            logo_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            preferences: Optional['Preferences'] = None,
            **unused,
        ) -> None:
        """
        Construct a new instance of this Card.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        self.source_file = source_file
        self.output_file = card_file
        self.logo = logo_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text)
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_season_text = hide_season_text
        self.hide_episode_text = hide_episode_text
        
        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift


    @property
    def logo_command(self) -> ImageMagickCommands:
        """ImageMagick commands to add the resized logo to the image."""

        return [
            # Resize logo
            f'\( "{self.logo.resolve()}"',
            f'-trim',
            f'+repage',
            f'-resize x650',
            f'-resize 1155x650\> \)',
            # Overlay resized logo
            f'-gravity northwest',
            f'-define colorspace:auto-grayscale=false',
            f'-type TrueColorAlpha',  
            f'-geometry "+50+50"',
            f'-composite',
        ]


    @property
    def title_text_command(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        center gravity.
        """

        # Get the title color and stroke for this logo
        title_color, stroke_color = self._get_logo_color()

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.font_interline_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 125 + self.font_vertical_shift

        return [
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
            f'-fill {stroke_color}',
            f'-stroke {stroke_color}',
            f'-strokewidth {stroke_width}',
            f'-annotate +50+{vertical_shift} "{self.title_text}"',
            f'-fill "{title_color}"',
            f'-annotate +50+{vertical_shift} "{self.title_text}"',
        ]


    def _get_logo_color(self) -> tuple[str, str]:
        """
        Get the logo color for this card's logo.

        Returns:
            Tuple whose values are the title color text and the stroke
            width color.
        """

        # If auto color wasn't indicated use indicated color and black stroke
        if self.font_color != 'auto':
            return self.font_color, 'black'

        # Command to get histogram of the colors in logo image
        command = ' '.join([
            f'convert "{self.logo.resolve()}"',
            f'-scale 100x100!',
            f'-depth 8 +dither',
            f'-colors 16',
            f'-format "%c" histogram:info:',
        ])

        # Get color data
        colordata = self.image_magick.run_get_output(command)
        cdata = {
            k: [num, hex_] for k, (num, hex_)
            in enumerate(findall(self.__COLORDATA_REGEX, colordata), start=1)
        }

        translist = []
        pixcount = []
        for key, pair in cdata.items():
            h = int(pair[1][-2:], 16)
            if h < 75:
                translist.append(key)
            else:
                pixcount.append(int(pair[0]))

        for key in translist:
            del cdata[key]

        # Go through colors in descending order of appearance
        pixcount.sort(reverse=True)
        pairs = list(cdata.values())
        for num in pixcount:
            # Get the RGB value from the hexcolor
            hexcolor = next(x[1][:7] for x in pairs if int(x[0]) == num)

            color_ = hexcolor.lstrip('#')
            lv = len(color_)
            r, g, b = (int(color_[i:i+lv//3], 16) for i in range(0, lv, lv//3))
            
            # Skip values that are too dark/light
            if min(r, g, b) > 240 or max(r, g, b) < 15:
                continue

            # First valid color, return color and stroke based on luminance
            luminance = (r * 0.299) + (g * 0.587) + (b * 0.114)
            return hexcolor, 'black' if luminance > 50 else 'white'

        # No valid colors identified, return defaults
        return self.TITLE_COLOR, 'black'

    
    @property
    def index_text_command(self) -> ImageMagickCommands:
        """
        ImageMagick commands required to add the index (season and
        episode) text to the image.
        """

        # Season hiding, just add episode text
        if self.hide_season_text:
            return [
                f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
                f'-kerning 5.42',
                f'-pointsize 67.75',
                f'-fill black',
                f'-stroke black',
                f'-strokewidth 6',
                f'-gravity southwest',
                f'-annotate +50+50 "{self.episode_text}"',
                f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-strokewidth 0.75',
                f'-annotate +50+50 "{self.episode_text}"',
            ]

        # Episode hiding, just add season text
        if self.hide_episode_text:
            return [
                f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
                f'-kerning 5.42',
                f'-pointsize 67.75',
                f'-fill black',
                f'-stroke black',
                f'-strokewidth 6',
                f'-gravity southwest',
                f'-annotate +50+50 "{self.season_text}"',
                f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-strokewidth 0.75',
                f'-annotate +50+50 "{self.season_text}"',
            ]

        return [
            f'-background transparent',
            f'+interword-spacing',
            f'-kerning 5.42',
            f'-pointsize 67.75',
            f'-fill black',
            f'-stroke black',
            f'-strokewidth 6',
            f'\( -gravity center',
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'label:"{self.season_text} •"',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'label:"{self.episode_text}"',
            f'+smush 30 \)',
            f'-gravity southwest',
            f'-geometry +50+50',
            f'-composite',
            f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-strokewidth 0.75',
            f'\( -gravity center',
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'label:"{self.season_text} •"',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'label:"{self.episode_text}"',
            f'+smush 30 \)',
            f'-gravity southwest',
            f'-geometry +50+50',
            f'-composite',
        ]


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given arguments represent a custom font
        for this card.
        
        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.color != TitleColorMatch.TITLE_COLOR)
            or (font.file != TitleColorMatch.TITLE_FONT)
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
            True if custom season titles are indicated, False otherwise.
        """

        standard_etf = TitleColorMatch.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map
                or episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        command = ' '.join([
            f'convert',
            # Resize source image
            f'"{self.source_file.resolve()}"',
            *self.resize_and_style,
            # Overlay gradient
            f'"{self.__GRADIENT_IMAGE}"',
            f'-composite',
            # Overlay resized logo
            *self.logo_command,
            # Put title text
            *self.title_text_command,
            # Put season/episode text
            *self.index_text_command,
            # Create and resize output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
