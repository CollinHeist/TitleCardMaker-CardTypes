from pathlib import Path

from modules.BaseCardType import BaseCardType
from modules.Debug import log
from modules.RemoteFile import RemoteFile

class BlacklistTitleCard(BaseCardType):
    """
    
    """

    """Characteristics for title splitting by this class"""
    TITLE_CHARACTERISTICS = {
        'max_line_width': 15,   # Character count to begin splitting titles
        'max_line_count': 4,    # Maximum number of lines a title can take up
        'top_heavy': True,     # This class uses bottom heavy titling
    }

    """How to name archive directories for this type of card"""
    ARCHIVE_NAME = 'Blacklist Style'

    """Characteristics of the default title font"""
    TITLE_FONT = str(RemoteFile('CollinHeist', 'blacklist/Blacklisted.ttf'))
    DEFAULT_FONT_CASE = 'upper'
    TITLE_COLOR = 'rgb(177,21,10)'
    FONT_REPLACEMENTS = {}

    """Characteristics of the episode text"""
    EPISODE_TEXT_FORMAT = 'NO. {episode_number}'

    """Whether this class uses season titles for the purpose of archives"""
    USES_SEASON_TITLE = False

    __slots__ = (
        'source_file', 'output_file', 'title', 'episode_text',
        'font', 'font_size', 'font_color', 'interline_spacing',
    )

    def __init__(self, source: Path, output_file: Path, title: str, 
                 episode_text: str, font: str, title_color: str,
                 font_size: float=1.0,
                 interline_spacing: int=0,
                 blur: bool=False,
                 grayscale: bool=False,
                 **unused) -> None:
        """
        Construct a new instance of this card.

        Args:
            source: Source image for this card.
            output_file: Output filepath for this card.
            title: The title for this card.
            episode_text: The episode text for this card.
            font: Font name or path (as string) to use for episode title.
            font_size: Scalar to apply to the title font size.
            title_color: Color to use for title text.
            interline_spacing: Offset to interline spacing of the title text
            blur: Whether to blur the source image.
            grayscale: Whether to make the source image grayscale.
            unused: Unused arguments.
        """

        # Initialize the parent class - this sets up an ImageMagickInterface
        super().__init__(blur, grayscale)

        # Store source and output file
        self.source_file = source
        self.output_file = output_file

        # Escape title, season, and episode text
        self.title = self.image_magick.escape_chars(title)
        self.episode_text = self.image_magick.escape_chars(episode_text.upper())

        # Font customizations
        self.font = font
        self.font_size = font_size
        self.font_color = title_color
        self.interline_spacing = interline_spacing


    @staticmethod
    def is_custom_font(font: 'Font') -> bool:
        """
        Determines whether the given arguments represent a custom font for this
        card. This CardType only uses custom font cases.

        Args:
            font: The Font being evaluated.

        Returns:
            True if a custom font is indicated, False otherwise.
        """

        return ((font.file != BlacklistTitleCard.TITLE_FONT)
            or  (font.size != 1.0)
            or  (font.color != BlacklistTitleCard.TITLE_COLOR)
            or  (font.vertical_shift != 0)
            or  (font.interline_spacing != 0)
            or  (font.kerning != 1.0))


    @staticmethod
    def is_custom_season_titles(custom_episode_map: bool, 
                                episode_text_format: str) -> bool:
        """
        Determines whether the given attributes constitute custom or generic
        season titles.

        Args:
            custom_episode_map: Whether the EpisodeMap was customized.
            episode_text_format: The episode text format in use.

        Returns:
            True if custom season titles are indicated, False otherwise.
        """

        return False


    def create(self) -> None:
        """
        Make the necessary ImageMagick and system calls to create this object's
        defined title card.
        """

        line_count = len(self.title.split('\n'))
        episode_text_offset = 150 + (250 * line_count)

        font_size = 230 * self.font_size
        interline_spacing = 30 + self.interline_spacing

        command = ' '.join([
            f'convert "{self.source_file.resolve()}"',
            # Resize and apply styles
            *self.resize_and_style,
            # Add title text
            f'-font "{self.font}"',
            f'-fill "{self.font_color}"',
            f'-interline-spacing {interline_spacing}',
            f'-pointsize {font_size}',
            f'-gravity northwest',
            f'-annotate +150+150 "{self.title}"',
            # Add episode text
            f'-pointsize 120',
            f'-annotate +150+{episode_text_offset} "{self.episode_text}"',
            f'"{self.output_file.resolve()}"',
        ])

        self.image_magick.run(command)