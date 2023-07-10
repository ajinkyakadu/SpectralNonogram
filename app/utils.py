import random
import dash_bootstrap_components as dbc
from dash import html, dcc

# Colors that can be used in the game
COLORS = ["blank", "danger", "success", "primary"]

# Mapping colors to their CSS equivalent
COLORS_TO_CSS = {
    "blank": "white",
    "danger": "red",
    "success": "green",
    "primary": "blue",
}

def generate_new_puzzle(k):
    """Generates a new nonogram puzzle of size kxk.

    The function randomly assigns a color to each cell in the kxk grid. Then it computes 
    the number of each color in each row and each column.

    Args:
        k (int): The size of the puzzle (k x k).

    Returns:
        Tuple: A tuple containing the color configuration of the puzzle, 
        the sums of each color in each row, and the sums of each color in each column.
    """
    # Randomly assign a color to each cell
    color_config = [random.choice(COLORS) for _ in range(k*k)]

    # Compute the number of each color in each row
    row_sums = [compute_color_sums(color_config[i*k:(i+1)*k]) for i in range(k)]

    # Compute the number of each color in each column
    col_sums = [compute_color_sums(color_config[i::k]) for i in range(k)]

    return color_config, row_sums, col_sums

def compute_color_sums(color_config):
    """Computes the number of each color in a given configuration.

    Args:
        color_config (list): The color configuration to compute the sums for.

    Returns:
        List: A list containing the number of each color in the configuration, 
        excluding 'blank'.
    """
    # Count the number of each color in the configuration, excluding 'blank'
    color_sums = [color_config.count(color) for color in COLORS[1:]]
    
    return color_sums


def is_puzzle_solved(current_config, true_config, k):
    """Checks if the current puzzle configuration matches the true configuration.

    Args:
        current_config (list): The current color configuration of the puzzle.
        true_config (list): The true color configuration of the puzzle.
        k (int): The size of the puzzle (k x k).

    Returns:
        Bool: True if the puzzle is solved correctly, False otherwise.
    """
    # Compute the number of each color in each row and column of the current configuration
    current_row_sums = [compute_color_sums(current_config[i*k:(i+1)*k]) for i in range(k)]
    current_col_sums = [compute_color_sums(current_config[i::k]) for i in range(k)]
    
    # Compute the number of each color in each row and column of the true configuration
    true_row_sums = [compute_color_sums(true_config[i*k:(i+1)*k]) for i in range(k)]
    true_col_sums = [compute_color_sums(true_config[i::k]) for i in range(k)]
    
    # Check if the current sums match the true sums
    is_solved = all(curr == true for curr, true in zip(current_row_sums, true_row_sums)) and \
           all(curr == true for curr, true in zip(current_col_sums, true_col_sums))
    
    return is_solved


def next_color(current_color):
    """Returns the next color in the sequence.

    The function rotates between the colors in the COLORS list in the following order: 
    'blank' -> 'danger' -> 'success' -> 'primary' -> 'blank' -> ...

    Args:
        current_color (str): The current color.

    Returns:
        Str: The next color in the sequence.
    """
    # Find the index of the current color in the COLORS list
    index = COLORS.index(current_color)
    
    # Compute the index of the next color
    next_index = (index + 1) % len(COLORS)
    
    # Return the next color
    return COLORS[next_index]

def create_cells(k):
    """
    Creates individual cells for the game board.

    Parameters:
        - k (int): The size of the game board.

    Returns:
        - list: A list of dbc.Button objects representing the cells of the game board.

    Example:
        create_cells(3)
    """
    cells = [
        dbc.Button(
            "", # The initial label of the button is an empty string.
            id={"type": "cell", "index": f"{i}-{j}"}, # The ID of the button is a dictionary with type and index.
            className="my-button square blank",  # The class of the button is used for CSS styling, Assign the "blank" class at creation
            style={"height": "50px", "width": "50px"} # The style of the button is defined inline with CSS.
        ) for i in range(k) for j in range(k)
    ]
    return cells


def create_sum_card(card_id, is_col=False):
    """
    Creates a sum card that shows the sum of a row or a column in the game board.

    Parameters:
        - card_id (str or dict): Identifier for the sum card. It can be a string or a dictionary with additional metadata.
        - is_col (bool): Indicates whether the sum card is for a column (default: False).

    Returns:
        - dash.development.base_component.Component: A Dash component representing the sum card.

    Example:
        sum_card = create_sum_card("row_sum_1")
    """

    # Depending on whether the sum card is for a column or a row, 
    # we adjust the flex direction of our card layout.
    if is_col:
        layout = {"display": "flex", "flex-direction": "column", "align-items": "center", "justify-content": "space-around"}
    else:
        layout = {"display": "flex", "flex-direction": "row", "align-items": "center", "justify-content": "space-around"}

    # Create the sum card with an empty body. The body is a list of Div elements,
    # each with a different color.
    return dbc.Card([
        dbc.CardBody([
            html.Div("", style={"color": "red"}),
            html.Div("", style={"color": "green"}),
            html.Div("", style={"color": "blue"}),
        ], style=layout),
    ], id=card_id, className="sum-card")


def create_sums(k):
    """
    Creates sum cards for all the rows and columns in the game board.

    Parameters:
        - k (int): The number of rows or columns in the game board.

    Returns:
        - tuple: A tuple containing two lists of sum cards representing row sums and column sums, respectively.

    Example:
        row_sums, col_sums = create_sums(4)
    """
    row_sums = [create_sum_card({"type": "row_sum", "index": str(i)}) for i in range(k)]
    col_sums = [create_sum_card({"type": "col_sum", "index": str(i)}, is_col=True) for i in range(k)]
    return row_sums, col_sums


def create_game_board_with_sums(game_board, row_sums, col_sums, k):
    """
    Combines the game board with the row and column sums, creating a new layout.

    Parameters:
        - game_board (list of lists): The game board represented as a 2D list.
        - row_sums (list of dash.development.base_component.Component): The list of row sum cards.
        - col_sums (list of dash.development.base_component.Component): The list of column sum cards.
        - k (int): The number of rows or columns in the game board.

    Returns:
        - dash.development.base_component.Component: A Dash component representing the game board with the sum cards.

    Example:
        combined_board = create_game_board_with_sums(game_board, row_sums, col_sums, 4)
    """

    # Append row sums to each row in the game board.
    game_board_with_row_sums = [game_board[i] + [row_sums[i]] for i in range(k)]

    # Append column sums to the end of the game board.
    game_board_with_row_sums.append(col_sums)

    return dbc.Container(
        [dbc.Row([dbc.Col(cell, width=2) for cell in row]) for row in game_board_with_row_sums],
        fluid=True
    )