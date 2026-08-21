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
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CONTROLE DE ACESSO / LOGIN DE ADMINISTRADOR
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

# Senha padrão de Administrador (Você pode alterar aqui se desejar)
SENHA_ADMIN = "admin123"

st.sidebar.title("📦 BUILD STOCK")
st.sidebar.markdown("---")

if not st.session_state.autenticado:
  st.sidebar.subheader("🔒 Acesso Restrito")
  senha_digitada = st.sidebar.text_input(
      "Digite a Senha do Administrador:", type="password"
  )
  if st.sidebar.button("🔓 Entrar"):
    if senha_digitada == SENHA_ADMIN:
      st.session_state.autenticado = True
      st.sidebar.success("Acesso liberado!")
      st.rerun()
    else:
      st.sidebar.error("Senha incorreta!")

  # Tela inicial bloqueada
  st.title("📦 BUILD STOCK - Controle de Almoxarifado")
  st.warning(
      "⚠️ O sistema está protegido. Por favor, digite a senha de administrador"
      " na barra lateral para acessar o aplicativo."
  )
  st.stop()

# Se o usuário estiver autenticado, exibe o menu completo
st.sidebar.success("✅ Sessão de Administrador Ativa")
if st.sidebar.button("🔒 Sair / Bloquear"):
  st.session_state.autenticado = False
  st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação:",
    ["🗄️ Arquivo & Tabela de Gavetas", "📊 Dashboard", "⚙️ Gerenciar Gavetas"],
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
          "Unidade_Medida",
          "Total1",
          "Total2",
          "Total3",
          "Entradas",
          "Saidas",
          "Data_Hora_Movimentacao",
      ]
  )
  st.session_state.materiais_gaveta.loc[0] = [
      "Gaveta de Insumos Básicos",
      "MAT-001",
      "Cimento Especial",
      "Alpha",
      "LOTE-99",
      "Unidades",
      2.0,
      5.0,
      10.0,
      100.0,
      20.0,
      datetime.now(),
  ]


def calcular_curva_abc_serie(serie_totais):
  if serie_totais.empty or serie_totais.sum() == 0:
    return ["C"] * len(serie_totais)

  df_temp = pd.DataFrame({"valor": serie_totais})
  df_temp = df_temp.sort_values(by="valor", ascending=False)
  total_geral = df_temp["valor"].sum()

  acumulado = 0
  curvas = []
  for val in df_temp["valor"]:
    acumulado += val
    perc = (acumulado / total_geral) * 100 if total_geral > 0 else 0
    if perc <= 70:
      curvas.append("A (Alto Impacto)")
    elif perc <= 90:
      curvas.append("B (Médio Impacto)")
    else:
      curvas.append("C (Baixo Impacto)")

  df_temp["Curva"] = curvas
  return df_temp.loc[serie_totais.index, "Curva"]


