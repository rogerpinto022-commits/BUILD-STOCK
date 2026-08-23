import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ADMIN CONTROLE TOTAL")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "SENHA":"admin123", "LOCAL":"AMBOS", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"anexa@empresa.com", "SENHA":"anexa123", "LOCAL":"SALA ANEXA", "ENTRADA":True, "SAIDA":False, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
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
    st.title("🔐 ADMIN LIBERA TUDO - LINK")
    with st.container(border=True):
        email = st.text_input("EMAIL").lower().strip()
        senha = st.text_input("SENHA INDIVIDUAL", type="password")
        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_e = pd.read_csv(ARQ_EMAILS)
            user = df_e[(df_e["EMAIL"]==email) & (df_e["SENHA"]==senha) & (df_e["STATUS"]=="LIBERADO")]
            if not user.empty:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = user.iloc[0]["PERFIL"]
                st.session_state.local_acesso = user.iloc[0]["LOCAL"]
                st.session_state.perm_entrada = user.iloc[0]["ENTRADA"]
                st.session_state.perm_saida = user.iloc[0]["SAIDA"]
                st.session_state.perm_grafico = user.iloc[0]["GRAFICO"]
                st.rerun()
            else:
                st.error("Bloqueado ou sem permissão do admin")
    st.info("ADMIN: admin@empresa.com / admin123 = LIBERA TUDO")
    st.stop()

st.sidebar.markdown(f"👤 {st.session_state.usuario}\n**{st.session_state.local_acesso}**\nENTRADA:{st.session_state.perm_entrada} SAIDA:{st.session_state.perm_saida} GRAFICO:{st.session_state.perm_grafico}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

# ADMIN - CONTROLE TOTAL DE TODAS AS FUNÇÕES
if st.session_state.perfil == "ADMINISTRADOR":
    with st.sidebar.expander("🔑 ADMIN LIBERA ACESSOS - CONTROLE TOTAL", expanded=True):
        st.markdown("**LIBERAR OPERADOR COM PERMISSÕES**")
        novo_email = st.text_input("Email operador").lower().strip()
        nova_senha = st.text_input("Senha individual", type="password")
        local = st.selectbox("O que pode acessar?", ["SALA ANEXA", "BARRACÃO", "AMBOS"])
        c1,c2,c3 = st.columns(3)
        p_entrada = c1.checkbox("Pode ENTRADA", value=True)
        p_saida = c2.checkbox("Pode SAIDA", value=True)
        p_grafico = c3.checkbox("Pode GRÁFICO", value=False)

        if st.button("✅ LIBERAR - ADMIN MANDA", type="primary", use_container_width=True):
            if "@" in novo_email and nova_senha:
                df_e = pd.read_csv(ARQ_EMAILS)
                df_e = df_e[~((df_e["EMAIL"]==novo_email) & (df_e["LOCAL"]==local))]
                novo = {"EMAIL":novo_email,"SENHA":nova_senha,"LOCAL":local,"ENTRADA":p_entrada,"SAIDA":p_saida,"GRAFICO":p_grafico,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}
                df_e = pd.concat([df_e, pd.DataFrame([novo])], ignore_index=True)
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"✅ {novo_email} liberado para {local} - ENTRADA:{p_entrada} SAIDA:{p_saida} GRAFICO:{p_grafico}")
                st.rerun()

        df_e = pd.read_csv(ARQ_EMAILS)
        st.dataframe(df_e, hide_index=True, use_container_width=True)

        st.markdown("**BLOQUEAR / EDITAR PERMISSÃO**")
        sel = st.selectbox("Selecione email para editar", df_e["EMAIL"].unique())
        df_user = df_e[df_e["EMAIL"]==sel]
        sel_local = st.selectbox("Local desse email", df_user["LOCAL"].tolist())
        row = df_user[df_user["LOCAL"]==sel_local].iloc[0]

        c1,c2,c3 = st.columns(3)
        edit_entrada = c1.checkbox("ENTRADA", value=bool(row["ENTRADA"]), key="e1")
        edit_saida = c2.checkbox("SAIDA", value=bool(row["SAIDA"]), key="e2")
        edit_grafico = c3.checkbox("GRAFICO", value=bool(row["GRAFICO"]), key="e3")

        b1,b2,b3 = st.columns(3)
        if b1.button("💾 Salvar Permissão"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "ENTRADA"] = edit_entrada
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "SAIDA"] = edit_saida
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "GRAFICO"] = edit_grafico
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.success("Permissão atualizada")
            st.rerun()
        if b2.button("🚫 BLOQUEAR"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "STATUS"]="BLOQUEADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()
        if b3.button("✅ DESBLOQUEAR"):
            df_e.loc[(df_e["EMAIL"]==sel) & (df_e["LOCAL"]==sel_local), "STATUS"]="LIBERADO"
            df_e.to_csv(ARQ_EMAILS, index=False)
            st.rerun()

    st.sidebar.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

# CALCULOS
df = pd.DataFrame(st.session_state.dados)
blocos_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==15)]["SALDO"].sum()
barras_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==16)]["SALDO"].sum()
blocos_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==15)]["SALDO"].sum()
barras_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==16)]["SALDO"].sum()

