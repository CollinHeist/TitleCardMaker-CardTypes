from pathlib import Path
from typing import Optional

from pydantic import FilePath, PositiveFloat, constr, root_validator
from app.schemas.base import BetterColor
from app.schemas.card_type import BaseCardType as BaseCardModel

from modules.BaseCardType import (
    BaseCardType, ImageMagickCommands, Extra, CardDescription
)
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class BlacklistTitleCard(BaseCardType):
    """
    This class describes a type of CardType that produces title cards
    intended for use for "The Blacklist" series. It features a title,
    with a subtitle of the "blacklist number" parsed via an extra.
    """

    API_DETAILS =  CardDescription(
        name='Blacklist',
        identifier='CollinHeist/BlacklistTitleCard',
        example='https://user-images.githubusercontent.com/17693271/216839561-ec4a1c27-dcdc-4869-87dd-8d592a26aee2.jpg',
        creators=['CollinHeist'],
        source='remote',
        supports_custom_fonts=True,
        supports_custom_seasons=False,
        supported_extras=[],
        description=[
            "Title Card intended for the 'The Blacklist' television series",
            "This Card features a prominent title and a customizable "
            "'blacklist number' beneath the title.", 'The default Font for '
            'this card is a modified version of Helvetica.',
        ]
    )

    class CardModel(BaseCardModel):
        title_text: str
        episode_text: constr(to_upper=True)
        hide_episode_text: bool = False
        font_color: BetterColor
        font_file: FilePath
        font_interline_spacing: int = 0
        font_size: PositiveFloat = 1.0
        font_vertical_shift: int = 0

        @root_validator
        def toggle_text_hiding(cls, values):
            values['hide_episode_text'] |= (len(values['episode_text']) == 0)

            return values

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 15,   # Character count to begin splitting titles
        'max_line_count': 4,    # Maximum number of lines a title can take up
        'top_heavy': True,      # This class uses bottom heavy titling
    }

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Blacklist Style'

    """Characteristics of the default title font"""
    TITLE_FONT = str(RemoteFile('CollinHeist', 'blacklist/Blacklisted.ttf'))
    TITLE_COLOR = 'rgb(177,21,10)'
    DEFAULT_FONT_CASE = 'upper'
    FONT_REPLACEMENTS = {}

    """Characteristics of the episode text"""
    EPISODE_TEXT_FORMAT = 'NO. {episode_number}'

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = False

    __slots__ = (
        'source_file', 'output_file', 'title_text', 'episode_text',
        'hide_episode_text', 'line_count', 'font_color', 'font_file',
        'font_size', 'font_interline_spacing', 'font_vertical_shift',
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
            font_size: float = 1.0,
            font_vertical_shift: int = 0.0,
            blur: bool = False,
            grayscale: bool = False,
            preferences: Optional['Preferences'] = None,
            **unused) -> None:
        """
        Construct a new instance of this Card.
        """

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale, preferences=preferences)

        # Store source and output file
        self.source_file = source_file
        self.output_file = card_file

        # Escape title, season, and episode text
        self.title_text = self.image_magick.escape_chars(title_text)
        self.episode_text = self.image_magick.escape_chars(episode_text)
        self.hide_episode_text = hide_episode_text
        self.line_count = len(title_text.split('\n'))

        # Font customizations
        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_size = font_size
        self.font_vertical_shift = font_vertical_shift


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

        return ((font.color != BlacklistTitleCard.TITLE_COLOR)
            or (font.file != BlacklistTitleCard.TITLE_FONT)
            or (font.interline_spacing != 0)
            or (font.size != 1.0)
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
            False, as custom season titles are not used.
        """

        return False


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this
        object's defined title card.
        """

        episode_text_offset = 150 + (250 * self.line_count)
        font_size = 230 * self.font_size
        interline_spacing = 30 + self.font_interline_spacing
        vertical_shift = 150 + self.font_vertical_shift

        if self.hide_episode_text:
            episode_text_commands = []
        else:
            episode_text_commands = [ 
                f'-pointsize 120',
                f'-annotate +150+{episode_text_offset} "{self.episode_text}"',
            ]

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            # Resize and apply styles
            *self.resize_and_style,
            # Add title text
            f'-font "{self.font_file}"',
            f'-fill "{self.font_color}"',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity northwest',
            f'-annotate +150+{vertical_shift} "{self.title_text}"',
            # Add episode text
            *episode_text_commands,
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)
