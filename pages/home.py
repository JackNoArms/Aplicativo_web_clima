"""Dash interface: accessible high-contrast weather summary and forecasts."""
from __future__ import annotations

from collections import defaultdict

from dash import Input, Output, State, callback, ctx, dcc, html, no_update
import plotly.graph_objects as go

from services.weather import WeatherError, demo_weather, fetch_weather


def metric(label: str, value: str, suffix: str = ""):
    return html.Article(className="stat", children=[
        html.Span(label, className="stat-label"),
        html.Div(children=[html.Strong(value), html.Span(suffix, className="stat-unit")]),
    ])


def forecast_figure(series: list[dict]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[row["time"] for row in series], y=[row["temp"] for row in series],
        mode="lines+markers",
        name="Temperatura",
        line={"color": "#bafa72", "width": 3, "shape": "spline"},
        marker={"size": 7, "color": "#dcffab", "line": {"color": "#15200b", "width": 2}},
        fill="tozeroy", fillcolor="rgba(186,250,114,0.06)",
        hovertemplate="%{x}<br>%{y:.1f}°C<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#abb8c1", "size": 12},
        margin={"l": 10, "r": 15, "t": 16, "b": 14},
        height=302, showlegend=False,
        hovermode="x", hoverlabel={"bgcolor": "#202931", "font_color": "#eff4f0"},
        xaxis={"showgrid": False, "zeroline": False, "tickangle": -30,
               "tickfont": {"size": 10}, "tickmode": "auto", "nticks": 8},
        yaxis={"gridcolor": "#293139", "zeroline": False, "ticksuffix": "°C"},
    )
    return fig


def daily_cards(series: list[dict]):
    by_day = defaultdict(list)
    for point in series:
        by_day[point["label"]].append(point["temp"])
    return [html.Article(className="day", children=[
        html.Span(day), html.Span("☁", className="day-icon", **{"aria-hidden": "true"}),
        html.Strong(f"{max(temps):.0f}°"), html.Small(f"{min(temps):.0f}° mín.")
    ]) for day, temps in list(by_day.items())[:5]]


def render_weather(weather: dict):
    series = weather["series"]
    temperatures = [row["temp"] for row in series]
    highest, lowest = max(temperatures), min(temperatures)
    demo = weather["demo"]
    badge = "● DEMONSTRAÇÃO · DADOS FICTÍCIOS" if demo else "● OPENWEATHERMAP · DADOS AO VIVO"
    summary = (
        f"Nas próximas projeções disponíveis, a temperatura varia entre "
        f"{lowest:.1f}°C e {highest:.1f}°C. "
        "Considere as condições locais antes de tomar decisões. "
        + ("Esta simulação não representa previsão real." if demo else "Previsões podem mudar com novas atualizações.")
    )
    return html.Div(className="results", children=[
        html.Div(className="result-flag "+("demo-flag" if demo else "live-flag"), children=badge),
        html.Div(className="location-row", children=[
            html.Div([html.Span("CONDIÇÃO ATUAL", className="eyebrow"),
                      html.H2(f"{weather['city']}, {weather['country']}"),
                      html.P(weather["description"], className="description")]),
            html.Div([html.Span("ATUALIZADO ÀS", className="info-label"),
                      html.Div(weather["observed_at"], className="timestamp")]),
        ]),
        html.Div(className="featured-grid", children=[
            html.Article(className="temperature-panel", children=[
                html.Span("TEMPERATURA", className="stat-label"),
                html.Div([html.Strong(f"{weather['temp']:.1f}"), html.Span("°C")], className="temperature"),
                html.P("Condição atual "+("— SIMULADA" if demo else "— API OpenWeatherMap")),
                html.Span("☁", className="weather-glyph", **{"aria-hidden":"true"}),
            ]),
            html.Div(className="stats-grid", children=[
                metric("SENSAÇÃO TÉRMICA", f"{weather['feels_like']:.1f}", "°C"),
                metric("UMIDADE RELATIVA", str(weather["humidity"]), "%"),
                metric("VENTO", f"{weather['wind_kmh']:.1f}", "km/h"),
                metric("PRESSÃO", str(weather["pressure"]), "hPa"),
            ]),
        ]),
        html.Div(className="narrative",children=[
            html.Span("✳  LEITURA DO PANORAMA", className="eyebrow"),
            html.P(summary),
        ]),
        html.Section(className="charts-section", children=[
            html.Div(className="section-title", children=[
                html.Div([html.Span("01 — EXPLORAR", className="eyebrow"),
                          html.H3("Variação da temperatura"), html.P("Pontos previstos em intervalos de três horas.")]),
                html.Span("°C", className="unit-label")]),
            html.Div(className="chart-panel", children=[
                dcc.Graph(figure=forecast_figure(series), className="forecast-chart",
                          config={"displayModeBar": False, "responsive": True},
                          ),
            ]),
        ]),
        html.Section(className="charts-section", children=[
            html.Div(className="section-title", children=[
                html.Div([html.Span("02 — PLANEJAR", className="eyebrow"), html.H3("Próximos dias"),
                          html.P("Máxima e mínima entre as projeções disponíveis por dia.")])]),
            html.Div(className="days-grid", children=daily_cards(series)),
        ]),
        html.P(
            "Fonte: OpenWeatherMap. Sem consulta real quando o modo Demonstração está ativo. "
            "Valores previstos são estimativas e podem variar.",
            className="footnote",
        ),
    ])


