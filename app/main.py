# First, we import the necessary libraries.
# os is a standard Python library for interfacing with the operating system.
# dash is the core library we are using to build our web application.
# dash_bootstrap_components is a library that provides Bootstrap components for Dash.
# layouts and callbacks are custom modules we wrote for this application.
import os
import dash
import dash_bootstrap_components as dbc
from layouts import get_layout
from callbacks import register_callbacks

# We then initialize our Dash application.
# Dash is a framework for building analytical web applications.
# No JavaScript or HTML required for the basic functions, though it is used in the background.
# The __name__ argument helps Dash find any static files associated with the application.
# external_stylesheets is used to link CSS files to style the application.
# In this case, we are using Bootstrap for easy CSS styling.
# suppress_callback_exceptions is set to True, which means exceptions raised 
# in callbacks won't halt the execution of the other callbacks.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Now we register the layout of our application. This is a Dash-specific term. 
# The layout describes what the application looks like.
# We use the get_layout() function defined in layouts.py to generate the layout.
app.layout = get_layout()

# Now that the layout of the application is registered, we need to register the callbacks.
# Callbacks are functions that Dash will call in response to user interactions, like a button click.
# This allows our application to be dynamic and responsive.
# We use the register_callbacks() function defined in callbacks.py to register the callbacks.
register_callbacks(app)

# Finally, we need to start our Dash server so it can serve our application to users.
# This line of code only gets executed when we run this file directly, not when it's imported as a module.
# This means when we run "python app.py", this line of code gets executed, but not when we do "import app".
# The server runs in debug mode, which provides more information about any errors that occur. 
# It also automatically restarts the server whenever we save changes to the source files.
# host='0.0.0.0' makes the server publicly available.
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
