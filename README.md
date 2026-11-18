# Clima Lab

**Dashboard meteorológico desenvolvido com Python, Dash e Plotly.** Consulte o tempo de uma cidade, acompanhe as condições atuais e visualize a previsão de temperatura em gráficos interativos.

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white) ![Dash](https://img.shields.io/badge/Dash-Web%20App-1967a0) ![Plotly](https://img.shields.io/badge/Plotly-Gráficos-6d62b5)

## Interface

| Desktop | Mobile |
| --- | --- |
| ![Tela do Clima Lab no desktop](docs/clima-desktop.png) | ![Tela do Clima Lab no celular](docs/clima-mobile.png) |

## Funcionalidades

- **Busca por localização:** consulte uma cidade informando o nome e o código de país, como `Recife` e `BR`.
- **Condições atuais:** temperatura, sensação térmica, umidade, velocidade do vento e pressão atmosférica.
- **Previsão interativa:** evolução da temperatura ao longo das próximas horas, com pontos detalhados ao passar o cursor.
- **Resumo por dia:** temperaturas máximas e mínimas entre os horários previstos.
- **Interface responsiva:** painel em tema escuro, adaptado para desktop e celular.
- **Modo demonstração:** explore todos os componentes do painel sem configurar uma chave de API.

O modo demonstração exibe valores de exemplo, identificados na interface. As consultas reais utilizam o OpenWeatherMap.

## Como executar

**Pré-requisitos:** Python 3.12 ou superior.

```powershell
git clone https://github.com/JackNoArms/Aplicativo_web_clima.git
cd Aplicativo_web_clima

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abra **http://127.0.0.1:8050** para usar o aplicativo.

### Consultar o clima real

1. Crie uma chave de API em [OpenWeatherMap](https://openweathermap.org/api).
2. Copie `.env.example` para um arquivo `.env`.
3. Preencha a variável abaixo com a sua chave:

```dotenv
OPENWEATHER_API_KEY=SUA_CHAVE_AQUI
```

4. Inicie o aplicativo e clique em **Consultar agora**.

Sem uma chave configurada, o botão **Ver demonstração** permanece disponível.

## Tecnologias

| Tecnologia | Aplicação |
| --- | --- |
| **Python** | Regras de negócio e integração |
| **Dash** | Componentes e atualização dinâmica da interface |
| **Plotly** | Gráfico de previsão de temperatura |
| **OpenWeatherMap API** | Condições meteorológicas e previsão |
| **Requests** | Requisições HTTP com tratamento de erros |
| **CSS e Bootstrap** | Layout responsivo e identidade visual |

## Organização do código

```text
app.py                  Inicialização do aplicativo
pages/home.py           Interface e gráficos
services/weather.py     Consulta e tratamento dos dados meteorológicos
assets/style.css        Estilos e responsividade
tests/                  Testes automatizados
```

## Testes

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

A integração também possui validação de entradas, timeout de requisições e mensagens para falhas da API.

**Fonte meteorológica:** [OpenWeatherMap](https://openweathermap.org/api).
