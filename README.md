
# JARVIS Mega-Sena 2.0 — painel web

## Rodar no computador

```bash
pip install -r requirements.txt
streamlit run app.py
```

Depois abra o endereço mostrado pelo Streamlit no navegador.

## Rodar na nuvem

Uma opção simples é publicar este projeto em um serviço que execute Streamlit. Você precisará enviar `app.py` e `requirements.txt`.

## Observação

O painel consulta a API pública da CAIXA para obter o histórico. A disponibilidade da API pode variar. O sistema é experimental: o score organiza combinações segundo heurísticas, mas não deve ser interpretado como uma probabilidade verdadeira de sorteio.

A próxima etapa pode incluir backtesting walk-forward completo, algoritmo genético, Monte Carlo e comparação estatística contra múltiplas estratégias aleatórias.
