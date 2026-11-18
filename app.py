"""Clima Lab — dashboard meteorológico com API ou demonstração fictícia."""
from __future__ import annotations

import os

import dash
from dotenv import load_dotenv

from pages.home import layout

load_dotenv()

app = dash.Dash(
    __name__,
    title="Clima Lab | Panorama meteorológico",
    suppress_callback_exceptions=True,
    external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"],
)
server = app.server
app.layout = layout

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    app.run(debug=False, host="127.0.0.1", port=port)
