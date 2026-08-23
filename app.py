import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA - TOTAL REALIZADO")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":0.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = []

df = pd.DataFrame(st.session_state.dados)

# SALDOS POR ITEM
for id_item in [15, 16]:
    df_item = df[df["ID"]==id_item]
    desc = df_item.iloc[0]["DESCRIÇÃO"]
    anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
    barracao = df_item[df_item["LOCAL"]=="BARRACÃO"]["SALDO"].sum()
    geral = anexa + barracao
    st.markdown(f"### ID {id_item} - {desc}")
    c1, c2, c3 = st.columns(3)
    c1.metric("SALDO SALA ANEXA", f"{anexa:.0f}")
    c2.metric("SALDO BARRACÃO", f"{barracao:.0f}")
    c3.metric("ESTOQUE GERAL", f"{geral:.0f}")

st.divider()

# CALCULO TOTAL DE ENTRADAS = TOTAL REALIZADO
if not st.session_state.mov:
    ent_anexa = sai_anexa = ent_bar = sai_bar = 0
else:
    df_mov = pd.DataFrame(st.session_state.mov)
    ent_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]["QTD"].sum()
    sai_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="SAIDA")]["QTD"].sum()
    ent_bar = df_mov[(df_mov["LOCAL"]=="BARRACÃO") & (df_mov["TIPO"]=="ENTRADA")]["QTD"].sum()
    sai_bar = df_mov[(df_mov["LOCAL"]=="BARRACÃO") & (df_mov["TIPO"]=="SAIDA")]["QTD"].sum()

# TOTAL REALIZADO = TOTAL DE ENTRADAS
total_entradas = ent_anexa + ent_bar
total_realizado = total_entradas # IGUAL COMO VOCÊ PEDIU

sai_anexa_div13 = sai_anexa / 13 if sai_anexa>0 else 0

st.subheader("📊 TOTAIS - TOTAL DE ENTRADAS = TOTAL REALIZADO")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("TOTAL DE ENTRADAS", f"{total_entradas:.0f}", "TOTAL REALIZADO")
c2.metric("TOTAL REALIZADO", f"{total_realizado:.0f}", "= ENTRADAS")
c3.metric("SALA ANEXA ENTRADAS", f"{ent_anexa:.0f}")
c4.metric("SALA ANEXA SAIDAS", f"{sai_anexa:.0f}")
c5.metric("SALA ANEXA SAIDAS /13", f"{sai_anexa_div13:.2f}", f"{sai_anexa:.0f}/13")

# GRÁFICO
df_graf = pd.DataFrame([
    {"LOCAL":"SALA ANEXA", "ENTRADAS":ent_anexa, "SAIDAS":sai_anexa, "SAIDAS/13":round(sai_anexa_div13,2), "TOTAL REALIZADO":ent_anexa},
    {"LOCAL":"BARRACÃO", "ENTRADAS":ent_bar, "SAIDAS":sai_bar, "SAIDAS/13":round(sai_bar/13,2) if sai_bar>0 else 0, "TOTAL REALIZADO":ent_bar},
])

st.bar_chart(df_graf.set_index("LOCAL")[["ENTRADAS","SAIDAS"]])
st.bar_chart(df_graf.set_index("LOCAL")[["TOTAL REALIZADO"]])
st.write("Tabela TOTAL DE ENTRADAS = TOTAL REALIZADO e SAIDAS/13")
st.dataframe(df_graf, use_container_width=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA", "EXCLUIR REGISTRO"])

with tab1:
    st.header("NOVA ENTRADA")
    st.info(f"TOTAL DE ENTRADAS = TOTAL REALIZADO = {total_realizado:.0f} - A cada NOVA ENTRADA aumenta o TOTAL REALIZADO")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="ent_id")
    local_sel = st.selectbox("LOCAL *", ["SALA ANEXA", "BARRACÃO"], key="ent_local")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=13.0, step=1.0, key="ent_qtd")
    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]==local_sel), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        st.session_state.mov.append({"TIPO":"ENTRADA", "ID":id_sel, "LOCAL":local_sel, "QTD":qtd})
        st.success(f"NOVA ENTRADA +{qtd:.0f} | TOTAL DE ENTRADAS {total_entradas:.0f} → {total_entradas+qtd:.0f} | TOTAL REALIZADO {total_realizado:.0f} → {total_realizado+qtd:.0f}")
        st.rerun()

with tab2:
    st.header("NOVA SAIDA")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="sai_id")
    local_sel = st.selectbox("LOCAL *", ["SALA ANEXA", "BARRACÃO"], key="sai_local")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=13.0, step=1.0, key="sai_qtd")
    if st.button("✅ REGISTRAR SAIDA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]==local_sel), None)
        if qtd > st.session_state.dados[idx]["SALDO"]:
            st.error(f"Só tem {st.session_state.dados[idx]['SALDO']:.0f}")
        else:
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"TIPO":"SAIDA", "ID":id_sel, "LOCAL":local_sel, "QTD":qtd})
            st.rerun()

with tab3:
    st.header("EXCLUIR REGISTRO")
    if st.session_state.mov:
        st.dataframe(pd.DataFrame(st.session_state.mov), use_container_width=True)
        idx_mov = st.selectbox("Registro para EXCLUIR *", range(len(st.session_state.mov)), format_func=lambda i: f"{st.session_state.mov[i]['TIPO']} ID {st.session_state.mov[i]['ID']} {st.session_state.mov[i]['LOCAL']} {st.session_state.mov[i]['QTD']:.0f}", key="exc")
        if st.checkbox("Confirmo EXCLUIR REGISTRO"):
            if st.button("🗑️ EXCLUIR REGISTRO", use_container_width=True):
                reg = st.session_state.mov[idx_mov]
                idx_dado = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                if reg["TIPO"]=="ENTRADA":
                    st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                else:
                    st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                del st.session_state.mov[idx_mov]
                st.rerun()
