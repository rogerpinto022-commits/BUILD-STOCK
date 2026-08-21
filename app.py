from datetime import datetime, timedelta
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
      "Gaveta de Insumos Básicos",
      "Galpão 1 - Corredor A",
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
          "Data_Fabricacao",
          "Validade_Meses",
          "Qtd_Paletes",
          "Sacos_Por_Palete",
          "Peso_Saco",
          "Unidade_Medida",
          "Entradas",
          "Saidas",
      ]
  )
  st.session_state.materiais_gaveta.loc[0] = [
      "Gaveta de Insumos Básicos",
      "MAT-001",
      "Cimento Especial",
      "Alpha",
      str(datetime.now().date()),
      12,
      2.0,
      40.0,
      50.0,
      "KG",
      0.0,
      0.0,
  ]

# Inicializa estado para controlar qual gaveta está aberta
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
# 2. GERENCIAR GAVETAS (Criação e Exclusão)
# -------------------------------------------------------------
elif menu == "⚙️ Gerenciar Gavetas":
  st.header("⚙️ Cadastro de Novas Gavetas no Armário")

  with st.form("form_nova_gaveta"):
    col1, col2 = st.columns(2)
    with col1:
      nome_gaveta = st.text_input("🏷️ Nome da Gaveta (Ex: Gaveta 02 - Ferramentaria)")
    with col2:
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
  st.markdown(
      "Clique em uma das gavetas abaixo para abrir sua tabela de materiais e"
      " fazer o gerenciamento completo:"
  )

  if st.session_state.gavetas.empty:
    st.warning(
        "Nenhuma gaveta criada ainda. Vá até a aba 'Gerenciar Gavetas' para"
        " criar a primeira."
    )
  else:
    # Se nenhuma gaveta estiver aberta, exibe o painel visual com todas as gavetas em colunas/cards
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

    # Se uma gaveta foi aberta, mostra a tabela interna dela com cadastro livre e edição
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
          f"📍 **Localização:** {dados_gaveta['Localizacao']} | 📝"
          f" **Descrição:** {dados_gaveta['Descricao']}"
      )

      # Formulário para cadastrar N materiais / marcas livremente na gaveta
      with st.form("form_adicionar_material_livre"):
        st.markdown("### ➕ Cadastrar Novo Material nesta Gaveta")
        c1, c2, c3 = st.columns(3)
        with c1:
          id_material = st.text_input("🆔 ID / Código do Material")
          desc = st.text_input("📝 Descrição do Material")
        with c2:
          marca = st.text_input("🏷️ Marca")
          data_fabricacao = st.date_input(
              "📅 Data de Fabricação", value=datetime.now().date()
          )
        with c3:
          validade_meses = st.number_input(
              "⏳ Validade (Meses)", value=12, min_value=1, step=1
          )
          unidade_medida = st.selectbox(
              "📐 Unidade", ["KG", "Sacos", "Unidades", "Litros", "M²"]
          )

        st.markdown(
            "### 🔢 Fatores de Cálculo (Paletes $\\times$ Sacos $\\times$ Peso)"
        )
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
          qtd_paletes = st.number_input(
              "📦 Qtd Paletes", value=1.0, min_value=0.0
          )
        with col_m2:
          sacos_palete = st.number_input(
              "🛍️ Sacos / Palete", value=40.0, min_value=0.0
          )
        with col_m3:
          peso_saco = st.number_input(
              "⚖️ Peso de Cada Saco", value=50.0, min_value=0.0
          )
        with col_m4:
          entradas = st.number_input("➕ Entradas", value=0.0, min_value=0.0)
        with col_m5:
          saidas = st.number_input("➖ Saídas", value=0.0, min_value=0.0)

        btn_salvar_mat = st.form_submit_button(
            "💾 Adicionar Material na Tabela"
        )

        if btn_salvar_mat:
          if id_material:
            novo_item = pd.DataFrame(
                [[
                    nome_gaveta_atual,
                    id_material,
                    desc,
                    marca,
                    str(data_fabricacao),
                    int(validade_meses),
                    float(qtd_paletes),
                    float(sacos_palete),
                    float(peso_saco),
                    unidade_medida,
                    float(entradas),
                    float(saidas),
                ]],
                columns=st.session_state.materiais_gaveta.columns,
            )
            st.session_state.materiais_gaveta = pd.concat(
                [st.session_state.materiais_gaveta, novo_item], ignore_index=True
            )
            st.success("Material cadastrado com sucesso!")
            st.rerun()
          else:
            st.warning("O ID do Material é obrigatório.")

      st.markdown("---")
      st.subheader("📊 Tabela de Informações e Saldo Automático")
      st.markdown(
          "💡 *Você pode editar diretamente os campos na tabela abaixo ou"
          " excluir linhas se necessário.*"
      )

      # Filtra materiais da gaveta atual
      df_gaveta = st.session_state.materiais_gaveta[
          st.session_state.materiais_gaveta["Nome_Gaveta"] == nome_gaveta_atual
      ].copy()

      if not df_gaveta.empty:
        # Cria colunas calculadas em tempo real
        df_gaveta["Total Calculado"] = (
            df_gaveta["Qtd_Paletes"]
            * df_gaveta["Sacos_Por_Palete"]
            * df_gaveta["Peso_Saco"]
        )
        df_gaveta["Saldo Total"] = (
            df_gaveta["Total Calculado"]
            + df_gaveta["Entradas"]
            - df_gaveta["Saidas"]
        )

        # Tabela editável pelo usuário no Streamlit
        colunas_edicao = [
            "ID_Material",
            "Descricao",
            "Marca",
            "Data_Fabricacao",
            "Validade_Meses",
            "Qtd_Paletes",
            "Sacos_Por_Palete",
            "Peso_Saco",
            "Unidade_Medida",
            "Entradas",
            "Saidas",
            "Total Calculado",
            "Saldo Total",
        ]

        # Mapeamento para exibição amigável
        df_editavel = df_gaveta[colunas_edicao].rename(
            columns={
                "ID_Material": "ID",
                "Descricao": "Descrição",
                "Marca": "Marca",
                "Data_Fabricacao": "Fabricação",
                "Validade_Meses": "Validade (Meses)",
                "Qtd_Paletes": "Paletes",
                "Sacos_Por_Palete": "Sacos/Palete",
                "Peso_Saco": "Peso/Saco",
                "Unidade_Medida": "Unidade",
                "Entradas": "Entradas",
                "Saidas": "Saídas",
                "Total Calculado": "Total Parcial",
                "Saldo Total": "Saldo Final",
            }
        )

        # Exibe editor de dados interativo
        df_resultado_editado = st.data_editor(
            df_editavel, use_container_width=True, num_rows="dynamic"
        )

        # Botão para salvar alterações feitas na tabela editável
        if st.button("💾 Salvar Alterações na Tabela"):
          # Reconstrói os dados de volta para o session state mantendo a gaveta
          df_atualizado_base = df_resultado_editado.rename(
              columns={
                  "ID": "ID_Material",
                  "Descrição": "Descricao",
                  "Marca": "Marca",
                  "Fabricação": "Data_Fabricacao",
                  "Validade (Meses)": "Validade_Meses",
                  "Paletes": "Qtd_Paletes",
                  "Sacos/Palete": "Sacos_Por_Palete",
                  "Peso/Saco": "Peso_Saco",
                  "Unidade": "Unidade_Medida",
                  "Entradas": "Entradas",
                  "Saídas": "Saidas",
              }
          )
          df_atualizado_base["Nome_Gaveta"] = nome_gaveta_atual

          # Remove os dados antigos desta gaveta e insere os novos editados
          st.session_state.materiais_gaveta = st.session_state.
          materiais_gaveta[
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
        st.info(
            "Nenhum material cadastrado nesta gaveta. Utilize o formulário"
            " acima para adicionar."
        )

# -------------------------------------------------------------
# 4. DASHBOARD GERAL
# -------------------------------------------------------------
elif menu == "📊 Dashboard Geral":
  st.header("📊 Dashboard Consolidado do Almoxarifado")
  if not st.session_state.materiais_gaveta.empty:
    df_global = st.session_state.materiais_gaveta.copy()
    df_global["Total Calculado"] = (
        df_global["Qtd_Paletes"]
        * df_global["Sacos_Por_Palete"]
        * df_global["Peso_Saco"]
    )
    df_global["Saldo Total"] = (
        df_global["Total Calculado"]
        + df_global["Entradas"]
        - df_global["Saidas"]
    )

    c1, c2, c3 = st.columns(3)
    with c1:
      st.metric("Total de Materiais", len(df_global))
    with c2:
      st.metric("Volume Geral", f"{df_global['Saldo Total'].sum():,.2f}")
    with c3:
      st.metric("Total de Gavetas", len(st.session_state.gavetas))

    st.markdown("---")
    st.subheader("📋 Relatório Consolidado de Todas as Gavetas")
    st.dataframe(df_global, use_container_width=True)
  else:
    st.info("Nenhum dado registrado para exibir no dashboard.")
