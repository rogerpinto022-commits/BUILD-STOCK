import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE - ADMIN CONTROLE TOTAL")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

# PROTEÇÃO CONTRA KeyError - SEMPRE VERIFICA COLUNAS
def verifica_emails():
    if not os.path.exists(ARQ_EMAILS):
        return False
    try:
        df = pd.read_csv(ARQ_EMAILS)
        colunas_ok = ["EMAIL","SENHA","LOCAL","ENTRADA","SAIDA","GRAFICO","STATUS","PERFIL"]
        for c in colunas_ok:
            if c not in df.columns:
                return False
        return True
    except:
        return False

if not verifica_emails():
    if os.path.exists(ARQ_EMAILS):
        os.remove(ARQ_EMAILS)
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "SENHA":"admin123", "LOCAL":"AMBOS", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"anexa@empresa.com", "SENHA":"anexa123", "LOCAL":"SALA ANEXA", "ENTRADA":True, "SAIDA":False, "GRAFICO":False, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
        {"EMAIL":"barracao@empresa.com", "SENHA":"barracao123", "LOCAL":"BARRACÃO", "ENTRADA":True, "SAIDA":True, "GRAFICO":False, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
    ]).to_csv(ARQ_EMAILS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records') if os.path.exists(ARQ_DADOS) else [
        {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = pd.read_csv(ARQ_MOV).to_dict('records') if os.path.exists(ARQ_MOV) else []

def salvar():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)
    st.toast("✅ SALVO")

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 SÓ QUEM ADMIN CADASTRAR E ENVIAR O LINK ACESSA")
    with st.container(border=True):
        email = st.text_input("EMAIL CADASTRADO PELO ADMIN").lower().strip()
        senha = st.text_input("SENHA INDIVIDUAL", type="password")
        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_e = pd.read_csv(ARQ_EMAILS)
            user = df_e[(df_e["EMAIL"]==email) & (df_e["SENHA"]==senha) & (df_e["STATUS"]=="LIBERADO")]
            if not user.empty:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = user.iloc[0]["PERFIL"]
                st.session_state.local_acesso = user.iloc[0]["LOCAL"]
                st.session_state.perm_entrada = bool(user.iloc[0]["ENTRADA"])
                st.session_state.perm_saida = bool(user.iloc[0]["SAIDA"])
                st.session_state.perm_grafico = bool(user.iloc[0]["GRAFICO"])
                st.rerun()
            else:
                st.error("❌ NÃO CADASTRADO OU BLOQUEADO PELO ADMIN - Mesmo com o link não entra")
    st.info("ADMIN: admin@empresa.com / admin123")
    st.stop()

# LOGADO
st.sidebar.markdown(f"👤 **{st.session_state.usuario}**\n📍 {st.session_state.local_acesso}\n✅ ENTRADA:{st.session_state.perm_entrada} SAIDA:{st.session_state.perm_saida} GRAF:{st.session_state.perm_grafico}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

# ADMIN CONTROLE TOTAL - SÓ QUEM EU CADASTRAR ACESSA E EU LIBERO O QUE QUISER
if st.session_state.perfil == "ADMINISTRADOR":
    with st.sidebar.expander("🔑 ADMIN - VOCÊ LIBERA TUDO", expanded=True):
        st.markdown("**CADASTRAR E LIBERAR ACESSO - SENHA INDIVIDUAL**")
        novo_email = st.text_input("Email operador").lower().strip()
        nova_senha = st.text_input("Senha individual", type="password")
        local = st.selectbox("Liberar acesso para:", ["SALA ANEXA", "BARRACÃO", "AMBOS"])
        c1,c2,c3 = st.columns(3)
        p_ent = c1.checkbox("Liberar ENTRADA", value=True)
        p_sai = c2.checkbox("Liberar SAIDA", value=True)
        p_graf = c3.checkbox("Liberar GRÁFICOS/INFO", value=False)

        if st.button("✅ CADASTRAR E LIBERAR - SÓ ELE ACESSA NO LINK", type="primary", use_container_width=True):
            if "@" in novo_email and nova_senha:
                df_e = pd.read_csv(ARQ_EMAILS)
                df_e = df_e[~((df_e["EMAIL"]==novo_email) & (df_e["LOCAL"]==local))]
                novo = {"EMAIL":novo_email,"SENHA":nova_senha,"LOCAL":local,"ENTRADA":p_ent,"SAIDA":p_sai,"GRAFICO":p_graf,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}
                df_e = pd.concat([df_e, pd.DataFrame([novo])], ignore_index=True)
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"✅ {novo_email} liberado! Envie o LINK + email + senha {nova_senha}")
                st.rerun()

        df_e = pd.read_csv(ARQ_EMAILS)
        st.dataframe(df_e, use_container_width=True, hide_index=True)

        st.markdown("**EDITAR / BLOQUEAR / TROCAR SENHA**")
        sel = st.selectbox("Selecione email", df_e["EMAIL"].unique())
        df_user = df_e[df_e["EMAIL"]==sel]
        sel_local = st.selectbox("Local dele", df_user["LOCAL"].tolist())
        row = df_user[df_user["LOCAL"]==sel_local].iloc[0]

        nova_senha_edit = st.text_input(f"Nova senha para {sel}", type="password", key="edit_senha")
        c1,c2,c3 = st.columns(3)
        e_ent = c1.checkbox("ENTRADA", value=bool(row["ENTRADA"]), key="ee")
        e_sai = c2.checkbox("SAIDA", value=bool(row["SAIDA"]), key="es")
        e_graf = c3.checkbox("GRAFICO", value=bool(row["GRAFICO"]), key="eg")

        b1,b2,b3 = st.columns(3)
        if b1.button("💾 Salvar tudo"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "ENTRADA"] = e_ent
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "SAIDA"] = e_sai
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "GRAFICO"] = e_graf
            if nova_senha_edit:
                df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "SENHA"] = nova_senha_edit
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.success("Atualizado")
            st.rerun()
        if b2.button("🚫 BLOQUEAR"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "STATUS"] = "BLOQUEADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()
        if b3.button("✅ LIBERAR"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "STATUS"] = "LIBERADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()

    st.sidebar.button("💾 SALVAR ESTOQUE", type="primary", on_click=salvar)

