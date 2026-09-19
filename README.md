# JARVIS — Mega-Sena AI

Aplicativo experimental em Streamlit para análise estatística e otimização combinatória de jogos da Mega-Sena.

## Execução
```bash
pip install -r requirements.txt
streamlit run app.py
```

O aplicativo consulta a API pública da CAIXA e carrega apenas os últimos 300 concursos para evitar uma inicialização lenta.

**Importante:** os scores são heurísticos e não representam probabilidades reais de sorteio.
