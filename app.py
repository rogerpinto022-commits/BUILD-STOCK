import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import os

st.set_page_config(page_title="Controle Duplo", layout="wide")
fuso = pytz.timezone('America/Sao_Paulo')

ARQ_DADOS = "dados.csv"
ARQ_MOV = "mov.csv"
ARQ_EMAILS = "emails.csv"

def init():
    if not os.path.exists(ARQ_EMAILS):
        pd.DataFrame([{"EMAIL":"admin@admin.com","SENHA":"admin","LOCAL":"AMBOS","ENTRADA":True,"SAIDA":True,"GRAFICO":True,"STATUS":"LIBERADO","PERFIL":"ADMINISTRADOR"}]).to_csv(ARQ_EMAILS, index=False)
    if not os.path.exists(ARQ_DADOS):
        pd.DataFrame([
            {"ID":15,"NOME":"BLOCOS","LOCAL":"SALA ANEXA","SALDO":0},
            {"ID":16,"NOME":"BARRAS","LOCAL":"SALA ANEXA","SALDO":0},
            {"ID":15,"NOME":"BLOCOS","LOCAL":"BARRACÃO","SALDO":0},
            {"ID":16,"NOME":"BARRAS","LOCAL":"BARRACÃO","SALDO":0},
        ]).to_csv(ARQ_DADOS, index=False)
    if not os.path.exists(ARQ_MOV):
        pd.DataFrame(columns=["DATA","ID","NOME","LOCAL","TIPO","QTD","USUARIO","OBS"]).to_csv(ARQ_MOV, index=False)

init()

def salvar():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Controle Duplo - Login")
    email = st.text_input("Email").lower().strip()
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary"):
        df_e = pd.read_csv(ARQ_EMAILS)
        user = df_e[(df_e["EMAIL"]==email) & (df_e["SENHA"]==senha) & (df_e["STATUS"]=="LIBERADO")]
        if not user.empty:
            st.session_state.logado=True
            st.session_state.usuario=email
            st.session_state.perfil=user.iloc[0]["PERFIL"]
            st.session_state.local_acesso=user.iloc[0]["LOCAL"]
            st.session_state.perm_entrada=bool(user.iloc[0]["ENTRADA"])
            st.session_state.perm_saida=bool(user.iloc[0]["SAIDA"])
            st.session_state.perm_grafico=bool(user.iloc[0]["GRAFICO"])
            st.session_state.dados=pd.read_csv(ARQ_DADOS).to_dict('records')
            try:
                st.session_state.mov=pd.read_csv(ARQ_MOV).to_dict('records')
            except:
                st.session_state.mov=[]
            st.rerun()
        else:
            st.error("Login inválido")
    st.stop()

agora_br = datetime.now(fuso)

# --- ADMIN ---
if st.session_state.perfil=="ADMINISTRADOR":
    with st.sidebar.expander("🔑 ADMIN - CONTROLE TOTAL", expanded=False):
        st.write("Cadastrar acesso")
        ne = st.text_input("Email").lower().strip()
        ns = st.text_input("Senha", type="password")
        loc = st.selectbox("Local", ["SALA ANEXA","BARRACÃO","AMBOS"])
        c1,c2,c3=st.columns(3)
        pe=c1.checkbox("ENTRADA",True)
        ps=c2.checkbox("SAIDA",True)
        pg=c3.checkbox("GRAFICOS",True)
        if st.button("Cadastrar"):
            if "@" in ne and ns:
                df_e=pd.read_csv(ARQ_EMAILS)
                df_e=df_e[~((df_e["EMAIL"]==ne)&(df_e["LOCAL"]==loc))]
                df_e=pd.concat([df_e,pd.DataFrame([{"EMAIL":ne,"SENHA":ns,"LOCAL":loc,"ENTRADA":pe,"SAIDA":ps,"GRAFICO":pg,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}])],ignore_index=True)
                df_e.to_csv(ARQ_EMAILS,index=False)
                st.success("Liberado"); st.rerun()

        st.divider()
        st.write("Cadastrar novo material - SÓ VOCÊ")
        nid=st.number_input("ID novo",min_value=1,step=1)
        nnome=st.text_input("Nome material").upper()
        if st.button("Cadastrar material"):
            if nnome:
                df_d=pd.read_csv(ARQ_DADOS)
                if nid not in df_d["ID"].values:
                    novos=[{"ID":nid,"NOME":nnome,"LOCAL":"SALA ANEXA","SALDO":0},{"ID":nid,"NOME":nnome,"LOCAL":"BARRACÃO","SALDO":0}]
                    df_d=pd.concat([df_d,pd.DataFrame(novos)],ignore_index=True)
                    df_d.to_csv(ARQ_DADOS,index=False)
                    st.session_state.dados=df_d.to_dict('records')
                    st.success(f"{nnome} cadastrado"); st.rerun()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear(); st.rerun()

