from pathlib import Path
from re import findall
from typing import Optional

from modules.BaseCardType import BaseCardType
from modules.RemoteFile import RemoteFile
from modules.Debug import log

class WhiteTextStandardLogo(BaseCardType):
    """
    WDVH's WhiteTextStandardLogo card type.
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

    """Whether this CardType uses unique source images"""
    USES_UNIQUE_SOURCES = False

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'White Text Standard Logo Style'

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'Sequel-Neue.otf'
    SERIES_COUNT_TEXT_COLOR = '#FFFFFF'

    """Paths to intermediate files that are deleted after the card is created"""
    __RESIZED_LOGO = BaseCardType.TEMP_DIR / 'resized_logo.png'
    __BACKDROP_WITH_LOGO = BaseCardType.TEMP_DIR / 'backdrop_logo.png'
    __LOGO_WITH_TITLE = BaseCardType.TEMP_DIR / 'logo_title.png'
    __SERIES_COUNT_TEXT = BaseCardType.TEMP_DIR / 'series_count_text.png'

    __slots__ = (
        'logo', 'output_file', 'title', 'season_text', 'episode_text', 'font',
        'font_size', 'title_color', 'hide_season', 'separator','vertical_shift', 
        'interline_spacing', 'kerning', 'stroke_width', 'background',
    )


    def __init__(self, *,
            card_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
            season_number: int = 1,
            episode_number: int = 1,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_kerning: float = 1.0,
            font_interline_spacing: int = 0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            logo: Optional[str] = None, 
            background: str = '#000000',
            separator: str = '-',
            **unused) -> None:
        """
        Initialize this CardType object.
        """
        
        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Look for logo if it's a format string
        if isinstance(logo, str):
            try:
                logo = logo.format(
                    season_number=season_number, episode_number=episode_number
                )
            except Exception:
                pass
            
            # Use either original or modified logo file
            self.logo = Path(logo)
        else:
            self.logo = None

        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text.upper())
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        self.hide_season = hide_season_text

        self.font = font_file
        self.font_size = font_size
        self.title_color = font_color
        self.vertical_shift = font_vertical_shift
        self.interline_spacing = font_interline_spacing
        self.kerning = font_kerning
        self.stroke_width = font_stroke_width

        self.background = background
        self.separator = separator


    def __title_text_global_effects(self) -> list[str]:
        """
        ImageMagick commands to implement the title text's global effects.
        Specifically the the font, kerning, fontsize, and center gravity.
        
        Returns:
            List of ImageMagick commands.
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


    def __title_text_black_stroke(self) -> list[str]:
        """
        ImageMagick commands to implement the title text's black stroke.
        
        Returns:
            List of ImageMagick commands.
        """

        stroke_width = 4.0 * self.stroke_width

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth {stroke_width}',
        ]


    def __series_count_text_global_effects(self) -> list[str]:
        """
        ImageMagick commands for global text effects applied to all series count
        text (season/episode count and dot).
        
        Returns:
            List of ImageMagick commands.
        """

        return [
            f'-kerning 5.42',
            f'-pointsize 85',
        ]


    def __series_count_text_black_stroke(self) -> list[str]:
        """
        ImageMagick commands for adding the necessary black stroke effects to
        series count text.
        
        Returns:
            List of ImageMagick commands.
        """

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
        ]


    def __series_count_text_effects(self) -> list[str]:
        """
        ImageMagick commands for adding the necessary text effects to the series
        count text.
        
        Returns:
            List of ImageMagick commands.
        """

        return [
            f'-fill white',
            f'-stroke "#062A40"',
            f'-strokewidth 2',
        ]


    def _resize_logo(self) -> Path:
        """
        Resize the logo into at most a 1875x1030 bounding box.
        
        Returns:
            Path to the created image.
        """

        command = ' '.join([
            f'convert',
            f'"{self.logo.resolve()}"',
            f'-resize x1030',
            f'-resize 1875x1030\>',
            f'"{self.__RESIZED_LOGO.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__RESIZED_LOGO


    def _add_logo_to_backdrop(self, resized_logo: Path) -> Path:
        """
        Add the resized logo to a fixed color backdrop.
        
        Returns:
            Path to the created image.
        """

        # Get height of the resized logo to determine offset
        height_command = ' '.join([
            f'identify',
            f'-format "%h"',
            f'"{resized_logo.resolve()}"',
        ])

        height = int(self.image_magick.run_get_output(height_command))

        # Get offset of where to place logo onto card
        offset = 60 + ((1030 - height) // 2)

        command = ' '.join([
            f'convert',
            f'-size "{self.TITLE_CARD_SIZE}"',  # Create backdrop
            f'xc:"{self.background}"',          # Fill canvas with color
            f'"{resized_logo.resolve()}"',
            f'-set colorspace sRGB',
            f'-gravity north',
            f'-geometry "+0+{offset}"',         # Put logo on backdrop
            f'-composite "{self.__BACKDROP_WITH_LOGO.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__BACKDROP_WITH_LOGO


    def _add_title_text(self, backdrop_logo: Path) -> Path:
        """
        Adds episode title text to the provide image.

        :param      backdrop_logo:  The backdrop and logo image.
        
        :returns:   Path to the created image that has the title text added.
        """

        vertical_shift = 245 + self.vertical_shift

        command = ' '.join([
            f'convert "{backdrop_logo.resolve()}"',
            *self.resize_and_style,
            *self.__title_text_global_effects(),
            *self.__title_text_black_stroke(),
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'-fill "{self.title_color}"',
            f'-annotate +0+{vertical_shift} "{self.title}"',
            f'"{self.__LOGO_WITH_TITLE.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__LOGO_WITH_TITLE


    def _add_series_count_text_no_season(self, titled_image: Path) -> Path:
        """
        Adds the series count text without season title/number.
        
        :param      titled_image:  The titled image to add text to.

        :returns:   Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert "{titled_image.resolve()}"',
            *self.__series_count_text_global_effects(),
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity center',
            *self.__series_count_text_black_stroke(),
            f'-annotate +0+697.2 "{self.episode_text}"',
            *self.__series_count_text_effects(),
            f'-annotate +0+697.2 "{self.episode_text}"',
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.output_file


    def _get_series_count_text_dimensions(self) -> dict:
        """
        Gets the series count text dimensions.
        
        :returns:   The series count text dimensions.
        """

        command = ' '.join([
            f'convert -debug annotate xc: ',
            *self.__series_count_text_global_effects(),
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'-gravity east',
            *self.__series_count_text_effects(),
            f'-annotate +1600+697.2 "{self.season_text} "',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'-gravity center',
            *self.__series_count_text_effects(),
            f'-annotate +0+689.5 "{self.separator} "',
            f'-gravity west',
            *self.__series_count_text_effects(),
            f'-annotate +1640+697.2 "{self.episode_text}"',
            f'null: 2>&1'
        ])

        # Get text dimensions from the output
        metrics = self.image_magick.run_get_output(command)
        widths = list(map(int, findall(r'Metrics:.*width:\s+(\d+)', metrics)))
        heights = list(map(int, findall(r'Metrics:.*height:\s+(\d+)', metrics)))

        # Don't raise IndexError if no dimensions were found
        if len(widths) < 2 or len(heights) < 2:
            log.warning(f'Unable to identify font dimensions, file bug report')
            widths = [370, 47, 357]
            heights = [68, 83, 83]

        return {
            'width':    sum(widths),
            'width1':   widths[0],
            'width2':   widths[1],
            'height':   max(heights)+25,
        }


    def _create_series_count_text_image(self,
            width: float, width1: float, width2: float, height: float) -> Path:
        """
        Creates an image with only series count text. This image is transparent,
        and not any wider than is necessary (as indicated by `dimensions`).
        
        :returns:   Path to the created image containing only series count text.
        """

        # Create text only transparent image of season count text
        command = ' '.join([
            f'convert -size "{width}x{height}"',
            f'-alpha on',
            f'-background transparent',
            f'xc:transparent',
            *self.__series_count_text_global_effects(),
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            *self.__series_count_text_black_stroke(),
            f'-annotate +0+{height-25} "{self.season_text} "',
            *self.__series_count_text_effects(),
            f'-annotate +0+{height-25} "{self.season_text} "',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            *self.__series_count_text_black_stroke(),
            f'-annotate +{width1}+{height-25-6.5} "{self.separator}"',
            *self.__series_count_text_effects(),
            f'-annotate +{width1}+{height-25-6.5} "{self.separator}"',
            *self.__series_count_text_black_stroke(),
            f'-annotate +{width1+width2}+{height-25} "{self.episode_text}"',
            *self.__series_count_text_effects(),
            f'-annotate +{width1+width2}+{height-25} "{self.episode_text}"',
            f'"PNG32:{self.__SERIES_COUNT_TEXT.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__SERIES_COUNT_TEXT


    def _combine_titled_image_series_count_text(self, titled_image: Path,
                                                series_count_image: Path)->Path:
        """
        Combine the titled image (image+backdrop+episode title) and the series
        count image (optional season number+optional dot+episode number) into a
        single image. This is written into the output image for this object.

        :param      titled_image:       Path to the titled image to add.
        :param      series_count_image: Path to the series count transparent
                                        image to add.

        :returns:   Path to the created image (the output file).
        """

        command = ' '.join([
            f'convert',
            f'"{titled_image.resolve()}"',
            f'-gravity center',
            f'"{series_count_image.resolve()}"',
            f'-geometry +0+690.2',
            f'-composite',
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

        return ((font.color != WhiteTextStandardLogo.TITLE_COLOR)
            or (font.file != WhiteTextStandardLogo.TITLE_FONT)
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
            True if custom season title are indicated. False otherwise.
        """

        standard_etf = WhiteTextStandardLogo.EPISODE_TEXT_FORMAT.upper()

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

        # Resize logo
        resized_logo = self._resize_logo()
        
        # Create backdrop+logo image
        backdrop_logo = self._add_logo_to_backdrop(resized_logo)

        # Add either one or two lines of episode text 
        titled_image = self._add_title_text(backdrop_logo)

        # If season text is hidden, just add episode text 
        if self.hide_season:
            self._add_series_count_text_no_season(titled_image)
        else:
            # If adding season text, create intermediate images and combine them
            series_count_image = self._create_series_count_text_image(
                **self._get_series_count_text_dimensions()
            )
            self._combine_titled_image_series_count_text(
                titled_image,
                series_count_image
            )

        # Delete all intermediate images
        images = [resized_logo, backdrop_logo, titled_image]
        if not self.hide_season:
            images.append(series_count_image)
        
        self.image_magick.delete_intermediate_images(*images)