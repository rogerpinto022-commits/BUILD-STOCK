import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE CADA ITEM É 1")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"operador@empresa.com", "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
    ]).to_csv(ARQ_EMAILS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records') if os.path.exists(ARQ_DADOS) else [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    if os.path.exists(ARQ_MOV):
        df_t = pd.read_csv(ARQ_MOV)
        df_t['DATA'] = pd.to_datetime(df_t['DATA'])
        st.session_state.mov = df_t.to_dict('records')
    else:
        st.session_state.mov = []

def salvar():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)
    st.toast("✅ SALVO")

# LOGIN MESMO PARA TUDO
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 MESMO LOGIN E SENHA")
    with st.container(border=True):
        email = st.text_input("EMAIL").lower().strip()
        senha = st.text_input("SENHA", type="password")
        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_e = pd.read_csv(ARQ_EMAILS)
            if email == "admin@empresa.com" and senha == "admin123":
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = "ADMINISTRADOR"
                st.rerun()
            acesso = df_e[(df_e["EMAIL"]==email) & (df_e["STATUS"]=="LIBERADO")]
            if not acesso.empty and senha == "123":
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = acesso.iloc[0]["PERFIL"]
                st.rerun()
            else:
                st.error("Não liberado ou bloqueado")
    st.stop()

st.sidebar.markdown(f"👤 {st.session_state.usuario}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

if st.session_state.perfil == "ADMINISTRADOR":
    with st.sidebar.expander("📧 LIBERAR/BLOQUEAR - MESMO LOGIN"):
        novo = st.text_input("Email").lower().strip()
        if st.button("✅ LIBERAR MESMO LOGIN", type="primary"):
            df_e = pd.read_csv(ARQ_EMAILS)
            if novo not in df_e["EMAIL"].values and "@" in novo:
                df_e = pd.concat([df_e, pd.DataFrame([{"EMAIL":novo,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}])], ignore_index=True)
            else:
                df_e.loc[df_e["EMAIL"]==novo, "STATUS"]="LIBERADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()
        df_e = pd.read_csv(ARQ_EMAILS)
        st.dataframe(df_e, hide_index=True, use_container_width=True)
        sel = st.selectbox("Bloquear", df_e["EMAIL"].tolist())
        c1,c2 = st.columns(2)
        if c1.button("🚫 BLOQUEAR"):
            df_e.loc[df_e["EMAIL"]==sel, "STATUS"]="BLOQUEADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()
        if c2.button("✅ LIBERAR"):
            df_e.loc[df_e["EMAIL"]==sel, "STATUS"]="LIBERADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()
    st.sidebar.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

# CALCULOS - CADA ITEM É 1 - NÃO SOMA
df = pd.DataFrame(st.session_state.dados)
# SALA ANEXA - CADA UM SEPARADO
blocos_anexa = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==15)]["SALDO"].sum()
barras_anexa = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==16)]["SALDO"].sum()
# BARRACÃO - CADA UM SEPARADO - ZERADO
blocos_bar = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==15)]["SALDO"].sum()
barras_bar = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==16)]["SALDO"].sum()

st.title("🗄️ CADA ITEM É 1 - NÃO SOMA")
st.markdown(f"**ID 15 BLOCOS = 1 item | ID 16 BARRAS = 1 item** | Logado: {st.session_state.usuario} - MESMO LOGIN")

c1,c2,c3 = st.columns(3)
if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
    st.session_state.tela = "ANEXA"
if c2.button("🏚️ BARRACÃO", use_container_width=True):
    st.session_state.tela = "BARRACAO"
if c3.button("📊 GRÁFICOS SEPARADOS", use_container_width=True):
    st.session_state.tela = "CONSULTA"
if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA"

st.divider()

