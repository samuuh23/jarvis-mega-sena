
import streamlit as st
import requests, itertools, random, statistics
from collections import Counter

st.set_page_config(page_title="JARVIS Mega-Sena", page_icon="🤖", layout="wide")

API = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"

@st.cache_data(ttl=3600)
def load_history():
    latest = requests.get(API, headers={"User-Agent":"Mozilla/5.0"}, timeout=20).json()
    last = int(latest["numero"])
    draws = []
    # Limit is deliberately generous; cache keeps later runs fast.
    for n in range(1, last + 1):
        try:
            d = requests.get(f"{API}/{n}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
            nums = tuple(sorted(int(x) for x in d["listaDezenas"]))
            if len(nums) == 6 and len(set(nums)) == 6:
                draws.append(nums)
        except Exception:
            pass
    return draws

def freq(draws):
    c = Counter(x for d in draws for x in d)
    return {n:c[n] for n in range(1,61)}

def score_numbers(draws, window):
    recent = draws[-min(window,len(draws)):]
    a, b = freq(recent), freq(draws)
    def norm(vals):
        lo, hi = min(vals), max(vals)
        return [0.5]*len(vals) if lo==hi else [(x-lo)/(hi-lo) for x in vals]
    ar, bl = norm([a[n] for n in range(1,61)]), norm([b[n] for n in range(1,61)])
    return {n:.7*ar[n-1]+.3*bl[n-1] for n in range(1,61)}

def generate(draws, amount, candidates, seed):
    rng=random.Random(seed)
    ns=score_numbers(draws, 150)
    recent=draws[-min(300,len(draws)):]
    target=statistics.mean(sum(d) for d in recent)
    pool=[]
    for _ in range(candidates):
        t=tuple(sorted(rng.sample(range(1,61),6)))
        ev=sum(x%2==0 for x in t)
        decades=len({(x-1)//10 for x in t})
        shape=(0 if ev in (2,3,4) else .06)+(0 if decades>=4 else .05)
        s=sum(ns[x] for x in t)/6 - shape - min(abs(sum(t)-target)/1000,.05)
        pool.append((s,t))
    pool.sort(reverse=True)
    chosen=[]
    for s,t in pool:
        if all(len(set(t)&set(old))/6 < .67 for _,old in chosen):
            chosen.append((s,t))
        if len(chosen)>=amount: break
    return chosen

st.title("🤖 JARVIS — Mega-Sena AI")
st.caption("Laboratório estatístico e combinatório • não é um previsor garantido")

with st.sidebar:
    st.header("⚙️ Configuração")
    amount=st.slider("Quantidade de jogos",1,100,10)
    candidates=st.slider("Combinações candidatas",1000,100000,20000,1000)
    seed=st.number_input("Seed",0,999999,2026)
    refresh=st.button("🔄 Atualizar histórico")

if refresh:
    load_history.clear()

try:
    draws=load_history()
except Exception as e:
    st.error(f"Não consegui acessar a API da CAIXA agora: {e}")
    st.stop()

c1,c2,c3=st.columns(3)
c1.metric("Concursos analisados",len(draws))
c2.metric("Primeiro concurso","—" if not draws else "1")
c3.metric("Último concurso",f"{len(draws):,}".replace(",","."))

st.divider()

tab1,tab2,tab3=st.tabs(["🎯 Gerador","📊 Estatísticas","🧪 Validação"])

with tab1:
    st.subheader("Carteira experimental")
    st.info("O score serve para ordenar combinações. Ele não representa a probabilidade real de uma dezena sair.")
    if st.button("🚀 Gerar jogos", type="primary"):
        result=generate(draws,amount,candidates,seed)
        for i,(s,t) in enumerate(result,1):
            st.code(f"{i:02d}   {'  '.join(f'{x:02d}' for x in t)}    score={s:.4f}")

with tab2:
    f=freq(draws)
    rows=sorted(f.items(),key=lambda x:(-x[1],x[0]))
    st.subheader("Frequência histórica")
    st.dataframe([{"Dezena":n,"Ocorrências":v} for n,v in rows], use_container_width=True, hide_index=True)
    sums=[sum(d) for d in draws]
    st.write(f"Soma média das dezenas: **{statistics.mean(sums):.2f}**")
    st.write(f"Desvio-padrão populacional da soma: **{statistics.pstdev(sums):.2f}**")

with tab3:
    st.subheader("Princípio científico")
    st.write("O JARVIS deve ser comparado com estratégias aleatórias em períodos que ele não viu. Padrões encontrados apenas no passado podem ser sobreajuste.")
    st.warning("Esta versão apresenta o painel de validação conceitual; o backtest completo da v0.1 continua disponível no pacote anterior.")

st.divider()
st.caption("Mega-Sena: 6 números entre 01 e 60. Nenhum método estatístico garante previsão de sorteios aleatórios.")