# CONTEUDO
df = pd.DataFrame(st.session_state.dados)
blocos_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==15)]["SALDO"].sum()
barras_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==16)]["SALDO"].sum()
blocos_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==15)]["SALDO"].sum()
barras_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==16)]["SALDO"].sum()

pode_anexa = st.session_state.local_acesso in ["SALA ANEXA", "AMBOS"]
pode_barracao = st.session_state.local_acesso in ["BARRACÃO", "AMBOS"]

st.title(f"🔐 Acesso: {st.session_state.local_acesso}")

c1,c2,c3 = st.columns(3)
if pode_anexa:
    if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
        st.session_state.tela = "ANEXA"
else:
    c1.button("📦 SALA ANEXA BLOQUEADA", disabled=True, use_container_width=True)

if pode_barracao:
    if c2.button("🏚️ BARRACÃO", use_container_width=True):
        st.session_state.tela = "BARRACAO"
else:
    c2.button("🏚️ BARRACÃO BLOQUEADO", disabled=True, use_container_width=True)

if st.session_state.perm_grafico:
    if c3.button("📊 GRÁFICOS/INFO", use_container_width=True):
        st.session_state.tela = "CONSULTA"
else:
    c3.button("📊 INFO BLOQUEADA PELO ADMIN", disabled=True, use_container_width=True)

if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA" if pode_anexa else "BARRACAO"

st.divider()

if st.session_state.tela == "ANEXA" and pode_anexa:
    st.subheader(f"📦 SALA ANEXA - BLOCOS: {blocos_a:.0f} | BARRAS: {barras_a:.0f}")
    id_e = st.selectbox("ID", [15,16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}")
    qtd = st.number_input("Qtd (cada 1 é 1 unid)", value=1.0, min_value=0.1)
    col1,col2 = st.columns(2)
    if st.session_state.perm_entrada:
        if col1.button("✅ ENTRADA - LIBERADO", type="primary", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA":datetime.now(),"TIPO":"ENTRADA","ID":id_e,"LOCAL":"SALA ANEXA","QTD":qtd,"USUARIO":st.session_state.usuario})
            salvar()
            st.rerun()
    else:
        col1.button("🚫 ENTRADA BLOQUEADA PELO ADMIN", disabled=True, use_container_width=True)

    if st.session_state.perm_saida:
        if col2.button("✅ SAIDA - LIBERADO", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"DATA":datetime.now(),"TIPO":"SAIDA","ID":id_e,"LOCAL":"SALA ANEXA","QTD":qtd,"USUARIO":st.session_state.usuario})
            salvar()
            st.rerun()
    else:
        col2.button("🚫 SAIDA BLOQUEADA PELO ADMIN", disabled=True, use_container_width=True)

elif st.session_state.tela == "BARRACAO" and pode_barracao:
    st.subheader(f"🏚️ BARRACÃO - BLOCOS: {blocos_b:.0f} | BARRAS: {barras_b:.0f}")
    id_e = st.selectbox("ID", [15,16], key="b", format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}")
    qtd = st.number_input("Qtd", value=1.0, min_value=0.1, key="qb")
    col1,col2 = st.columns(2)
    if st.session_state.perm_entrada:
        if col1.button("✅ ENTRADA BARRACÃO", type="primary", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA":datetime.now(),"TIPO":"ENTRADA","ID":id_e,"LOCAL":"BARRACÃO","QTD":qtd,"USUARIO":st.session_state.usuario})
            salvar()
            st.rerun()
    else:
        col1.button("🚫 ENTRADA BLOQUEADA", disabled=True, use_container_width=True)

    if st.session_state.perm_saida:
        if col2.button("✅ SAIDA BARRACÃO", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"DATA":datetime.now(),"TIPO":"SAIDA","ID":id_e,"LOCAL":"BARRACÃO","QTD":qtd,"USUARIO":st.session_state.usuario})
            salvar()
            st.rerun()
    else:
        col2.button("🚫 SAIDA BLOQUEADA", disabled=True, use_container_width=True)

else:
    if st.session_state.perm_grafico:
        st.subheader("📊 INFORMAÇÕES LIBERADAS PELO ADMIN")
        c1,c2 = st.columns(2)
        if pode_anexa:
            c1.bar_chart(pd.DataFrame([{"ITEM":"BLOCOS","QTD":blocos_a},{"ITEM":"BARRAS","QTD":barras_a}]).set_index("ITEM"))
        if pode_barracao:
            c2.bar_chart(pd.DataFrame([{"ITEM":"BLOCOS","QTD":blocos_b},{"ITEM":"BARRAS","QTD":barras_b}]).set_index("ITEM"))
        st.dataframe(pd.DataFrame(st.session_state.mov).tail(20), use_container_width=True)
    else:
        st.error("🚫 INFORMAÇÕES BLOQUEADAS PELO ADMIN")
