import numpy as np
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

### Functions for creating a uniquely solvable board

# Add restrictions for column combinations (c1, c2) with characters (ch1,ch2)
def addColumnRestriction(columnRestrict, c1, c2, ch1, ch2):
    # Check if the location is already marked as restricted
    if(ch1 == ch2 or columnRestrict[c1,c2,ch1,ch2] == 1):
        return columnRestrict[c1,c2,:,:]
    # If not, mark it
    else:
        columnRestrict[c1,c2,ch1,ch2] = 1
        # Check row for further restrictions that need to be added
        for j in range(0,len(COLORS)):
            if(columnRestrict[c1,c2,ch2,j] == 1):
                addColumnRestriction(columnRestrict, c1, c2, ch1, j)
        # Check column for further restriction that need to be added
        for i in range(0,len(COLORS)):
            if(columnRestrict[c1,c2,i,ch1]) == 1:
                addColumnRestriction(columnRestrict, c1, c2, i, ch2)
        return columnRestrict[c1,c2,:,:]

# Add restrictions for row combinations (r1, r2) with characters (ch1,ch2)
def addRowRestriction(rowRestrict, r1, r2, ch1, ch2):
    # Check if the location is already marked as restricted
    if(ch1 == ch2 or rowRestrict[r1,r2,ch1,ch2] == 1):
        return rowRestrict[r1,r2,:,:]
    # If not, mark it
    else:
        rowRestrict[r1,r2,ch1,ch2] = 1
        # Check row for further restrictions that need to be added
        for j in range(0,len(COLORS)):
            if(rowRestrict[r1,r2,ch2,j] == 1):
                addRowRestriction(rowRestrict, r1, r2, ch1, j)
        # Check column for further restriction that need to be added
        for i in range(0,len(COLORS)):
            if(rowRestrict[r1,r2,i,ch1]) == 1:
                addRowRestriction(rowRestrict, r1, r2, i, ch2)
        return rowRestrict[r1,r2,:,:]

# Function for checking whether character 'kar' can be inserted at location
# (c1,c2) on the board by checking the columnRestrict array
def checkColumnRestrictions(board, columnRestrict, r1, r2, kar):
    for j in range(0, r2):
        if(columnRestrict[r2,j,board[r1,j],kar] == 1):
            return False
    return True

# Function for checking whether character 'kar' can be inserted at location
# (c1,c2) on the board by checking the rowRestrict array
def checkRowRestrictions(board, rowRestrict, c1, c2, kar):
    for i in range(0, c1):
        if(rowRestrict[c1,i,board[i,c2],kar] == 1):
            return False
    return True

def generate_unique_board(k):
    nx = k
    ny = k
    board = np.zeros((ny,nx), dtype = int)
    #These arrays indicate which characters combinations in 
    #specific column combinations are not allowed
    columnRestrict = np.zeros((nx,nx,len(COLORS),len(COLORS)), dtype = int)
    rowRestrict = np.zeros((ny,ny,len(COLORS),len(COLORS)), dtype = int)
    
    #Loop over the board
    for i in range(0,ny):
        for j in range(0, nx):
            validPick = False
            kars = list(range(0,len(COLORS)))
            while(validPick == False):
                kar = kars.pop(random.randrange(len(kars)))
                if i == 0 or j == 0:
                    validPick = True
                else:
                    checkcol = checkColumnRestrictions(board, columnRestrict, i, j, kar)
                    checkrow = checkRowRestrictions(board, rowRestrict, i, j, kar)
                    if (checkcol == True and checkrow == True):
                        validPick = True

            board[i][j] = kar

            #Update column restrictions
            if(j > 0 and i < ny-1):
                for k in range(0, j):
                    #No board[i,k] after board[i,j] in column combination (k,j)
                    columnRestrict[j,k,:,:] = addColumnRestriction(columnRestrict,j,k,board[i,j],board[i,k])
            #Update row restrictions
            if(i > 0 and j < nx-1):
                for l in range(0, i):
                    #No board[l,j] after board[i,j] in row combination (l,i)
                    rowRestrict[i,l,:,:] = addRowRestriction(rowRestrict,i,l,board[i,j],board[l,j])

    return board
###

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

    # Randomly assign a color to each cell such that puzzel is uniquely solvable
    board = generate_unique_board(k).tolist()
    color_config = [COLORS[i] for j in board for i in j] 
    print(color_config)

    # Randomly assign a color to each cell (old version)
    #color_config = [random.choice(COLORS) for _ in range(k*k)]

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
