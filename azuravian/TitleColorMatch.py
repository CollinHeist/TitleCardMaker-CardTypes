from pathlib import Path
from re import findall, compile as re_compile

from modules.BaseCardType import BaseCardType
from modules.CleanPath import CleanPath
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class TitleColorMatch(BaseCardType):
    """
    This class describes a type of CardType created by azuravian, and is 
    a modification of Beedman's GradientLogoTitleCard class with a few changes, 
    specifically the ability to autoselect a font color that matches the logo, 
    as well as trimming the logo of any extra transparent space that makes its 
    location incorrect.
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
    FONT_REPLACEMENTS = {'[': '(', ']': ')', '(': '[', ')': ']', '―': '-',
                         '…': '...'}

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

    """Paths to intermediate files that are deleted after the card is created"""
    __RESIZED_LOGO = BaseCardType.TEMP_DIR / 'resized_logo.png'
    __SOURCE_WITH_GRADIENT = BaseCardType.TEMP_DIR / 'source_gradient.png'
    __GRADIENT_WITH_TITLE = BaseCardType.TEMP_DIR / 'gradient_title.png'
    __SERIES_COUNT_TEXT = BaseCardType.TEMP_DIR / 'series_count_text.png'

    """Regex to match colors/counts in ImageMagick histograms"""
    __COLORDATA_REGEX = re_compile(r'[\s]*(\d*)?:\s.*\s(#\w{8}).*\n?')

    __slots__ = (
        'source_file', 'logo', 'output_file', 'title', 'season_text',
        'episode_text', 'font', 'font_size', 'title_color', 'hide_season',
        'vertical_shift', 'interline_spacing', 'kerning', 'stroke_width'
    )


    def __init__(self, source: Path, output_file: Path, title: str,
                 season_text: str, episode_text: str, font: str,
                 font_size: float, title_color: str, hide_season: bool,
                 vertical_shift: int=0,
                 interline_spacing: int=0,
                 kerning: float=1.0,
                 stroke_width: float=1.0,
                 season_number: int=1,
                 episode_number: int=1,
                 blur: bool=False,
                 grayscale: bool=False,
                 logo: str=None,
                 **unused) -> None:
        """
        Initialize the TitleCardMaker object. This primarily just stores
        instance variables for later use in `create()`. If the provided font
        does not have a character in the title text, a space is used instead.

        Args:
            source: Source image.
            output_file: Output file.
            title: Episode title.
            season_text: Text to use as season count text.
            episode_text: Text to use as episode count text.
            font: Font to use for the episode title.
            font_size: Scalar to apply to the title font size.
            title_color: Color to use for the episode title.
            hide_season: Whether to omit the season text (and joining character)
                from the title card completely.
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            vertical_shift: Pixels to adjust title vertical shift by.
            interline_spacing: Pixels to adjust title interline spacing by.
            kerning: Scalar to apply to kerning of the title text.
            stroke_width: Scalar to apply to black stroke of the title text.
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


    def __title_text_global_effects(self) -> list:
        """
        ImageMagick commands to implement the title text's global effects.
        Specifically the the font, kerning, fontsize, and center gravity.
        
        :returns:   List of ImageMagick commands.
        """

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.interline_spacing
        kerning = -1.25 * self.kerning

        return [
            f'-font "{self.font}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southwest',
        ]   


    def __title_text_black_stroke(self, stroke) -> list:
        """
        ImageMagick commands to implement the title text's black stroke.
        
        :returns:   List of ImageMagick commands.
        """

        stroke_width = 3.0 * self.stroke_width

        return [
            f'-fill {stroke}',
            f'-stroke {stroke}',
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
            f'-pointsize 67.75',
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
            f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-stroke "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-strokewidth 0.75',
        ]

    def _resize_logo(self) -> Path:
        """
        Resize the logo into at most a 1155x650 bounding box.
        
        :returns:   Path to the created image.
        """
        
        command = ' '.join([
            f'convert',
            f'"{self.logo.resolve()}"',
            f'-trim +repage',
            f'-resize x650',
            f'-resize 1155x650\>',
            f'"{self.__RESIZED_LOGO.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__RESIZED_LOGO
        
    def _add_gradient(self) -> Path:
        """
        Add the static gradient to this object's source image.
        
        :returns:   Path to the created image.
        """

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            *self.resize_and_style,
            f'"{self.__GRADIENT_IMAGE}"',
            f'-background None',
            f'-layers Flatten',
            f'"{self.__SOURCE_WITH_GRADIENT.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__SOURCE_WITH_GRADIENT

    def _add_logo_to_backdrop(self, resized_logo: Path, gradient_image: Path) -> Path:
        """
        Add the resized logo to the same intermediate image as above because that's what worked.
        
        :returns:   Path to the created image.
        """

        command = ' '.join([
            f'convert "{gradient_image.resolve()}"',
            f'"{resized_logo.resolve()}"',
            f'-gravity northwest',
            # Keep color logo on a black and white image
            f'-define colorspace:auto-grayscale=false',
            f'-type TrueColorAlpha',  
            f'-geometry "+50+50"',
            f'-composite "{self.__SOURCE_WITH_GRADIENT.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__SOURCE_WITH_GRADIENT


    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        """
        Convert the given hex color to an RGB tuple.

        Args:
            value: Hex value to convert

        Returns:
            Tuple of integers that are RGB.
        """

        value = value.lstrip('#')
        lv = len(value)

        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv//3))


    def _get_logo_color(self) -> tuple[str, tuple[int, int, int]]:
        """
        Get the logo color for this card's logo.

        Returns:
            Tuple whose values are the title color text and the RGB color
            values.
        """

        # If auto color wasn't indicated
        if self.title_color.lower() != 'auto':
            return self.title_color, None

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
        cdata = {k: [num, hex] for k, (num, hex)
                 in enumerate(findall(self.__COLORDATA_REGEX,colordata),start=1)}

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
            hexcolor = next(x[1][:7] for x in pairs if int(x[0])==num)
            rgb = self._hex_to_rgb(hexcolor)
            # Skip values that are too dark/light
            if min(rgb) > 240 or max(rgb) < 15:
                continue
            else:
                return hexcolor, rgb

        # No valid colors identified, return defaults
        return self.TITLE_COLOR, (235, 235, 235)

    
    def _add_title_text(self, gradient_image: Path) -> Path:
        """
        Adds episode title text to the provided image.

        :param      gradient_image: The image with gradient added.
        
        :returns:   Path to the created image that has a gradient and the title
                    text added.
        """
        
        # Get the title color for this logo (if indicated)
        t_color, rgb = self._get_logo_color()

        # If a valid color was found, get apparant luminance
        if rgb is not None:
            r, g, b = rgb
            lum = (r*0.299 + g*0.587 + b*0.114)
        else:
            lum = 255

        # Use white stroke only if luminance is very low
        stroke = 'black' if lum > 50 else 'white'
        vertical_shift = 125 + self.vertical_shift

        command = ' '.join([
            f'convert "{gradient_image.resolve()}"',
            *self.__title_text_global_effects(),
            *self.__title_text_black_stroke(stroke),
            f'-annotate +50+{vertical_shift} "{self.title}"',
            f'-fill "{t_color}"',
            f'-annotate +50+{vertical_shift} "{self.title}"',
            f'"{self.__GRADIENT_WITH_TITLE.resolve()}"',
        ])

        self.image_magick.run(command)

        return self.__GRADIENT_WITH_TITLE


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
            f'-gravity southwest',
            *self.__series_count_text_black_stroke(),
            f'-annotate +50+50 "{self.episode_text}"',
            *self.__series_count_text_effects(),
            f'-annotate +50+50 "{self.episode_text}"',
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
            f'-annotate +0+689.5 "• "',
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


    def _create_series_count_text_image(self, width: float, width1: float,
                                        width2: float, height: float) -> Path:
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
            f'-annotate +{width1}+{height-25-6.5} "•"',
            *self.__series_count_text_effects(),
            f'-annotate +{width1}+{height-25-6.5} "•"',
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
        Combine the titled image (image+gradient+episode title) and the series
        count image (optional season number+optional dot+episode number) into a
        single image. This is written into the output image for this object.

        :param      titled_image:       Path to the titled image to add.
        :param      series_count_image: Path to the series count transparent
                                        image to add.

        :returns:   Path to the created image (the output file).
        """

        command = ' '.join([
            f'composite',
            f'-gravity southwest',
            f'-geometry +50+50',
            f'"{series_count_image.resolve()}"',
            f'"{titled_image.resolve()}"',
            *self.resize_output,
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
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
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
        
        # Add the gradient to the source image (always)
        gradient_image = self._add_gradient()
        
        # Create backdrop+logo image
        backdrop_logo = self._add_logo_to_backdrop(resized_logo, gradient_image)

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
        images = [gradient_image, titled_image]
        if not self.hide_season:
            images.append(series_count_image)

        self.image_magick.delete_intermediate_images(*images)
