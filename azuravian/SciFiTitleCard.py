from pathlib import Path
from typing import Optional

from modules.BaseCardType import BaseCardType, ImageMagickCommands
from modules.Debug import log
from modules.RemoteFile import RemoteFile


class SciFiTitleCard(BaseCardType):
    """
    This class describes a type of BaseCardType that produces title cards
    in a SciFi style as if viewed through a HUD.
    """

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'azuravian' / 'ref' / 'SciFi'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 20,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,      # This class uses bottom heavy titling
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str((REF_DIRECTORY / 'PcapTerminal-BO9B.ttf').resolve())
    TITLE_COLOR = 'white'
    STROKE_COLOR = 'black'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {
        '[': '(', ']': ')', '(': '[', ')': ']', '―': '-', '…': '...'
    }

    """Characteristics of the episode text"""
    EPISODE_TEXT_FORMAT = "S{season_number:02}E{episode_number:02}"
    EPISODE_TEXT_FONT = REF_DIRECTORY / 'PcapTerminal-BO9B.ttf'
    EPISODE_NUMBER_FONT = REF_DIRECTORY / 'PcapTerminal-BO9B.ttf'

    """Default fonts and color for series count text"""
    SEASON_COUNT_FONT = REF_DIRECTORY / 'PcapTerminal-BO9B.ttf'
    EPISODE_COUNT_FONT = REF_DIRECTORY / 'PcapTerminal-BO9B.ttf'
    SERIES_COUNT_TEXT_COLOR = 'white'

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = True

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Sci-Fi Style'

    """Path to the hud images to overlay on all source images"""
    __OVERLAY_BASE = str(RemoteFile('azuravian', 'ref/SciFi/Base.png'))
    __OVERLAY_BOTTOM = str(RemoteFile('azuravian', 'ref/SciFi/Bottom.png'))
    __OVERLAY_MIDDLE = str(RemoteFile('azuravian', 'ref/SciFi/Middle.png'))
    __OVERLAY_TOP = str(RemoteFile('azuravian', 'ref/SciFi/Top.png'))
    __OVERLAY_RECTANGLES = str(RemoteFile('azuravian', 'ref/SciFi/Rectangles.png'))
    
    __slots__ = (
        'source_file', 'output_file', 'title_text', 'season_text',
        'episode_text', 'hide_season_text', 'hide_episode_text', 'font_color',
        'stroke_color', 'font_file', 'font_interline_spacing', 'font_kerning', 'font_size',
        'font_stroke_width', 'font_vertical_shift', 'episode_prefix',
        'overlay_bottom_color', 'overlay_middle_color', 'overlay_top_color',
        'overlay_rectangles_color', 'overlay_base_alpha','overlay_middle_alpha',
        'overlay_bottom_alpha', 'overlay_top_alpha', 'overlay_rectangles_alpha',
    )

    def __init__(self,
            source_file: Path,
            card_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            stroke_color: str = STROKE_COLOR,
            font_interline_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            season_number: int = 1,
            episode_number: int = 1,
            overlay_bottom_color: str = 'rgb(58, 255, 255)',
            overlay_middle_color: str = 'rgb(255, 255, 255)',
            overlay_top_color: str = 'rgb(255, 49, 255)',
            overlay_rectangles_color: str = 'rgb(102, 211, 122)',
            overlay_base_alpha: float = 1.0,
            overlay_bottom_alpha: float = 0.6,
            overlay_middle_alpha: float = 0.6,
            overlay_top_alpha: float = 0.6,
            overlay_rectangles_alpha: float = 0.6,
            blur: bool = False,
            grayscale: bool = False,
            preferences: Optional['Preferences'] = None, # type: ignore
            **unused,
        ) -> None:
        """
        Initialize the CardType object.
        """

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        # Store source and output file
        self.source_file = source_file
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text.upper())
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        self.hide_season_text = hide_season_text
        self.hide_episode_text = hide_episode_text

        # Font customizations
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift

        # Attempt to detect prefix text
        if self.hide_episode_text:
            self.episode_prefix, self.episode_text = None, None
        else:
            if ' ' in episode_text:
                prefix, text = episode_text.upper().split(' ', 1)
                self.episode_prefix, self.episode_text = map(
                    self.image_magick.escape_chars,
                    (prefix, text)
                )
            else:
                self.episode_text = episode_text

        # Optional extras
        self.overlay_bottom_color = overlay_bottom_color
        self.overlay_top_color = overlay_top_color
        self.overlay_middle_color = overlay_middle_color
        self.overlay_rectangles_color = overlay_rectangles_color
        self.overlay_base_alpha = 1 / overlay_base_alpha
        self.overlay_bottom_alpha = 1 / overlay_bottom_alpha
        self.overlay_top_alpha = 1 / overlay_top_alpha
        self.overlay_middle_alpha = 1 / overlay_middle_alpha
        self.overlay_rectangles_alpha = 1 / overlay_rectangles_alpha


    @property
    def title_text_command(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        center gravity.

        Returns:
            List of ImageMagick commands.
        """

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.font_interline_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 250 + self.font_vertical_shift
        title_text = f'{self.title_text}_'

        return [
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing 50',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity southeast',
            f'-strokewidth {stroke_width}',
            f'-stroke {self.stroke_color}',
            f'-fill {self.TITLE_COLOR}',
            f'-annotate +200+{vertical_shift} "{title_text}"'
        ]


    @property
    def index_text_command(self) -> ImageMagickCommands:
        """
        Get the ImageMagick commands required to add the index (season
        and episode) text to the image.

        Returns:
            List of ImageMagick commands.
        """
        stroke_width = 3.0 * self.font_stroke_width

        # Season hiding, just add episode text
        if self.hide_season_text:
            return [
                f'-kerning 5.42',
                f'-pointsize 67.75',
                f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
                f'-gravity northwest',
                f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
                f'-strokewidth {stroke_width}',
                f'-stroke {self.stroke_color}',
                f'-annotate +160+100 "{self.episode_text}"'
            ]

        return [
            f'-background transparent',
            f'+interword-spacing',
            f'-kerning 5.42',
            f'-pointsize 67.75',
            f'-fill "{self.SERIES_COUNT_TEXT_COLOR}"',
            f'-strokewidth {stroke_width}',
            f'-stroke {self.stroke_color}',
            f'\( -gravity center',
            f'-font "{self.SEASON_COUNT_FONT.resolve()}"',
            f'label:"{self.season_text}"',
            f'-font "{self.EPISODE_COUNT_FONT.resolve()}"',
            f'label:"{self.episode_text}"',
            f'+smush 5.42 \)',
            f'-gravity northwest',
            f'-geometry +160+100',
            f'-composite'
        ]


    @staticmethod
    def modify_extras(
            extras: dict,
            custom_font: bool,
            custom_season_titles: bool,
        ) -> None:
        """
        Modify the given extras based on whether font or season titles
        are custom.

        Args:
            extras: Dictionary to modify.
            custom_font: Whether the font are custom.
            custom_season_titles: Whether the season titles are custom.
        """

        # Generic font, reset episode text and box colors
        # TODO
        ...


    @staticmethod
    def is_custom_font(font: 'Font') -> bool: # type: ignore
        """
        Determines whether the given arguments represent a custom font
        for this card.

        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.color != SciFiTitleCard.TITLE_COLOR)
            or (font.file != SciFiTitleCard.TITLE_FONT)
            or (font.interline_spacing != 0)
            or (font.interword_spacing != 0)
            or (font.size != 1.0)
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

        standard_etf = SciFiTitleCard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map or
                episode_text_format.upper() != standard_etf)


    def overlay_hud(self, overlay, color, alpha) -> Path:
        """
        Edit the rectangles hud layer to selected color and transparency.
        
        :returns:   Path to the created image.
        """

        return [
            f'\( "{overlay}"',
            f'-fill "{color}"',
            f'-colorize 100%',
            f'-alpha set',
            f'-channel A',
            f'-evaluate Divide {alpha} \)',
            f'-composite'
        ]


    def create(self) -> None:
        """Create the title card as defined by this object."""

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            # Resize and apply styles
            *self.resize_and_style,
            # Overlay hud
            *self.overlay_hud(self.__OVERLAY_BASE, "black", self.overlay_base_alpha),
            *self.overlay_hud(self.__OVERLAY_BOTTOM, self.overlay_bottom_color, self.overlay_bottom_alpha),
            *self.overlay_hud(self.__OVERLAY_MIDDLE, self.overlay_middle_color, self.overlay_middle_alpha),
            *self.overlay_hud(self.__OVERLAY_TOP, self.overlay_top_color, self.overlay_top_alpha),
            *self.overlay_hud(self.__OVERLAY_RECTANGLES, self.overlay_rectangles_color, self.overlay_rectangles_alpha),
            # Put title text
            *self.title_text_command,
            # Put season/episode text
            *self.index_text_command,
            # Create and resize output
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