# -------------------------------------------------------------
# 1. GERENCIAR GAVETAS (Criar, Editar Nomes e Excluir)
# -------------------------------------------------------------
if menu == "⚙️ Gerenciar Gavetas":
  st.header("⚙️ Gerenciamento e Edição de Gavetas")
  st.markdown("Crie, edite os nomes/locais ou remova compartimentos.")

  # Criar Nova Gaveta
  with st.form("form_nova_gaveta"):
    st.subheader("➕ Criar Nova Gaveta")
    col1, col2 = st.columns(2)
    with col1:
      nome_gaveta = st.text_input("🏷️ Nome da Gaveta")
    with col2:
      localizacao = st.text_input("📍 Local de Armazenagem")

    status = st.selectbox("Status", ["Ativa", "Manutenção", "Inativa"])
    descricao_gaveta = st.text_area("Observações")
    submitted = st.form_submit_button("💾 Criar Gaveta")

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
        st.warning("Preencha o Nome e o Local.")

  st.markdown("---")

  # Editar Gaveta Existente
  st.subheader("✏️ Editar Nome ou Local de uma Gaveta")
  if not st.session_state.gavetas.empty:
    gaveta_editar = st.selectbox(
        "Selecione a gaveta para editar:",
        st.session_state.gavetas["Nome_Gaveta"].tolist(),
    )
    dados_atual_g = st.session_state.gavetas[
        st.session_state.gavetas["Nome_Gaveta"] == gaveta_editar
    ].iloc[0]

    with st.form("form_editar_gaveta"):
      novo_nome_gaveta = st.text_input(
          "Novo Nome da Gaveta", value=dados_atual_g["Nome_Gaveta"]
      )
      nova_local_gaveta = st.text_input(
          "Nova Localização", value=dados_atual_g["Localizacao"]
      )
      novo_status = st.selectbox(
          "Status",
          ["Ativa", "Manutenção", "Inativa"],
          index=["Ativa", "Manutenção", "Inativa"].index(
              dados_atual_g["Status"]
              if dados_atual_g["Status"]
              in ["Ativa", "Manutenção", "Inativa"]
              else "Ativa"
          ),
      )
      btn_salvar_g = st.form_submit_button("🔄 Atualizar Gaveta")

      if btn_salvar_g:
        idx_g = st.session_state.gavetas[
            st.session_state.gavetas["Nome_Gaveta"] == gaveta_editar
        ].index[0]
        # Atualiza também nas referências de materiais vinculados
        st.session_state.materiais_gaveta.loc[
            st.session_state.materiais_gaveta["Nome_Gaveta"] == gaveta_editar,
            "Nome_Gaveta",
        ] = novo_nome_gaveta

        st.session_state.gavetas.loc[idx_g, "Nome_Gaveta"] = novo_nome_gaveta
        st.session_state.gavetas.loc[idx_g, "Localizacao"] = nova_local_gaveta
        st.session_state.gavetas.loc[idx_g, "Status"] = novo_status

        st.success("Gaveta atualizada com sucesso!")
        st.rerun()

  st.markdown("---")
  st.subheader("🗑️ Excluir Gaveta")
  if not st.session_state.gavetas.empty:
    gaveta_para_excluir = st.selectbox(
        "Selecione a gaveta para remover:",
        st.session_state.gavetas["Nome_Gaveta"].tolist(),
        key="del_gaveta",
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
# 2. ARQUIVO & TABELA DE GAVETAS
# -------------------------------------------------------------
elif menu == "🗄️ Arquivo & Tabela de Gavetas":
  st.header("🗄️ Tabela Interna de Materiais")
  st.markdown("Gerencie os itens da gaveta selecionada.")

  if st.session_state.gavetas.empty:
    st.warning("Cadastre pelo menos uma gaveta na aba 'Gerenciar Gavetas'.")
  else:
    gavetas_opcoes = st.session_state.gavetas.apply(
        lambda x: f"{x['Nome_Gaveta']} (📍 Local: {x['Localizacao']})", axis=1
    ).tolist()
    gaveta_selecionada_str = st.selectbox(
        "🎯 Selecione a Gaveta:", gavetas_opcoes
    )
    nome_gaveta_atual = gaveta_selecionada_str.split(" (📍 Local:")[0]

    dados_gaveta = st.session_state.gavetas[
        st.session_state.gavetas["Nome_Gaveta"] == nome_gaveta_atual
    ].iloc[0]
    st.info(
        f"**Gaveta Ativa:** {nome_gaveta_atual} | **Local:** 📍"
        f" {dados_gaveta['Localizacao']}"
    )

    st.markdown("---")
    st.subheader("➕ Adicionar Material na Tabela da Gaveta")

    with st.form("form_adicionar_material"):
      c1, c2, c3 = st.columns(3)
      with c1:
        id_material = st.text_input("🆔 ID do Material")
        desc = st.text_input("Descrição")
      with c2:
        marca = st.text_input("Marca")
        lote = st.text_input("Lote")
      with c3:
        unidade_medida = st.selectbox(
            "📐 Unidade de Medida",
            [
                "Unidades",
                "M² (Metro Quadrado)",
                "M (Metros Lineares)",
                "Kilos (kg)",
                "Peças",
                "Rolos",
                "Caixas",
                "Litros",
                "Sacos",
            ],
        )

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
          data_hora_atual = datetime.now()
          novo_item = pd.DataFrame(
              [[
                  nome_gaveta_atual,
                  id_material,
                  desc,
                  marca,
                  lote,
                  unidade_medida,
                  total1,
                  total2,
                  total3,
                  entradas,
                  saidas,
                  data_hora_atual,
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

    df_tabela = st.session_state.materiais_gaveta[
        st.session_state.materiais_gaveta["Nome_Gaveta"] == nome_gaveta_atual
    ].copy()

    if not df_tabela.empty:
      df_tabela["Total em Estoque"] = (
          df_tabela["Total1"] * df_tabela["Total2"] * df_tabela["Total3"]
      )
      df_tabela["Saldo em Estoque"] = (
          df_tabela["Total em Estoque"]
          + df_tabela["Entradas"]
          - df_tabela["Saidas"]
      )
      df_tabela["Curva_ABC"] = calcular_curva_abc_serie(
          df_tabela["Total em Estoque"]
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
      df_tabela["Indice_Original"] = df_tabela.index

      colunas_exibicao = [
          "Indice_Original",
          "ID_Material",
          "Descricao",
          "Marca",
          "Lote",
          "Unidade_Medida",
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

      opcoes_linhas = {
          f"Linha {idx}: ID [{row['ID_Material']}] - {row['Descricao']} (Marca: {row['Marca']})": idx
          for idx, row in df_tabela.iterrows()
      }

      st.markdown("---")
      st.subheader("✏️ Editar Material (Unidade, Multiplicação e Movimentação)")

      if opcoes_linhas:
        escolha_edicao = st.selectbox(
            "Selecione exatamente qual linha deseja editar:",
            list(opcoes_linhas.keys()),
            key="select_editar_linha",
        )
        idx_selecionado = opcoes_linhas[escolha_edicao]
        item_atual = st.session_state.materiais_gaveta.loc[idx_selecionado]

        lista_unidades = [
            "Unidades",
            "M² (Metro Quadrado)",
            "M (Metros Lineares)",
            "Kilos (kg)",
            "Peças",
            "Rolos",
            "Caixas",
            "Litros",
            "Sacos",
        ]
        unidade_atual_val = (
            item_atual["Unidade_Medida"]
            if item_atual["Unidade_Medida"] in lista_unidades
            else "Unidades"
        )

        with st.form("form_editar_material"):
          st.markdown(
              f"Editando: **ID {item_atual['ID_Material']} - {item_atual['Descricao']}**"
          )
          c_u1, c_u2 = st.columns(2)
          with c_u1:
            nova_unidade = st.selectbox(
                "📐 Unidade de Medida",
                lista_unidades,
                index=lista_unidades.index(unidade_atual_val),
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

          btn_atualizar = st.form_submit_button("🔄 Atualizar Este Registro")

          if btn_atualizar:
            st.session_state.materiais_gaveta.loc[
                idx_selecionado, "Unidade_Medida"
            ] = nova_unidade
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

            st.success("Registro atualizado com sucesso!")
            st.rerun()

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
  st.markdown("Visão consolidada e gráficos analíticos.")

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
    df_global["Curva_ABC"] = calcular_curva_abc_serie(
        df_global["Total em Estoque"]
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

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
      st.metric("Total de Registros/Itens", len(df_global))
    with col_m2:
      st.metric("Volume Geral em Estoque", f"{df_global['Saldo em Estoque'].sum():,.2f}")
    with col_m3:
      st.metric("Gavetas Ativas", len(st.session_state.gavetas))

    st.markdown("---")
    st.subheader("📈 Gráficos Analíticos")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
      st.markdown("#### Saldo em Estoque por Material")
      df_chart_estoque = df_global.set_index("Descricao")["Saldo em Estoque"]
      st.bar_chart(df_chart_estoque)

    with col_g2:
      st.markdown("#### Entradas vs Saídas Globais")
      df_chart_mov = df_global.set_index("Descricao")[["Entradas", "Saidas"]]
      st.bar_chart(df_chart_mov)

    st.markdown("---")
    st.subheader("📋 Tabela Geral Consolidada")
    colunas_dash = [
        "Nome_Gaveta",
        "ID_Material",
        "Descricao",
        "Marca",
        "Lote",
        "Unidade_Medida",
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