if st.session_state.tela == "ANEXA":
    st.subheader("📦 SALA ANEXA - CADA ITEM É 1")
    if st.button("👁️ VER INFORMAÇÕES"):
        st.session_state.ver_a = not st.session_state.get('ver_a', False)
    if st.session_state.get('ver_a', False):
        c1,c2 = st.columns(2)
        c1.metric("ID 15 - BLOCOS DE FUNDO", f"{blocos_anexa:.0f} UNIDADES", "CADA UM É 1")
        c2.metric("ID 16 - BARRAS CATODICAS", f"{barras_anexa:.0f} UNIDADES", "CADA UM É 1")
        st.info(f"BLOCOS {blocos_anexa:.0f} + BARRAS {barras_anexa:.0f} = {blocos_anexa+barras_anexa:.0f} itens no total, mas cada um é 1 separado")

    op = st.radio("Ação:", ["NOVA ENTRADA","NOVA SAIDA","SALVAR ENTRADA E SAIDA"], horizontal=True)
    if op == "NOVA ENTRADA":
        id_e = st.selectbox("Qual item? Cada um é 1", [15,16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO (1 item = 1 unidade)' if x==15 else 'BARRAS CATODICAS (1 item = 1 unidade)'}")
        qtd = st.number_input("Quantas unidades? (cada 1 = 1 item)", value=1.0, min_value=1.0)
        if st.button("✅ SALVAR ENTRADA - CADA ITEM É 1", type="primary"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_e, "LOCAL":"SALA ANEXA", "QTD":qtd})
            salvar()
            st.rerun()
    elif op == "NOVA SAIDA":
        id_s = st.selectbox("Qual item?", [15,16], key="sai_a", format_func=lambda x: f"ID {x} - {'BLOCOS' if x==15 else 'BARRAS'}")
        qtd = st.number_input("Qtd", value=1.0, key="qtd_a")
        if st.button("✅ SALVAR SAIDA - CADA ITEM É 1"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_s and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_s, "LOCAL":"SALA ANEXA", "QTD":qtd})
            salvar()
            st.rerun()
    else:
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

elif st.session_state.tela == "BARRACAO":
    st.subheader("🏚️ BARRACÃO - CADA ITEM É 1 - ZERADO")
    if st.button("👁️ VER BARRACÃO"):
        st.session_state.ver_b = not st.session_state.get('ver_b', False)
    if st.session_state.get('ver_b', False):
        c1,c2 = st.columns(2)
        c1.metric("ID 15 - BLOCOS BARRACÃO", f"{blocos_bar:.0f} UNIDADES", "ZERADO - CADA 1 É 1")
        c2.metric("ID 16 - BARRAS BARRACÃO", f"{barras_bar:.0f} UNIDADES", "ZERADO - CADA 1 É 1")

    op = st.radio("Ação:", ["NOVA ENTRADA","NOVA SAIDA","SALVAR"], horizontal=True, key="op_b")
    if op == "NOVA ENTRADA":
        id_e = st.selectbox("ID", [15,16], key="ent_b", format_func=lambda x: f"ID {x} - {'BLOCOS (cada 1 é 1)' if x==15 else 'BARRAS (cada 1 é 1)'}")
        qtd = st.number_input("Qtd", value=1.0, key="qtd_b")
        if st.button("✅ SALVAR ENTRADA BARRACÃO", type="primary"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_e, "LOCAL":"BARRACÃO", "QTD":qtd})
            salvar()
            st.rerun()

else:
    st.subheader("📊 GRÁFICOS - CADA ITEM É 1 - NÃO SOMA")
    if st.button("👁️ MOSTRAR GRÁFICOS SEPARADOS", type="primary"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📦 SALA ANEXA - CADA ITEM É 1")
            st.metric("BLOCOS ID 15", f"{blocos_anexa:.0f} unidades")
            st.metric("BARRAS ID 16", f"{barras_anexa:.0f} unidades")
            # GRÁFICO SEPARADO - NÃO SOMA
            df_graf_a = pd.DataFrame([
                {"ITEM":"ID 15 BLOCOS (cada 1 é 1)", "QTD":blocos_anexa},
                {"ITEM":"ID 16 BARRAS (cada 1 é 1)", "QTD":barras_anexa},
            ])
            st.bar_chart(df_graf_a.set_index("ITEM"))

        with col2:
            st.markdown("### 🏚️ BARRACÃO - CADA ITEM É 1 - ZERADO")
            st.metric("BLOCOS ID 15", f"{blocos_bar:.0f} unidades")
            st.metric("BARRAS ID 16", f"{barras_bar:.0f} unidades")
            df_graf_b = pd.DataFrame([
                {"ITEM":"ID 15 BLOCOS (cada 1 é 1)", "QTD":blocos_bar},
                {"ITEM":"ID 16 BARRAS (cada 1 é 1)", "QTD":barras_bar},
            ])
            st.bar_chart(df_graf_b.set_index("ITEM"))

        st.divider()
        st.markdown("### COMPARATIVO - CADA ITEM SEPARADO")
        df_comp = pd.DataFrame([
            {"LOCAL":"ANEXA BLOCOS ID15", "QTD":blocos_anexa},
            {"LOCAL":"ANEXA BARRAS ID16", "QTD":barras_anexa},
            {"LOCAL":"BARRACÃO BLOCOS ID15", "QTD":blocos_bar},
            {"LOCAL":"BARRACÃO BARRAS ID16", "QTD":barras_bar},
        ])
        st.bar_chart(df_comp.set_index("LOCAL"))
   
