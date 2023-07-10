# Import the necessary modules. We are using Dash's html and dcc modules,
# the dash_bootstrap_components module for its components, and the random module
# from Python's standard library.
from dash import html, dcc
import dash_bootstrap_components as dbc
import random


# This function creates an output Div. The output Div is where we will display
# the result of the game.
def create_output_div():
    return dbc.Row(dbc.Col(html.Div(id="output")))


# This function gets the layout of the application. It uses all the functions
# we defined above to create the different parts of the layout, then combines
# them into a single layout.
def get_layout():
    output_div = create_output_div()

    # Dropdown for board size selection
    board_size_dropdown = dcc.Dropdown(
        id='board-size-dropdown',
        options=[{'label': f'{i}x{i}', 'value': i} for i in range(2, 7)],
        value=5,  # default value
        clearable=False,
        style={
            'backgroundColor': '#ffffff',
            'color': 'black',
            'borderRadius': '5px',
            'border': '1px solid gray',
            'padding': '5px',
            'cursor': 'pointer'
        },
        className='my-dropdown'
    )

    # Board size selection card
    board_size_card = dbc.Card(
        [
            dbc.CardHeader("Choose Grid Size", className="text-center header-style"),
            dbc.CardBody(
                dbc.Row(
                    dbc.Col(board_size_dropdown, className="mx-auto"),
                ),
            ),
        ],
        className="mb-3",
    )

    # Celebration dialog
    celebration_dialog = dbc.Modal(
        [
            dbc.ModalHeader("Congratulations!"),
            dbc.ModalBody("You solved the puzzle!"),
            dbc.ModalFooter(
                dbc.Button("Close", id="celebration-dialog-close", className="ml-auto")
            ),
        ],
        id="celebration-dialog",
        centered=True,
    )


    # The layout is a Container that includes a title, a welcome message, a start button,
    # the game board with the sum cards, a success message, a store for the puzzle data,
    # a div for displaying the color configuration, a div for displaying the true cell colors,
    # the output div, and a button for showing the answer.
    # The layout is a Sidebar layout with a sidebar and content area.
    layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(""),
                            html.Hr(),
                            board_size_card,
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            html.H1("Spectral Nonogram", className="my-h1"),
                            html.P(
                                "Welcome to the Spectral Nonogram! This is a colorful puzzle game where your goal is to fill the grid so that the color sum of each row and column matches the provided clues. The clues are given as RGB color values (Red, Green, Blue) on the right and bottom of the grid. Each cell can be clicked to cycle through 4 states: blank, red, green, and blue. Use the 'Reset' button to start a new game. Happy solving!",
                                className="my-p",
                            ),
                            dbc.Button("Start", id="start-button", className="start-button mb-3"),
                            html.Hr(),
                            dbc.Container(
                                id="game-board-placeholder",
                                className="mb-4 game-board border border-dark p-2",
                                style={"max-width": "615px", "margin": "0 auto"},
                            ),
                            dcc.Store(id='puzzle-store', data={}),
                            output_div,
                            dbc.Button("Show Answer", id="show-answer-button", className="reset-button"),
                            celebration_dialog,
                        ],
                        width=9,
                    ),
                ],
                className="justify-content-between",
            ),
        ],
        fluid=True,
        className="container my-container",
    )

    return layout
