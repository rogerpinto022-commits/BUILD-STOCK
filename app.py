from datetime import datetime
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="BUILD STOCK - Armário Inteligente", page_icon="📦", layout="wide"
)

# Estilização Visual Customizada
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
        background-color: #ffffff;
        border: 2px solid #d4c5b9;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CONTROLE DE ACESSO
# -------------------------------------------------------------
if "emails_permitidos" not in st.session_state:
  st.session_state.emails_permitidos = [
      "admin@buildstock.com",
      "gerente@buildstock.com",
  ]

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
  st.session_state.usuario_logado = ""

SENHA_ADMIN = "admin123"

st.sidebar.title("📦 BUILD STOCK")
st.sidebar.markdown("---")

if not st.session_state.autenticado:
  st.sidebar.subheader("🔒 Acesso Restrito")
  email_digitado = st.sidebar.text_input("Seu E-mail:")
  senha_digitada = st.sidebar.text_input(
      "Senha do Administrador:", type="password"
  )

  if st.sidebar.button("🔓 Entrar"):
    if senha_digitada == SENHA_ADMIN:
      if email_digitado.strip().lower() in [
          e.lower() for e in st.session_state.emails_permitidos
      ]:
        st.session_state.autenticado = True
        st.session_state.usuario_logado = email_digitado
        st.sidebar.success("Acesso liberado!")
        st.rerun()
      else:
        st.sidebar.error(
            "⚠️ Este e-mail não está autorizado a acessar o aplicativo."
        )
    else:
      st.sidebar.error("Senha incorreta!")

  st.title("📦 BUILD STOCK - Controle de Almoxarifado")
  st.warning(
      "⚠️ O sistema é restrito. Digite seu e-mail autorizado e a senha de"
      " administrador na barra lateral."
  )
  st.stop()

st.sidebar.success(f"✅ Conectado como:\n{st.session_state.usuario_logado}")
if st.sidebar.button("🔒 Sair / Bloquear"):
  st.session_state.autenticado = False
  st.session_state.usuario_logado = ""
  st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "🗄️ Armário (Gavetas Visuais)",
        "📊 Dashboard Geral",
        "⚙️ Gerenciar Gavetas",
        "👥 Controle de E-mails",
    ],
)

# Inicialização do Banco de Dados em Memória (Session State)
if "gavetas" not in st.session_state:
  st.session_state.gavetas = pd.DataFrame(
      columns=["Nome_Gaveta", "Localizacao", "Descricao", "Status"]
  )
  st.session_state.gavetas.loc[0] = [
      "Gaveta de Cimentos",
      "Galpão 1 - Corredor A",
      "Estoque de cimentos e ligas",
      "Ativa",
  ]

if "materiais_gaveta" not in st.session_state:
  st.session_state.materiais_gaveta = pd.DataFrame(
      columns=[
          "Nome_Gaveta",
          "ID",
          "DESCRIÇÃO",
          "MARCA",
          "LOTE",
          "VALIDADE",
          "QTD/PALETE",
          "ENTRADA",
          "PESO UNITÁRIO",
          "TOTAL",
          "UNIDADE DE MEDIDA",
          "LOCAL DE ARMAZENAGEM",
          "DATA HORA",
      ]
  )
  st.session_state.materiais_gaveta.loc[0] = [
      "Gaveta de Cimentos",
      "1",
      "CIMENTO",
      "FONDU",
      "010101",
      "2027-12-31",
      56.0,
      10.0,
      25.0,
      14000.0,
      "KG",
      "Galpão 1 - Corredor A",
      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  ]

if "gaveta_selecionada_ativa" not in st.session_state:
  st.session_state.gaveta_selecionada_ativa = None


# -------------------------------------------------------------
# 1. CONTROLE DE E-MAILS
# -------------------------------------------------------------
if menu == "👥 Controle de E-mails":
  st.header("👥 Gerenciamento de Acessos por E-mail")
  with st.form("form_adicionar_email"):
    novo_email = st.text_input("Digite o e-mail do usuário:")
    btn_add_email = st.form_submit_button("💾 Liberar Acesso")
    if btn_add_email:
      if novo_email and "@" in novo_email:
        if novo_email.lower() in [
            e.lower() for e in st.session_state.emails_permitidos
        ]:
          st.warning("Este e-mail já está cadastrado!")
        else:
          st.session_state.emails_permitidos.append(novo_email.strip())
          st.success(f"E-mail '{novo_email}' adicionado com sucesso!")
          st.rerun()
      else:
        st.error("Digite um e-mail válido.")

  st.markdown("---")
  if st.session_state.emails_permitidos:
    df_emails = pd.DataFrame(
        st.session_state.emails_permitidos, columns=["E-mail Autorizado"]
    )
    st.dataframe(df_emails, use_container_width=True)
    email_remover = st.selectbox(
        "Selecione um e-mail para remover o acesso:",
        st.session_state.emails_permitidos,
    )
    if st.button("❌ Revogar Acesso"):
      if len(st.session_state.emails_permitidos) <= 1:
        st.error("Você precisa manter pelo menos um e-mail cadastrado.")
      else:
        st.session_state.emails_permitidos.remove(email_remover)
        st.success("Acesso revogado com sucesso!")
        st.rerun()

