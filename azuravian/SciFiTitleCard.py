from pathlib import Path
from typing import Optional

from pydantic import FilePath, PositiveFloat, constr, root_validator
from app.schemas.base import BetterColor
from app.schemas.card_type import BaseCardTypeCustomFontNoText

from modules.BaseCardType import BaseCardType, ImageMagickCommands
from modules.Debug import log
from modules.RemoteFile import RemoteFile


class SciFiTitleCard(BaseCardType):
    """
    This class describes a type of BaseCardType that produces title
    cards in a SciFi style as if viewed through a HUD.
    """

    class CardModel(BaseCardTypeCustomFontNoText):
        title_text: str
        episode_text: constr(to_upper=True)
        hide_episode_text: bool = False
        font_color: BetterColor = 'white'
        font_file: FilePath
        add_trailing_underscore: bool = True
        overlay_bottom_color: BetterColor = 'rgb(58, 255, 255)'
        overlay_middle_color: BetterColor = 'rgb(255, 255, 255)'
        overlay_top_color: BetterColor = 'rgb(255, 49, 255)'
        overlay_rectangles_color: BetterColor = 'rgb(102, 211, 122)'
        overlay_base_alpha: PositiveFloat = 1.0
        overlay_bottom_alpha: PositiveFloat = 0.6
        overlay_middle_alpha: PositiveFloat = 0.6
        overlay_top_alpha: PositiveFloat = 0.6
        overlay_rectangles_alpha: PositiveFloat = 0.6
        episode_text_color: BetterColor = 'white'
        stroke_color: BetterColor = 'black'

        @root_validator(skip_on_failure=True, allow_reuse=True)
        def toggle_text_hiding(cls, values):
            values['hide_episode_text'] |= (len(values['episode_text']) == 0)

            return values

    """Directory where all reference files used by this card are stored"""
    REF_DIRECTORY = Path(__file__).parent.parent / 'azuravian' / 'ref' / 'SciFi'

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 20,   # Character count to begin splitting titles
        'max_line_count': 3,    # Maximum number of lines a title can take up
        'top_heavy': False,      # This class uses bottom heavy titling
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str(RemoteFile('azuravian', 'ref/SciFi/PcapTerminal-BO9B.ttf'))
    TITLE_COLOR = 'white'
    STROKE_COLOR = 'black'

    """Default characters to replace in the generic font"""
    FONT_REPLACEMENTS = {}

    """Characteristics of the episode text"""
    EPISODE_TEXT_FORMAT = 'S{season_number:02}E{episode_number:02}'
    EPISODE_TEXT_FONT = str(RemoteFile('azuravian', 'ref/SciFi/PcapTerminal-BO9B.ttf'))

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = False

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Sci-Fi Style'

    """Path to the hud images to overlay on all source images"""
    __OVERLAY_BASE = str(RemoteFile('azuravian', 'ref/SciFi/Base.png'))
    __OVERLAY_BOTTOM = str(RemoteFile('azuravian', 'ref/SciFi/Bottom.png'))
    __OVERLAY_MIDDLE = str(RemoteFile('azuravian', 'ref/SciFi/Middle.png'))
    __OVERLAY_TOP = str(RemoteFile('azuravian', 'ref/SciFi/Top.png'))
    __OVERLAY_RECTANGLES = str(RemoteFile('azuravian', 'ref/SciFi/Rectangles.png'))

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'episode_text',
        'hide_episode_text', 'font_color', 'stroke_color', 'font_file',
        'font_interline_spacing', 'font_interword_spacing', 'font_kerning',
        'font_size', 'font_stroke_width', 'font_vertical_shift',
        'add_trailing_underscore', 'overlay_bottom_color',
        'overlay_middle_color', 'overlay_top_color', 'overlay_rectangles_color',
        'overlay_base_alpha', 'overlay_middle_alpha', 'overlay_bottom_alpha',
        'overlay_top_alpha', 'overlay_rectangles_alpha', 'episode_text_color',
    )

    def __init__(self,
            source_file: Path,
            card_file: Path,
            title_text: str,
            episode_text: str,
            hide_episode_text: bool = False,
            font_color: str = TITLE_COLOR,
            font_file: str = TITLE_FONT,
            font_interline_spacing: int = 0,
            font_interword_spacing: int = 0,
            font_kerning: float = 1.0,
            font_size: float = 1.0,
            font_stroke_width: float = 1.0,
            font_vertical_shift: int = 0,
            blur: bool = False,
            grayscale: bool = False,
            add_trailing_underscore: bool = True,
            overlay_bottom_color: str = 'rgb(58, 255, 255)',
            overlay_middle_color: str = 'rgb(255, 255, 255)',
            overlay_top_color: str = 'rgb(255, 49, 255)',
            overlay_rectangles_color: str = 'rgb(102, 211, 122)',
            overlay_base_alpha: float = 1.0,
            overlay_bottom_alpha: float = 0.6,
            overlay_middle_alpha: float = 0.6,
            overlay_top_alpha: float = 0.6,
            overlay_rectangles_alpha: float = 0.6,
            episode_text_color: str = TITLE_COLOR,
            stroke_color: str = STROKE_COLOR,
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
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_episode_text = hide_episode_text

        # Font customizations
        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_interword_spacing = font_interword_spacing
        self.font_kerning = font_kerning
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift

        # Optional extras
        self.add_trailing_underscore = add_trailing_underscore
        self.episode_text_color = episode_text_color
        self.overlay_bottom_color = overlay_bottom_color
        self.overlay_top_color = overlay_top_color
        self.overlay_middle_color = overlay_middle_color
        self.overlay_rectangles_color = overlay_rectangles_color
        self.overlay_base_alpha = 1 / overlay_base_alpha
        self.overlay_bottom_alpha = 1 / overlay_bottom_alpha
        self.overlay_top_alpha = 1 / overlay_top_alpha
        self.overlay_middle_alpha = 1 / overlay_middle_alpha
        self.overlay_rectangles_alpha = 1 / overlay_rectangles_alpha
        self.stroke_color = stroke_color


    @property
    def title_text_command(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        center gravity.

        Returns:
            List of ImageMagick commands.
        """

        title_text = (
            self.title_text + ('_' if self.add_trailing_underscore else '')
        )

        font_size = 157.41 * self.font_size
        interline_spacing = -22 + self.font_interline_spacing
        interword_spacing = 50 + self.font_interword_spacing
        kerning = -1.25 * self.font_kerning
        stroke_width = 3.0 * self.font_stroke_width
        vertical_shift = 215 + self.font_vertical_shift

        return [
            f'-font "{self.font_file}"',
            f'-kerning {kerning}',
            f'-interword-spacing {interword_spacing}',
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

        # All text is hidden, return 
        if self.hide_episode_text:
            return []
   
        return [
            f'-font "{self.EPISODE_TEXT_FONT.resolve()}"',
            f'-fill "{self.episode_text_color}"',
            f'-kerning 5.42',
            f'-pointsize 67.75',
            f'-gravity northwest',
            f'-strokewidth 3',
            f'-stroke black',
            f'+interword-spacing',
            f'-annotate +150+100 "{self.episode_text}"'
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

        standard_etf = SciFiTitleCard.EPISODE_TEXT_FORMAT.upper()

        return (custom_episode_map or
                episode_text_format.upper() != standard_etf)


    def overlay_hud(self,
            overlay: str,
            color: str,
            alpha: float,
        ) -> ImageMagickCommands:
        """
        Edit the rectangles hud layer to selected color and transparency.
        
        Args:
            overlay: Filepath (as a string) to the overlay file.
            color: Color to colorize the overlay with.
            alpha: Transparency of this overlay.

        Returns:
            List of ImageMagick commands.
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
            # Overlay huds
            *self.overlay_hud(self.__OVERLAY_BASE, 'black', self.overlay_base_alpha),
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
