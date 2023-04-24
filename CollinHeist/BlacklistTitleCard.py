from pathlib import Path

from modules.BaseCardType import BaseCardType, ImageMagickCommands
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class BlacklistTitleCard(BaseCardType):
    """
    
    """

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
        'line_count', 'font_color', 'font_file', 'font_size',
        'font_interline_spacing',
    )

    def __init__(self,
            source_file: Path,
            card_file: Path,
            title_text: str, 
            episode_text: str,
            font_file: str = TITLE_FONT,
            font_color: str = TITLE_COLOR,
            font_interline_spacing: int = 0,
            font_size: float = 1.0,
            blur: bool = False,
            grayscale: bool = False,
            **unused) -> None:
        """
        Construct a new instance of this Card.
        """

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Store source and output file
        self.source_file = source_file
        self.output_file = card_file

        # Escape title, season, and episode text
        self.title_text = self.image_magick.escape_chars(title_text)
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())
        self.line_count = len(title_text.split('\n'))

        # Font customizations
        self.font_color = font_color
        self.font_file = font_file
        self.font_interline_spacing = font_interline_spacing
        self.font_size = font_size


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
            or (font.kerning != 1.0)
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
            f'-annotate +150+150 "{self.title_text}"',
            # Add episode text
            f'-pointsize 120',
            f'-annotate +150+{episode_text_offset} "{self.episode_text}"',
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)