import json
import os
from datetime import datetime, date
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BUILD STOCK - Armário Inteligente de Almoxarifado",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "estoque_armario_gavetas.json"

# --- ESTILIZAÇÃO VISUAL (ARMÁRIO METÁLICO & RETRÔ) ---
st.markdown("""
<style>
    .cabinet-container {
        background-color: #261c16;
        border: 10px solid #120c0a;
        border-radius: 8px;
        padding: 25px;
        box-shadow: inset 0 0 25px rgba(0,0,0,0.9), 0 10px 25px rgba(0,0,0,0.6);
        margin-bottom: 25px;
    }
    .cabinet-title {
        color: #d4a373;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .drawer-card {
        background: linear-gradient(135deg, #4a3b32 0%, #32251e 100%);
        border: 3px solid #1a1310;
        border-radius: 6px;
        padding: 20px;
        color: #fefae0;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        margin-bottom: 15px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .drawer-card:hover {
        transform: translateY(-3px);
        border-color: #dda15e;
    }
    .drawer-handle {
        background: linear-gradient(to bottom, #dda15e 0%, #bc6c25 50%, #8d4915 100%);
        border: 1px solid #482307;
        border-radius: 4px;
        width: 75px;
        height: 16px;
        margin: 14px auto 0 auto;
        box-shadow: 0 3px 6px rgba(0,0,0,0.6);
    }
    .drawer-badge {
        background-color: #fefae0;
        color: #261c16;
        padding: 3px 10px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 0.95rem;
        border-radius: 3px;
        display: inline-block;
        border: 1px dashed #bc6c25;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- PERSISTÊNCIA DOS DADOS ---
def carregar_dados() -> Dict[str, Any]:
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {
        "GAV-001": {
            "nome": "Gaveta Principal - Insumos",
            "movimentacoes": []
        }
    }

def salvar_dados(dados: Dict[str, Any]) -> None:
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar dados: {e}")


# --- INICIALIZAÇÃO DE ESTADO ---
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

if "gaveta_ativa" not in st.session_state:
    chaves = list(st.session_state.estoque.keys())
    st.session_state.gaveta_ativa = chaves[0] if chaves else ""


# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.caption("Almoxarifado & Controle Inteligente")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "🗄️ Visualizar Armário & Gavetas",
        "📊 Dashboard Dinâmico & Relatórios",
        "⚙️ Gerenciar (Criar/Excluir Gavetas)"
    ]
)
st.sidebar.markdown("---")


# ==============================================================================
# MÓDULO 1: ARMÁRIO DE GAVETAS INTERATIVO & REGISTROS
# ==============================================================================
if menu == "🗄️ Visualizar Armário & Gavetas":
    st.title("🗄️ Armário Metálico de Gavetas - Almoxarifado")
    st.markdown("Clique ou selecione abaixo a gaveta para gerenciar o seu conteúdo, lançar entradas/saídas e consultar o histórico completo.")

    lista_gavetas = sorted(list(st.session_state.estoque.keys()))

    if not lista_gavetas:
        st.warning("Nenhuma gaveta cadastrada. Vá na aba 'Gerenciar' para criar a sua primeira gaveta.")
    else:
        # REPRESENTAÇÃO VISUAL EM FORMA DE ARMÁRIO
        st.markdown('<div class="cabinet-container">', unsafe_allow_html=True)
        st.markdown('<div class="cabinet-title">🗄️ Estrutura de Gavetas do Almoxarifado</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, g_id in enumerate(lista_gavetas):
            g_info = st.session_state.estoque[g_id]
            qtd_regs = len(g_info.get("movimentacoes", []))
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="drawer-card">
                        <span class="drawer-badge">{g_id}</span><br>
                        <strong>{g_info.get('nome', 'Gaveta')}</strong><br>
                        <small>Registros: {qtd_regs}</small>
                        <div class="drawer-handle"></div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # SELEÇÃO DA GAVETA ATIVA PARA OPERAÇÃO
        gaveta_selecionada = st.selectbox(
            "🎯 Selecione a Gaveta Ativa:",
            options=lista_gavetas,
            index=lista_gavetas.index(st.session_state.gaveta_ativa) if st.session_state.gaveta_ativa in lista_gavetas else 0
        )
        st.session_state.gaveta_ativa = gaveta_selecionada
        gaveta_atual = st.session_state.estoque[gaveta_selecionada]
        historico = gaveta_atual.get("movimentacoes", [])

        # FORMULÁRIO PADRÃO SOLICITADO
        with st.form(key=f"form_gav_{gaveta_selecionada}"):
            st.subheader(f"📝 Lançamento na Gaveta: [{gaveta_selecionada}] {gaveta_atual.get('nome')}")

            c1, c2, c3 = st.columns(3)
            with c1:
                id_mat = st.text_input("ID do Material:", placeholder="Ex: MAT-001").strip().upper()
                descricao = st.text_input("Descrição:", placeholder="Ex: Cimento CP-II").strip().title()
            with c2:
                marca = st.text_input("Marca / Fabricante:", placeholder="Ex: Votoran").strip().title()
                lote = st.text_input("Número do Lote:", placeholder="Ex: LOTE-2026A").strip().upper()
            with c3:
                data_fab = st.date_input("📅 Data de Fabricação:", value=date.today())
                tempo_validade_dias = st.number_input("⏳ Tempo de Validade (em dias):", min_value=1, value=180, step=1)

            st.markdown("##### 📐 Fatores de Cálculo e Quantidades")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                qtd_recebida = st.number_input("Qtd Recebida (Manual):", min_value=1, value=10, step=1)
            with f2:
                total_paletes = st.number_input("Total de Paletes:", min_value=0, value=1, step=1)
            with f3:
                total_unit_palete = st.number_input("Total Unitários por Palete:", min_value=1, value=56, step=1)
            with f4:
                unidade_medida = st.selectbox("Unidade / Medida:", ["KG", "UN", "Metros (M)", "Metros Quadrados (m²)", "Caixas", "Litros (L)"])

            op1, op2 = st.columns(2)
            with op1:
                tipo_operacao = st.radio("Tipo de Operação:", ["Entrada (+)", "Saída (-)"], horizontal=True)
            with op2:
                observacao = st.text_input("Observação / Projeto:", placeholder="Opcional")

            btn_salvar = st.form_submit_button("💾 Salvar Movimentação na Gaveta", use_container_width=True)

        if btn_salvar:
            if id_mat and descricao and marca:
                # Cálculo automático do total geral em quilos/unidades/m² com base na quantidade recebida informada manualmente
                total_geral_calculado = float(qtd_recebida) * float(total_unit_palete if total_unit_palete > 0 else 1)

                # Validação de estoque para saídas
                entradas_totais = sum(m["total_geral"] for m in historico if m["id_mat"] == id_mat and m["operacao"] == "Entrada (+)")
                saidas_totais = sum(m["total_geral"] for m in historico if m["id_mat"] == id_mat and m["operacao"] == "Saída (-)")
                saldo_atual = entradas_totais - saidas_totais

                if tipo_operacao == "Saída (-)" and saldo_atual < total_geral_calculado:
                    st.error(f"🚫 Saldo insuficiente! Saldo atual disponível para este item: {saldo_atual:,.2f} {unidade_medida}")
                else:
                    # Data de validade calculada automaticamente somando os dias de validade à data de fabricação
                    from datetime import timedelta
                    data_val_calc = data_fab + timedelta(days=int(tempo_validade_dias))

                    novo_lancamento = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "id_mat": id_mat,
                        "descricao": descricao,
                        "marca": marca,
                        "lote": lote,
                        "data_fabricacao": data_fab.strftime("%Y-%m-%d"),
                        "tempo_validade_dias": int(tempo_validade_dias),
                        "data_validade": data_val_calc.strftime("%Y-%m-%d"),
                        "qtd_recebida": int(qtd_recebida),
                        "total_paletes": int(total_paletes),
                        "total_unit_palete": int(total_unit_palete),
                        "total_geral": float(total_geral_calculado),
                        "unidade_medida": unidade_medida,
                        "operacao": tipo_operacao,
                        "observacao": observacao
                    }

                    gaveta_atual["movimentacoes"].append(novo_lancamento)
                    salvar_dados(st.session_state.estoque)
                    st.toast("Movimentação registrada com sucesso!", icon="✅")
                    st.rerun()
            else:
                st.error("Preencha os campos obrigatórios: ID do Material, Descrição e Marca.")

        # TABELA DE HISTÓRICO DA GAVETA
        if historico:
            st.subheader("📜 Histórico de Lançamentos da Gaveta")
            df_h = pd.DataFrame(historico)
            st.dataframe(
                df_h[[
                    "timestamp", "id_mat", "descricao", "marca", "lote", 
                    "data_fabricacao", "data_validade", "operacao", 
                    "total_paletes", "qtd_recebida", "total_geral", "unidade_medida"
                ]].rename(columns={
                    "timestamp": "Data/Hora",
                    "id_mat": "ID",
                    "descricao": "Descrição",
                    "marca": "Marca",
                    "lote": "Lote",
                    "data_fabricacao": "Fabricação",
                    "data_validade": "Validade",
                    "operacao": "Op",
                    "total_paletes": "Paletes",
                    "qtd_recebida": "Qtd Rec.",
                    "total_geral": "Total Geral",
                    "unidade_medida": "Unidade"
                }),
                use_container_width=True,
                hide_index=True
            )

            # EXCLUIR REGISTRO DO HISTÓRICO
            st.markdown("#### 🗑️ Excluir Lançamento Específico")
            idx_del = st.selectbox(
                "Selecione o registro para remover:",
                options=range(len(historico)),
                format_func=lambda i: f"[{historico[i]['timestamp']}] ID: {historico[i]['id_mat']} - {historico[i]['descricao']} ({historico[i]['operacao']})"
            )
            if st.button("🗑️ Remover Registro Selecionado"):
                gaveta_atual["movimentacoes"].pop(idx_del)
                salvar_dados(st.session_state.estoque)
                st.toast("Registro removido!", icon="🗑️")
                st.rerun()
        else:
            st.info("Nenhuma movimentação registrada nesta gaveta ainda.")


# ==============================================================================
# MÓDULO 2: DASHBOARD DINÂMICO & RELATÓRIOS ANALÍTICOS
# ==============================================================================
elif menu == "📊 Dashboard Dinâmico & Relatórios":
    st.title("📊 Painel Analítico & Gráficos Dinâmicos")
    st.markdown("Todos os indicadores e gráficos abaixo se atualizam automaticamente conforme as movimentações de entrada e saída.")

    todas_movs = []
    for g_id, g_data in st.session_state.estoque.items():
        for mov in g_data.get("movimentacoes", []):
            item = mov.copy()
            item["gaveta_id"] = g_id
            item["gaveta_nome"] = g_data.get("nome", "N/A")
            todas_movs.append(item)

    if todas_movs:
        df_geral = pd.DataFrame(todas_movs)
        df_geral["data_dt"] = pd.to_datetime(df_geral["timestamp"])
        df_geral["dias_em_estoque"] = (datetime.now() - df_geral["data_dt"]).dt.days

        # FILTRO DE PERÍODO DINÂMICO
        st.markdown("##### ⏱️ Filtro Temporal de Análise:")
        filtro_periodo = st.selectbox(
            "Selecione o período de visualização dos gráficos:",
            ["Todo o Período", "Diário (Hoje)", "Semanal (Últimos 7 dias)", "Mensal (Últimos 30 dias)", "Semestral (Últimos 6 meses)", "Anual (Último ano)"],
            index=0
        )

        # APLICAR FILTRO TEMPORAL NO DATAFRAME
        hoje = datetime.now()
        if filtro_periodo == "Diário (Hoje)":
            df_geral = df_geral[df_geral["data_dt"].dt.date == hoje.date()]
        elif filtro_periodo == "Semanal (Últimos 7 dias)":
            df_geral = df_geral[df_geral["data_dt"] >= (hoje - pd.Timedelta(days=7))]
        elif filtro_periodo == "Mensal (Últimos 30 dias)":
            df_geral = df_geral[df_geral["data_dt"] >= (hoje - pd.Timedelta(days=30))]
        elif filtro_periodo == "Semestral (Últimos 6 meses)":
            df_geral = df_geral[df_geral["data_dt"] >= (hoje - pd.Timedelta(days=180))]
        elif filtro_periodo == "Anual (Último ano)":
            df_geral = df_geral[df_geral["data_dt"] >= (hoje - pd.Timedelta(days=365))]

        if df_geral.empty:
            st.warning("Nenhum dado encontrado para o período selecionado.")
        else:
            # CONSOLIDAÇÃO DE ENTRADAS E SAÍDAS POR MATERIAL
            df_ent = df_geral[df_geral["operacao"] == "Entrada (+)"].groupby(["gaveta_id", "id_mat", "descricao", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Entradas")
            df_sai = df_geral[df_geral["operacao"] == "Saída (-)"].groupby(["gaveta_id", "id_mat", "descricao", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Saídas")

            df_dash = pd.merge(df_ent, df_sai, on=["gaveta_id", "id_mat", "descricao", "marca", "unidade_medida"], how="outer").fillna(0)
            df_dash["Saldo Total"] = df_dash["Entradas"] - df_dash["Saídas"]

            # MÉTRICAS PRINCIPAIS
            m1, m2, m3 = st.columns(3)
            m1.metric("📦 Entradas no Período", f"{df_dash['Entradas'].sum():,.2f}")
            m2.metric("📤 Saídas / Consumo", f"{df_dash['Saídas'].sum():,.2f}")
            m3.metric("📊 Saldo Geral Atual", f"{df_dash['Saldo Total'].sum():,.2f}")

            st.markdown("---")

            # GRÁFICO 1: GRÁFICO DE CONSUMO DINÂMICO (ENTRADAS VS SAÍDAS)
            st.subheader("📉 Gráfico Dinâmico de Consumo & Movimentação")
            fig_cons = px.bar(
                df_dash, x="descricao", y=["Entradas", "Saídas"],
                barmode="group", title="Dinâmica de Entradas e Consumo por Material",
                labels={"descricao": "Material", "value": "Quantidade", "variable": "Operação"}
            )
            st.plotly_chart(fig_cons, use_container_width=True)

            st.markdown("---")

            col_g1, col_g2 = st.columns(2)

            # GRÁFICO 2: CURVA ABC
            with col_g1:
                st.subheader("📈 Curva ABC (Volume em Estoque)")
                df_abc = df_dash.sort_values(by="Saldo Total", ascending=False).reset_index(drop=True)
                fig_abc = px.bar(
                    df_abc, x="descricao", y="Saldo Total", color="id_mat",
                    title="Curva ABC de Materiais Armazenados",
                    labels={"descricao": "Material", "Saldo Total": "Saldo Atual"}
                )
                st.plotly_chart(fig_abc, use_container_width=True)

            # GRÁFICO 3: VALIDADE DOS MATERIAIS DINÂMICO
            with col_g2:
                st.subheader("⏳ Gráfico Dinâmico de Validade dos Lotes")
                fig_val = px.timeline(
                    df_geral, x_start="timestamp", x_end="data_validade", y="descricao",
                    color="lote", title="Cronograma de Validade e Lotes Ativos",
                    labels={"descricao": "Material", "data_validade": "Validade Limite"}
                )
                fig_val.update_yaxes(categoryorder="total ascending")
                st.plotly_chart(fig_val, use_container_width=True)

            st.markdown("---")

            col_t1, col_t2 = st.columns(2)

            # TEMPO EM ESTOQUE
            with col_t1:
                st.subheader("⏱️ Tempo que o Material está em Estoque")
                df_tempo = df_geral[["gaveta_id", "id_mat", "descricao", "lote", "dias_em_estoque", "unidade_medida"]]
                st.dataframe(df_tempo.rename(columns={"gaveta_id": "Gaveta", "id_mat": "ID", "descricao": "Material", "dias_em_estoque": "Dias no Estoque"}), use_container_width=True, hide_index=True)

            # FILA FIFO (First In, First Out)
            with col_t2:
                st.subheader("🔄 Fila FIFO (Prioridade de Saída)")
                st.info("Lotes mais antigos (menor data/hora de entrada) possuem prioridade na saída.")
                df_fifo = df_geral.sort_values("timestamp").groupby(["gaveta_id", "id_mat"]).first().reset_index()
                st.dataframe(df_fifo[["gaveta_id", "id_mat", "descricao", "lote", "timestamp"]].rename(columns={"gaveta_id": "Gaveta", "id_mat": "ID", "descricao": "Material", "timestamp": "Lote Mais Antigo (A Saída)"}), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("📋 Relatório Consolidado Geral")
            st.dataframe(df_dash, use_container_width=True, hide_index=True)

            # EXPORTAÇÃO EM CSV
            csv_export = df_dash.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Exportar Relatório Consolidado (CSV)",
                data=csv_export,
                file_name=f"relatorio_estoque_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum dado cadastrado para exibir os relatórios e gráficos.")


# ==============================================================================
# MÓDULO 3: GERENCIAR GAVETAS (CRIAR E EXCLUIR)
# ==============================================================================
elif menu == "⚙️ Gerenciar (Criar/Excluir Gavetas)":
    st.title("⚙️ Gerenciamento Estrutural do Armário")
    st.markdown("Crie novas gavetas com um clique ou exclua gavetas existentes do almoxarifado.")

    tab_c, tab_d = st.tabs(["➕ Criar Nova Gaveta", "❌ Excluir Gaveta"])

    with tab_c:
        with st.form("form_nova_gaveta"):
            id_nova = st.text_input("ID da Nova Gaveta (Ex: GAV-002):", placeholder="GAV-002").strip().upper()
            nome_nova = st.text_input("Descrição / Nome da Gaveta:", placeholder="Ex: Ferramentas Elétricas").strip()
            
            btn_criar = st.form_submit_button("💾 Criar Nova Gaveta no Armário", use_container_width=True)

        if btn_criar:
            if id_nova and nome_nova:
                if id_nova in st.session_state.estoque:
                    st.error("Este ID de gaveta já existe!")
                else:
                    st.session_state.estoque[id_nova] = {
                        "nome": nome_nova,
                        "movimentacoes": []
                    }
                    salvar_dados(st.session_state.estoque)
                    st.toast(f"Gaveta {id_nova} criada com sucesso!", icon="✅")
                    st.rerun()
            else:
                st.error("Preencha o ID e o Nome/Descrição da gaveta.")

    with tab_d:
        gavetas_existentes = list(st.session_state.estoque.keys())
        if gavetas_existentes:
            gav_del = st.selectbox("Selecione a Gaveta para Excluir:", options=gavetas_existentes)
            if st.button("🗑️ Excluir Gaveta Permanentemente", type="primary"):
                del st.session_state.estoque[gav_del]
                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {gav_del} removida com sucesso!", icon="🗑️")
                st.rerun()
        else:
            st.info("Não há gavetas cadastradas para exclusão.")
