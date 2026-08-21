from datetime import datetime
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
    .main {
        background-color: #f8f6f0;
    }
    h1, h2, h3 {
        color: #3b2716 !important;
        font-family: 'Georgia', serif;
    }
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
      columns=["Nome_Gaveta", "Localizacao", "Descricao", "Status"]
  )
  st.session_state.gavetas.loc[0] = [
      "Gaveta de Insumos Básicos",
      "Galpão 1 - Corredor A - Estante 2",
      "Insumos gerais",
      "Ativa",
  ]

if "materiais_gaveta" not in st.session_state:
  st.session_state.materiais_gaveta = pd.DataFrame(
      columns=[
          "Nome_Gaveta",
          "ID_Material",
          "Descricao",
          "Marca",
          "Lote",
          "Total1",
          "Total2",
          "Total3",
          "Entradas",
          "Saidas",
          "Data_Hora_Movimentacao",
          "Curva_ABC",
      ]
  )
  st.session_state.materiais_gaveta.loc[0] = [
      "Gaveta de Insumos Básicos",
      "MAT-001",
      "Cimento Especial",
      "Alpha",
      "LOTE-99",
      2.0,
      5.0,
      10.0,
      100.0,
      20.0,
      datetime.now(),
      "A",
  ]

# Menu Lateral Estilizado
st.sidebar.title("📦 BUILD STOCK")
st.sidebar.markdown("---")
st.sidebar.markdown("Sistema de Arquivo & Rastreio")
menu = st.sidebar.radio(
    "Navegação:",
    ["🗄️ Arquivo & Tabela de Gavetas", "📊 Dashboard", "⚙️ Gerenciar Gavetas"],
)

# -------------------------------------------------------------
# 1. GERENCIAR GAVETAS (Criar e Excluir)
# -------------------------------------------------------------
if menu == "⚙️ Gerenciar Gavetas":
  st.header("⚙️ Gerenciamento de Gavetas / Arquivos")
  st.markdown("Crie novas gavetas ou remova compartimentos existentes.")

  with st.form("form_nova_gaveta"):
    col1, col2 = st.columns(2)
    with col1:
      nome_gaveta = st.text_input("🏷️ Nome da Gaveta (Ex: Ferramentas)")
    with col2:
      localizacao = st.text_input(
          "📍 Local de Armazenagem (Ex: Galpão B, Estante 3)"
      )

    status = st.selectbox("Status", ["Ativa", "Manutenção", "Inativa"])
    descricao_gaveta = st.text_area("Observações")
    submitted = st.form_submit_button("💾 Criar Nova Gaveta")

    if submitted:
      if nome_gaveta and localizacao:
        if nome_gaveta in st.session_state.gavetas["Nome_Gaveta"].values:
          st.error("Já existe uma gaveta com este nome!")
        else:
          nova_linha = pd.DataFrame(
              [[nome_gaveta, localizacao, descricao_gaveta, status]],
              columns=st.session_state.gavetas.columns,
          )
          st.session_state.gavetas = pd.concat(
              [st.session_state.gavetas, nova_linha], ignore_index=True
          )
          st.success(f"Gaveta '{nome_gaveta}' criada com sucesso!")
          st.rerun()
      else:
        st.warning("Preencha o Nome e o Local de Armazenagem.")

  st.markdown("---")
  st.subheader("🗑️ Excluir Gaveta Existente")
  if not st.session_state.gavetas.empty:
    gaveta_para_excluir = st.selectbox(
        "Selecione a gaveta para remover:",
        st.session_state.gavetas["Nome_Gaveta"].tolist(),
    )
    if st.button("❌ Excluir Gaveta Selecionada"):
      st.session_state.gavetas = st.session_state.gavetas[
          st.session_state.gavetas["Nome_Gaveta"] != gaveta_para_excluir
      ]
      st.session_state.materiais_gaveta = st.session_state.materiais_gaveta[
          st.session_state.materiais_gaveta["Nome_Gaveta"] != gaveta_para_excluir
      ]
      st.success(f"Gaveta '{gaveta_para_excluir}' excluída com sucesso!")
      st.rerun()
  else:
    st.info("Nenhuma gaveta cadastrada.")

