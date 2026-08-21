import json
import os
from datetime import datetime, date
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BUILD STOCK - Armário Inteligente",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "estoque_gavetas.json"

# --- ESTILIZAÇÃO CSS (VISUAL DE ARMÁRIO METÁLICO RETRÔ) ---
st.markdown("""
<style>
    .cabinet-wrapper {
        background-color: #2b211d;
        border: 8px solid #14100e;
        border-radius: 8px;
        padding: 25px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.9), 0 10px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .cabinet-header {
        color: #d4a373;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .drawer-card {
        background: linear-gradient(135deg, #4a3b32 0%, #352821 100%);
        border: 3px solid #1a1411;
        border-radius: 6px;
        padding: 18px;
        color: #fefae0;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        margin-bottom: 15px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .drawer-card:hover {
        transform: translateY(-3px);
        border-color: #dda15e;
    }
    .drawer-handle {
        background: linear-gradient(to bottom, #dda15e 0%, #bc6c25 50%, #985213 100%);
        border: 1px solid #582f0e;
        border-radius: 4px;
        width: 70px;
        height: 16px;
        margin: 12px auto 0 auto;
        box-shadow: 0 3px 5px rgba(0,0,0,0.6);
    }
    .drawer-badge {
        background-color: #fefae0;
        color: #2b211d;
        padding: 3px 10px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 0.9rem;
        border-radius: 3px;
        display: inline-block;
        border: 1px dashed #bc6c25;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- PERSISTÊNCIA DE DADOS ---
def carregar_dados() -> Dict[str, Any]:
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {
        "GAV-001": {
            "nome": "Gaveta de Insumos Básicos",
            "movimentacoes": []
        }
    }

def salvar_dados(dados: Dict[str, Any]) -> None:
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar dados: {e}")


# --- INICIALIZAÇÃO DO ESTADO ---
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

if "gaveta_ativa" not in st.session_state:
    gavetas_iniciais = list(st.session_state.estoque.keys())
    st.session_state.gaveta_ativa = gavetas_iniciais[0] if gavetas_iniciais else ""


# --- MENU LATERAL ---
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.caption("Gestão de Almoxarifado por Gavetas")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "🗄️ Armário de Gavetas",
        "📊 Dashboard & Indicadores",
        "⚙️ Gerenciar Gavetas"
    ]
)
st.sidebar.markdown("---")


# ==============================================================================
# MÓDULO 1: ARMÁRIO DE GAVETAS INTERATIVO & MOVIMENTAÇÕES DETALHADAS
# ==============================================================================
if menu == "🗄️ Armário de Gavetas":
    st.title("🗄️ Arquivo de Armazenamento - Visão de Gavetas")
    st.markdown("Clique ou selecione uma gaveta para gerenciar seu conteúdo, registrar lotes e controlar conversões.")

    lista_gavetas = sorted(list(st.session_state.estoque.keys()))

    if not lista_gavetas:
        st.warning("Nenhuma gaveta cadastrada. Vá em 'Gerenciar Gavetas' para criar uma nova.")
    else:
        # VISUAL DO ARMÁRIO EM GRADE
        st.markdown('<div class="cabinet-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="cabinet-header">🗄️ Arquivo de Gavetas Metálicas Industrial</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, g_id in enumerate(lista_gavetas):
            g_info = st.session_state.estoque[g_id]
            total_itens = len(g_info.get("movimentacoes", []))
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="drawer-card">
                        <span class="drawer-badge">{g_id}</span><br>
                        <strong>{g_info.get('nome', 'Gaveta')}</strong><br>
                        <small>Registros: {total_itens}</small>
                        <div class="drawer-handle"></div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # SELETOR DE GAVETA ATIVA
        gaveta_selecionada = st.selectbox(
            "🎯 Selecione a Gaveta para Operação:", 
            options=lista_gavetas,
            index=lista_gavetas.index(st.session_state.gaveta_ativa) if st.session_state.gaveta_ativa in lista_gavetas else 0
        )
        st.session_state.gaveta_ativa = gaveta_selecionada
        gaveta_atual = st.session_state.estoque[gaveta_selecionada]
        historico_gaveta = gaveta_atual.get("movimentacoes", [])

        # FORMULÁRIO DE ENTRADA / SAÍDA COM TODOS OS CAMPOS SOLICITADOS
        with st.form(key=f"form_gaveta_{gaveta_selecionada}"):
            st.subheader(f"➕ Operação na Gaveta: [{gaveta_selecionada}] {gaveta_atual.get('nome')}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                id_material = st.text_input("ID do Material (Ex: MAT-01):", placeholder="MAT-001").strip().upper()
                descricao = st.text_input("Descrição do Material:", placeholder="Ex: Cimento CP-II").strip().title()
            with c2:
                marca = st.text_input("Marca / Fabricante:", placeholder="Ex: Votoran").strip().title()
                lote = st.text_input("Número do Lote:", placeholder="Ex: LOTE-2026A").strip().upper()
            with c3:
                data_fab = st.date_input("📅 Data de Fabricação:", value=date.today())
                data_val = st.date_input("⏳ Data de Validade:", value=date.today())

            st.markdown("##### 📦 Cálculos Volumétricos e Quantidades")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                qtd_paletes = st.number_input("Qtd de Paletes:", min_value=0, value=1, step=1)
            with f2:
                qtd_por_palete = st.number_input("Qtd Embalagens/Palete:", min_value=1, value=56, step=1)
            with f3:
                qtd_recebida_emb = st.number_input("Qtd de Embalagens Recebidas:", min_value=1, value=56, step=1)
            with f4:
                qtd_unit_peso = st.number_input("Qtd Unitária / Peso por Embalagem (KG/UN):", min_value=0.1, value=25.0, step=0.1)

            op1, op2 = st.columns(2)
            with op1:
                tipo_operacao = st.radio("Tipo de Operação:", ["Entrada (+)", "Saída (-)"], horizontal=True)
            with op2:
                unidade_medida = st.selectbox("Unidade de Medida:", ["KG", "UN", "Metros (M)", "Litros (L)", "Saco", "Lata"])

            btn_enviar = st.form_submit_button("💾 Salvar Registro na Gaveta", use_container_width=True)

        if btn_enviar:
            if id_material and descricao and marca:
                # Cálculos automáticos em todas as formas possíveis
                total_geral_calculado = qtd_recebida_emb * qtd_unit_peso

                # Validação de saída por saldo
                entradas_totais = sum(m["total_geral"] for m in historico_gaveta if m["material_id"] == id_material and m["operacao"] == "Entrada (+)")
                saidas_totais = sum(m["total_geral"] for m in historico_gaveta if m["material_id"] == id_material and m["operacao"] == "Saída (-)")
                saldo_atual_mat = entradas_totais - saidas_totais

                if tipo_operacao == "Saída (-)" and saldo_atual_mat < total_geral_calculado:
                    st.error(f"🚫 Saldo insuficiente! Saldo atual do item: {saldo_atual_mat:,.2f} {unidade_medida}")
                else:
                    novo_reg = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "material_id": id_material,
                        "descricao": descricao,
                        "marca": marca,
                        "lote": lote,
                        "data_fabricacao": data_fab.strftime("%Y-%m-%d"),
                        "data_validade": data_val.strftime("%Y-%m-%d"),
                        "operacao": tipo_operacao,
                        "qtd_paletes": int(qtd_paletes),
                        "qtd_por_palete": int(qtd_por_palete),
                        "qtd_recebida_embalagens": int(qtd_recebida_emb),
                        "qtd_unitario_peso": float(qtd_unit_peso),
                        "total_geral": float(total_geral_calculado),
                        "unidade_medida": unidade_medida
                    }

                    gaveta_atual["movimentacoes"].append(novo_reg)
                    salvar_dados(st.session_state.estoque)
                    st.toast("Movimentação registrada com sucesso!", icon="✅")
                    st.rerun()
            else:
                st.error("Preencha os campos obrigatórios: ID do Material, Descrição e Marca.")

        # EXIBIÇÃO DO HISTÓRICO DA GAVETA
        if historico_gaveta:
            st.subheader("📜 Histórico Detalhado da Gaveta Selecionada")
            df_hist = pd.DataFrame(historico_gaveta)
            st.dataframe(
                df_hist[[
                    "timestamp", "material_id", "descricao", "marca", "lote", 
                    "data_fabricacao", "data_validade", "operacao", 
                    "qtd_paletes", "qtd_recebida_embalagens", "total_geral", "unidade_medida"
                ]].rename(columns={
                    "timestamp": "Data/Hora",
                    "material_id": "ID",
                    "descricao": "Descrição",
                    "marca": "Marca",
                    "lote": "Lote",
                    "data_fabricacao": "Fabricação",
                    "data_validade": "Validade",
                    "operacao": "Op",
                    "qtd_paletes": "Paletes",
                    "qtd_recebida_embalagens": "Qtd Emb.",
                    "total_geral": "Total Geral",
                    "unidade_medida": "UN"
                }),
                use_container_width=True,
                hide_index=True
            )

            # EXCLUIR REGISTRO DO HISTÓRICO
            st.markdown("#### 🗑️ Excluir Registro Específico")
            idx_del = st.selectbox(
                "Selecione o registro para remover:", 
                options=range(len(historico_gaveta)),
                format_func=lambda i: f"[{historico_gaveta[i]['timestamp']}] ID: {historico_gaveta[i]['material_id']} - {historico_gaveta[i]['descricao']} ({historico_gaveta[i]['operacao']})"
            )
            if st.button("🗑️ Remover Registro Selecionado"):
                gaveta_atual["movimentacoes"].pop(idx_del)
                salvar_dados(st.session_state.estoque)
                st.toast("Registro removido!", icon="🗑️")
                st.rerun()
        else:
            st.info("Esta gaveta ainda não possui movimentações registradas.")


# ==============================================================================
# MÓDULO 2: DASHBOARD & INDICADORES (CURVA ABC, TEMPO, VALIDADE, FIFO)
# ==============================================================================
elif menu == "📊 Dashboard & Indicadores":
    st.title("📊 Painel Analítico & Relatórios Estratégicos")

    todas_movs = []
    for g_id, g_data in st.session_state.estoque.items():
        for mov in g_data.get("movimentacoes", []):
            item = mov.copy()
            item["gaveta_id"] = g_id
            item["gaveta_nome"] = g_data.get("nome", "N/A")
            todas_movs.append(item)

    if todas_movs:
        df_geral = pd.DataFrame(todas_movs)

        # Cálculo de tempo em estoque (em dias) a partir da data de fabricação/registro
        df_geral["data_ref"] = pd.to_datetime(df_geral["timestamp"])
        df_geral["dias_em_estoque"] = (datetime.now() - df_geral["data_ref"]).dt.days

        # Consolidado de Entradas, Saídas e Saldo Total por Material e Gaveta
        df_ent = df_geral[df_geral["operacao"] == "Entrada (+)"].groupby(["gaveta_id", "material_id", "descricao", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Entradas")
        df_sai = df_geral[df_geral["operacao"] == "Saída (-)"].groupby(["gaveta_id", "material_id", "descricao", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Saídas")

        df_dash = pd.merge(df_ent, df_sai, on=["gaveta_id", "material_id", "descricao", "marca", "unidade_medida"], how="outer").fillna(0)
        df_dash["Saldo Total"] = df_dash["Entradas"] - df_dash["Saídas"]

        # MÉTRICAS DE TOPO
        m1, m2, m3 = st.columns(3)
        m1.metric("📦 Entradas Totais", f"{df_dash['Entradas'].sum():,.2f}")
        m2.metric("📤 Saídas Totais", f"{df_dash['Saídas'].sum():,.2f}")
        m3.metric("📊 Saldo Geral em Estoque", f"{df_dash['Saldo Total'].sum():,.2f}")

        st.markdown("---")

        # GRÁFICO 1: CURVA ABC
        st.subheader("📈 Análise de Curva ABC (Volume em Estoque por Material)")
        df_abc = df_dash.sort_values(by="Saldo Total", ascending=False).reset_index(drop=True)
        fig_abc = px.bar(
            df_abc, x="descricao", y="Saldo Total", color="material_id",
            title="Curva ABC - Distribuição de Valor/Volume em Estoque",
            labels={"descricao": "Material", "SaldoTotal": "Saldo Atual"}
        )
        st.plotly_chart(fig_abc, use_container_width=True)

        st.markdown("---")

        # GRÁFICO 2: GRÁFICO DINÂMICO DE VALIDADE DOS MATERIAIS
        st.subheader("⏳ Gráfico Dinâmico de Validade dos Lotes")
        fig_val = px.timeline(
            df_geral, x_start="timestamp", x_end="data_validade", y="descricao",
            color="lote", title="Cronograma de Validade dos Lotes Armazenados",
            labels={"descricao": "Material", "data_validade": "Validade Limite"}
        )
        fig_val.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_val, use_container_width=True)

        st.markdown("---")

        col_t1, col_t2 = st.columns(2)

        # TEMPO EM ESTOQUE
        with col_t1:
            st.subheader("⏱️ Tempo de Permanência em Estoque")
            df_tempo = df_geral[["gaveta_id", "material_id", "descricao", "lote", "dias_em_estoque", "unidade_medida"]]
            st.dataframe(df_tempo.rename(columns={"gaveta_id": "Gaveta", "material_id": "ID", "descricao": "Material", "dias_em_estoque": "Dias no Estoque"}), use_container_width=True, hide_index=True)

        # CONTROLE FIFO (First In, First Out)
        with col_t2:
            st.subheader("🔄 Fila FIFO (Prioridade de Saída)")
            st.info("Lotes mais antigos (menor data/hora de entrada) possuem prioridade na saída.")
            df_fifo = df_geral.sort_values("timestamp").groupby(["gaveta_id", "material_id"]).first().reset_index()
            st.dataframe(df_fifo[["gaveta_id", "material_id", "descricao", "lote", "timestamp"]].rename(columns={"gaveta_id": "Gaveta", "material_id": "ID", "descricao": "Material", "timestamp": "Lote Mais Antigo (Prioridade)"}), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📋 Relatório Consolidado Geral")
        st.dataframe(df_dash, use_container_width=True, hide_index=True)

        # EXPORTAÇÃO
        csv_export = df_dash.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar Relatório Geral (CSV)",
            data=csv_export,
            file_name=f"relatorio_estoque_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado cadastrado para exibir os relatórios e gráficos.")


# ==============================================================================
# MÓDULO 3: GERENCIAR GAVETAS (CRIAR E EXCLUIR)
# ==============================================================================
elif menu == "⚙️ Gerenciar Gavetas":
    st.title("⚙️ Gestão de Gavetas do Armário")

    tab_c, tab_d = st.tabs(["➕ Criar Nova Gaveta", "❌ Excluir Gaveta"])

    with tab_c:
        with st.form("form_nova_gaveta"):
            id_nova = st.text_input("ID da Nova Gaveta (Ex: GAV-002):", placeholder="GAV-002").strip().upper()
            nome_nova = st.text_input("Descrição / Setor da Gaveta:", placeholder="Ex: Ferramentas e Peças").strip()
            
            btn_criar = st.form_submit_button("💾 Criar Gaveta no Armário", use_container_width=True)

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
                st.error("Preencha o ID e a Descrição da gaveta.")

    with tab_d:
        gavetas_existentes = list(st.session_state.estoque.keys())
        if gavetas_existentes:
            gav_para_excluir = st.selectbox("Selecione a Gaveta para Excluir:", options=gavetas_existentes)
            if st.button("🗑️ Excluir Gaveta Permanentemente", type="primary"):
                del st.session_state.estoque[gav_para_excluir]
                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {gav_para_excluir} removida!", icon="🗑️")
                st.rerun()
        else:
            st.info("Não há gavetas cadastradas para exclusão.")
      
