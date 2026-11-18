# Segurança e credenciais

## Credencial legada exposta

A primeira versão deste projeto tinha uma chave OpenWeatherMap inserida diretamente em `pages/home.py`, que foi publicada em commits históricos. Este documento **não** reproduz o valor.

Nesta modernização:

- A chave foi removida do código atual.
- Consultas usam `OPENWEATHER_API_KEY` carregada do ambiente / `.env` local ignorado pelo Git.
- O cliente valida entradas, usa timeout e responde com erros controlados, sem mostrar URL com token no navegador.
- O modo demonstração não realiza chamadas reais e exibe marcação persistente de dados fictícios.

**Ação indispensável do proprietário:** entrar no portal OpenWeatherMap, revogar a chave antiga e gerar uma nova. A aplicação não pode fazer essa rotação por conta própria. Revisão/remoção de credenciais do histórico exigiria um processo explícito de reescrita de Git (com impacto em forks/clones), e não foi realizado.

Nunca compartilhe `.env`, `.cache/`, tokens, sessões de navegador ou dumps de logs. Os testes devem usar chaves artificiais e transporte mockado.

## Limites

- O projeto usa o servidor de desenvolvimento Flask/Dash para uso local; não é configuração para exposição direta na internet.
- O mecanismo não contém proteção para grandes volumes de chamadas de múltiplos usuários; use gateway e rate limit em produção.
- Mudanças de endpoint e políticas do provedor exigem revisão da integração.
