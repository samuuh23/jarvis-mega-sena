import streamlit as st
import requests
import pandas as pd
import numpy as np
import random
from collections import Counter
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# JARVIS — Mega-Sena AI / VISUAL EDITION
# ============================================================

st.set_page_config(
    page_title="JARVIS • Mega-Sena AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

API = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
TIMEOUT = 8
HISTORY_LIMIT = 300
MAX_WORKERS = 12


# ----------------------------- CSS -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');

:root {
  --jarvis-blue: #55c7ff;
  --jarvis-cyan: #27e1ff;
  --jarvis-purple: #8b7cff;
  --jarvis-bg: #070b13;
  --jarvis-card: rgba(17, 25, 40, .72);
  --jarvis-border: rgba(110, 205, 255, .18);
  --jarvis-text: #edf8ff;
  --jarvis-muted: #8da2b7;
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
}

.stApp {
  background:
    radial-gradient(circle at 12% 5%, rgba(39,225,255,.12), transparent 28%),
    radial-gradient(circle at 88% 10%, rgba(139,124,255,.11), transparent 25%),
    linear-gradient(145deg, #05080f 0%, #09111d 48%, #060912 100%);
  color: var(--jarvis-text);
}

/* Subtle animated background */
.stApp:before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(85,199,255,.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(85,199,255,.025) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, black, transparent 85%);
  animation: gridMove 18s linear infinite;
}
@keyframes gridMove {
  from { transform: translateY(0); }
  to { transform: translateY(42px); }
}

/* Hide Streamlit chrome */
#MainMenu, footer {visibility: hidden;}
[data-testid="stHeader"] {background: transparent;}

/* Main entrance animation */
.block-container {
  max-width: 1380px;
  padding-top: 2rem;
  animation: pageIn .65s ease-out both;
}
@keyframes pageIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hero */
.jarvis-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--jarvis-border);
  border-radius: 28px;
  padding: 30px 32px;
  background:
    radial-gradient(circle at 88% 20%, rgba(39,225,255,.13), transparent 30%),
    linear-gradient(135deg, rgba(17,29,48,.92), rgba(8,13,24,.78));
  box-shadow: 0 25px 70px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.04);
}
.jarvis-hero:after {
  content: "";
  position: absolute;
  width: 260px;
  height: 260px;
  right: -100px;
  top: -120px;
  border: 1px solid rgba(85,199,255,.22);
  border-radius: 50%;
  box-shadow: 0 0 50px rgba(39,225,255,.08);
  animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { transform: scale(.92); opacity:.55; }
  50% { transform: scale(1.05); opacity:1; }
}
.eyebrow {
  color: var(--jarvis-cyan);
  font-size: .78rem;
  letter-spacing: .18em;
  font-weight: 800;
  text-transform: uppercase;
}
.hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(2.1rem, 5vw, 4rem);
  font-weight: 800;
  letter-spacing: -.04em;
  margin: 8px 0 4px;
  background: linear-gradient(90deg, #f4fbff, #63d8ff 45%, #a69cff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-sub {
  color: #a8bbce;
  max-width: 720px;
  font-size: 1rem;
  line-height: 1.6;
}
.status-pill {
  display:inline-flex;
  align-items:center;
  gap:8px;
  margin-top:18px;
  padding:8px 13px;
  border-radius:999px;
  border:1px solid rgba(65,235,173,.22);
  background:rgba(25,180,120,.08);
  color:#7ff1c2;
  font-size:.82rem;
  font-weight:700;
}
.status-dot {
  width:8px;height:8px;border-radius:50%;
  background:#51e8ae;
  box-shadow:0 0 14px #51e8ae;
  animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink { 50% {opacity:.35; transform:scale(.75);} }

/* Cards */
.metric-card {
  border:1px solid var(--jarvis-border);
  border-radius:20px;
  padding:18px 20px;
  background:linear-gradient(145deg, rgba(18,29,47,.75), rgba(9,14,25,.7));
  box-shadow:0 12px 35px rgba(0,0,0,.18);
  transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease;
  animation: cardIn .55s ease-out both;
}
.metric-card:hover {
  transform:translateY(-4px);
  border-color:rgba(85,199,255,.38);
  box-shadow:0 18px 42px rgba(39,225,255,.09);
}
.metric-label {color:#8298ad;font-size:.78rem;text-transform:uppercase;letter-spacing:.1em;}
.metric-value {font-family:'Orbitron';font-size:1.65rem;font-weight:700;margin-top:5px;}
.metric-accent {color:#5bd6ff;}
@keyframes cardIn {
  from {opacity:0; transform:translateY(10px);}
  to {opacity:1; transform:translateY(0);}
}

/* Number balls */
.ticket-card {
  border:1px solid rgba(85,199,255,.17);
  border-radius:22px;
  padding:18px;
  margin:10px 0;
  background:linear-gradient(145deg, rgba(16,27,44,.84), rgba(7,12,21,.78));
  transition:all .25s ease;
}
.ticket-card:hover {
  transform:translateY(-3px);
  border-color:rgba(85,199,255,.42);
}
.ticket-head {
  display:flex; justify-content:space-between; align-items:center;
  margin-bottom:14px;
}
.ticket-index {
  color:#8298ad; font-size:.75rem; letter-spacing:.12em; text-transform:uppercase;
}
.ticket-score {
  color:#6ce0ff; font-size:.75rem; font-weight:700;
}
.balls {display:flex; flex-wrap:wrap; gap:10px;}
.ball {
  width:47px; height:47px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-family:'Orbitron'; font-weight:700; font-size:.88rem;
  color:#eaffff;
  border:1px solid rgba(100,225,255,.42);
  background:radial-gradient(circle at 32% 25%, #65ddff 0%, #168bbd 42%, #07334d 100%);
  box-shadow:0 0 18px rgba(39,225,255,.13), inset 0 1px 4px rgba(255,255,255,.35);
  animation: ballIn .45s ease both;
}
.ball:nth-child(2){animation-delay:.04s}.ball:nth-child(3){animation-delay:.08s}
.ball:nth-child(4){animation-delay:.12s}.ball:nth-child(5){animation-delay:.16s}
.ball:nth-child(6){animation-delay:.20s}
@keyframes ballIn {
  from {opacity:0; transform:scale(.65) rotate(-10deg);}
  to {opacity:1; transform:scale(1) rotate(0);}
}

/* Section headings */
.section-title {
  font-family:'Orbitron';
  font-size:1.1rem;
  margin:24px 0 10px;
}
.section-sub {color:#7f94a9;font-size:.88rem;margin-bottom:14px;}

/* Buttons */
.stButton > button {
  border-radius:14px !important;
  border:1px solid rgba(85,199,255,.25) !important;
  background:linear-gradient(135deg, rgba(30,91,125,.8), rgba(58,49,126,.8)) !important;
  color:white !important;
  font-weight:700 !important;
  transition:all .2s ease !important;
  min-height:44px;
}
.stButton > button:hover {
  transform:translateY(-2px);
  border-color:rgba(85,199,255,.55) !important;
  box-shadow:0 10px 28px rgba(39,225,255,.13) !important;
}

/* Tabs */
button[data-baseweb="tab"] {
  font-weight:700 !important;
  color:#8398ac !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color:#66dbff !important;
}
div[data-baseweb="tab-highlight"] {background:#51d7ff !important;}

/* Sidebar */
section[data-testid="stSidebar"] {
  background:linear-gradient(180deg, rgba(7,12,21,.97), rgba(9,14,25,.97));
  border-right:1px solid rgba(85,199,255,.1);
}
.sidebar-brand {
  font-family:'Orbitron';
  color:#66dcff;
  font-size:1.05rem;
  letter-spacing:.08em;
  margin-bottom:5px;
}
.sidebar-small {color:#71869b;font-size:.76rem;line-height:1.5;}

/* Dataframe */
[data-testid="stDataFrame"] {
  border:1px solid rgba(85,199,255,.12);
  border-radius:16px;
  overflow:hidden;
}

/* Mobile */
@media (max-width: 700px) {
  .block-container {padding:1rem .75rem 2rem;}
  .jarvis-hero {padding:22px 18px;border-radius:22px;}
  .hero-title {font-size:2rem;}
  .ball {width:42px;height:42px;font-size:.76rem;}
  .balls {gap:7px;}
}
</style>
""", unsafe_allow_html=True)


# ----------------------------- DATA -----------------------------
def fetch_one(n):
    try:
        r = requests.get(f"{API}/{n}", timeout=TIMEOUT)
        r.raise_for_status()
        d = r.json()
        nums = d.get("listaDezenas", [])
        if len(nums) != 6:
            return None
        return {
            "concurso": int(d["numero"]),
            "data": d.get("dataApuracao", ""),
            "dezenas": sorted(int(x) for x in nums),
        }
    except Exception:
        return None


@st.cache_data(ttl=1800, show_spinner=False)
def load_history(limit=HISTORY_LIMIT):
    latest = requests.get(API, timeout=TIMEOUT).json()
    latest_num = int(latest["numero"])
    first = max(1, latest_num - limit + 1)

    draws = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(fetch_one, n) for n in range(first, latest_num + 1)]
        for fut in as_completed(futures):
            item = fut.result()
            if item:
                draws.append(item)

    draws.sort(key=lambda x: x["concurso"])
    if not draws:
        raise RuntimeError("A Caixa não retornou os concursos.")
    return draws


def frequency(draws):
    c = Counter()
    for d in draws:
        c.update(d["dezenas"])
    return c


def pair_frequency(draws):
    c = Counter()
    for d in draws:
        c.update(combinations(d["dezenas"], 2))
    return c


def recency(draws):
    last = {n: None for n in range(1, 61)}
    for i, d in enumerate(draws):
        for n in d["dezenas"]:
            last[n] = i
    end = len(draws) - 1
    return {n: end - last[n] if last[n] is not None else len(draws) for n in range(1,61)}


def shape_score(ticket):
    odd = sum(n % 2 for n in ticket)
    total = sum(ticket)
    decades = len(set((n-1)//10 for n in ticket))
    consecutive = sum(b == a+1 for a,b in zip(ticket,ticket[1:]))
    score = 0
    if 2 <= odd <= 4: score += 10
    if 150 <= total <= 240: score += 10
    if decades >= 4: score += 5
    score -= 4 * consecutive
    return score


def score_ticket(ticket, freq, pairs, recent, delay, strategy):
    mf = max(freq.values()) or 1
    mr = max(recent.values()) or 1
    mp = max(pairs.values()) or 1
    score = 0

    for n in ticket:
        f = freq[n] / mf
        r = recent[n] / mr
        fresh = 1/(1+delay[n])
        if strategy == "recent":
            score += .25*f + .60*r + .15*fresh
        elif strategy == "frequency":
            score += .80*f + .20*r
        elif strategy == "contrarian":
            score += .45*f + .10*r + .45*(1-fresh)
        else:
            score += .45*f + .40*r + .15*fresh

    for a,b in combinations(ticket,2):
        score += .35 * pairs[(a,b)] / mp

    return score + shape_score(ticket)


def generate(draws, amount, candidates, seed, strategy):
    rng = random.Random(seed)
    freq = frequency(draws)
    pairs = pair_frequency(draws)
    recent = frequency(draws[-50:])
    delay = recency(draws)

    scored = []
    for _ in range(candidates):
        ticket = sorted(rng.sample(range(1,61), 6))
        scored.append((score_ticket(ticket,freq,pairs,recent,delay,strategy),ticket))
    scored.sort(reverse=True,key=lambda x:x[0])

    selected, used = [], []
    for score,ticket in scored:
        s=set(ticket)
        if any(len(s & u) >= 5 for u in used):
            continue
        penalty = np.mean([len(s & u) for u in used]) * 1.5 if used else 0
        selected.append((score-penalty,ticket))
        used.append(s)
        if len(selected) >= amount:
            break
    return sorted(selected, reverse=True)


def ticket_html(i, score, ticket):
    balls = "".join(f'<span class="ball">{n:02d}</span>' for n in ticket)
    return f"""
    <div class="ticket-card">
      <div class="ticket-head">
        <div class="ticket-index">JOGO {i:02d}</div>
        <div class="ticket-score">SCORE {score:.2f}</div>
      </div>
      <div class="balls">{balls}</div>
    </div>
    """


def historical_df(draws):
    rows=[]
    for d in draws:
        rows.append({
            "Concurso": d["concurso"],
            "Data": d["data"],
            **{f"D{i+1}":n for i,n in enumerate(d["dezenas"])},
            "Soma": sum(d["dezenas"]),
            "Pares": sum(n%2==0 for n in d["dezenas"])
        })
    return pd.DataFrame(rows)


# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">◈ JARVIS CORE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-small">Sistema experimental de análise combinatória</div>', unsafe_allow_html=True)
    st.divider()

    amount = st.slider("Quantidade de jogos", 1, 30, 10)
    candidates = st.slider("Combinações analisadas", 500, 12000, 4000, step=500)
    strategy = st.selectbox(
        "Modo de análise",
        ["balanced","recent","frequency","contrarian"],
        format_func=lambda x: {
            "balanced":"⚖️ Equilibrado",
            "recent":"⚡ Recência",
            "frequency":"📈 Frequência",
            "contrarian":"🧩 Contrarian"
        }[x]
    )
    seed = st.number_input("Seed", 0, 999999, 42)

    st.divider()
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        '<div class="sidebar-small">Os índices do JARVIS são heurísticos. '
        'Eles não representam uma probabilidade real de uma dezena ser sorteada.</div>',
        unsafe_allow_html=True
    )


# ----------------------------- LOAD -----------------------------
try:
    with st.spinner("Inicializando núcleo JARVIS..."):
        draws = load_history()
except Exception as e:
    st.error(f"Falha ao carregar dados: {e}")
    st.stop()

latest = draws[-1]
hist = historical_df(draws)

# ----------------------------- HERO -----------------------------
st.markdown(f"""
<div class="jarvis-hero">
  <div class="eyebrow">JARVIS // MEGA-SENA AI</div>
  <div class="hero-title">INTELLIGENCE<br>FOR COMBINATIONS</div>
  <div class="hero-sub">
    Análise estatística, otimização combinatória e validação histórica
    em uma interface criada para explorar hipóteses — não para prometer
    previsões impossíveis.
  </div>
  <div class="status-pill"><span class="status-dot"></span> SISTEMA ONLINE • CONCURSO #{latest["concurso"]}</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# Metrics
c1,c2,c3,c4 = st.columns(4)
metrics = [
    ("CONCURSOS", f"{len(draws)}", "base ativa"),
    ("ÚLTIMO", f"#{latest['concurso']}", latest["data"]),
    ("NÚMEROS", "01 — 60", "universo"),
    ("MOTOR", "ONLINE", "JARVIS Core"),
]
for col,(label,value,small) in zip([c1,c2,c3,c4],metrics):
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value metric-accent">{value}</div>'
        f'<div class="sidebar-small">{small}</div></div>',
        unsafe_allow_html=True
    )

# ----------------------------- TABS -----------------------------
tabs = st.tabs(["🎯  GERADOR", "📊  INTELIGÊNCIA", "🧪  VALIDAÇÃO", "🗃️  HISTÓRICO"])

with tabs[0]:
    st.markdown('<div class="section-title">Painel de geração</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">O motor pesquisa milhares de combinações e seleciona '
        'jogos com pontuação heurística e baixa redundância entre si.</div>',
        unsafe_allow_html=True
    )

    if st.button("⚡ ATIVAR JARVIS", type="primary", use_container_width=True):
        with st.spinner("Analisando o espaço combinatório..."):
            results = generate(draws, amount, candidates, int(seed), strategy)

        for i,(score,ticket) in enumerate(results,1):
            st.markdown(ticket_html(i,score,ticket), unsafe_allow_html=True)

        export = pd.DataFrame([
            {"Jogo":i,"Números":" - ".join(f"{n:02d}" for n in ticket),"Score":round(score,3)}
            for i,(score,ticket) in enumerate(results,1)
        ])
        st.download_button(
            "⬇️ EXPORTAR JOGOS",
            export.to_csv(index=False).encode(),
            "jarvis_jogos.csv",
            "text/csv",
            use_container_width=True
        )

with tabs[1]:
    st.markdown('<div class="section-title">Central de inteligência</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Indicadores descritivos do recorte histórico carregado.</div>', unsafe_allow_html=True)

    freq = frequency(draws)
    fdf = pd.DataFrame({"Número":range(1,61),"Frequência":[freq[n] for n in range(1,61)]})

    left,right = st.columns([1.6,1])
    with left:
        st.bar_chart(fdf.set_index("Número"), height=360)
    with right:
        top = fdf.sort_values("Frequência",ascending=False).head(12)
        st.markdown("**Mais frequentes no recorte**")
        st.dataframe(top,use_container_width=True,hide_index=True)

        delay = recency(draws)
        late = pd.DataFrame({
            "Número":range(1,61),
            "Atraso":[delay[n] for n in range(1,61)]
        }).sort_values("Atraso",ascending=False).head(12)
        st.markdown("**Maior intervalo desde ocorrência**")
        st.dataframe(late,use_container_width=True,hide_index=True)

    m1,m2,m3 = st.columns(3)
    m1.metric("Soma média", f"{hist['Soma'].mean():.1f}")
    m2.metric("Média de pares", f"{hist['Pares'].mean():.2f}")
    m3.metric("Soma mediana", f"{hist['Soma'].median():.0f}")

with tabs[2]:
    st.markdown('<div class="section-title">Laboratório de validação</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Teste walk-forward: o modelo só usa informação anterior ao concurso testado.</div>',
        unsafe_allow_html=True
    )

    test_n = st.slider("Concursos de teste", 10, 50, 20)
    train_n = st.slider("Janela de treino", 50, 250, 150, step=25)
    per_draw = st.slider("Jogos por concurso", 1, 10, 5)

    if st.button("🧪 EXECUTAR BACKTEST", use_container_width=True):
        if len(draws) < train_n + test_n:
            st.error("Histórico insuficiente para estes parâmetros.")
        else:
            rows=[]
            rng=random.Random(int(seed))
            start=len(draws)-test_n
            for i in range(start,len(draws)):
                train=draws[max(0,i-train_n):i]
                actual=draws[i]["dezenas"]
                pred=generate(train,per_draw,800,int(seed)+i,"balanced")
                mh=[len(set(t)&set(actual)) for _,t in pred]
                rh=[len(set(rng.sample(range(1,61),6))&set(actual)) for _ in range(per_draw)]
                rows.append({
                    "Concurso":draws[i]["concurso"],
                    "Máx. JARVIS":max(mh),
                    "Máx. Aleatório":max(rh),
                    "Média JARVIS":np.mean(mh),
                    "Média Aleatório":np.mean(rh)
                })
            bt=pd.DataFrame(rows)
            a,b,c,d=st.columns(4)
            a.metric("Máximo JARVIS",f"{bt['Máx. JARVIS'].mean():.2f}")
            b.metric("Máximo aleatório",f"{bt['Máx. Aleatório'].mean():.2f}")
            c.metric("Média JARVIS",f"{bt['Média JARVIS'].mean():.3f}")
            d.metric("Média aleatória",f"{bt['Média Aleatório'].mean():.3f}")
            st.line_chart(bt.set_index("Concurso")[["Máx. JARVIS","Máx. Aleatório"]])
            st.dataframe(bt,use_container_width=True,hide_index=True)

with tabs[3]:
    st.markdown('<div class="section-title">Memória do sistema</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Os dados abaixo são a base atualmente utilizada pelo motor.</div>', unsafe_allow_html=True)
    st.dataframe(hist.sort_values("Concurso",ascending=False),use_container_width=True,hide_index=True)
