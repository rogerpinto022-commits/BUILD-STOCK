import json
import os
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BUILD STOCK",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "estoque_id.json"


# --- PERSISTÊNCIA DE DADOS ---
def carregar_dados() -> Dict[str, Any]:
    """Carrega os dados do arquivo JSON ou retorna a estrutura inicial padrão."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error(f"Erro ao ler o arquivo de dados: {e}")
            return {}
    
    return {
        "GAV-001": {
            "nome": "Gaveta Principal",
            "tipo_embalagem": "Caixa",
            "qtd_por_embalagem": 10,
            "unidade_medida": "UN",
            "movimentacoes": []
        }
    }


def salvar_dados(dados: Dict[str, Any]) -> None:
    """Salva a estrutura atualizada do estoque no arquivo JSON."""
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar os dados no arquivo: {e}")


# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()


# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.caption("Sistema Avançado de Gestão de Estoque")
st.sidebar.markdown("---")

opcao_menu = st.sidebar.radio(
    "Navegação:",
    [
        "🗄️ Movimentação da Gaveta",
        "📊 Dashboard & Relatórios",
        "⚙️ Gerenciar Gavetas",
    ]
)

st.sidebar.markdown("---")


# ==============================================================================
# MÓDULO 1: MOVIMENTAÇÃO DA GAVETA
# ==============================================================================
if opcao_menu == "🗄️ Movimentação da Gaveta":
    st.title("🗄️ Operações por Gaveta")

    lista_gavetas = sorted(list(st.session_state.estoque.keys()))

    if not lista_gavetas:
        st.warning("Nenhuma gaveta cadastrada no sistema. Cadastre uma no menu 'Gerenciar Gavetas'.")
    else:
        id_selecionado = st.selectbox("Selecione a Gaveta de Destino:", options=lista_gavetas)

        if id_selecionado in st.session_state.estoque:
            gaveta = st.session_state.estoque[id_selecionado]
            historico = gaveta.get("movimentacoes", [])

            # Indicadores da Gaveta
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📍 ID da Gaveta", id_selecionado)
            col2.metric("🏷️ Setor / Nome", gaveta.get("nome", "N/A"))
            col3.metric("📦 Embalagem", gaveta.get("tipo_embalagem", "N/A"))
            col4.metric(
                "🔢 Capacidade/Embalagem", 
                f"{gaveta.get('qtd_por_embalagem', 1)} {gaveta.get('unidade_medida', 'UN')}"
            )

            st.markdown("---")

            # Formulário de Operações
            with st.form(key=f"form_movimentacao_{id_selecionado}"):
                st.subheader("➕ Nova Entrada / Saída")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    material_in = st.text_input("Material:", placeholder="Ex: Parafuso Sextavado M8").strip().title()
                with col_m2:
                    marca_in = st.text_input("Marca / Modelo:", placeholder="Ex: Tramontina").strip().title()

                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    qtd_in = st.number_input(
                        f"Quantidade ({gaveta.get('unidade_medida', 'UN')}):", 
                        min_value=1, 
                        value=1, 
                        step=1
                    )
                with col_q2:
                    tipo_op = st.radio("Tipo de Operação:", ["Entrada (+)", "Saída (-)"], horizontal=True)

                submit_btn = st.form_submit_button("💾 Salvar Registros", use_container_width=True)

            if submit_btn:
                if material_in and marca_in:
                    # Cálculo do saldo disponível para validação
                    entradas = sum(
                        m["quantidade"] for m in historico
                        if m["material"] == material_in and m["marca"] == marca_in and m["operacao"] == "Entrada (+)"
                    )
                    saidas = sum(
                        m["quantidade"] for m in historico
                        if m["material"] == material_in and m["marca"] == marca_in and m["operacao"] == "Saída (-)"
                    )
                    saldo_atual = entradas - saidas

                    if tipo_op == "Saída (-)" and saldo_atual < qtd_in:
                        st.error(f"🚫 Saldo insuficiente! Saldo atual de '{material_in}': {saldo_atual} {gaveta.get('unidade_medida', 'UN')}")
                    else:
                        novo_registro = {
                            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "material": material_in,
                            "marca": marca_in,
                            "operacao": tipo_op,
                            "quantidade": int(qtd_in),
                            "embalagem": gaveta.get("tipo_embalagem", "UN"),
                            "unidade_medida": gaveta.get("unidade_medida", "UN")
                        }
                        
                        st.session_state.estoque[id_selecionado]["movimentacoes"].append(novo_registro)
                        salvar_dados(st.session_state.estoque)
                        st.toast("Movimentação salva com sucesso!", icon="✅")
                        st.rerun()
                else:
                    st.error("Por favor, preencha os campos de Material e Marca.")

            # Exibição do Saldo e Histórico
            if historico:
                df_hist = pd.DataFrame(historico)

                # Resumo Consolidado
                df_ent = df_hist[df_hist["operacao"] == "Entrada (+)"].groupby(["material", "marca"])["quantidade"].sum().reset_index(name="Entradas")
                df_sai = df_hist[df_hist["operacao"] == "Saída (-)"].groupby(["material", "marca"])["quantidade"].sum().reset_index(name="Saídas")

                df_resumo = pd.merge(df_ent, df_sai, on=["material", "marca"], how="outer").fillna(0)
                df_resumo["Saldo Atual"] = df_resumo["Entradas"] - df_resumo["Saídas"]
                df_resumo["Unidade"] = gaveta.get("unidade_medida", "UN")

                st.subheader("📊 Saldo Atual na Gaveta")
                st.dataframe(
                    df_resumo.rename(columns={"material": "Material", "marca": "Marca"}),
                    use_container_width=True,
                    hide_index=True
                )

                with st.expander("📜 Visualizar Histórico Detalhado"):
                    st.dataframe(
                        df_hist[["data_hora", "material", "marca", "operacao", "quantidade", "unidade_medida"]],
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("Esta gaveta não possui movimentações registradas.")


# ==============================================================================
# MÓDULO 2: DASHBOARD & RELATÓRIOS
# ==============================================================================
elif opcao_menu == "📊 Dashboard & Relatórios":
    st.title("📊 Painel Geral do Estoque")

    todas_movimentacoes = []
    for g_id, g_data in st.session_state.estoque.items():
        for mov in g_data.get("movimentacoes", []):
            mov_item = mov.copy()
            mov_item["gaveta_id"] = g_id
            mov_item["gaveta_nome"] = g_data.get("nome", "N/A")
            todas_movimentacoes.append(mov_item)

    if todas_movimentacoes:
        df_geral = pd.DataFrame(todas_movimentacoes)

        # Processamento de Dados para Indicadores Gerais
        df_ent_g = df_geral[df_geral["operacao"] == "Entrada (+)"].groupby(["gaveta_id", "gaveta_nome", "material", "marca"])["quantidade"].sum().reset_index(name="Entradas")
        df_sai_g = df_geral[df_geral["operacao"] == "Saída (-)"].groupby(["gaveta_id", "gaveta_nome", "material", "marca"])["quantidade"].sum().reset_index(name="Saídas")

        df_dash = pd.merge(df_ent_g, df_sai_g, on=["gaveta_id", "gaveta_nome", "material", "marca"], how="outer").fillna(0)
        df_dash["Saldo Geral"] = df_dash["Entradas"] - df_dash["Saídas"]

        # Métricas de Topo
        m1, m2, m3 = st.columns(3)
        m1.metric("📦 Entradas Totais", f"{int(df_dash['Entradas'].sum()):,}".replace(",", "."))
        m2.metric("📤 Saídas Totais", f"{int(df_dash['Saídas'].sum()):,}".replace(",", "."))
        m3.metric("📊 Saldo Atual em Estoque", f"{int(df_dash['Saldo Geral'].sum()):,}".replace(",", "."))

        st.markdown("---")

        # Gráficos Analíticos
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("📊 Distribuição do Saldo por Gaveta")
            fig_bar = px.bar(
                df_dash,
                x="gaveta_id",
                y="Saldo Geral",
                color="material",
                title="Saldo Atual Agrupado por Gaveta",
                labels={"gaveta_id": "Gaveta ID", "Saldo Geral": "Unidades em Estoque"},
                barmode="stack"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            st.subheader("🔄 Balanço Entradas vs Saídas")
            df_comp = df_dash.groupby("material")[["Entradas", "Saídas"]].sum().reset_index()
            fig_comp = px.bar(
                df_comp,
                x="material",
                y=["Entradas", "Saídas"],
                title="Total Movimentado por Material",
                labels={"material": "Material", "value": "Quantidade"},
                barmode="group"
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        st.subheader("📋 Relatório Consolidado de Itens")
        st.dataframe(df_dash, use_container_width=True, hide_index=True)

        # Botão de Exportação
        data_csv = df_dash.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar Relatório Consolidado (CSV)",
            data=data_csv,
            file_name=f"relatorio_estoque_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Sem dados cadastrados no histórico global para exibição do dashboard.")


# ==============================================================================
# MÓDULO 3: GERENCIAR GAVETAS
# ==============================================================================
elif opcao_menu == "⚙️ Gerenciar Gavetas":
    st.title("⚙️ Gestão de Gavetas e Estrutura")

    tab_cad, tab_del = st.tabs(["➕ Cadastrar / Editar Gaveta", "❌ Excluir Gaveta"])

    with tab_cad:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            id_gaveta = st.text_input("ID da Gaveta:", placeholder="Ex: GAV-001").strip().upper()
            nome_gaveta = st.text_input("Setor / Descrição:", placeholder="Ex: Ferramentas Elétricas").strip()
        
        with col_c2:
            tipo_embalagem = st.selectbox(
                "Tipo de Embalagem Padrão:",
                ["Caixa", "Pacote", "Saco", "Rolo", "Unidade Individual", "Outro"]
            )
            qtd_embalagem = st.number_input("Quantidade por Embalagem:", min_value=1, value=1, step=1)
            unidade_medida = st.selectbox("Unidade de Medida:", ["UN", "KG", "Metros (M)", "Litros (L)", "Par", "Jogo"])

        if st.button("💾 Cadastrar / Atualizar Estrutura", use_container_width=True):
            if id_gaveta and nome_gaveta:
                movs_salvas = []
                if id_gaveta in st.session_state.estoque:
                    movs_salvas = st.session_state.estoque[id_gaveta].get("movimentacoes", [])

                st.session_state.estoque[id_gaveta] = {
                    "nome": nome_gaveta,
                    "tipo_embalagem": tipo_embalagem,
                    "qtd_por_embalagem": int(qtd_embalagem),
                    "unidade_medida": unidade_medida,
                    "movimentacoes": movs_salvas
                }

                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {id_gaveta} salva com sucesso!", icon="✅")
                st.rerun()
            else:
                st.error("Campos 'ID da Gaveta' e 'Setor / Descrição' são obrigatórios.")

    with tab_del:
        gavetas_disponiveis = list(st.session_state.estoque.keys())
        if gavetas_disponiveis:
            id_deletar = st.selectbox("Selecione a Gaveta a ser Removida:", options=gavetas_disponiveis)
            if st.button("🗑️ Confirmar Remoção Permanente", type="primary", use_container_width=True):
                del st.session_state.estoque[id_deletar]
                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {id_deletar} removida!", icon="🗑️")
                st.rerun()
        else:
            st.info("Não existem gavetas cadastradas para exclusão.")
            