# -------------------------------------------------------------
# 2. ARQUIVO & TABELA DE GAVETAS (Gestão Interna de Cada Gaveta)
# -------------------------------------------------------------
elif menu == "🗄️ Arquivo & Tabela de Gavetas":
  st.header("🗄️ Arquivo de Gavetas - Tabela Interna de Materiais")
  st.markdown(
      "Selecione uma gaveta para gerenciar os itens e visualizar todos os"
      " cálculos."
  )

  if st.session_state.gavetas.empty:
    st.warning("Cadastre pelo menos uma gaveta na aba 'Gerenciar Gavetas'.")
  else:
    # Seletor de Gaveta
    gavetas_opcoes = st.session_state.gavetas.apply(
        lambda x: f"{x['Nome_Gaveta']} (📍 Local: {x['Localizacao']})", axis=1
    ).tolist()
    gaveta_selecionada_str = st.selectbox(
        "🎯 Selecione a Gaveta:", gavetas_opcoes
    )
    nome_gaveta_atual = gaveta_selecionada_str.split(" (📍 Local:")[0]

    # Dados da gaveta ativa
    dados_gaveta = st.session_state.gavetas[
        st.session_state.gavetas["Nome_Gaveta"] == nome_gaveta_atual
    ].iloc[0]
    st.info(
        f"**Gaveta Ativa:** {nome_gaveta_atual} | **Local de Armazenagem:** 📍"
        f" {dados_gaveta['Localizacao']}"
    )

    st.markdown("---")
    st.subheader(f"➕ Adicionar Material na Tabela da Gaveta")

    with st.form("form_adicionar_material"):
      c1, c2, c3 = st.columns(3)
      with c1:
        id_material = st.text_input("🆔 ID do Material")
        desc = st.text_input("Descrição")
      with c2:
        marca = st.text_input("Marca")
        lote = st.text_input("Lote")
      with c3:
        curva_abc = st.selectbox("Curva ABC", ["A", "B", "C"])

      st.markdown("### 🔢 Fatores de Multiplicação e Movimentação")
      col_t1, col_t2, col_t3, col_ent, col_sai = st.columns(5)
      with col_t1:
        total1 = st.number_input("Total 1", value=1.0, min_value=0.0)
      with col_t2:
        total2 = st.number_input("Total 2", value=1.0, min_value=0.0)
      with col_t3:
        total3 = st.number_input("Total 3", value=1.0, min_value=0.0)
      with col_ent:
        entradas = st.number_input("Entradas", value=0.0, min_value=0.0)
      with col_sai:
        saidas = st.number_input("Saídas", value=0.0, min_value=0.0)

      btn_salvar = st.form_submit_button(
          "💾 Salvar Novo Material (IDs duplicados permitidos)"
      )

      if btn_salvar:
        if id_material:
          # Permite IDs repetidos sem restrição alguma
          data_hora_atual = datetime.now()
          novo_item = pd.DataFrame(
              [[
                  nome_gaveta_atual,
                  id_material,
                  desc,
                  marca,
                  lote,
                  total1,
                  total2,
                  total3,
                  entradas,
                  saidas,
                  data_hora_atual,
                  curva_abc,
              ]],
              columns=st.session_state.materiais_gaveta.columns,
          )
          st.session_state.materiais_gaveta = pd.concat(
              [st.session_state.materiais_gaveta, novo_item], ignore_index=True
          )
          st.success("Material adicionado com sucesso!")
          st.rerun()
        else:
          st.warning("O campo ID do Material é obrigatório.")

    st.markdown("---")
    st.subheader(f"📊 Tabela de Estoque da Gaveta: {nome_gaveta_atual}")

    # Filtra os materiais da gaveta selecionada mantendo o índice original para referência
    df_tabela = st.session_state.materiais_gaveta[
        st.session_state.materiais_gaveta["Nome_Gaveta"] == nome_gaveta_atual
    ].copy()

    if not df_tabela.empty:
      # Cálculos
      df_tabela["Total em Estoque"] = (
          df_tabela["Total1"] * df_tabela["Total2"] * df_tabela["Total3"]
      )
      df_tabela["Saldo em Estoque"] = (
          df_tabela["Total em Estoque"]
          + df_tabela["Entradas"]
          - df_tabela["Saidas"]
      )

      agora = pd.to_datetime(datetime.now())
      df_tabela["Data_Hora_Movimentacao"] = pd.to_datetime(
          df_tabela["Data_Hora_Movimentacao"]
      )
      diferenca = agora - df_tabela["Data_Hora_Movimentacao"]
      df_tabela["Tempo no Estoque"] = (
          diferenca.dt.days.astype(str)
          + " dias, "
          + (diferenca.dt.seconds // 3600).astype(str)
          + "h"
      )

      df_tabela["Data/Hora Registro"] = df_tabela[
          "Data_Hora_Movimentacao"
      ].dt.strftime("%d/%m/%Y %H:%M:%S")
      df_tabela["Local de Armazenagem"] = dados_gaveta["Localizacao"]

      # Mantemos o índice visível/mapeado para permitir seleção sem conflito de IDs repetidos
      df_tabela["Indice_Original"] = df_tabela.index

      colunas_exibicao = [
          "Indice_Original",
          "ID_Material",
          "Descricao",
          "Marca",
          "Lote",
          "Total1",
          "Total2",
          "Total3",
          "Total em Estoque",
          "Entradas",
          "Saidas",
          "Saldo em Estoque",
          "Curva_ABC",
          "Data/Hora Registro",
          "Tempo no Estoque",
          "Local de Armazenagem",
      ]

      st.dataframe(df_tabela[colunas_exibicao], use_container_width=True)

      # Opções baseadas no índice exato da linha para evitar travar com IDs repetidos
      opcoes_linhas = {
          f"Linha {idx}: ID [{row['ID_Material']}] - {row['Descricao']} (Marca: {row['Marca']})": idx
          for idx, row in df_tabela.iterrows()
      }

      # -------------------------------------------------------------
      # EDITAR REGISTRO EXISTENTE POR LINHA EXATA
      # -------------------------------------------------------------
      st.markdown("---")
      st.subheader(
          "✏️ Editar Multiplicação e Movimentação (Por Item Específico)"
      )

      if opcoes_linhas:
        escolha_edicao = st.selectbox(
            "Selecione exatamente qual linha deseja editar:",
            list(opcoes_linhas.keys()),
            key="select_editar_linha",
        )
        idx_selecionado = opcoes_linhas[escolha_edicao]
        item_atual = st.session_state.materiais_gaveta.loc[idx_selecionado]

        with st.form("form_editar_material"):
          st.markdown(
              f"Editando: **ID {item_atual['ID_Material']} - {item_atual['Descricao']}** (Marca: {item_atual['Marca']})"
          )
          c_e1, c_e2, c_e3, c_e4, c_e5 = st.columns(5)
          with c_e1:
            novo_t1 = st.number_input(
                "Total 1", value=float(item_atual["Total1"]), min_value=0.0
            )
          with c_e2:
            novo_t2 = st.number_input(
                "Total 2", value=float(item_atual["Total2"]), min_value=0.0
            )
          with c_e3:
            novo_t3 = st.number_input(
                "Total 3", value=float(item_atual["Total3"]), min_value=0.0
            )
          with c_e4:
            nova_entrada = st.number_input(
                "Entradas", value=float(item_atual["Entradas"]), min_value=0.0
            )
          with c_e5:
            nova_saida = st.number_input(
                "Saídas", value=float(item_atual["Saidas"]), min_value=0.0
            )

          btn_atualizar = st.form_submit_button(
              "🔄 Atualizar Este Registro (Atualiza Data/Hora)"
          )

          if btn_atualizar:
            st.session_state.materiais_gaveta.loc[idx_selecionado, "Total1"] = (
                novo_t1
            )
            st.session_state.materiais_gaveta.loc[idx_selecionado, "Total2"] = (
                novo_t2
            )
            st.session_state.materiais_gaveta.loc[idx_selecionado, "Total3"] = (
                novo_t3
            )
            st.session_state.materiais_gaveta.loc[
                idx_selecionado, "Entradas"
            ] = nova_entrada
            st.session_state.materiais_gaveta.loc[idx_selecionado, "Saidas"] = (
                nova_saida
            )
            st.session_state.materiais_gaveta.loc[
                idx_selecionado, "Data_Hora_Movimentacao"
            ] = datetime.now()

            st.success(
                "Registro atualizado com sucesso (Nova data/hora registrada)!"
            )
            st.rerun()

      # -------------------------------------------------------------
      # EXCLUIR REGISTRO POR LINHA EXATA
      # -------------------------------------------------------------
      st.markdown("---")
      st.subheader("🗑️ Excluir Registro Específico da Tabela")

      escolha_exclusao = st.selectbox(
          "Selecione exatamente qual linha deseja excluir:",
          list(opcoes_linhas.keys()),
          key="select_excluir_linha",
      )
      idx_excluir = opcoes_linhas[escolha_exclusao]

      if st.button("❌ Excluir Este Registro"):
        st.session_state.materiais_gaveta = (
            st.session_state.materiais_gaveta.drop(idx_excluir)
        )
        st.success("Registro excluído com sucesso!")
        st.rerun()

    else:
      st.info("Nenhum material cadastrado nesta gaveta ainda.")

# -------------------------------------------------------------
# 3. DASHBOARD GLOBAL
# -------------------------------------------------------------
elif menu == "📊 Dashboard":
  st.header("📊 Dashboard Geral do Almoxarifado")
  st.markdown("Visão consolidada de todos os materiais e locais.")

  if not st.session_state.materiais_gaveta.empty:
    df_global = st.session_state.materiais_gaveta.copy()
    df_global["Total em Estoque"] = (
        df_global["Total1"] * df_global["Total2"] * df_global["Total3"]
    )
    df_global["Saldo em Estoque"] = (
        df_global["Total em Estoque"]
        + df_global["Entradas"]
        - df_global["Saidas"]
    )

    df_global["Data/Hora Registro"] = pd.to_datetime(
        df_global["Data_Hora_Movimentacao"]
    ).dt.strftime("%d/%m/%Y %H:%M:%S")

    df_global = pd.merge(
        df_global,
        st.session_state.gavetas[["Nome_Gaveta", "Localizacao"]],
        on="Nome_Gaveta",
        how="left",
    )
    df_global.rename(
        columns={"Localizacao": "Local de Armazenagem"}, inplace=True
    )

    colunas_dash = [
        "Nome_Gaveta",
        "ID_Material",
        "Descricao",
        "Marca",
        "Lote",
        "Total em Estoque",
        "Entradas",
        "Saidas",
        "Saldo em Estoque",
        "Curva_ABC",
        "Data/Hora Registro",
        "Local de Armazenagem",
    ]

    st.dataframe(df_global[colunas_dash], use_container_width=True)
  else:
    st.info("Nenhum dado registrado para exibir no dashboard.")
