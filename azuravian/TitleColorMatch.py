from pathlib import Path
from re import findall, compile as re_compile
from typing import Optional

from modules.BaseCardType import BaseCardType
from modules.CleanPath import CleanPath
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class TitleColorMatch(BaseCardType):
    """
    This class describes a type of CardType created by azuravian, and is 
    a modification of Beedman's GradientLogoTitleCard class with a few
    changes,  specifically the ability to autoselect a font color that
    matches the logo, as well as trimming the logo of any extra
    transparent space that makes its  location incorrect.
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
        'source_file', 'logo', 'output_file', 'title', 'season_text',
        'episode_text', 'font', 'font_size', 'title_color', 'hide_season',
        'vertical_shift', 'interline_spacing', 'kerning', 'stroke_width'
    )


    def __init__(self,
            source: Path,
            output_file: Path,
            title: str,
            season_text: str,
            episode_text: str,
            font: str,
            font_size: float,
            title_color: str,
            hide_season: bool = False,
            vertical_shift: int = 0,
            interline_spacing: int = 0,
            kerning: float = 1.0,
            stroke_width: float = 1.0,
            season_number: int = 1,
            episode_number: int = 1,
            blur: bool = False,
            grayscale: bool = False,
            logo: Optional[str] = None,
            **unused) -> None:
        """
        Construct a new instance of this card.

        Args:
            source: Source image.
            output_file: Output file.
            title: Episode title.
            season_text: Text to use as season count text.
            episode_text: Text to use as episode count text.
            font: Font to use for the episode title.
            font_size: Scalar to apply to the title font size.
            title_color: Color to use for the episode title.
            hide_season: Whether to omit the season text (and joining
                character) from the title card completely.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            vertical_shift: Pixels to adjust title vertical shift by.
            interline_spacing: Pixels to adjust title interline spacing.
            kerning: Scalar to apply to kerning of the title text.
            stroke_width: Scalar to apply to black stroke of the title
                text.
            logo: Filepath to the logo file.
            kwargs: Unused arguments.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        self.source_file = source
        self.output_file = output_file
        if logo is None:
            self.logo = None
        else:
            try:
                logo = logo.format(season_number=season_number,
                                   episode_number=episode_number)
                self.logo = Path(CleanPath(logo).sanitize())
            except Exception as e:
                self.valid = False
                log.exception(f'Invalid logo file "{logo}"', e)

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title)
        self.season_text = self.image_magick.escape_chars(season_text.upper())
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        
        self.font = font
        self.font_size = font_size
        self.title_color = title_color
        self.hide_season = hide_season
        self.blur = blur
        self.vertical_shift = vertical_shift
        self.interline_spacing = interline_spacing
        self.kerning = kerning
        self.stroke_width = stroke_width


    @property
    def logo_command(self) -> list[str]:
        """
        Get the ImageMagick commands to add the resized logo to the
        source image.

        Returns:
            List of ImageMagick commands.
        """

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
    def title_text(self) -> list[str]:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        center gravity.

        Returns:
            List of ImageMagick commands.
        """

        # Get the title color and stroke for this logo
        title_color, stroke_color = self._get_logo_color()

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.interline_spacing
        kerning = -1.25 * self.kerning
        stroke_width = 3.0 * self.stroke_width
        vertical_shift = 125 + self.vertical_shift

        return [
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
            f'-fill {stroke_color}',
            f'-stroke {stroke_color}',
            f'-strokewidth {stroke_width}',
            f'-annotate +50+{vertical_shift} "{self.title}"',
            f'-fill "{title_color}"',
            f'-annotate +50+{vertical_shift} "{self.title}"',
        ]   


    def _get_logo_color(self) -> tuple[str, str]:
        """
        Get the logo color for this card's logo.

        Returns:
            Tuple whose values are the title color text and the stroke
            width color.
        """

        # If auto color wasn't indicated use indicated color and black stroke
        if self.title_color.lower() != 'auto':
            return self.title_color, 'black'

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
    def index_text_command(self) -> list[str]:
        """
        Get the ImageMagick commands required to add the index (season
        and episode) text to the image.

        Returns:
            List of ImageMagick commands.
        """

        # Season hiding, just add episode text
        if self.hide_season:
            return [
                f'-kerning 5.42',
                f'-pointsize 67.75',
                f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
                f'-gravity southwest',
                f'-fill black',
                f'-stroke black',
                f'-strokewidth 6',
                f'-annotate +50+50 "{self.episode_text}"',
                f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-strokewidth 0.75',
                f'-annotate +50+50 "{self.episode_text}"',
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
        Determines whether the given font characteristics constitute a default
        or custom font.
        
        :param      font:   The Font being evaluated.
        
        :returns:   True if a custom font is indicated, False otherwise.
        """

        return ((font.file != TitleColorMatch.TITLE_FONT)
             or (font.size != 1.0)
             or (font.color != TitleColorMatch.TITLE_COLOR)
             or (font.replacements != TitleColorMatch.FONT_REPLACEMENTS)
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

        standard_etf = TitleColorMatch.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map or
                episode_text_format.upper() != standard_etf)


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """
        
        # Skip card if logo doesn't exist
        if self.logo is None:
            log.error(f'Logo file not specified')
            return None
        elif not self.logo.exists():
            log.error(f'Logo file "{self.logo.resolve()}" does not exist')
            return None

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
            *self.title_text,
            # Put season/episode text
            *self.index_text_command,
            # Create and resize output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)