# --- DADOS ---
df_estoque = pd.DataFrame(st.session_state.dados)
pode_anexa = st.session_state.local_acesso in ["SALA ANEXA","AMBOS"]
pode_barracao = st.session_state.local_acesso in ["BARRACÃO","AMBOS"]

st.title(f"📦 {st.session_state.local_acesso} | {agora_br.strftime('%d/%m/%Y %H:%M')} Brasília - Mogi das Cruzes")

# SALDOS
pivot = df_estoque.pivot_table(index=["ID","NOME"], columns="LOCAL", values="SALDO", aggfunc="sum", fill_value=0).reset_index()
if "BARRACÃO" not in pivot.columns: pivot["BARRACÃO"]=0
if "SALA ANEXA" not in pivot.columns: pivot["SALA ANEXA"]=0
pivot["TOTAL GERAL"] = pivot["BARRACÃO"] + pivot["SALA ANEXA"]

st.dataframe(pivot, use_container_width=True)

c1,c2,c3 = st.columns(3)
if pode_anexa:
    if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True): st.session_state.tela="ANEXA"
if pode_barracao:
    if c2.button("🏚️ BARRACÃO", use_container_width=True): st.session_state.tela="BARRACAO"
if st.session_state.perm_grafico:
    if c3.button("📊 GRÁFICOS", use_container_width=True): st.session_state.tela="GRAFICOS"

if "tela" not in st.session_state: st.session_state.tela="ANEXA" if pode_anexa else "BARRACAO"
st.divider()

# --- LÓGICA AUTOMÁTICA QUE VOCÊ PEDIU ---
def lancar(id_sel, qtd, local_sel, tipo_sel):
    agora = datetime.now(fuso)
    nome = next(d["NOME"] for d in st.session_state.dados if d["ID"]==id_sel)

    idx_anexa = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]=="SALA ANEXA"),None)
    idx_barracao = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]=="BARRACÃO"),None)

    obs=""

    if local_sel=="SALA ANEXA" and tipo_sel=="Entrada":
        # AUTOMÁTICO: Sai do Barracão e entra na Sala - TOTAL NÃO MUDA
        st.session_state.dados[idx_barracao]["SALDO"] -= qtd
        st.session_state.dados[idx_anexa]["SALDO"] += qtd
        obs = f"TRANSFERÊNCIA AUTO: Barracão -> Sala Anexa | Total Geral não muda"

    elif local_sel=="BARRACÃO" and tipo_sel=="Saída":
        # AUTOMÁTICO: Sai do Barracão e entra na Sala - TOTAL NÃO MUDA (mesma coisa ao contrário)
        st.session_state.dados[idx_barracao]["SALDO"] -= qtd
        st.session_state.dados[idx_anexa]["SALDO"] += qtd
        obs = f"TRANSFERÊNCIA AUTO: Barracão -> Sala Anexa | Total Geral não muda"

    elif local_sel=="SALA ANEXA" and tipo_sel=="Saída":
        # VENDA REAL: Sai da Sala e desconta do TOTAL GERAL
        st.session_state.dados[idx_anexa]["SALDO"] -= qtd
        obs = f"SAÍDA REAL: Descontou da Sala e do TOTAL GERAL"

    elif local_sel=="BARRACÃO" and tipo_sel=="Entrada":
        # COMPRA REAL: Entra no Barracão e aumenta TOTAL GERAL
        st.session_state.dados[idx_barracao]["SALDO"] += qtd
        obs = f"ENTRADA REAL: Compra - Aumentou Barracão e TOTAL GERAL"

    st.session_state.mov.append({"DATA":agora, "ID":id_sel, "NOME":nome, "LOCAL":local_sel, "TIPO":tipo_sel, "QTD":qtd, "USUARIO":st.session_state.usuario, "OBS":obs})
    salvar()

if st.session_state.tela=="ANEXA" and pode_anexa:
    st.subheader("📦 SALA ANEXA")
    ids = df_estoque[df_estoque["LOCAL"]=="SALA ANEXA"]["ID"].unique()
    nomes = {r["ID"]:r["NOME"] for r in st.session_state.dados if r["LOCAL"]=="SALA ANEXA"}
    id_e = st.selectbox("Material", ids, format_func=lambda x: f"{x} - {nomes[x]}")
    qtd = st.number_input("Qtd", value=1.0, min_value=0.1)
    col1,col2=st.columns(2)
    if st.session_state.perm_entrada and col1.button("✅ ENTRADA na ANEXA (vem do Barracão) - AUTO", type="primary", use_container_width=True):
        lancar(id_e, qtd, "SALA ANEXA", "Entrada"); st.success("Transferência feita! Barracão diminuiu, Anexa aumentou. Total igual."); st.rerun()
    if st.session_state.perm_saida and col2.button("✅ SAÍDA da ANEXA (venda real) - Desconta TOTAL", use_container_width=True):
        lancar(id_e, qtd, "SALA ANEXA", "Saída"); st.warning("Saída real! Descontou da Anexa e do TOTAL GERAL"); st.rerun()

