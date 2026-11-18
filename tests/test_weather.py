"""Controlled tests with synthetic API data; no real credentials or outbound calls."""
import pytest
import requests

from services.weather import WeatherError, demo_weather, fetch_weather, validate_place
from pages.home import forecast_figure, render_weather


class Response:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def json(self):
        return self.payload


class Transport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append((url, params, timeout))
        return self.responses.pop(0)


CURRENT = {
    "name": "Recife", "dt": 1750000000, "timezone": -10800,
    "main": {"temp": 26.5, "feels_like": 28.0, "humidity": 77, "pressure": 1012},
    "wind": {"speed": 3}, "weather": [{"main": "Clouds", "description": "nuvens dispersas"}],
}
FORECAST = {"list": [
    {"dt": 1750000000 + h * 3600,
     "main": {"temp": 26 + h / 10, "humidity": 78},
     "weather": [{"description": "nuvens"}]}
    for h in (3, 6, 9)
]}


def test_validate_place_and_country():
    assert validate_place(" Água Branca ", "br") == ("Água Branca", "BR")
    for city, country in [("", "BR"), ("a", "BR"), ("Recife", "BRA"), ("Recife", "B1")]:
        with pytest.raises(WeatherError):
            validate_place(city, country)


def test_no_key_has_safe_message(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    with pytest.raises(WeatherError, match="não configurada"):
        fetch_weather("Recife", "BR")


def test_current_and_forecast_are_parsed():
    transport = Transport([Response(CURRENT), Response(FORECAST)])
    data = fetch_weather("Recife", "BR", session=transport, api_key="FAKE-ONLY-TEST")
    assert data["demo"] is False
    assert data["city"] == "Recife" and data["temp"] == 26.5
    assert len(data["series"]) == 3
    assert data["wind_kmh"] == 10.8
    assert all(call[2] == 12 for call in transport.calls)
    assert all("FAKE-ONLY-TEST" not in call[0] for call in transport.calls)


@pytest.mark.parametrize("status,message", [
    (401, "inválida"), (404, "não encontrada"), (429, "Limite"), (500, "não respondeu"),
])
def test_http_errors_are_actionable(status, message):
    transport = Transport([Response({}, status)])
    with pytest.raises(WeatherError, match=message):
        fetch_weather("Recife", "BR", session=transport, api_key="dummy-key")


def test_connection_errors_hide_full_urls_and_secrets():
    class Broken:
        def get(self, url, params, timeout):
            raise requests.RequestException("appid=PRIVATE-SECRET-WHICH-MUST-NOT-LEAK")
    with pytest.raises(WeatherError) as exc:
        fetch_weather("Recife", "BR", session=Broken(), api_key="PRIVATE-SECRET-WHICH-MUST-NOT-LEAK")
    assert "PRIVATE-SECRET-WHICH-MUST-NOT-LEAK" not in str(exc.value)


def test_malformed_response_is_safe():
    transport = Transport([Response({"main": {}, "weather": []}), Response(FORECAST)])
    with pytest.raises(WeatherError, match="incompletos"):
        fetch_weather("Recife", "BR", session=transport, api_key="dummy")


def test_demo_is_explicit_and_renders_chart():
    demo = demo_weather()
    assert demo["demo"] is True
    assert len(demo["series"]) == 20
    figure = forecast_figure(demo["series"])
    assert len(figure.data) == 1
    panel = render_weather(demo)
    assert panel.className == "results"
    assert demo["observed_at"].endswith("(simulado)")