layout = html.Div(className="app", children=[
    html.A("Pular para o conteúdo", href="#main", className="skip-link"),
    html.Header(className="topbar", children=[
        html.A(className="brand", href="#main", children=[
            html.Span("C", className="brand-mark"), html.Span(["CLIMA ", html.Small("LAB")])
        ]),
        html.Div(className="nav-right", children=[
            html.Span("DASHBOARD METEOROLÓGICO", className="nav-label"),
            html.Span("PORTFÓLIO / V2", className="nav-badge"),
        ]),
    ]),
    html.Main(id="main", children=[
        html.Section(className="hero", children=[
            html.P("PREVISÃO · ANÁLISE · CONTEXTO", className="eyebrow"),
            html.H1(["Entenda o clima. ", html.Em("Planeje melhor.")]),
            html.P("Consulte condições atuais e explore tendências nas próximas horas com uma visualização simples, clara e acessível.", className="subtitle"),
        ]),
        html.Section(className="search-panel", **{"aria-label": "Consultar cidade"}, children=[
            html.Div(className="field city-field", children=[
                html.Label("CIDADE", htmlFor="cidade"),
                dcc.Input(id="cidade", type="text", value="Recife",
                          maxLength=80, debounce=True, placeholder="Ex.: Recife",
                          className="search-input"),
            ]),
            html.Div(className="field country-field", children=[
                html.Label("PAÍS (ISO)", htmlFor="pais"),
                dcc.Input(id="pais", type="text", value="BR",
                          maxLength=2, debounce=True, placeholder="BR",
                          className="search-input"),
            ]),
            html.Button("Consultar agora ↗", id="search-btn", n_clicks=0, className="action-btn"),
            html.Button("Ver demonstração", id="demo-btn", n_clicks=0, className="demo-btn"),
        ]),
        html.Div(id="error-banner", role="alert", **{"aria-live": "assertive"}),
        dcc.Loading(id="loading", type="circle", children=html.Div(
            id="results", children=render_weather(demo_weather()),
        )),
        html.Section(className="how-to", children=[
            html.Span("TRANSPARÊNCIA", className="eyebrow"),
            html.H3("Uma previsão deve ser compreensível."),
            html.P("A demonstração inicial usa dados sintéticos identificados. Para consultar o clima real, configure sua própria chave OpenWeatherMap no arquivo .env e pressione Consultar agora. Credenciais nunca devem ser incorporadas ao código-fonte."),
        ]),
    ]),
    html.Footer(["CLIMA LAB", html.Span("Python · Dash · Plotly · OpenWeatherMap · UX/UI")]),
])


@callback(
    Output("results", "children"),
    Output("error-banner", "children"),
    Input("search-btn", "n_clicks"),
    Input("demo-btn", "n_clicks"),
    State("cidade", "value"),
    State("pais", "value"),
    prevent_initial_call=True,
)
def update_weather(_search_clicks, _demo_clicks, city, country):
    if ctx.triggered_id == "demo-btn":
        return render_weather(demo_weather()), ""
    try:
        return render_weather(fetch_weather(city, country)), ""
    except WeatherError as exc:
        return no_update, html.Div(str(exc), className="error-message")
