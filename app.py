import json
import os
from datetime import datetime, date
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BUILD STOCK - Gestão Avançada",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "estoque_id.json"
ARQUIVO_MATERIAIS = "materiais_padrao.json"

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
<style>
    .cabinet-container {
        background-color: #2c221e;
        border: 8px solid #1a1412;
        border-radius: 6px;
        padding: 20px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.8), 0 8px 16px rgba(0,0,0,0.4);
        margin-bottom: 25px;
    }
    .cabinet-title {
        color: #d4a373;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .retro-drawer {
        background: linear-gradient(135deg, #4a3b32 0%, #382c25 100%);
        border: 3px solid #221a16;
        border-radius: 4px;
        padding: 15px;
        color: #fefae0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
        position: relative;
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }
    .retro-drawer:hover {
        transform: translateY(-2px);
        border-color: #d4a373;
    }
    .drawer-handle {
        background: linear-gradient(to bottom, #d4a373 0%, #b08968 50%, #9c6644 100%);
        border: 1px solid #582f0e;
        border-radius: 3px;
        width: 60px;
        height: 14px;
        margin: 8px auto 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    .drawer-label {
        background-color: #fefae0;
        color: #2c221e;
        padding: 2px 8px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 0.85rem;
        border-radius: 2px;
        display: inline-block;
        border: 1px dashed #bc6c25;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)


# --- PERSISTÊNCIA DE DADOS ---
def carregar_dados() -> Dict[str, Any]:
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error(f"Erro ao ler dados de estoque: {e}")
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
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar dados de estoque: {e}")

def carregar_materiais_padrao() -> Dict[str, Any]:
    if os.path.exists(ARQUIVO_MATERIAIS):
        try:
            with open(ARQUIVO_MATERIAIS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {
        "MAT-001": {
            "descricao": "Cimento CP-II",
            "marca": "Votoran",
            "qtd_por_palete": 56,
            "qtd_por_embalagem": 25,
            "unidade_medida": "KG"
        }
    }

def salvar_materiais_padrao(dados: Dict[str, Any]) -> None:
    try:
        with open(ARQUIVO_MATERIAIS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except IOError as e:
        st.error(f"Erro ao salvar materiais padrão: {e}")


# --- INICIALIZAÇÃO DO ESTADO ---
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

if "materiais_padrao" not in st.session_state:
    st.session_state.materiais_padrao = carregar_materiais_padrao()


# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.caption("Almoxarifado & Controle Inteligente")
st.sidebar.markdown("---")

opcao_menu = st.sidebar.radio(
    "Navegação:",
    [
        "🗄️ Armário de Gavetas",
        "📋 Catálogo de Materiais",
        "📊 Dashboard & Relatórios",
        "⚙️ Gerenciar Gavetas",
    ]
)

st.sidebar.markdown("---")


# ==============================================================================
# MÓDULO 1: ARMÁRIO DE GAVETAS & MOVIMENTAÇÃO (FIFO + VALIDADE + CÁLCULOS)
# ==============================================================================
if opcao_menu == "🗄️ Armário de Gavetas":
    st.title("🗄️ Arquivo de Gavetas & Movimentações")
    st.markdown("Selecione uma gaveta e registre as entradas informando paletes, sacos e conversão de peso unitário.")

    lista_gavetas = sorted(list(st.session_state.estoque.keys()))

    if not lista_gavetas:
        st.warning("Nenhuma gaveta cadastrada. Vá em 'Gerenciar Gavetas'.")
    else:
        # Exibição visual retrô das gavetas
        st.markdown('<div class="cabinet-container">', unsafe_allow_html=True)
        st.markdown('<div class="cabinet-title">🗄️ Arquivo de Gavetas Metálicas</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, g_id in enumerate(lista_gavetas):
            gaveta_info = st.session_state.estoque[g_id]
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="retro-drawer">
                        <span class="drawer-label">{g_id}</span><br>
                        <strong>{gaveta_info.get('nome', 'Gaveta')}</strong><br>
                        <small>Padrão: {gaveta_info.get('tipo_embalagem', 'UN')}</small>
                        <div class="drawer-handle"></div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        id_selecionado = st.selectbox("🎯 Escolha a Gaveta Ativa:", options=lista_gavetas)

        if id_selecionado in st.session_state.estoque:
            gaveta = st.session_state.estoque[id_selecionado]
            historico = gaveta.get("movimentacoes", [])

            # Autopreenchimento por ID de Material Cadastrado
            lista_ids_materiais = [""] + list(st.session_state.materiais_padrao.keys())
            id_material_busca = st.selectbox("🔍 Buscar ID do Material Padrão (Autopreenchimento):", options=lista_ids_materiais)

            mat_auto = ""
            marca_auto = ""
            qtd_palete_auto = 1
            qtd_emb_auto = 1
            un_auto = "UN"

            if id_material_busca and id_material_busca in st.session_state.materiais_padrao:
                m_info = st.session_state.materiais_padrao[id_material_busca]
                mat_auto = m_info.get("descricao", "")
                marca_auto = m_info.get("marca", "")
                qtd_palete_auto = int(m_info.get("qtd_por_palete", 1))
                qtd_emb_auto = int(m_info.get("qtd_por_embalagem", 1))
                un_auto = m_info.get("unidade_medida", "UN")

            with st.form(key=f"form_mov_{id_selecionado}"):
                st.subheader("➕ Registrar Entrada / Saída de Carga")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    material_in = st.text_input("Descrição do Material:", value=mat_auto).strip().title()
                with col_m2:
                    marca_in = st.text_input("Marca / Fabricante:", value=marca_auto).strip().title()

                st.markdown("##### 📐 Fatores de Conversão e Quantidades")
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    qtd_paletes = st.number_input("Qtd de Paletes Recebidos:", min_value=0, value=1, step=1)
                with col_f2:
                    qtd_por_palete = st.number_input("Unidades / Embalagens por Palete:", min_value=1, value=qtd_palete_auto, step=1)
                with col_f3:
                    peso_ou_qtd_unit = st.number_input(f"Peso/Qtd por Embalagem ({un_auto}):", min_value=0.1, value=float(qtd_emb_auto), step=0.1)

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    tipo_op = st.radio("Tipo de Operação:", ["Entrada (+)", "Saída (-)"], horizontal=True)
                with col_t2:
                    data_validade = st.date_input("📅 Data de Validade do Lote:", value=date.today())

                submit_btn = st.form_submit_button("💾 Salvar Registro no Histórico", use_container_width=True)

            if submit_btn:
                if material_in and marca_in:
                    # Cálculo volumétrico completo
                    # Ex: 1 Palete com 56 sacos, cada saco com 25kg = 56 * 25 = 1400 kg totais
                    total_unidades_embalagem = qtd_paletes * qtd_por_palete
                    total_geral_calculado = total_unidades_embalagem * peso_ou_qtd_unit

                    # Validação de saída baseada em saldo FIFO
                    entradas_totais = sum(m["total_geral"] for m in historico if m["material"] == material_in and m["operacao"] == "Entrada (+)")
                    saidas_totais = sum(m["total_geral"] for m in historico if m["material"] == material_in and m["operacao"] == "Saída (-)")
                    saldo_atual_mat = entradas_totais - saidas_totais

                    if tipo_op == "Saída (-)" and saldo_atual_mat < total_geral_calculado:
                        st.error(f"🚫 Saldo insuficiente! Saldo atual: {saldo_atual_mat:,.2f} {un_auto}")
                    else:
                        novo_registro = {
                            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "data_validade": data_validade.strftime("%Y-%m-%d"),
                            "material": material_in,
                            "marca": marca_in,
                            "operacao": tipo_op,
                            "qtd_paletes": int(qtd_paletes),
                            "qtd_por_palete": int(qtd_por_palete),
                            "peso_unitario": float(peso_ou_qtd_unit),
                            "total_embalagens": int(total_unidades_embalagem),
                            "total_geral": float(total_geral_calculado),
                            "unidade_medida": un_auto
                        }

                        st.session_state.estoque[id_selecionado]["movimentacoes"].append(novo_registro)
                        salvar_dados(st.session_state.estoque)
                        st.toast("Movimentação e conversões calculadas com sucesso!", icon="✅")
                        st.rerun()
                else:
                    st.error("Preencha a Descrição e a Marca do material.")

            # Listagem do Histórico e Saldos
            if historico:
                df_hist = pd.DataFrame(historico)
                st.subheader("📜 Histórico de Materiais na Gaveta (Com Totais Calculados)")
                st.dataframe(
                    df_hist[[
                        "data_hora", "data_validade", "material", "marca", "operacao", 
                        "qtd_paletes", "total_embalagens", "peso_unitario", "total_geral", "unidade_medida"
                    ]].rename(columns={
                        "data_hora": "Data/Hora",
                        "data_validade": "Validade",
                        "material": "Material",
                        "marca": "Marca",
                        "operacao": "Op",
                        "qtd_paletes": "Paletes",
                        "total_embalagens": "Qtd Embalagens",
                        "peso_unitario": "Medida/Emb",
                        "total_geral": "Total Geral",
                        "unidade_medida": "UN"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

                # Opção de excluir registro específico do histórico
                st.markdown("#### 🗑️ Excluir Registro do Histórico")
                idx_para_excluir = st.selectbox("Selecione o registro pelo índice para remover:", options=range(len(historico)), format_func=lambda i: f"[{historico[i]['data_hora']}] {historico[i]['material']} - {historico[i]['operacao']} ({historico[i]['total_geral']} {historico[i]['unidade_medida']})")
                if st.button("🗑️ Remover Registro Selecionado"):
                    st.session_state.estoque[id_selecionado]["movimentacoes"].pop(idx_para_excluir)
                    salvar_dados(st.session_state.estoque)
                    st.toast("Registro removido com sucesso!", icon="🗑️")
                    st.rerun()
            else:
                st.info("Nenhuma movimentação registrada nesta gaveta.")


# ==============================================================================
# MÓDULO 2: CADASTRO PRINCIPAL DE MATERIAIS PADRÃO
# ==============================================================================
elif opcao_menu == "📋 Catálogo de Materiais":
    st.title("📋 Cadastro Principal de Materiais Padrão")
    st.markdown("Cadastre os padrões de materiais para facilitar o autopreenchimento no almoxarifado.")

    tab_cad_mat, tab_ger_mat = st.tabs(["➕ Cadastrar / Editar Material", "🗑️ Lista & Exclusão"])

    with tab_cad_mat:
        with st.form("form_mat_padrao"):
            id_mat_in = st.text_input("ID do Material (Ex: MAT-001):", placeholder="MAT-001").strip().upper()
            desc_mat_in = st.text_input("Descrição do Material:", placeholder="Ex: Cimento CP-II").strip().title()
            marca_mat_in = st.text_input("Marca Padrão:", placeholder="Ex: Votoran").strip().title()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                p_palete = st.number_input("Qtd por Palete (Padrão):", min_value=1, value=56)
            with c2:
                p_emb = st.number_input("Qtd/Peso por Embalagem:", min_value=0.1, value=25.0)
            with c3:
                un_med = st.selectbox("Unidade de Medida:", ["KG", "UN", "Metros (M)", "Litros (L)", "Saco", "Lata"])

            btn_salvar_mat = st.form_submit_button("💾 Salvar Material no Catálogo", use_container_width=True)

        if btn_salvar_mat:
            if id_mat_in and desc_mat_in:
                st.session_state.materiais_padrao[id_mat_in] = {
                    "descricao": desc_mat_in,
                    "marca": marca_mat_in,
                    "qtd_por_palete": int(p_palete),
                    "qtd_por_embalagem": float(p_emb),
                    "unidade_medida": un_med
                }
                salvar_materiais_padrao(st.session_state.materiais_padrao)
                st.toast(f"Material {id_mat_in} salvo no catálogo!", icon="✅")
                st.rerun()
            else:
                st.error("Informe o ID e a Descrição do material.")

    with tab_ger_mat:
        if st.session_state.materiais_padrao:
            df_mats = pd.DataFrame([
                {"ID": k, **v} for k, v in st.session_state.materiais_padrao.items()
            ])
            st.dataframe(df_mats, use_container_width=True, hide_index=True)

            id_del_mat = st.selectbox("Selecione o ID para excluir do catálogo:", options=list(st.session_state.materiais_padrao.keys()))
            if st.button("🗑️ Excluir Material do Catálogo", type="primary"):
                del st.session_state.materiais_padrao[id_del_mat]
                salvar_materiais_padrao(st.session_state.materiais_padrao)
                st.toast("Material removido do catálogo!", icon="🗑️")
                st.rerun()
        else:
            st.info("Nenhum material cadastrado no catálogo.")


# ==============================================================================
# MÓDULO 3: DASHBOARD & RELATÓRIOS (CURVA ABC, FIFO, VALIDADE, TEMPO, ENTRADAS/SAÍDAS)
# ==============================================================================
elif opcao_menu == "📊 Dashboard & Relatórios":
    st.title("📊 Painel de Inteligência e Indicadores")

    todas_movs = []
    for g_id, g_data in st.session_state.estoque.items():
        for mov in g_data.get("movimentacoes", []):
            item = mov.copy()
            item["gaveta_id"] = g_id
            item["gaveta_nome"] = g_data.get("nome", "N/A")
            todas_movs.append(item)

    if todas_movs:
        df_geral = pd.DataFrame(todas_movs)

        # Cálculo de Entradas e Saídas Consolidadas
        df_ent = df_geral[df_geral["operacao"] == "Entrada (+)"].groupby(["gaveta_id", "gaveta_nome", "material", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Entradas")
        df_sai = df_geral[df_geral["operacao"] == "Saída (-)"].groupby(["gaveta_id", "gaveta_nome", "material", "marca", "unidade_medida"])["total_geral"].sum().reset_index(name="Saídas")

        df_dash = pd.merge(df_ent, df_sai, on=["gaveta_id", "gaveta_nome", "material", "marca", "unidade_medida"], how="outer").fillna(0)
        df_dash["Saldo Total"] = df_dash["Entradas"] - df_dash["Saídas"]

        # Métricas de Topo
        m1, m2, m3 = st.columns(3)
        m1.metric("📦 Total de Entradas", f"{df_dash['Entradas'].sum():,.2f}")
        m2.metric("📤 Total de Saídas", f"{df_dash['Saídas'].sum():,.2f}")
        m3.metric("📊 Saldo Geral em Estoque", f"{df_dash['Saldo Total'].sum():,.2f}")

        st.markdown("---")

        # Gráfico 1: Entradas e Saídas por Material
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("🔄 Balanço Entradas vs Saídas")
            fig_es = px.bar(
                df_dash, x="material", y=["Entradas", "Saídas"],
                barmode="group", title="Movimentação Global por Material"
            )
            st.plotly_chart(fig_es, use_container_width=True)

        # Gráfico 2: Curva ABC Simplificada (baseada no volume de estoque)
        with col_g2:
            st.subheader("📈 Curva ABC (Volume em Estoque)")
            df_abc = df_dash.sort_values(by="Saldo Total", ascending=False).reset_index(drop=True)
            if not df_abc.empty:
                fig_abc = px.bar(
                    df_abc, x="material", y="Saldo Total",
                    color="Saldo Total", title="Curva ABC de Materiais Armazenados"
                )
                st.plotly_chart(fig_abc, use_container_width=True)

        st.markdown("---")

        # Seção de Validade e FIFO
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("⏳ Controle de Validade dos Lotes")
            if "data_validade" in df_geral.columns:
                df_val = df_geral[["gaveta_id", "material", "marca", "data_validade", "total_geral", "unidade_medida"]].sort_values("data_validade")
                st.dataframe(df_val.rename(columns={"gaveta_id": "Gaveta", "material": "Material", "data_validade": "Validade", "total_geral": "Qtd"}), use_container_width=True, hide_index=True)

        with col_v2:
            st.subheader("🔄 Fila FIFO (First In, First Out)")
            st.info("O sistema organiza as saídas respeitando automaticamente o lote mais antigo registrado por data/hora.")
            df_fifo = df_geral.sort_values("data_hora").groupby(["gaveta_id", "material"]).first().reset_index()
            st.dataframe(df_fifo[["gaveta_id", "material", "marca", "data_hora", "unidade_medida"]].rename(columns={"gaveta_id": "Gaveta", "material": "Material", "data_hora": "Lote Mais Antigo (A Saída)"}), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📋 Relatório Consolidado Geral")
        st.dataframe(df_dash, use_container_width=True, hide_index=True)

        # Exportação CSV
        csv_data = df_dash.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar Relatório Geral (CSV)",
            data=csv_data,
            file_name=f"relatorio_geral_estoque_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado de movimentação registrado para gerar os relatórios.")


# ==============================================================================
# MÓDULO 4: GERENCIAR GAVETAS
# ==============================================================================
elif opcao_menu == "⚙️ Gerenciar Gavetas":
    st.title("⚙️ Gestão Estrutural das Gavetas")

    tab_cad_g, tab_del_g = st.tabs(["➕ Criar / Editar Gaveta", "❌ Excluir Gaveta"])

    with tab_cad_g:
        c1, c2 = st.columns(2)
        with c1:
            id_gav = st.text_input("ID da Gaveta:", placeholder="Ex: GAV-002").strip().upper()
            nome_gav = st.text_input("Setor / Descrição:", placeholder="Ex: Ferramentas Manuais").strip()
        with c2:
            tipo_emb = st.selectbox("Tipo de Embalagem Padrão:", ["Caixa", "Pacote", "Saco", "Rolo", "Palete", "Outro"])
            qtd_emb = st.number_input("Quantidade Padrão por Embalagem:", min_value=1, value=1)
            un_med = st.selectbox("Unidade de Medida:", ["UN", "KG", "Metros (M)", "Litros (L)", "Par", "Jogo"])

        if st.button("💾 Salvar Gaveta", use_container_width=True):
            if id_gav and nome_gav:
                movs_antigas = []
                if id_gav in st.session_state.estoque:
                    movs_antigas = st.session_state.estoque[id_gav].get("movimentacoes", [])

                st.session_state.estoque[id_gav] = {
                    "nome": nome_gav,
                    "tipo_embalagem": tipo_emb,
                    "qtd_por_embalagem": int(qtd_emb),
                    "unidade_medida": un_med,
                    "movimentacoes": movs_antigas
                }
                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {id_gav} salva com sucesso!", icon="✅")
                st.rerun()
            else:
                st.error("Preencha o ID e o Setor/Descrição da gaveta.")

    with tab_del_g:
        gavs_disp = list(st.session_state.estoque.keys())
        if gavs_disp:
            gav_del = st.selectbox("Selecione a Gaveta para excluir:", options=gavs_disp)
            if st.button("🗑️ Excluir Gaveta Permanentemente", type="primary"):
                del st.session_state.estoque[gav_del]
                salvar_dados(st.session_state.estoque)
                st.toast(f"Gaveta {gav_del} removida!", icon="🗑️")
                st.rerun()
        else:
            st.info("Não há gavetas cadastradas para exclusão.")
            
