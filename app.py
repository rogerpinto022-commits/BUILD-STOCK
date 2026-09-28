import streamlit as st
import pandas as pd

st.set_page_config(page_title="Estoque Simples", layout="centered")

# DADOS DA SUA TABELA - já com saldo inicial da foto
if "estoque" not in st.session_state:
    st.session_state.estoque = [
        {"ID": 1, "DESCRICAO": "CIMENTO - FONDU", "QTD": 12.0},
        {"ID": 2, "DESCRICAO": "CARBETO DE SILICIO - SHINAGAWA", "QTD": 2.5},
        {"ID": 3, "DESCRICAO": "ARGAMASSA REFRATARIA - TECNOFIRE", "QTD": 5.0},
        {"ID": 4, "DESCRICAO": "CONCRETO REFRATARIO - CASTIBAR PSI UG", "QTD": 3.0},
        {"ID": 5, "DESCRICAO": "LÃ DE ROCHA - IBAR", "QTD": 4.0},
        {"ID": 6, "DESCRICAO": "TIJOLO SEMI ISOLANTE - MOSCONI AB 70", "QTD": 19.0},
        {"ID": 7, "DESCRICAO": "TIJOLO ISOLANTE - MOSCONI AB 55", "QTD": 311.0},
        {"ID": 8, "DESCRICAO": "TIJOLO REFRATARIO - SUPERIBAR AS ALUM", "QTD": 153.0},
        {"ID": 9, "DESCRICAO": "CORDÃO DE BARRAS(GAXETA) - ITEELL", "QTD": 0.0},
        {"ID": 10, "DESCRICAO": "PLACAS DE BANHO (VERMICULITA) - ITEELL", "QTD": 32.0},
        {"ID": 11, "DESCRICAO": "CHAMOTE - IBAR", "QTD": 18.0},
        {"ID": 12, "DESCRICAO": "PASTA FRIA - ELKEN", "QTD": 0.0},
        {"ID": 13, "DESCRICAO": "PASTA FRIA - CARBON", "QTD": 0.0},
        {"ID": 14, "DESCRICAO": "BLOCOS LATERAL - CARBON", "QTD": 0.0},
        {"ID": 15, "DESCRICAO": "BLOCOS ENGUSADOS", "QTD": 0.0},
        {"ID": 16, "DESCRICAO": "BARRAS CATÓDICAS - CEMAÇO", "QTD": 0.0},
        {"ID": 17, "DESCRICAO": "BLOCOS DE FUNDO - SEC", "QTD": 0.0},
    ]

st.title("🧱 ESTOQUE - SIMPLES")

df = pd.DataFrame(st.session_state.estoque)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Movimentação")

id_selecionado = st.selectbox("Selecione o ID", [f"{x['ID']} - {x['DESCRICAO']}" for x in st.session_state.estoque])
id_num = int(id_selecionado.split(" - ")[0])

col1, col2, col3 = st.columns(3)
with col1:
    qtd = st.number_input("QTD", min_value=0.1, value=1.0, step=1.0)
with col2:
    tipo = st.radio("Tipo", ["ENTRADA", "SAÍDA"], horizontal=True)
with col3:
    st.write("")
    st.write("")
    if st.button("CONFIRMAR", type="primary", use_container_width=True):
        for item in st.session_state.estoque:
            if item["ID"] == id_num:
                if tipo == "ENTRADA":
                    item["QTD"] += qtd
                else:
                    if item["QTD"] >= qtd:
                        item["QTD"] -= qtd
                    else:
                        st.error(f"Saldo insuficiente! Tem só {item['QTD']}")
                        st.stop()
                st.success(f"{tipo} de {qtd} no ID {id_num} OK!")
                st.rerun()

item_atual = next(x for x in st.session_state.estoque if x["ID"] == id_num)
st.metric(f"QTD ATUAL - ID {id_num}", item_atual["QTD"])