pode_anexa = st.session_state.local_acesso in ["SALA ANEXA", "AMBOS"]
pode_barracao = st.session_state.local_acesso in ["BARRACÃO", "AMBOS"]

st.title(f"🔐 ADMIN LIBEROU: {st.session_state.local_acesso}")

c1,c2,c3 = st.columns(3)
if pode_anexa:
    if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
        st.session_state.tela = "ANEXA"
else:
    c1.button("📦 SEM ACESSO ANEXA", disabled=True, use_container_width=True)

if pode_barracao:
    if c2.button("🏚️ BARRACÃO", use_container_width=True):
        st.session_state.tela = "BARRACAO"
else:
    c2.button("🏚️ SEM ACESSO BARRACÃO", disabled=True, use_container_width=True)

if st.session_state.perm_grafico:
    if c3.button("📊 GRÁFICOS", use_container_width=True):
        st.session_state.tela = "CONSULTA"
else:
    c3.button("📊 GRÁFICO BLOQUEADO PELO ADMIN", disabled=True, use_container_width=True)

if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA" if pode_anexa else "BARRACAO"

st.divider()

if st.session_state.tela == "ANEXA" and pode_anexa:
    st.subheader("📦 SALA ANEXA - CADA ITEM É 1")
    st.metric("BLOCOS", f"{blocos_a:.0f} unid")
    st.metric("BARRAS", f"{barras_a:.0f} unid")

    if not st.session_state.perm_entrada and not st.session_state.perm_saida:
        st.error("🚫 ADMIN BLOQUEOU ENTRADA E SAIDA PARA VOCÊ")
    else:
        id_e = st.selectbox("Item", [15,16], format_func=lambda x: f"ID {x} - {'BLOCOS' if x==15 else 'BARRAS'}")
        qtd = st.number_input("Qtd", value=1.0, key="qa")
        col1,col2 = st.columns(2)
        if st.session_state.perm_entrada:
            if col1.button("✅ ENTRADA - LIBERADO PELO ADMIN", type="primary", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_e, "LOCAL":"SALA ANEXA", "QTD":qtd, "USUARIO":st.session_state.usuario})
                salvar()
                st.rerun()
        else:
            col1.button("🚫 ENTRADA BLOQUEADA PELO ADMIN", disabled=True, use_container_width=True)

        if st.session_state.perm_saida:
            if col2.button("✅ SAIDA - LIBERADO PELO ADMIN", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] -= qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_e, "LOCAL":"SALA ANEXA", "QTD":qtd, "USUARIO":st.session_state.usuario})
                salvar()
                st.rerun()
        else:
            col2.button("🚫 SAIDA BLOQUEADA PELO ADMIN", disabled=True, use_container_width=True)

elif st.session_state.tela == "BARRACAO" and pode_barracao:
    st.subheader("🏚️ BARRACÃO - CADA ITEM É 1")
    st.metric("BLOCOS", f"{blocos_b:.0f}")
    st.metric("BARRAS", f"{barras_b:.0f}")

    if not st.session_state.perm_entrada and not st.session_state.perm_saida:
        st.error("🚫 ADMIN BLOQUEOU ENTRADA E SAIDA PARA VOCÊ")
    else:
        id_e = st.selectbox("Item", [15,16], key="qb")
        qtd = st.number_input("Qtd", value=1.0, key="qb2")
        col1,col2 = st.columns(2)
        if st.session_state.perm_entrada:
            if col1.button("✅ ENTRADA BARRACÃO - LIBERADO", type="primary", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] += qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_e, "LOCAL":"BARRACÃO", "QTD":qtd, "USUARIO":st.session_state.usuario})
                salvar()
                st.rerun()
        else:
            col1.button("🚫 ENTRADA BLOQUEADA", disabled=True, use_container_width=True)

        if st.session_state.perm_saida:
            if col2.button("✅ SAIDA BARRACÃO - LIBERADO", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] -= qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_e, "LOCAL":"BARRACÃO", "QTD":qtd, "USUARIO":st.session_state.usuario})
                salvar()
                st.rerun()
        else:
            col2.button("🚫 SAIDA BLOQUEADA", disabled=True, use_container_width=True)

else:
    if not st.session_state.perm_grafico:
        st.error("🚫 GRÁFICOS BLOQUEADOS PELO ADMIN - PEÇA LIBERAÇÃO")
    else:
        st.subheader("📊 GRÁFICOS LIBERADOS PELO ADMIN")
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("### 📦 SALA ANEXA")
            if pode_anexa:
                st.bar_chart(pd.DataFrame([{"ITEM":"BLOCOS","QTD":blocos_a},{"ITEM":"BARRAS","QTD":barras_a}]).set_index("ITEM"))
            else:
                st.error("Sem acesso anexa")
        with col2:
            st.markdown("### 🏚️ BARRACÃO")
            if pode_barracao:
                st.bar_chart(pd.DataFrame([{"ITEM":"BLOCOS","QTD":blocos_b},{"ITEM":"BARRAS","QTD":barras_b}]).set_index("ITEM"))
            else:
                st.error("Sem acesso barracão")
