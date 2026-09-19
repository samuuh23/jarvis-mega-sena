import streamlit as st
import requests
import pandas as pd
import numpy as np
import random
from collections import Counter
from itertools import combinations

st.set_page_config(page_title="JARVIS — Mega-Sena AI", page_icon="🤖", layout="wide")

API = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
TIMEOUT = 8
MAX_HISTORY = 300

@st.cache_data(ttl=1800)
def load_history(limit=MAX_HISTORY):
    """Carrega somente os últimos concursos para evitar milhares de requisições."""
    try:
        latest = requests.get(API, timeout=TIMEOUT).json()
        latest_num = int(latest["numero"])
        first = max(1, latest_num - limit + 1)

        draws = []
        # Buscar do mais recente para trás e parar no limite.
        for n in range(latest_num, first - 1, -1):
            try:
                r = requests.get(f"{API}/{n}", timeout=TIMEOUT)
                r.raise_for_status()
                d = r.json()
                nums = d.get("listaDezenas", [])
                if len(nums) == 6:
                    draws.append({
                        "concurso": int(d["numero"]),
                        "data": d.get("dataApuracao", ""),
                        "dezenas": [int(x) for x in nums]
                    })
            except Exception:
                continue

        if not draws:
            raise RuntimeError("Não foi possível obter os concursos da Caixa.")

        draws.sort(key=lambda x: x["concurso"])
        return draws

    except Exception as e:
        raise RuntimeError(f"Falha ao carregar histórico: {e}")

def frequency(draws):
    c = Counter()
    for d in draws:
        c.update(d["dezenas"])
    return c

def pair_frequency(draws):
    c = Counter()
    for d in draws:
        c.update(combinations(sorted(d["dezenas"]), 2))
    return c

def ticket_score(ticket, freq, pairs, recent_freq, seed=0):
    score = 0.0
    # Frequência histórica e recente: sinal experimental, não probabilidade real.
    for n in ticket:
        score += 0.35 * freq[n]
        score += 0.65 * recent_freq[n]

    for a, b in combinations(sorted(ticket), 2):
        score += 0.18 * pairs[(a, b)]

    odd = sum(n % 2 for n in ticket)
    total = sum(ticket)

    if 2 <= odd <= 4:
        score += 8
    if 140 <= total <= 240:
        score += 8

    # Penaliza excesso de números consecutivos.
    consecutive = sum(1 for a, b in zip(ticket, ticket[1:]) if b == a + 1)
    score -= 3 * consecutive

    return score

def generate_tickets(draws, amount=10, candidates=3000, seed=42):
    rng = random.Random(seed)
    freq = frequency(draws)
    pairs = pair_frequency(draws)
    recent = draws[-50:]
    recent_freq = frequency(recent)

    pool = list(range(1, 61))
    scored = []

    for _ in range(candidates):
        ticket = sorted(rng.sample(pool, 6))
        s = ticket_score(ticket, freq, pairs, recent_freq)
        scored.append((s, ticket))

    scored.sort(reverse=True, key=lambda x: x[0])

    selected = []
    selected_sets = []

    # Seleção gulosa buscando qualidade + diversidade.
    for base_score, ticket in scored:
        tset = set(ticket)
        if any(len(tset & other) >= 5 for other in selected_sets):
            continue

        diversity_bonus = 0
        if selected_sets:
            avg_overlap = np.mean([len(tset & other) for other in selected_sets])
            diversity_bonus = max(0, 6 - avg_overlap) * 2

        selected.append((base_score + diversity_bonus, ticket))
        selected_sets.append(tset)

        if len(selected) >= amount:
            break

    return sorted(selected, reverse=True)

st.title("🤖 JARVIS — Mega-Sena AI")
st.caption("Laboratório estatístico e combinatório • não é um previsor garantido")

with st.sidebar:
    st.header("⚙️ Configuração")
    amount = st.slider("Quantidade de jogos", 1, 30, 10)
    candidates = st.slider("Candidatos analisados", 500, 10000, 3000, step=500)
    seed = st.number_input("Seed", min_value=0, value=42, step=1)

    if st.button("🔄 Atualizar histórico"):
        st.cache_data.clear()
        st.rerun()

try:
    with st.spinner("Carregando os últimos concursos da Caixa..."):
        draws = load_history()
    st.success(f"Histórico carregado: {len(draws)} concursos.")
except Exception as e:
    st.error(str(e))
    st.info("A API da Caixa pode estar temporariamente indisponível. Tente novamente em alguns minutos.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🎯 Gerador", "📊 Estatísticas", "🧪 Validação"])

with tab1:
    st.subheader("Jogos experimentais")
    st.write("Os jogos abaixo são gerados por um modelo heurístico de frequência, recência, pares e diversidade.")
    if st.button("🚀 Gerar jogos", type="primary"):
        results = generate_tickets(draws, amount, candidates, seed)
        df = pd.DataFrame({
            "Jogo": [i + 1 for i in range(len(results))],
            "Números": [" - ".join(f"{n:02d}" for n in ticket) for _, ticket in results],
            "Score experimental": [round(score, 2) for score, _ in results]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Frequência dos números")
    freq = frequency(draws)
    freq_df = pd.DataFrame({
        "Número": list(range(1, 61)),
        "Frequência": [freq[n] for n in range(1, 61)]
    })
    st.bar_chart(freq_df.set_index("Número"))

    sums = [sum(d["dezenas"]) for d in draws]
    st.write(f"**Soma média dos últimos {len(sums)} concursos:** {np.mean(sums):.1f}")
    st.write(f"**Menor soma:** {min(sums)}  •  **Maior soma:** {max(sums)}")

with tab3:
    st.subheader("Validação")
    st.write("Esta versão mantém a geração experimental. A próxima etapa será adicionar backtest walk-forward contra jogos aleatórios.")
    st.warning("Frequência histórica e padrões de concursos anteriores não garantem vantagem preditiva em um sorteio aleatório.")