# -------------------------------------------------------------
# 2. GERENCIAR GAVETAS
# -------------------------------------------------------------
elif menu == "⚙️ Gerenciar Gavetas":
  st.header("⚙️ Cadastro de Novas Gavetas no Armário")

  with st.form("form_nova_gaveta"):
    nome_gaveta = st.text_input("🏷️ Nome da Gaveta (Ex: Gaveta de Cimentos)")
    localizacao = st.text_input("📍 Local de Armazenagem")
    status = st.selectbox("Status", ["Ativa", "Manutenção", "Inativa"])
    descricao_gaveta = st.text_area("Observações da Gaveta")
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
  st.subheader("🗑️ Excluir Gaveta")
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
      st.success("Gaveta excluída com sucesso!")
      st.rerun()

# -------------------------------------------------------------
# 3. ARMÁRIO VISUAL E TABELAS DE CADA GAVETA
# -------------------------------------------------------------
elif menu == "🗄️ Armário (Gavetas Visuais)":
  st.header("🗄️ Armário Inteligente de Gavetas")

  if st.session_state.gavetas.empty:
    st.warning(
        "Nenhuma gaveta criada ainda. Vá até a aba 'Gerenciar Gavetas' para"
        " criar a primeira."
    )
  else:
    if st.session_state.gaveta_selecionada_ativa is None:
      cols = st.columns(3)
      for idx, row in st.session_state.gavetas.iterrows():
        with cols[idx % 3]:
          st.markdown(
              f"""
                    <div class="gaveta-card">
                        <h3>🗄️ {row['Nome_Gaveta']}</h3>
                        <p><b>Local:</b> {row['Localizacao']}</p>
                        <p><b>Status:</b> {row['Status']}</p>
                        <p><i>{row['Descricao']}</i></p>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
          if st.button(
              f"📂 Abrir Tabela: {row['Nome_Gaveta']}", key=f"btn_gav_{idx}"
          ):
            st.session_state.gaveta_selecionada_ativa = row["Nome_Gaveta"]
            st.rerun()
    else:
      nome_gaveta_atual = st.session_state.gaveta_selecionada_ativa
      dados_gaveta = st.session_state.gavetas[
          st.session_state.gavetas["Nome_Gaveta"] == nome_gaveta_atual
      ].iloc[0]

      if st.button("⬅️ Voltar para o Armário de Gavetas"):
        st.session_state.gaveta_selecionada_ativa = None
        st.rerun()

      st.markdown("---")
      st.subheader(f"📂 Gaveta Ativa: {nome_gaveta_atual}")
      st.info(
          f"📍 *Localização:* {dados_gaveta['Localizacao']} | 📝"
          f" *Descrição:* {dados_gaveta['Descricao']}"
      )

      # ➕ Adicionar Novo Lançamento de Material (Incluindo UNIDADES)
      with st.expander("➕ Adicionar Novo Lançamento de Material"):
        with st.form("form_novo_registro"):
          id_mat = st.text_input("ID", value="1")
          descricao = st.text_input("DESCRIÇÃO", value="CIMENTO")
          marca = st.text_input("MARCA", value="FONDU")
          lote = st.text_input("LOTE", value="010101")
          validade = st.date_input("VALIDADE")
          qtd_palete = st.number_input(
              "QTD/PALETE (Sacos por Palete)", value=56.0, min_value=0.0
          )
          entrada = st.number_input(
              "ENTRADA (Qtd Recebida de Paletes)", value=10.0, min_value=0.0
          )
          peso_unitario = st.number_input(
              "PESO UNITÁRIO (Peso de cada saco/unidade)",
              value=25.0,
              min_value=0.0,
          )
          unidade_medida = st.selectbox(
              "UNIDADE DE MEDIDA",
              ["KG", "TON", "SACOS", "UNIDADES", "LITROS", "M²"],
          )
          local_armazenagem = st.text_input(
              "LOCAL DE ARMAZENAGEM", value=dados_gaveta["Localizacao"]
          )

          btn_salvar_mat = st.form_submit_button(
              "💾 Salvar Lançamento na Gaveta"
          )

          if btn_salvar_mat:
            if id_mat:
              total_calculado = (
                  float(qtd_palete) * float(entrada) * float(peso_unitario)
              )
              data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

              novo_item = pd.DataFrame(
                  [[
                      nome_gaveta_atual,
                      str(id_mat),
                      descricao.upper(),
                      marca.upper(),
                      lote,
                      str(validade),
                      float(qtd_palete),
                      float(entrada),
                      float(peso_unitario),
                      float(total_calculado),
                      unidade_medida,
                      local_armazenagem,
                      data_hora_atual,
                  ]],
                  columns=[
                      c
                      for c in st.session_state.materiais_gaveta.columns
                      if c in st.session_state.materiais_gaveta.columns
                  ],
              )

              # Assegurar colunas dinâmicas extras se houver
              for col in st.session_state.materiais_gaveta.columns:
                if col not in novo_item.columns:
                  novo_item[col] = ""

              st.session_state.materiais_gaveta = pd.concat(
                  [st.session_state.materiais_gaveta, novo_item],
                  ignore_index=True,
              )
              st.success("Lançamento adicionado com sucesso!")
              st.rerun()
            else:
              st.warning("O campo ID é obrigatório.")

      # 🛠️ Criar Nova Coluna Customizada na Tabela
      with st.expander("🛠️ Criar Nova Coluna / Campo Personalizado"):
        with st.form("form_nova_coluna"):
          nome_nova_coluna = st.text_input(
              "Nome da Nova Coluna (Ex: OBSERVAÇÃO, FORNECEDOR)"
          )
          btn_criar_col = st.form_submit_button("➕ Adicionar Coluna à Tabela")
          if btn_criar_col:
            if nome_nova_coluna.strip():
              col_upper = nome_nova_coluna.strip().upper()
              if col_upper in st.session_state.materiais_gaveta.columns:
                st.warning("Esta coluna já existe!")
              else:
                st.session_state.materiais_gaveta[col_upper] = ""
                st.success(f"Coluna '{col_upper}' criada com sucesso!")
                st.rerun()
            else:
              st.error("Digite um nome válido para a coluna.")

      st.markdown("---")
      st.subheader(
          "📊 Tabela de Lançamentos da Gaveta (Filtros e Visualização)"
      )

      df_gaveta = st.session_state.materiais_gaveta[
          st.session_state.materiais_gaveta["Nome_Gaveta"] == nome_gaveta_atual
      ].copy()

      if not df_gaveta.empty:
        unidades_disponiveis = df_gaveta["UNIDADE DE MEDIDA"].unique().tolist()
        filtro_unidade = st.multiselect(
            "🔍 Filtrar por UNIDADE DE MEDIDA:",
            options=unidades_disponiveis,
            default=unidades_disponiveis,
        )

        if filtro_unidade:
          df_gaveta = df_gaveta[
              df_gaveta["UNIDADE DE MEDIDA"].isin(filtro_unidade)
          ]

        # Pega todas as colunas atuais do DataFrame para exibição (inclusive as criadas pelo usuário)
        colunas_exibicao = [
            c for c in st.session_state.materiais_gaveta.columns if c != "Nome_Gaveta"
        ]

        df_editavel = df_gaveta[colunas_exibicao]

        df_resultado_editado = st.data_editor(
            df_editavel, use_container_width=True, num_rows="dynamic"
        )

        if st.button("💾 Salvar Alterações na Tabela"):
          df_atualizado_base = df_resultado_editado.copy()
          if "QTD/PALETE" in df_atualizado_base.columns and "ENTRADA" in df_atualizado_base.columns and "PESO UNITÁRIO" in df_atualizado_base.columns and "TOTAL" in df_atualizado_base.columns:
            df_atualizado_base["TOTAL"] = (
                df_atualizado_base["QTD/PALETE"]
                * df_atualizado_base["ENTRADA"]
                * df_atualizado_base["PESO UNITÁRIO"]
            )
          df_atualizado_base["Nome_Gaveta"] = nome_gaveta_atual

          st.session_state.materiais_gaveta = st.session_state.materiais_gaveta[
              st.session_state.materiais_gaveta["Nome_Gaveta"]
              != nome_gaveta_atual
          ]
          st.session_state.materiais_gaveta = pd.concat(
              [
                  st.session_state.materiais_gaveta,
                  df_atualizado_base[
                      st.session_state.materiais_gaveta.columns
                  ],
              ],
              ignore_index=True,
          )
          st.success("Alterações salvas com sucesso!")
          st.rerun()
      else:
        st.info("Nenhum lançamento cadastrado nesta gaveta com esse filtro.")

# -------------------------------------------------------------
# 4. DASHBOARD GERAL
# -------------------------------------------------------------
elif menu == "📊 Dashboard Geral":
  st.header("📊 Dashboard Consolidado do Almoxarifado")
  if not st.session_state.materiais_gaveta.empty:
    df_global = st.session_state.materiais_gaveta.copy()

    c1, c2, c3 = st.columns(3)
    with c1:
      st.metric("Total de Registros", len(df_global))
    with c2:
      if "TOTAL" in df_global.columns:
        st.metric("Total Geral Acumulado", f"{df_global['TOTAL'].sum():,.2f}")
    with c3:
      st.metric("Total de Gavetas", len(st.session_state.gavetas))

    st.markdown("---")
    st.subheader("📋 Relatório Consolidado de Todas as Gavetas")
    st.dataframe(
        df_global.drop(columns=["Nome_Gaveta"], errors="ignore"),
        use_container_width=True,
    )
  else:
    st.info("Nenhum dado registrado para exibir no dashboard.")
