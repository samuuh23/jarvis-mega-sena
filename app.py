import streamlit as st
import requests
import pandas as pd
import numpy as np
import random
import time
from collections import Counter
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="JARVIS 3.0 • Mega-Sena Intelligence", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

API = "https://raw.githubusercontent.com/maickon/free-apiloterias/refs/heads/master/database/megasena"
TIMEOUT = 8
HISTORY_LIMIT = 180
MAX_WORKERS = 12

# ========================= JARVIS 3.0 =========================
# Product-ready Streamlit edition: dashboard, strategies, missions,
# local session history, radar, walk-forward validation and export.

CSS = r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');
:root{--c:#58d5ff;--c2:#8f82ff;--bg:#050912;--card:rgba(13,22,37,.78);--muted:#8ba0b5;--line:rgba(88,213,255,.18)}
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:radial-gradient(circle at 10% 0%,rgba(37,211,255,.13),transparent 30%),radial-gradient(circle at 95% 5%,rgba(143,130,255,.14),transparent 28%),linear-gradient(145deg,#03060d,#09111d 55%,#040711);color:#edf8ff}.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(88,213,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(88,213,255,.025) 1px,transparent 1px);background-size:40px 40px;mask-image:linear-gradient(to bottom,black,transparent 82%);animation:grid 18s linear infinite}@keyframes grid{to{transform:translateY(40px)}}
#MainMenu,footer{visibility:hidden}[data-testid="stHeader"]{background:transparent}.block-container{max-width:1420px;padding-top:1.4rem;animation:in .55s ease-out}@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.hero{border:1px solid var(--line);border-radius:28px;padding:28px 30px;background:linear-gradient(135deg,rgba(15,29,48,.94),rgba(6,11,20,.8));box-shadow:0 25px 70px #0007;position:relative;overflow:hidden}.hero:after{content:"";position:absolute;width:280px;height:280px;right:-120px;top:-150px;border:1px solid #58d5ff44;border-radius:50%;box-shadow:0 0 60px #58d5ff18;animation:pulse 3s ease-in-out infinite}@keyframes pulse{50%{transform:scale(1.08);opacity:.7}}
.eyebrow{font-size:.72rem;letter-spacing:.2em;color:#5ee0ff;font-weight:800;text-transform:uppercase}.title{font:800 clamp(2rem,5vw,4rem) Orbitron;letter-spacing:-.05em;background:linear-gradient(90deg,#f5fcff,#58d5ff 45%,#a49cff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:7px 0}.sub{color:#a6bacd;max-width:760px;line-height:1.6}.pill{display:inline-flex;gap:8px;align-items:center;margin-top:16px;padding:8px 12px;border-radius:999px;background:#1cbb8515;border:1px solid #55e9b044;color:#7cf1c2;font-size:.78rem;font-weight:800}.dot{width:8px;height:8px;background:#55e9b0;border-radius:50%;box-shadow:0 0 14px #55e9b0}
.card{border:1px solid var(--line);border-radius:20px;padding:18px;background:linear-gradient(145deg,rgba(16,29,47,.8),rgba(6,12,22,.72));box-shadow:0 12px 35px #0004;transition:.22s}.card:hover{transform:translateY(-3px);border-color:#58d5ff55}.label{color:#7f95aa;font-size:.72rem;text-transform:uppercase;letter-spacing:.12em}.value{font:700 1.55rem Orbitron;margin-top:5px}.cyan{color:#61dcff}.purple{color:#a59aff}.green{color:#74edbc}.muted{color:#8297ab}.section{font:700 1.05rem Orbitron;margin:25px 0 7px}.section-sub{color:#7e93a7;font-size:.86rem;margin-bottom:12px}
.ticket{border:1px solid #58d5ff20;border-radius:20px;padding:16px;margin:10px 0;background:linear-gradient(145deg,rgba(15,28,45,.86),rgba(6,11,20,.8));transition:.22s}.ticket:hover{border-color:#58d5ff55;transform:translateY(-2px)}.ticket-head{display:flex;justify-content:space-between;margin-bottom:12px}.balls{display:flex;gap:9px;flex-wrap:wrap}.ball{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 .84rem Orbitron;color:#efffff;border:1px solid #8ce6ff66;background:radial-gradient(circle at 30% 22%,#72e4ff,#168bbd 44%,#07344d);box-shadow:0 0 18px #27e1ff18,inset 0 1px 4px #fff5}.tag{font-size:.7rem;font-weight:800;color:#69dcff;border:1px solid #58d5ff30;border-radius:999px;padding:5px 8px;background:#58d5ff0d}.mission{border:1px solid #9a8dff30;background:linear-gradient(135deg,#18163a99,#09152699);border-radius:22px;padding:20px}.mission h3{font-family:Orbitron;margin:0 0 7px}.mini{font-size:.78rem;color:#8197ac}.warn{border:1px solid #ffc66b33;background:#ffb52b0b;border-radius:14px;padding:12px;color:#d9c19a;font-size:.8rem}.stButton>button{border-radius:13px!important;border:1px solid #58d5ff35!important;background:linear-gradient(135deg,#1d5574cc,#40347acc)!important;color:#fff!important;font-weight:800!important;min-height:43px;transition:.2s!important}.stButton>button:hover{transform:translateY(-2px);box-shadow:0 10px 28px #27e1ff16!important;border-color:#58d5ff77!important}.stProgress>div>div{background:linear-gradient(90deg,#58d5ff,#9588ff)}button[data-baseweb="tab"]{font-weight:800!important;color:#8095aa!important}button[data-baseweb="tab"][aria-selected="true"]{color:#65dcff!important}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#060b14,#09111d)!important;border-right:1px solid #58d5ff12}.sidebar-title{font:700 1rem Orbitron;color:#6bdfff}.side-plan{border:1px solid #58d5ff2b;background:#58d5ff08;border-radius:15px;padding:12px;margin:12px 0}.side-plan b{color:#64dcff}.smallcaps{font-size:.68rem;letter-spacing:.14em;color:#70869a;text-transform:uppercase}.stDataFrame{border-radius:16px;overflow:hidden}
@media(max-width:700px){.block-container{padding:1rem .7rem}.hero{padding:21px}.title{font-size:2rem}.ball{width:42px;height:42px}.card{padding:14px}}
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)

def api_get(url=API):
    if url == API:
        url = f"{API}/_ultimo.json"
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"JARVIS-Mega/3.0"})
    r.raise_for_status()
    return r.json()
@st.cache_data(ttl=600, show_spinner=False)
def latest_draw():
    return api_get()

@st.cache_data(ttl=1800, show_spinner=False)
def load_history(limit=HISTORY_LIMIT):
    data = api_get(f"{API}/_todos.json")
    rows = []

    for d in data:
        nums = d.get("listaDezenas") or d.get("dezenasSorteadasOrdemSorteio")
        if not nums:
            continue

        rows.append({
            "concurso": int(d.get("numero", 0)),
            "data": d.get("dataApuracao", ""),
            "nums": sorted(map(int, nums))
        })

    rows.sort(key=lambda x: x["concurso"], reverse=True)
    return rows


def df_history(hist):
    return pd.DataFrame(hist)

def frequency(hist, window=None):
    h=hist[:window] if window else hist
    c=Counter(n for d in h for n in d["nums"])
    return c

def pair_frequency(hist, window=150):
    c=Counter()
    for d in hist[:window]: c.update(combinations(d["nums"],2))
    return c

def recency_score(hist):
    s={n:0.0 for n in range(1,61)}
    for i,d in enumerate(hist):
        decay=np.exp(-i/70)
        for n in d["nums"]: s[n]+=decay
    return s

def shape_score(ticket):
    odd=sum(n%2 for n in ticket); s=sum(ticket)
    decades=len(set((n-1)//10 for n in ticket))
    score=0
    if odd in (2,3,4): score+=1.4
    if 120<=s<=230: score+=1.4
    if decades>=4: score+=1.0
    if max(ticket)-min(ticket)>=30: score+=.8
    return score

def score_ticket(ticket, freq, pairs, recent, mode="balanced"):
    # Heuristic ranking only; it is not a probability model.
    f=np.mean([freq.get(n,0) for n in ticket])
    r=np.mean([recent.get(n,0) for n in ticket])
    p=np.mean([pairs.get(x,0) for x in combinations(ticket,2)]) if len(ticket)>1 else 0
    sh=shape_score(ticket)
    if mode=="frequency": return .55*f+.15*r+.10*p+.20*sh
    if mode=="recent": return .20*f+.55*r+.10*p+.15*sh
    if mode=="contrarian":
        maxf=max(freq.values()) if freq else 1
        anti=np.mean([1-freq.get(n,0)/maxf for n in ticket])
        return .55*anti+.15*r+.10*p+.20*sh
    return .30*f+.30*r+.18*p+.22*sh

def generate(hist, qty=8, candidates=5000, mode="balanced", seed=42):
    random.seed(seed); np.random.seed(seed)
    freq=frequency(hist); pairs=pair_frequency(hist); recent=recency_score(hist)
    scored=[]
    for _ in range(candidates):
        t=tuple(sorted(random.sample(range(1,61),6)))
        sc=score_ticket(t,freq,pairs,recent,mode)
        scored.append((sc,t))
    scored.sort(reverse=True)
    chosen=[]
    used=set()
    for sc,t in scored:
        if all(len(set(t)&set(x[1]))<=3 for x in chosen) and t not in used:
            chosen.append((sc,t)); used.add(t)
            if len(chosen)>=qty: break
    return chosen

def ticket_html(i,score,t,mode):
    balls=''.join(f'<span class="ball">{n:02d}</span>' for n in t)
    return f'''<div class="ticket"><div class="ticket-head"><span class="mini">MISSÃO {i:02d} · {mode.upper()}</span><span class="tag">SCORE {score:.2f}</span></div><div class="balls">{balls}</div></div>'''

def random_ticket(): return tuple(sorted(random.sample(range(1,61),6)))

def backtest(hist, rounds=40, games=8, mode="balanced", seed=7):
    if len(hist)<rounds+25: return pd.DataFrame()
    rng=random.Random(seed); out=[]
    for i in range(rounds,0,-1):
        train=hist[i:]
        target=set(hist[i-1]["nums"])
        picks=generate(train,games,1200,mode,rng.randint(0,10_000_000))
        hits=[len(set(t)&target) for _,t in picks]
        rand=[len(set(random_ticket())&target) for _ in range(games)]
        out.append({"concurso":hist[i-1]["concurso"],"jarvis_max":max(hits) if hits else 0,"jarvis_media":np.mean(hits) if hits else 0,"aleatorio_max":max(rand) if rand else 0,"aleatorio_media":np.mean(rand) if rand else 0})
    return pd.DataFrame(out)

# ========================= STATE =========================
if "tickets" not in st.session_state: st.session_state.tickets=[]
if "mission_count" not in st.session_state: st.session_state.mission_count=0
if "favorites" not in st.session_state: st.session_state.favorites=[]
if "activity" not in st.session_state: st.session_state.activity=[]
if "refresh_requested" not in st.session_state: st.session_state.refresh_requested=False

refreshing = st.session_state.pop("refresh_requested", False)
try:
    if refreshing:
        # Refresh only the data caches; keep the user's mission/favorites/session intact.
        latest_draw.clear()
        load_history.clear()
        with st.status("🔄 Atualizando inteligência...", expanded=True) as refresh_status:
            st.write("Consultando o último concurso da CAIXA...")
            last=latest_draw()
            st.write("Atualizando o histórico estatístico...")
            hist=load_history()
            refresh_status.update(label="✅ Inteligência atualizada", state="complete", expanded=False)
    else:
        last=latest_draw()
        hist=load_history()
    online=True
except Exception as e:
    online=False; last={}; hist=[]; load_error=str(e)

# ========================= SIDEBAR =========================
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 JARVIS 3.0</div>',unsafe_allow_html=True)
    st.caption("Mega-Sena Intelligence Lab")
    st.markdown('<div class="side-plan"><span class="smallcaps">plano atual</span><br><b>JARVIS PRO</b><br><span class="mini">Acesso ativo</span></div>',unsafe_allow_html=True)
    page=st.radio("Navegação",["⚡ Dashboard","🎯 Gerador","🧠 Radar","🧪 Backtest","🗂️ Histórico"],label_visibility="collapsed")
    st.divider()
    qty=st.slider("Jogos por missão",1,20,8)
    candidates=st.slider("Candidatos analisados",500,12000,5000,500)
    mode=st.selectbox("Estratégia",["balanced","recent","frequency","contrarian"],format_func=lambda x:{"balanced":"Balanceada","recent":"Recência","frequency":"Frequência","contrarian":"Contrarian"}[x])
    seed=st.number_input("Seed",0,999999,42)
    if st.button("↻ Atualizar inteligência",use_container_width=True):
        st.session_state.refresh_requested=True
        st.rerun()
    st.markdown('<div class="warn">⚠️ O JARVIS classifica combinações por heurísticas estatísticas. Não existe garantia de previsão ou aumento das probabilidades matemáticas do sorteio.</div>',unsafe_allow_html=True)

# ========================= HERO =========================
contest=last.get("numero","—") if last else "—"
date=last.get("dataApuracao","—") if last else "—"
st.markdown(f'''<div class="hero"><div class="eyebrow">JARVIS · MEGA-SENA INTELLIGENCE</div><div class="title">MISSION CONTROL</div><div class="sub">Um laboratório experimental para análise estatística, otimização combinatória, diversidade de carteiras e validação fora da amostra.</div><div class="pill"><span class="dot"></span>{'SISTEMA ONLINE' if online else 'MODO OFFLINE'}</div></div>''',unsafe_allow_html=True)

if not online:
    st.error(f"Não consegui acessar os dados da CAIXA agora. Detalhe: {load_error}")
    st.stop()

# ========================= DASHBOARD =========================
freq=frequency(hist); recent=frequency(hist,60)
if page=="⚡ Dashboard":
    cols=st.columns(4)
    vals=[("ÚLTIMO CONCURSO",contest,"cyan"),("HISTÓRICO CARREGADO",len(hist),"purple"),("DEZENAS ANALISADAS",60,"green"),("MISSÕES NESTA SESSÃO",st.session_state.mission_count,"cyan")]
    for c,(lab,val,cl) in zip(cols,vals): c.markdown(f'<div class="card"><div class="label">{lab}</div><div class="value {cl}">{val}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">Painel de comando</div><div class="section-sub">Concurso mais recente carregado e estado atual do laboratório.</div>',unsafe_allow_html=True)
    c1,c2=st.columns([1.2,.8])
    with c1:
        st.markdown(f'<div class="mission"><h3>🚀 PRÓXIMA MISSÃO</h3><div class="mini">Último concurso conhecido: <b>{contest}</b> · {date}</div><br>Execute uma nova geração para criar uma carteira diversificada com a estratégia selecionada.</div>',unsafe_allow_html=True)
        if st.button("INICIAR MISSÃO",use_container_width=True):
            st.session_state.tickets=generate(hist,qty,candidates,mode,seed+st.session_state.mission_count)
            st.session_state.mission_count+=1
            st.session_state.activity.append((time.strftime("%H:%M:%S"),f"Missão #{st.session_state.mission_count} · {mode}"))
            st.rerun()
    with c2:
        top=sorted(freq.items(),key=lambda x:x[1],reverse=True)[:6]
        st.markdown('<div class="card"><div class="label">TOP 6 · HISTÓRICO</div>',unsafe_allow_html=True)
        for n,v in top: st.progress(min(v/max(freq.values()),1.0),text=f"Dezena {n:02d} · {v} ocorrências")
        st.markdown('</div>',unsafe_allow_html=True)
    if st.session_state.tickets:
        st.markdown('<div class="section">Última carteira</div>',unsafe_allow_html=True)
        for i,(sc,t) in enumerate(st.session_state.tickets,1): st.markdown(ticket_html(i,sc,t,mode),unsafe_allow_html=True)

# ========================= GENERATOR =========================
elif page=="🎯 Gerador":
    st.markdown('<div class="section">Gerador de missão</div><div class="section-sub">O motor cria muitos candidatos e seleciona combinações com score heurístico + diversidade.</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a: st.metric("Estratégia",{"balanced":"Balanceada","recent":"Recência","frequency":"Frequência","contrarian":"Contrarian"}[mode])
    with b: st.metric("Candidatos",f"{candidates:,}")
    with c: st.metric("Jogos",qty)
    if st.button("⚡ GERAR CARTEIRA",use_container_width=True):
        with st.spinner("JARVIS calculando espaço de combinações..."):
            st.session_state.tickets=generate(hist,qty,candidates,mode,seed+st.session_state.mission_count)
            st.session_state.mission_count+=1
            st.session_state.activity.append((time.strftime("%H:%M:%S"),f"Geração #{st.session_state.mission_count} · {mode}"))
        st.success("Carteira gerada.")
    if st.session_state.tickets:
        rows=[]
        for i,(sc,t) in enumerate(st.session_state.tickets,1):
            st.markdown(ticket_html(i,sc,t,mode),unsafe_allow_html=True)
            if st.button(f"☆ Favoritar missão {i}",key=f"fav{i}"):
                if t not in st.session_state.favorites: st.session_state.favorites.append(t)
        rows.append({"jogo":i,"numeros":" ".join(f"{n:02d}" for n in t),"score":round(sc,4)})
        if rows:
            csv=pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar carteira CSV",csv,"jarvis_carteira.csv","text/csv",use_container_width=True)
    else: st.info("Clique em GERAR CARTEIRA para iniciar.")

# ========================= RADAR =========================
elif page=="🧠 Radar":
    st.markdown('<div class="section">Radar estatístico</div><div class="section-sub">Frequência, recência, soma e formato dos concursos observados. Descritivo, não preditivo.</div>',unsafe_allow_html=True)
    fdf=pd.DataFrame({"dezena":range(1,61),"histórico":[freq.get(n,0) for n in range(1,61)],"últimos_60":[recent.get(n,0) for n in range(1,61)]})
    st.bar_chart(fdf.set_index("dezena")[["histórico","últimos_60"]],height=360)
    sums=[sum(d["nums"]) for d in hist]
    odds=[sum(n%2 for n in d["nums"]) for d in hist]
    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="card"><div class="label">SOMA MÉDIA</div><div class="value cyan">{np.mean(sums):.1f}</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="label">SOMA MEDIANA</div><div class="value purple">{np.median(sums):.1f}</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><div class="label">MÉDIA DE ÍMPARES</div><div class="value green">{np.mean(odds):.2f}</div></div>',unsafe_allow_html=True)
    st.dataframe(fdf.sort_values("histórico",ascending=False).head(20),use_container_width=True,hide_index=True)

# ========================= BACKTEST =========================
elif page=="🧪 Backtest":
    st.markdown('<div class="section">Laboratório de validação</div><div class="section-sub">Walk-forward: o JARVIS só usa dados anteriores ao concurso testado. O comparativo aleatório é uma referência, não uma prova de previsão.</div>',unsafe_allow_html=True)
    r=st.slider("Rodadas históricas",10,80,30)
    g=st.slider("Jogos por rodada",2,15,6)
    if st.button("🧪 EXECUTAR BACKTEST",use_container_width=True):
        with st.spinner("Executando validação fora da amostra..."):
            bt=backtest(hist,r,g,mode,int(seed))
        st.session_state.backtest=bt
    bt=st.session_state.get("backtest")
    if bt is not None and len(bt):
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Rodadas",len(bt));m2.metric("Máx JARVIS",f"{bt.jarvis_max.mean():.2f}");m3.metric("Máx aleatório",f"{bt.aleatorio_max.mean():.2f}");m4.metric("≥4 acertos",int((bt.jarvis_max>=4).sum()))
        st.line_chart(bt.set_index("concurso")[["jarvis_max","aleatorio_max"]])
        st.dataframe(bt,use_container_width=True,hide_index=True)
        st.caption("Resultados históricos não garantem comportamento futuro. A validação serve para medir a heurística contra uma referência aleatória.")
    else: st.info("Execute o backtest para medir o comportamento histórico.")

# ========================= HISTORY =========================
elif page=="🗂️ Histórico":
    st.markdown('<div class="section">Memória do sistema</div><div class="section-sub">Últimos concursos usados pelo laboratório e atividades desta sessão.</div>',unsafe_allow_html=True)
    hdf=pd.DataFrame([{"concurso":d["concurso"],"data":d["data"],"dezenas":" - ".join(f"{n:02d}" for n in d["nums"]),"soma":sum(d["nums"])} for d in hist])
    st.dataframe(hdf.head(100),use_container_width=True,hide_index=True)
    st.markdown('<div class="section">Atividade da sessão</div>',unsafe_allow_html=True)
    if st.session_state.activity:
        for t,a in reversed(st.session_state.activity[-15:]): st.markdown(f'<div class="card" style="margin:6px 0;padding:11px"><span class="mini">{t}</span> · {a}</div>',unsafe_allow_html=True)
    else: st.info("Nenhuma missão executada ainda.")
    st.markdown('<div class="section">Favoritos</div>',unsafe_allow_html=True)
    if st.session_state.favorites:
        for t in st.session_state.favorites: st.markdown(ticket_html(0,0,t,"favorito"),unsafe_allow_html=True)
    else: st.info("Você ainda não favoritou nenhum jogo.")

st.markdown('<div style="text-align:center;color:#536b7e;font-size:.72rem;margin:32px 0 8px">JARVIS 3.0 · laboratório experimental · dados públicos da CAIXA · sem promessa de prêmio</div>',unsafe_allow_html=True)
