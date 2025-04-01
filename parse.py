import ast
from hashlib import md5
import json
import os
from pathlib import Path
import re

CARDS_FILE = 'cards.json'


def convert_to_dict(node: ast.expr):
    """
    Recursively converts AST nodes into dictionaries where applicable.
    """

    if isinstance(node, ast.Expr):
        return convert_to_dict(node.value)  # Extract the expression's value

    if isinstance(node, ast.Call):
        if (isinstance(node.func, ast.Name)
            and node.func.id in ('CardDescription', 'Extra', 'dict')):
            return {kw.arg: convert_to_dict(kw.value) for kw in node.keywords}

    if isinstance(node, ast.Dict):
        return {
            convert_to_dict(k): convert_to_dict(v)
            for k, v in zip(node.keys, node.values)
        }

    if isinstance(node, ast.List):
        return [convert_to_dict(el) for el in node.elts]

    if isinstance(node, ast.Tuple):
        return tuple(convert_to_dict(el) for el in node.elts)

    return ast.literal_eval(node) # Safely evaluate literals like strings, numbers, and booleans


def extract_card_details(file_path: Path):
    """Extracts details of CardDescription instances from a Python file."""

    # Regex pattern to find the API_DETAILS assignment
    content = file_path.read_text()
    match = re.search(r'(\w+)\s*=\s*CardDescription\((.*?)\n\s{4}\)', content, re.DOTALL)
    if not match:
        return None
    
    card_data = match.group(2)
    # Parse using AST (Abstract Syntax Tree) to safely evaluate the structure
    try:
        # Redifine the CardDescription and Extra objects as dictionaries
        final_card_data = (
            f'CardDescription = dict\nExtra = dict\nCardDescription({card_data})'
        )
        nodes = ast.parse(final_card_data)
        return convert_to_dict(nodes.body[2].value)
    except Exception as e:
        print(f'Error parsing {file_path}: {e}')
        return None


def update_cards_json(directory: Path):
    """
    Updates the card JSON file with the Card API descriptions of all the
    child Python files.
    """

    # Generate card JSON data
    cards = []
    for card_file in sorted(directory.glob('**/*.py'), key=lambda p: p.name):
        if (details := extract_card_details(card_file)):
            # Remove source key, add to list
            details.pop('source', None)

            # Add hashes
            details['hash'] = md5(card_file.read_bytes()).hexdigest()

            cards.append(details)

    # Write to JSON file
    with open(CARDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=4, ensure_ascii=False)
    print(f'Updated {CARDS_FILE} with {len(cards)} entries.')


if __name__ == '__main__':
    update_cards_json(Path('./'))
