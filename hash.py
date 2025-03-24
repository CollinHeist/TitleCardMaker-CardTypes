from hashlib import md5
from pathlib import Path


def print_file_hashes() -> None:
    """
    Print the file hashes of all Python files in local subdirectories.
    """

    for card_file in Path(__file__).parent.glob('*/*.py'):
        file_hash = md5(card_file.read_text().encode('utf-8')).hexdigest()
        print(f'{card_file.parent.name}/{card_file.name} : {file_hash}')


if __name__ == '__main__':
    print_file_hashes()
