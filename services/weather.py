"""OpenWeatherMap API integration. No API credentials inside source or logs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import re
from typing import Any

import requests

BASE = "https://api.openweathermap.org/data/2.5"
TIMEOUT = 12


class WeatherError(Exception):
    """Safe human-readable errors that never include API tokens or request URLs."""


def validate_place(city: str | None, country: str | None) -> tuple[str, str]:
    c = (city or "").strip()
    country = (country or "BR").strip().upper()
    if not 2 <= len(c) <= 80 or not re.fullmatch(r"[\w\sÀ-ÿ.'\-]+", c, re.UNICODE):
        raise WeatherError("Informe uma cidade válida, com 2 a 80 caracteres.")
    if not re.fullmatch(r"[A-Z]{2}", country):
        raise WeatherError("Informe o código ISO de duas letras do país (ex.: BR).")
    return c, country


def _safe_request(session: Any, endpoint: str, params: dict) -> dict:
    try:
        response = session.get(BASE + endpoint, params=params, timeout=TIMEOUT)
    except requests.RequestException:
        raise WeatherError("Serviço de clima indisponível. Verifique a conexão e tente novamente.") from None
    if response.status_code == 401:
        raise WeatherError("Chave OpenWeatherMap inválida. Confira OPENWEATHER_API_KEY.")
    if response.status_code == 404:
        raise WeatherError("Localidade não encontrada. Confira cidade e país.")
    if response.status_code == 429:
        raise WeatherError("Limite de consultas da API atingido. Tente novamente mais tarde.")
    if response.status_code >= 400:
        raise WeatherError("O serviço meteorológico não respondeu corretamente.")
    try:
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("malformed JSON")
        return data
    except (ValueError, TypeError):
        raise WeatherError("A API retornou dados inesperados.") from None


def _number(data: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default


def fetch_weather(city: str | None, country: str | None, *, session=None, api_key: str | None = None) -> dict:
    c, co = validate_place(city, country)
    key = api_key if api_key is not None else os.getenv("OPENWEATHER_API_KEY", "")
    if not key or not key.strip():
        raise WeatherError("Chave de API não configurada. Use o modo Demonstração ou defina OPENWEATHER_API_KEY no .env.")
    transport = session or requests.Session()
    params = {"q": f"{c},{co}", "appid": key.strip(), "lang": "pt_br", "units": "metric"}
    current = _safe_request(transport, "/weather", params)
    forecast = _safe_request(transport, "/forecast", params)
    try:
        main = current["main"]
        weather = current["weather"][0]
        timezone_seconds = int(current.get("timezone", 0))
        now_utc = datetime.fromtimestamp(int(current["dt"]), tz=timezone.utc)
        items = []
        for item in forecast["list"]:
            local_time = datetime.fromtimestamp(int(item["dt"]), tz=timezone.utc) + timedelta(seconds=timezone_seconds)
            items.append({
                "time": local_time.strftime("%d/%m %Hh"),
                "label": local_time.strftime("%d/%m"),
                "hour": local_time.strftime("%H:%M"),
                "temp": round(float(item["main"]["temp"]), 1),
                "humidity": int(item["main"]["humidity"]),
                "description": str(item["weather"][0]["description"]).capitalize(),
            })
        if not items:
            raise ValueError("empty forecast")
        return {
            "city": str(current.get("name") or c),
            "country": co,
            "temp": round(float(main["temp"]), 1),
            "feels_like": round(float(main["feels_like"]), 1),
            "humidity": int(main["humidity"]),
            "pressure": int(main.get("pressure", 0)),
            "wind_kmh": round(_number(current.get("wind") or {}, "speed") * 3.6, 1),
            "description": str(weather["description"]).capitalize(),
            "condition": str(weather.get("main", "Clouds")),
            "observed_at": (now_utc + timedelta(seconds=timezone_seconds)).strftime("%d/%m/%Y %H:%M"),
            "series": items,
            "demo": False,
        }
    except (KeyError, IndexError, ValueError, TypeError, OverflowError):
        raise WeatherError("A API retornou dados meteorológicos incompletos.") from None


def demo_weather() -> dict:
    """Always visibly synthetic. Deterministic data for non-credentialed reviewers."""
    anchor = datetime(2022, 6, 15, 9)
    temperatures = [25.2, 28.4, 29.7, 27.1, 24.8, 25.0, 28.0, 29.2, 26.6, 24.3, 24.8, 27.6, 29.0, 26.1, 23.8, 24.4, 27.2, 28.7, 25.8, 23.5]
    points = []
    for i, temp in enumerate(temperatures):
        date = anchor + timedelta(hours=i * 3)
        points.append({"time": date.strftime("%d/%m %Hh"), "label": date.strftime("%d/%m"),
                       "hour": date.strftime("%H:%M"), "temp": temp,
                       "humidity": 71 - i % 6, "description": "Céu parcialmente nublado"})
    return {"city": "Recife", "country": "BR", "temp": 27.4, "feels_like": 29.1,
            "humidity": 71, "pressure": 1012, "wind_kmh": 13.7,
            "description": "Parcialmente nublado", "condition": "Clouds",
            "observed_at": "15/06/2022 09:00 (simulado)",
            "series": points, "demo": True}
