from dash import html, dcc, callback, Input, Output, State
import pyowm

# Configurações da API do OpenWeatherMap
API_KEY = 'Sua chave'

# Criar uma instância do cliente OpenWeatherMap
owm = pyowm.OWM(API_KEY)
mgr = owm.weather_manager()

layout = html.Div(
    id='tela',
    children=[
        html.H1(id='titulo', children='Previsão do Tempo'),
        html.Label('Cidade', id='label-cidade', htmlFor='cidade'),
        dcc.Input(id='cidade'),
        html.Br(),
        html.Label('País', id='label-pais', htmlFor='pais'),
        dcc.Input(id='pais', type='text'),
        html.Br(),
        html.Button('Obter Previsão', id='botao'),
        html.P(id='temperatura'),
        html.P(id='descricao'),
    ]
)

@callback(
    Output('temperatura', 'children'),
    Output('descricao', 'children'),
    Input('botao', 'n_clicks'),
    State('cidade', 'value'),
    State('pais', 'value')
)
def update_weather(n_clicks, cidade, pais):
    print("Função update_weather chamada")
    if n_clicks and cidade and pais:
        try:
            observation = mgr.weather_at_place(f"{cidade},{pais}")
            weather = observation.weather
            temperatura = weather.temperature('celsius')["temp"]
            descricao = weather.status
            return f"Temperatura: {temperatura}°C", f"Descrição: {descricao}"
        except Exception as e:
            return f"Ocorreu um erro ao obter a previsão do tempo: {str(e)}", ""
    else:
        return "", ""
