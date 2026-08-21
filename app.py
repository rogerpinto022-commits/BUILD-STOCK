import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="BUILD STOCK - Armário Inteligente", page_icon="📦", layout="wide"
)

# Estilização Visual Customizada (Tema Rústico / Clássico / Madeira & Bronze)
st.markdown(
    """
    <style>
    /* Estilo geral e fontes */
    .main {
        background-color: #f8f6f0;
    }
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3 {
        color: #3b2716 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Cartões de Gavetas no Estilo Arquivo de Madeira */
    .gaveta-card {
        background: linear-gradient(135deg, #5c3a21 0%, #3b2716 100%);
        border: 2px solid #2d7a57;
        border-radius: 12px;
        padding: 20px;
        color: #ffffff;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    .gaveta-card h3 {
        color: #e6c887 !important;
        margin-top: 0;
    }
    
    .badge-local {
        background-color: #2d7a57;
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicialização do Banco de Dados em Memória (Session State)
if "gavetas" not in st.session_state:
  st.session_state.gavetas = pd.DataFrame(
      columns=[
          "ID_Gaveta",
          "Nome_Gaveta",
          "Localizacao",
          "Descricao",
          "Status",
      ]
  )
  # Exemplo inicial de gaveta vinculada a um local físico
  st.session_state.gavetas.loc[0] = [
      "GAV-001",
      "Gaveta de Insumos Básicos",
      "Galpão 1 - Corredor A - Estante 2",
      "Insumos de construção gerais",
      "Ativa",
  ]

if "movimentacoes" not in st.session_state:
  st.session_state.movimentacoes = pd.DataFrame(
      columns=[
          "ID_Gaveta",
          "ID_Material",
          "Descricao",
          "Marca",
          "Lote",
          "Fabricacao",
          "Validade",
          "Qtd_Total",
          "Unidade",
          "Operacao",
      ]
  )

# Menu Lateral Estilizado
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.markdown(
    "---"
)  # Linha divisória em substituição à tag descontinuada
st.sidebar.markdown("Sistema de Arquivo & Rastreio")
menu = st.sidebar.radio(
    "Navegação:",
    ["🗄️ Arquivo de Gavetas", "📊 Dashboard & Indicadores", "⚙️ Gerenciar Gavetas"],
)

# -------------------------------------------------------------
# 1. GERENCIAR GAVETAS (Criação e Rastreio com Localização)
# -------------------------------------------------------------
if menu == "⚙️ Gerenciar Gavetas":
  st.header("⚙️ Cadastro de Gavetas / Arquivos Físicos")
  st.markdown(
      "Adicione novos compartimentos ao sistema. Eles aparecerão"
      " **automaticamente** no arquivo geral e no dashboard."
  )

  with st.form("form_nova_gaveta"):
    col1, col2 = st.columns(2)
    with col1:
      id_gaveta = st.text_input("ID da Gaveta (Ex: GAV-002)")
      nome_gaveta = st.text_input("Nome/Título da Gaveta")
    with col2:
      # CAMPO ESSENCIAL DE LOCAL DE ARMAZENAGEM
      localizacao = st.text_input(
          "📍 Local de Armazenagem (Ex: Galpão B, Corredor 4, Prateleira 2)"
      )
      status = st.selectbox("Status Operacional", ["Ativa", "Manutenção", "Inativa"])

    descricao_gaveta = st.text_area("Observações sobre o compartimento")
    submitted = st.form_submit_button("💾 Salvar Gaveta no Arquivo")

    if submitted:
      if id_gaveta and nome_gaveta and localizacao:
        if id_gaveta in st.session_state.gavetas["ID_Gaveta"].values:
          st.error("Este ID de gaveta já está cadastrado!")
        else:
          nova_linha = pd.DataFrame(
              [[id_gaveta, nome_gaveta, localizacao, descricao_gaveta, status]],
              columns=st.session_state.gavetas.columns,
          )
          st.session_state.gavetas = pd.concat(
              [st.session_state.gavetas, nova_linha], ignore_index=True
          )
          st.success(
              f"Gaveta {id_gaveta} criada com sucesso e já disponível no sistema!"
          )
          st.rerun()
      else:
        st.warning(
            "Por favor, preencha o ID, o Nome e o Local de Armazenagem para"
            " prosseguir."
        )

  st.markdown("---")
  st.subheader("📋 Gavetas Cadastradas (Visão Geral)")
  if not st.session_state.gavetas.empty:
    st.dataframe(st.session_state.gavetas, use_container_width=True)
  else:
    st.info("Nenhuma gaveta cadastrada no momento.")

# -------------------------------------------------------------
# 2. ARQUIVO DE GAVETAS (Visão Interativa Estilo Armário)
# -------------------------------------------------------------
elif menu == "🗄️ Arquivo de Gavetas":
  st.header("🗄️ Arquivo de Armazenamento - Visão de Gavetas")
  st.markdown(
      "Selecione uma gaveta abaixo para gerenciar seu conteúdo e verificar o"
      " rastreio exato do material."
  )

  if st.session_state.gavetas.empty:
    st.warning(
        "Nenhuma gaveta encontrada. Vá até a aba '⚙️ Gerenciar Gavetas' para"
        " criar a primeira."
    )
  else:
    # Renderização Visual em Cartões (Estilo Arquivo/Móvel Clássico)
    st.markdown("### 🗃️ Compartimentos Disponíveis no Arquivo")
    cols = st.columns(3)
    for index, row in st.session_state.gavetas.iterrows():
      with cols[index % 3]:
        st.markdown(
            f"""
                <div class="gaveta-card">
                    <h3>🗄️ {row['ID_Gaveta']}</h3>
                    <p><b>{row['Nome_Gaveta']}</b></p>
                    <p style="font-size: 0.9rem; color: #ddd;">{row['Descricao']}</p>
                    <span class="badge-local">📍 {row['Localizacao']}</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Seletor Interativo para Operações na Gaveta Escolhida
    gavetas_opcoes = st.session_state.gavetas.apply(
        lambda x: f"{x['ID_Gaveta']} - {x['Nome_Gaveta']} (Local: {x['Localizacao']})",
        axis=1,
    ).tolist()

    gaveta_selecionada_str = st.selectbox(
        "🎯 Selecione a Gaveta para Movimentação de Materiais:", gavetas_opcoes
    )
    id_gaveta_atual = gaveta_selecionada_str.split(" - ")[0]

    # Exibe destaque do local atual da gaveta selecionada
    dados_gaveta = st.session_state.gavetas[
        st.session_state.gavetas["ID_Gaveta"] == id_gaveta_atual
    ].iloc[0]
    st.info(
        f"**Gaveta Ativa:** {dados_gaveta['ID_Gaveta']} | **Localização Física"
        f" de Armazenagem:** 📍 {dados_gaveta['Localizacao']} | **Status:**"
        f" {dados_gaveta['Status']}"
    )

    st.markdown("---")
    st.subheader(f"➕ Registrar Material na Gaveta: {id_gaveta_atual}")

    with st.form("form_movimentacao"):
      col1, col2, col3 = st.columns(3)
      with col1:
        id_material = st.text_input("ID do Material (Ex: MAT-01)")
        desc_mat = st.text_input("Descrição do Material")
      with col2:
        marca = st.text_input("Marca / Fabricante")
        lote = st.text_input("Número do Lote")
      with col3:
        dt_fab = st.date_input("Data de Fabricação")
        dt_val = st.date_input("Data de Validade")

      st.markdown("### 📦 Quantidades e Unidades")
      c1, c2, c3, c4 = st.columns(4)
      with c1:
        qtd_paletes = st.number_input("Qtd de Volumes", min_value=1, value=1)
      with c2:
        qtd_emb = st.number_input("Embalagens/Volume", min_value=1, value=1)
      with c3:
        peso_unit = st.number_input("Peso/Qtd Unitária (KG/UN)", value=25.0)
      with c4:
        operacao = st.selectbox("Tipo de Operação", ["Entrada (+)", "Saída (-)"])

      salvar = st.form_submit_button("💾 Salvar Registro na Gaveta")

      if salvar:
        total_qtd = qtd_paletes * qtd_emb * peso_unit
        nova_mov = pd.DataFrame(
            [[
                id_gaveta_atual,
                id_material,
                desc_mat,
                marca,
                lote,
                dt_fab,
                dt_val,
                total_qtd,
                "KG/UN",
                operacao,
            ]],
            columns=st.session_state.movimentacoes.columns,
        )
        st.session_state.movimentacoes = pd.concat(
            [st.session_state.movimentacoes, nova_mov], ignore_index=True
        )
        st.success(
            f"Material registrado na gaveta e vinculado ao local:"
            f" {dados_gaveta['Localizacao']}!"
        )
        st.rerun()

    st.markdown("---")
    st.subheader(f"📊 Materiais Armazenados na {id_gaveta_atual}")
    movs_gaveta = st.session_state.movimentacoes[
        st.session_state.movimentacoes["ID_Gaveta"] == id_gaveta_atual
    ]
    if not movs_gaveta.empty:
      st.dataframe(movs_gaveta, use_container_width=True)
    else:
      st.info("Esta gaveta ainda não possui materiais armazenados.")

# -------------------------------------------------------------
# 3. DASHBOARD & INDICADORES (Rastreamento Global)
# -------------------------------------------------------------
elif menu == "📊 Dashboard & Indicadores":
  st.header("📊 Dashboard Geral de Rastreabilidade")
  st.markdown(
      "Visão consolidada unindo cada material diretamente ao seu"
      " **Local de Armazenagem** físico."
  )

  if not st.session_state.movimentacoes.empty and not st.session_state.gavetas.empty:
    # Cruza os dados das movimentações com o cadastro de gavetas e locais
    df_completo = pd.merge(
        st.session_state.movimentacoes,
        st.session_state.gavetas[["ID_Gaveta", "Nome_Gaveta", "Localizacao"]],
        on="ID_Gaveta",
        how="left",
    )
    st.subheader("🔍 Mapa Completo de Rastreio (Gaveta + Localização)")
    st.dataframe(df_completo, use_container_width=True)
  else:
    st.info(
        "Cadastre gavetas e registre materiais para visualizar o mapa de"
        " rastreio completo."
    )
      
