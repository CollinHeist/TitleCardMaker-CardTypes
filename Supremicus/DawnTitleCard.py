from pathlib import Path
from typing import TYPE_CHECKING, Optional, Literal, Union

from pydantic import root_validator

from app.schemas.card_type import BaseCardTypeCustomFontAllText

from modules.BaseCardType import (
    BaseCardType,
    CardDescription,
    Extra,
    ImageMagickCommands,
)
from modules.Debug import log
from modules.EpisodeInfo2 import EpisodeInfo
from modules.RemoteFile import RemoteFile
from modules.Title import SplitCharacteristics

if TYPE_CHECKING:
    from app.models.preferences import Preferences
    from modules.Font import Font


class DawnTitleCard(BaseCardType):
    """
    CardType that produces title cards with left, centered or right
    aligned text on the bottom. CRT TV overlay (nobezel or bezel) with
    optional watched style based on Yozora's Retro title card for shows
    like Stranger Things with a retro theme.
    """

    """API Parameters"""
    API_DETAILS = CardDescription(
        name='Dawn',
        identifier='Supremicus/Dawn',
        example=(
            'https://raw.githubusercontent.com/CollinHeist/'
            'TitleCardMaker-CardTypes/web-ui/Supremicus/'
            'DawnTitleCard.preview.jpg'
        ),
        creators=['Supremicus'],
        source='remote',
        supports_custom_fonts=True,
        supports_custom_seasons=True,
        supported_extras=[
            Extra(
                name='Stroke Text Color',
                identifier='stroke_color',
                description='Color to use for the text stroke',
                tooltip='Default is <c>black</c>.',
                default='black',
            ),
            Extra(
                name='Title Text Horizontal Shift',
                identifier='title_text_horizontal_shift',
                description='Horizontal shift for the title text',
                tooltip=(
                    'Horizontal shift to apply to the title text. Default is '
                    '0. Unit is pixels.'
                ),
                default=0,
            ),
            Extra(
                name='Episode Text Vertical Shift',
                identifier='episode_text_vertical_shift',
                description='Vertical shift for episode text',
                tooltip=(
                    'Additional vertical shift to apply to the season and '
                    'episode text. If you encounter multi-line issues, problem '
                    'fonts maybe fixed by Fix vertical metrics at '
                    '<v>https://transfonter.org/</v>. Default is <v>0</v>. '
                    'Unit is pixels.'
                ),
                default=0,
            ),
            Extra(
                name='Episode Text Font',
                identifier='episode_text_font',
                description='Font to use for the season and episode text',
                tooltip=(
                    'This can be just a file name if the font file is in the '
                    "Series' source directory, <v>{title_font}</v> to match "
                    'the Font used for the title text, or a full path to the '
                    'font file.'
                ),
            ),
            Extra(
                name='Episode Text Font Size',
                identifier='episode_text_font_size',
                description='Size adjustment for the season and episode text',
                tooltip='Number ≥<v>0.0</v>. Default is <v>1.0</v>.',
                default=1.0,
            ),
            Extra(
                name='Episode Text Color',
                identifier='episode_text_color',
                description='Color to use for the episode text',
                tooltip='Defaults to match the Title Color.',
            ),
            Extra(
                name='Episode Stroke Text Color',
                identifier='episode_text_stroke_color',
                description='Color to use for the stroke of the episode text',
                tooltip='Defaults to match the Stroke Text Color.',
            ),
            Extra(
                name='Episode Text Kerning',
                identifier='episode_text_kerning',
                description='Spacing between characters for the episode text',
                tooltip='Default is <v>18</v>. Unit is pixels.',
                default=18,
            ),
            Extra(
                name='Separator Character',
                identifier='separator',
                description='Character to separate season and episode text',
                tooltip='Default is <v>•</v>.',
                default='•',
            ),
            Extra(
                name='Horizontal Alignment',
                identifier='h_align',
                description='Horizontal alignment of text',
                tooltip=(
                    'Either <v>left</v>, <v>center</v>, or <v>right</v>. '
                    'Default is <v>left</v>.'
                ),
                default='left',
            ),
            Extra(
                name='CRT TV Overlay',
                identifier='crt_overlay',
                description='CRT TV Overlay Toggle',
                tooltip=(
                    'Whether to display the CRT TV overlay. Either '
                    '<v>nobezel</v>, or <v>bezel</v>. Default is no overlay.'
                ),
            ),
            Extra(
                name='CRT TV Watched/Unwatched Overlay',
                identifier='crt_state_overlay',
                description='CRT TV Overlay Watched-Status Toggle',
                tooltip=(
                    'Whether to change the CRT overlay with the watched status '
                    'of the Episode. Either <v>True</v> or <v>False</v>. '
                    'Default is <v>False</v>. Will only work if the CRT TV '
                    'Overlay Toggle is enabled.'
                ),
                default='False',
            ),
            Extra(
                name='Gradient Omission',
                identifier='omit_gradient',
                description='Whether to omit the gradient overlay',
                tooltip=(
                    'Either <v>True</v> or <v>False</v>. Set to <v>False</v> '
                    'if you have trouble reading the text on brighter images.'
                    'Default is <v>True</v>.'
                ),
                default='True',
            ),
        ],
        description=[
            'Produce TitleCards with left, centered or right aligned text on '
            'the bottom.', 'An optional CRT TV overlay can be added for shows '
            'with a retro theme (like Stranger Things)',
        ]
    )

    class CardModel(BaseCardTypeCustomFontAllText):
        stroke_color: str = 'black'
        title_text_horizontal_shift: int = 0
        episode_text_vertical_shift: int = 0
        episode_text_font: Union[
            Literal['{title_font}'],
            str,
            Path
        ] = str(RemoteFile('Supremicus', 'ref/fonts/ExoSoft-Medium.ttf'))
        episode_text_font_size: float = 1.0
        episode_text_color: str | None = None
        episode_text_stroke_color: str | None = None
        episode_text_kerning: int = 18
        separator: str = '•'
        h_align: Literal['left', 'center', 'right'] = 'left'
        crt_overlay: Literal['nobezel', 'bezel'] | None = None
        crt_state_overlay: bool = False
        omit_gradient: bool = True

        @root_validator(skip_on_failure=True)
        def validate_episode_text_font_file(cls, values: dict) -> dict:
            # Specified as "{title_font}" - use title font file
            if (etf := values['episode_text_font']) == '{title_font}':
                values['episode_text_font'] = values['font_file']
            # Episode text font does not exist, search alongside source image
            elif not (etf := Path(etf)).exists():
                if (new_etf := values['source_file'].parent / etf.name).exists():
                    values['episode_text_font'] = new_etf

            # Verify new specified font file does exist
            values['episode_text_font'] = Path(values['episode_text_font'])
            if not Path(values['episode_text_font']).exists():
                raise ValueError(
                    f'Specified Episode Text Font ('
                    f'{values["episode_text_font"]}) does not exist'
                )

            return values

        @root_validator(skip_on_failure=True)
        def validate_extras(cls, values: dict) -> dict:
            # Convert None colors to the default font color
            if values['episode_text_color'] is None:
                values['episode_text_color'] = values['font_color']
            if values['episode_text_stroke_color'] is None:
                values['episode_text_stroke_color'] = values['stroke_color']

            return values

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS: SplitCharacteristics = {
        'max_line_width': 28,
        'max_line_count': 4,
        'style': 'bottom',
    }

    """Characteristics of the default title font"""
    TITLE_FONT = str(RemoteFile('Supremicus', 'ref/fonts/HelveticaNeue-Bold.ttf'))
    TITLE_COLOR = 'white'
    FONT_REPLACEMENTS = {}

    """Whether this CardType uses season titles for archival purposes"""
    USES_SEASON_TITLE = True

    """Standard class has standard archive name"""
    ARCHIVE_NAME = 'Dawn'

    """Characteristics of episode text"""
    EPISODE_TEXT_FORMAT = 'EPISODE {to_cardinal(episode_number)}'
    EPISODE_TEXT_FONT = RemoteFile('Supremicus', 'ref/fonts/ExoSoft-Medium.ttf')

    """Source path for CRT overlays to be overlayed if enabled"""
    __OVERLAY_PLAIN = RemoteFile('Supremicus', 'ref/overlays/overlay_plain.png')
    __OVERLAY_PLAIN_BEZEL = RemoteFile('Supremicus', 'ref/overlays/overlay_plain_bezel.png')
    __OVERLAY_PLAY = RemoteFile('Supremicus', 'ref/overlays/overlay_play.png')
    __OVERLAY_PLAY_BEZEL = RemoteFile('Supremicus', 'ref/overlays/overlay_play_bezel.png')
    __OVERLAY_REWIND = RemoteFile('Supremicus', 'ref/overlays/overlay_rewind.png')
    __OVERLAY_REWIND_BEZEL = RemoteFile('Supremicus', 'ref/overlays/overlay_rewind_bezel.png')

    """Source path for the gradient image"""
    __GRADIENT_IMAGE = RemoteFile('Supremicus', 'ref/overlays/gradient.png')

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'season_text',
        'episode_text', 'hide_season_text', 'hide_episode_text',
        'line_count', 'font_color', 'font_file', 'font_interline_spacing',
        'font_interword_spacing', 'font_kerning', 'font_size', 'font_stroke_width',
        'font_vertical_shift', 'stroke_color', 'title_text_horizontal_shift',
        'episode_text_vertical_shift', 'episode_text_font', 'episode_text_font_size',
        'episode_text_color', 'episode_text_stroke_color', 'episode_text_kerning', 
        'separator', 'h_align', 'crt_overlay', 'crt_state_overlay', 'omit_gradient'
    )

    def __init__(self, *,
            source_file: Path,
            card_file: Path,
            title_text: str,
            season_text: str,
            episode_text: str,
            hide_season_text: bool = False,
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
            stroke_color: str = 'black',
            title_text_horizontal_shift: int = 0,
            episode_text_vertical_shift: int = 0,
            episode_text_font: Path = EPISODE_TEXT_FONT,
            episode_text_font_size: float = 1.0,
            episode_text_color: str = None,
            episode_text_stroke_color: str = None,
            episode_text_kerning: int = 18,
            separator: str = '•',
            h_align: Literal['left', 'center', 'right'] = 'left',
            crt_overlay: Literal['nobezel', 'bezel'] | None = None,
            crt_state_overlay: bool = False,
            omit_gradient: bool = True,
            preferences: Optional['Preferences'] = None,
            **unused,
        ) -> None:
        """Construct a new instance of this card."""

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        self.source_file = source_file
        self.output_file = card_file

        # Ensure characters that need to be escaped are
        self.title_text = self.image_magick.escape_chars(title_text)
        self.season_text = self.image_magick.escape_chars(season_text)
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_season_text = hide_season_text
        self.hide_episode_text = hide_episode_text
        self.line_count = len(title_text.split('\n'))

        # Font/card customizations
        self.font_color = font_color
        self.font_file = font_file
        self.font_kerning = font_kerning
        self.font_interline_spacing = font_interline_spacing
        self.font_interword_spacing = font_interword_spacing
        self.font_size = font_size
        self.font_stroke_width = font_stroke_width
        self.font_vertical_shift = font_vertical_shift

        # Optional extras
        self.stroke_color = stroke_color
        self.title_text_horizontal_shift = title_text_horizontal_shift
        self.episode_text_vertical_shift = episode_text_vertical_shift
        self.episode_text_font = episode_text_font
        self.episode_text_font_size = episode_text_font_size
        self.episode_text_color = episode_text_color
        self.episode_text_stroke_color = episode_text_stroke_color
        self.episode_text_kerning = episode_text_kerning
        self.separator = separator
        self.h_align = h_align
        self.crt_overlay = crt_overlay
        self.crt_state_overlay = crt_state_overlay
        self.omit_gradient = omit_gradient


    @property
    def index_text_commands(self) -> ImageMagickCommands:
        """Subcommand for adding the index text to the image."""

        # All text hidden, return empty commands
        if self.hide_season_text and self.hide_episode_text:
            return []

        # Set index text based on which text is hidden/not
        if self.hide_season_text:
            index_text = self.episode_text
        elif self.hide_episode_text:
            index_text = self.season_text
        else:
            index_text = f'{self.season_text} {self.separator} {self.episode_text}'

        # Horizontal Alignment
        if self.h_align == 'left':
            gravity = 'southwest'
            x = 200
        elif self.h_align == 'center':
            gravity = 'south'
            x = 0
        else:
            gravity = 'southeast'
            x = 200

        # Font customizations
        stroke_width = 4.0 * self.font_stroke_width

        # Base commands
        base_commands = [
            f'-background transparent',
            f'-kerning {self.episode_text_kerning}',
            f'-pointsize {60 * self.episode_text_font_size}',
            f'-interword-spacing 14.5',
            f'-gravity {gravity}',
            f'-font "{self.episode_text_font.resolve()}"',
        ]

        # Text offsets
        offset = (124 * self.font_size) * self.line_count
        vertical_shift = 50 + self.font_vertical_shift
        y = 80 + vertical_shift + offset + self.episode_text_vertical_shift

        return [
            *base_commands,
            f'-fill {self.episode_text_stroke_color}',
            f'-stroke {self.episode_text_stroke_color}',
            f'-strokewidth {stroke_width}',
            f'-annotate {x:+}{y:+} "{index_text}"',
            f'-fill "{self.episode_text_color}"',
            f'-stroke "{self.episode_text_color}"',
            f'-strokewidth 0',
            f'-annotate {x:+}{y:+} "{index_text}"',
        ]

    @property
    def title_text_commands(self) -> ImageMagickCommands:
        """Subcommands required to add the title text."""

        # If no title text, return empty commands
        if not self.title_text:
            return []

        # Horizontal Alignment
        if self.h_align == 'left':
            x = 200 + self.title_text_horizontal_shift
        elif self.h_align == 'center':
            x = 0
        else:
            x = 200 + self.title_text_horizontal_shift

        # Text offsets
        vertical_shift = 50 + self.font_vertical_shift
        y = 80 + vertical_shift

        return [
            *self.title_text_global_effects,
            *self.title_text_black_stroke,
            f'-annotate {x:+}{y:+} "{self.title_text}"',
            *self.title_text_effects,
            f'-annotate {x:+}{y:+} "{self.title_text}"',
        ]


    @property
    def title_text_global_effects(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's global
        effects. Specifically the the font, kerning, fontsize, and
        southwest gravity.
        """

        # Horizontal Alignment
        if self.h_align == 'left':
            gravity = 'southwest'
        elif self.h_align == 'center':
            gravity = 'south'
        else:
            gravity = 'southeast'

        # Font customizations
        font_size = 124 * self.font_size
        interline_spacing = -20 + self.font_interline_spacing
        interword_spacing = 50 + self.font_interword_spacing
        kerning = -1.25 * self.font_kerning

        return [
            f'-font "{self.font_file.resolve()}"',
            f'-kerning {kerning}',
            f'-interline-spacing {interline_spacing}',
            f'-interword-spacing {interword_spacing}',
            f'-pointsize {font_size}',
            f'-gravity {gravity}',
        ]


    @property
    def title_text_black_stroke(self) -> ImageMagickCommands:
        """
        ImageMagick commands to implement the title text's black stroke.
        """

        # No stroke, return empty command
        if self.font_stroke_width == 0:
            return []

        stroke_width = 4.0 * self.font_stroke_width

        return [
            f'-fill "{self.stroke_color}"',
            f'-stroke "{self.stroke_color}"',
            f'-strokewidth {stroke_width}',
        ]


    @property
    def title_text_effects(self) -> ImageMagickCommands:
        """Subcommands to implement the title text's standard effects."""

        return [
            f'-fill "{self.font_color}"',
            f'-stroke "{self.font_color}"',
            f'-strokewidth 0',
        ]


    @property
    def add_crt_overlay_commands(self) -> ImageMagickCommands:
        """Add the static gradient to this object's source image."""

        if self.crt_overlay is None:
            return []

        # Select CRT overlay based on watch status
        if self.crt_overlay == 'nobezel':
            if self.crt_state_overlay and not self.watched:
                crt_overlay_image = self.__OVERLAY_PLAY
            elif self.crt_state_overlay and self.watched:
                crt_overlay_image = self.__OVERLAY_REWIND
            else:
                crt_overlay_image = self.__OVERLAY_PLAIN
        elif self.crt_overlay == 'bezel':
            if self.crt_state_overlay and not self.watched:
                crt_overlay_image = self.__OVERLAY_PLAY_BEZEL
            elif self.crt_state_overlay and self.watched:
                crt_overlay_image = self.__OVERLAY_REWIND_BEZEL
            else:
                crt_overlay_image = self.__OVERLAY_PLAIN_BEZEL
        else:
            crt_overlay_image = self.__OVERLAY_PLAIN

        return [
            f'"{crt_overlay_image.resolve()}"',
            f'-composite',
        ]


    @property
    def gradient_commands(self) -> ImageMagickCommands:
        """
        Subcommand to overlay the gradient to this image. This rotates
        and repositions the gradient overlay based on the text position.
        """

        if self.omit_gradient:
            return []

        return [
            f'"{self.__GRADIENT_IMAGE.resolve()}"',
            f'-composite',
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

        # Generic font, reset custom episode text color
        if not custom_font:
            for extra in (
                'episode_text_color',
                'episode_text_font',
                'episode_text_font_size',
                'episode_text_kerning',
                'episode_text_stroke_color',
                'episode_text_vertical_shift',
                'stroke_color',
                'title_text_horizontal_shift',
            ):
                if extra in extras:
                    del extras[extra]


    @staticmethod
    def is_custom_font(font: 'Font', extras: dict) -> bool:
        """
        Determine whether the given font characteristics constitute a
        default or custom font.

        Args:
            font: The Font being evaluated.
            extras: Dictionary of extras for evaluation.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        custom_extras = (
            ('stroke_color' in extras
                and extras['stroke_color'] != 'black')
            or ('title_text_horizontal_shift' in extras
                and extras['title_text_horizontal_shift'] != 0)
            or ('episode_text_vertical_shift' in extras
                and extras['episode_text_vertical_shift'] != 0)
        )

        return custom_extras or DawnTitleCard._is_custom_font(font)


    @staticmethod
    def is_custom_season_titles(
            custom_episode_map: bool,
            episode_text_format: str,
        ) -> bool:
        """
        Determine whether the given attributes constitute custom or
        generic season titles.

        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.

        Returns:
            True if custom season titles are indicated, False otherwise.
        """

        return (
            custom_episode_map
            or episode_text_format != DawnTitleCard.EPISODE_TEXT_FORMAT
        )


    @staticmethod
    def SEASON_TEXT_FORMATTER(episode_info: EpisodeInfo) -> str:
        """
        Fallback season title formatter.

        Args:
            episode_info: Info of the Episode whose season text is being
                determined.

        Returns:
            'Specials' if the season number is 0; otherwise the cardinal
            version of the season number. If that's not possible, then
            just 'S{xx}'.
        """

        if episode_info.season_number == 0:
            return 'Specials'

        return 'S{season_number:02}'


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        self.image_magick.run([
            f'convert "{self.source_file.resolve()}"',
            # Resize and optionally blur source image
            *self.resize_and_style,
            # Overlay gradient
            *self.gradient_commands,
            # Add season episode text
            *self.index_text_commands,
            # Title text
            *self.title_text_commands,
            # Add CRT TV overlay
            *self.add_crt_overlay_commands,
            # Attempt to overlay mask
            *self.add_overlay_mask(self.source_file),
            # Create card
            *self.resize_output,
            f'"{self.output_file.resolve()}"',
        ])