elif st.session_state.tela=="BARRACAO" and pode_barracao:
    st.subheader("🏚️ BARRACÃO")
    ids = df_estoque[df_estoque["LOCAL"]=="BARRACÃO"]["ID"].unique()
    nomes = {r["ID"]:r["NOME"] for r in st.session_state.dados if r["LOCAL"]=="BARRACÃO"}
    id_e = st.selectbox("Material", ids, key="b", format_func=lambda x: f"{x} - {nomes[x]}")
    qtd = st.number_input("Qtd", value=1.0, min_value=0.1, key="qb")
    col1,col2=st.columns(2)
    if st.session_state.perm_entrada and col1.button("✅ ENTRADA no BARRACÃO (compra real) - Aumenta TOTAL", type="primary", use_container_width=True):
        lancar(id_e, qtd, "BARRACÃO", "Entrada"); st.success("Compra! Aumentou Barracão e TOTAL GERAL"); st.rerun()
    if st.session_state.perm_saida and col2.button("✅ SAÍDA do BARRACÃO (vai pra Anexa) - AUTO", use_container_width=True):
        lancar(id_e, qtd, "BARRACÃO", "Saída"); st.success("Transferência! Barracão -> Anexa"); st.rerun()

else: # GRAFICOS
    if st.session_state.perm_grafico:
        st.subheader("📊 Gráficos - Horário Brasília")

        # Grafico estoque barra vs sala
        fig1 = px.bar(pivot, x="NOME", y=["BARRACÃO","SALA ANEXA"], barmode="group", title="Estoque: Barracão vs Sala Anexa")
        st.plotly_chart(fig1, use_container_width=True)

        # Pizza total geral
        fig_pizza = px.pie(pivot, values="TOTAL GERAL", names="NOME", title="Pizza - TOTAL GERAL (Barracão + Sala)")
        st.plotly_chart(fig_pizza, use_container_width=True)

        # Mensal, Semestral, Anual
        if st.session_state.mov:
            df_mov = pd.DataFrame(st.session_state.mov)
            df_mov["DATA"] = pd.to_datetime(df_mov["DATA"])
            df_mov["MES"] = df_mov["DATA"].dt.to_period("M").astype(str)
            df_mov["SEMESTRE"] = df_mov["DATA"].dt.year.astype(str) + "-S" + ((df_mov["DATA"].dt.month-1)//6+1).astype(str)
            df_mov["ANO"] = df_mov["DATA"].dt.year.astype(str)

            c1,c2,c3 = st.columns(3)
            with c1:
                mensal = df_mov.groupby(["MES","TIPO"])["QTD"].sum().reset_index()
                fig_m = px.bar(mensal, x="MES", y="QTD", color="TIPO", barmode="group", title="Mensal - Entrada x Saída")
                st.plotly_chart(fig_m, use_container_width=True)
            with c2:
                sem = df_mov.groupby(["SEMESTRE","TIPO"])["QTD"].sum().reset_index()
                fig_s = px.bar(sem, x="SEMESTRE", y="QTD", color="TIPO", barmode="group", title="Semestral")
                st.plotly_chart(fig_s, use_container_width=True)
            with c3:
                anual = df_mov.groupby(["ANO","TIPO"])["QTD"].sum().reset_index()
                fig_a = px.bar(anual, x="ANO", y="QTD", color="TIPO", barmode="group", title="Anual")
                st.plotly_chart(fig_a, use_container_width=True)

            st.divider()
            st.subheader("📋 Histórico com hora de Brasília")
            st.dataframe(df_mov.sort_values("DATA", ascending=False), use_container_width=True)

            st.subheader("🗑️ Excluir registro - Reverte saldo automaticamente")
            if not df_mov.empty:
                idx = st.number_input("Índice para excluir (0 é o primeiro)", min_value=0, max_value=len(st.session_state.mov)-1, value=len(st.session_state.mov)-1)
                if st.button("🗑️ EXCLUIR E REVERTER"):
                    mov = st.session_state.mov[idx]
                    # Reverte lógica
                    idx_an = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==mov["ID"] and d["LOCAL"]=="SALA ANEXA"),None)
                    idx_ba = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==mov["ID"] and d["LOCAL"]=="BARRACÃO"),None)

                    if "TRANSFERÊNCIA" in mov["OBS"]:
                        # Desfaz transferência
                        st.session_state.dados[idx_ba]["SALDO"] += mov["QTD"]
                        st.session_state.dados[idx_an]["SALDO"] -= mov["QTD"]
                    elif "SAÍDA REAL" in mov["OBS"]:
                        st.session_state.dados[idx_an]["SALDO"] += mov["QTD"]
                    elif "ENTRADA REAL" in mov["OBS"]:
                        st.session_state.dados[idx_ba]["SALDO"] -= mov["QTD"]

                    del st.session_state.mov[idx]
                    salvar()
                    st.success("Excluído e revertido!"); st.rerun()
