import dash
from dash import html, dcc
from pages import home

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return home.layout
    
    else:
        return '404'
    
        

if __name__ == '__main__':
    app.run_server(debug=True)