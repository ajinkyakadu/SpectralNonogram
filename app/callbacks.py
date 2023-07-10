# dash - Helps us make web applications using Python.
import dash

# json - Lets us work with data in a special format called JSON, which is often used for sending data over the internet.
import json

# These tools from dash.dependencies help us connect different parts of our application.
# "Input" and "Output" let us set up actions that happen when a user interacts with our application.
# "State" lets us store some data in our application that can change over time.
# "ALL" lets us apply changes to all elements of a certain type.
# dash.exceptions has special errors that Dash uses to handle different situations.
from dash.dependencies import Input, Output, ALL, State
from dash.exceptions import PreventUpdate

# dash.dcc has special elements we can use to make our application look and behave the way we want.
# dash.html lets us use HTML, the language that makes up the structure of web pages.
from dash import dcc, html

# The "utils" file has some useful functions that we use in our app.
# The "layouts" file has functions for setting up different parts of our app's appearance.
from utils import generate_new_puzzle, next_color, compute_color_sums, is_puzzle_solved, COLORS_TO_CSS
from utils import create_sums, create_cells, create_game_board_with_sums



def register_callbacks(app):
    """Register all the callbacks for the Dash app.
    
    The Dash app uses callbacks to update and render the components of the game. 
    Callbacks are functions that modify the data of an Output property when an 
    Input property changes. These functions are automatically called by Dash 
    whenever an input property changes.
    """

    @app.callback(
        Output('game-board-placeholder', 'children'),  # Output: Updated game board rendered in 'children' property of 'game-board-placeholder' component
        Input('start-button', 'n_clicks'),             # Input: Callback triggered by 'n_clicks' property of 'start-button' component
        State('board-size-dropdown', 'value'),         # State: Current value of 'board-size-dropdown' component
    )
    def update_game_board(n_clicks, board_size):
        """
        Updates the game board based on user interactions.

        Parameters:
            - n_clicks (int): The number of times the start button has been clicked.
            - board_size (int): The size of the game board selected by the user.

        Returns:
            - list: A list representing the updated game board with sum cards.
        """
        if n_clicks is None:
            # The button hasn't been clicked yet, so don't create a game board.
            return []
        else:
            # The button has been clicked, so create a new game board of the specified size.
            cells = create_cells(board_size)
            game_board = [cells[i*board_size:i*board_size+board_size] for i in range(board_size)]
            row_sums, col_sums = create_sums(board_size)
            game_board_with_sums = create_game_board_with_sums(game_board, row_sums, col_sums, board_size)
            return game_board_with_sums


    @app.callback(
        [
            Output('puzzle-store', 'data'),                         # Output: data stored in the puzzle store
            Output('celebration-dialog', 'is_open')                 # Output: celebration dialog
        ],
        [
            Input('start-button', 'n_clicks'),                      # Input: "Start" button
            Input("show-answer-button", "n_clicks"),                # Input: 'Show Answer' button
            Input({"type": "cell", "index": ALL}, "n_clicks"),      # Input: Cells in the puzzle grid
            Input('celebration-dialog-close', 'n_clicks'),          # Input: "Close" button in the modal
        ],
        [
            State({"type": "cell", "index": ALL}, "id"),            # State: Ids of the cells
            State('puzzle-store', 'data'),                          # State: Data stored in the puzzle store
            State('board-size-dropdown', 'value'),                  # State: value of k (board size)
        ]
    )
    def update_puzzle_store(start_clicks, show_answer_clicks, cell_n_clicks, close_clicks, cell_ids, puzzle_store, k):
        """Updates the puzzle store.

        This function is responsible for handling the interactions with the puzzle.
        It updates the puzzle store in response to four events:
        1. The start button is clicked
        2. The show answer button is clicked
        3. A cell in the puzzle grid is clicked
        4. The close button in the modal is clicked

        Args:
            start_clicks (int): Number of times the start button has been clicked.
            show_answer_clicks (int): Number of times the show answer button has been clicked.
            cell_n_clicks (list): List of numbers of times each cell has been clicked.
            close_clicks (int): Number of times the close button in the modal has been clicked.
            cell_ids (list): List of ids of the cells.
            puzzle_store (dict): The current state of the puzzle store.

        Returns:
            dict: The updated puzzle store.
        """
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate  # No updates to the store if no inputs have been triggered

        # Initialize the puzzle store if it's None
        if puzzle_store is None:
            puzzle_store = {
                'cell_colors_true': None,       # True color configuration of the cells
                'row_sums_true': None,          # True sum of colors in each row
                'col_sums_true': None,          # True sum of colors in each column
                'current_color_config': None    # Current color configuration of the cells
            }

        for trigger in ctx.triggered:
            triggering_component_id = trigger["prop_id"].split(".")[0]
            # Initialize or reset the puzzle store when the Start button is clicked
            if triggering_component_id == 'start-button':
                puzzle_store['cell_colors_true'], puzzle_store['row_sums_true'], puzzle_store['col_sums_true'] = generate_new_puzzle(k)
                puzzle_store['current_color_config'] = ["blank" for _ in range(k*k)]

                return puzzle_store, False

            # Reveal the answer when the Show Answer button is clicked
            elif triggering_component_id.startswith("show-answer-button"):
                if all(value is not None for value in puzzle_store.values()):
                    puzzle_store['current_color_config'] = puzzle_store['cell_colors_true']

            # Change the color of a cell when it is clicked
            elif triggering_component_id.startswith('{'):
                triggering_component_id_dict = json.loads(triggering_component_id)
                if triggering_component_id_dict.get('type') == 'cell' and 'current_color_config' in puzzle_store:
                    clicked_cell_index = triggering_component_id_dict["index"]
                    clicked_cell_index = int(clicked_cell_index.split("-")[0])*k + int(clicked_cell_index.split("-")[1])
                    puzzle_store['current_color_config'][clicked_cell_index] = next_color(puzzle_store['current_color_config'][clicked_cell_index])

            # Close the dialog when the Close button is clicked
            elif triggering_component_id == 'celebration-dialog-close':
                return puzzle_store, False

        if 'current_color_config' in puzzle_store and 'cell_colors_true' in puzzle_store:
            if is_puzzle_solved(puzzle_store['current_color_config'], puzzle_store['cell_colors_true'], k):
            # If the puzzle is solved, show the celebration dialog
                return puzzle_store, True
            
        # If the puzzle is not solved, don't show the celebration dialog
        return puzzle_store, False
        

    @app.callback(
        Output({"type": "cell", "index": ALL}, "style"),    # Output: Updated style of cells in the puzzle
        [Input('puzzle-store', 'data')]                     # Input: Callback triggered by changes in the 'data' property of the 'puzzle-store' component
    )
    def update_cell_colors(puzzle_store):
        """
        Updates the cell colors in a puzzle based on changes in the 'puzzle-store' data.

        Parameters:
            - puzzle_store (dict): The data stored in the 'puzzle-store'.

        Returns:
            - list: A list of dictionaries representing the updated style of the cells.
        """
        if puzzle_store is None or puzzle_store['current_color_config'] is None:
            raise PreventUpdate
        return [{"background-color": COLORS_TO_CSS[color], "height": "50px", "width": "50px"} for color in puzzle_store['current_color_config']]


    @app.callback(
        Output({"type": "row_sum", "index": ALL}, "children"),  # Output: Updated children (HTML div elements) representing the sum of colors for each row
        [Input('puzzle-store', 'data')]                         # Input: Callback triggered by changes in the 'data' property of the 'puzzle-store' component
    )
    def update_row_sums(puzzle_store):
        """Updates the sum of colors for each row.

        Args:
            puzzle_store (dict): The current state of the puzzle store.

        Raises:
            PreventUpdate: No updates to the row sums if the puzzle store is None or if the true row sums are None.

        Returns:
            list: A list of HTML div elements displaying the sum of each color in each row.
        """
        if puzzle_store is None or puzzle_store['row_sums_true'] is None:
            raise PreventUpdate
        return [html.Div([
                html.Div(f"R:{sum_list[0]}", style={"color": "red"}),
                html.Div(f"G:{sum_list[1]}", style={"color": "green"}),
                html.Div(f"B:{sum_list[2]}", style={"color": "blue"}),
            ], style={"display": "flex", "justifyContent": "center", "gap": "10px"}) 
            for sum_list in puzzle_store['row_sums_true']]



    @app.callback(
        Output({"type": "col_sum", "index": ALL}, "children"),  # Output: Updated children (HTML div elements) representing the sum of colors for each column
        [Input('puzzle-store', 'data')]                         # Input: Callback triggered by changes in the 'data' property of the 'puzzle-store' component
    )
    def update_column_sums(puzzle_store):
        """Updates the sum of colors for each column.

        Args:
            puzzle_store (dict): The current state of the puzzle store.

        Raises:
            PreventUpdate: No updates to the column sums if the puzzle store is None or if the true column sums are None.

        Returns:
            list: A list of HTML div elements displaying the sum of each color in each column.
        """
        if puzzle_store is None or puzzle_store['col_sums_true'] is None:
            raise PreventUpdate
        return [html.Div([
            html.Div(f"R:{sum_list[0]}", style={"color": "red"}),
            html.Div(f"G:{sum_list[1]}", style={"color": "green"}),
            html.Div(f"B:{sum_list[2]}", style={"color": "blue"}),
        ]) for sum_list in puzzle_store['col_sums_true']]
