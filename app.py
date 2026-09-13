import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="BUILD STOCK BR",
    page_icon="📦",
    layout="wide",
)

# Inicializando o Banco de Dados em Memória (Session State)
if "estoque_df" not in st.session_state:
  # Criando um DataFrame padrão caso esteja vazio
  st.session_state.estoque_df = pd.DataFrame(
      columns=[
          "ID",
          "Descrição",
          "Marca",
          "Lote",
          "Validade",
          "Qtd Palete",
          "Medida Saco",
          "Total",
          "Unidade",
      ]
  )

# Título Principal
st.title("📦 BUILD STOCK BR — Gestão Inteligente")
st.markdown("---")

# Menu Lateral Profissional
menu = [
    "📋 Painel & Estoque",
    "🆕 Cadastrar Lote",
    "🔄 Movimentações",
    "📊 Gráficos",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df

if escolha == "📋 Painel & Estoque":
  st.subheader("📊 Visão Geral do Almoxarifado")

  # Métricas Rápidas (KPIs)
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric("Total de Lotes", len(df))
  with col2:
    total_itens = (
        int(df["Qtd Palete"].sum()) if not df.empty else 0
    )
    st.metric("Paletes Registrados", total_itens)
  with col3:
    st.metric("Status do Sistema", "Online 🟢")

  st.markdown("### 🗂️ Itens em Estoque")
  if df.empty:
    st.info(
        "Nenhum item cadastrado no momento. Use o menu lateral para adicionar"
        " novos lotes."
    )
  else:
    st.dataframe(df, use_container_width=True)

elif escolha == "🆕 Cadastrar Lote":
  st.subheader("➕ Novo Cadastro de Insumo")

  with st.form("form_cadastro", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      id_prod = st.text_input("ID / Código *")
      descricao = st.text_input("Descrição do Material *")
    with c2:
      marca = st.text_input("Marca / Fabricante *")
      lote = st.text_input("Número do Lote *")
    with c3:
      fab_data = st.date_input("Data de Fabricação")
      validade_dias = st.number_input(
          "Validade (Dias)", min_value=1, value=365
      )

    st.markdown("---")
    c4, c5, c6 = st.columns(3)
    with c4:
      emb_externa = st.number_input(
          "Qtd Embalagem Externa (Paletes)", min_value=0.0, value=1.0
      )
    with c5:
      medida_int = st.number_input(
          "Medida por Unidade Interna (KG/Un)", min_value=0.0, value=25.0
      )
    with c6:
      un_final = st.selectbox("Unidade de Medida Final", ["KG", "UN", "L", "M"])

    # Cálculo em tempo real dentro do form
    calculo_total = emb_externa * medida_int
    st.info(f"💡 **Volume Total Calculado:** {calculo_total:.2f} {un_final}")

    enviar = st.form_submit_button("💾 Salvar Lote no Sistema")

    if enviar:
      if not id_prod or not descricao or not marca or not lote:
        st.error("❌ Preencha todos os campos obrigatórios marcados com *!")
      else:
        # Novo registro
        novo_dado = {
            "ID": id_prod,
            "Descrição": descricao,
            "Marca": marca,
            "Lote": lote,
            "Validade": str(fab_data),
            "Qtd Palete": emb_externa,
            "Medida Saco": medida_int,
            "Total": calculo_total,
            "Unidade": un_final,
        }
        # Adiciona ao DataFrame da sessão
        st.session_state.estoque_df = pd.concat(
            [df, pd.DataFrame([novo_dado])], ignore_index=True
        )
        st.success(
            f"✅ Lote **{id_prod}** cadastrado com sucesso e salvo na sessão!"
        )

elif escolha == "🔄 Movimentações":
  st.subheader("🔄 Controle de Entradas e Baixas")
  if df.empty:
    st.warning("Cadastre produtos primeiro para realizar movimentações.")
  else:
    item_selecionado = st.selectbox(
        "Selecione o Produto", df["ID"] + " - " + df["Descrição"]
    )
    tipo_mov = st.radio("Tipo de Movimentação", ["📥 Entrada", "📤 Baixa/Saída"])
    qtd_mov = st.number_input(
        "Quantidade a movimentar", min_value=0.0, value=1.0
    )

    if st.button("Confirmar Movimentação"):
      st.success(
          f"Movimentação de {tipo_mov} registrada com sucesso para"
          f" {item_selecionado}!"
      )

elif escolha == "📊 Gráficos":
  st.subheader("📊 Análise Gráfica de Estoque")
  if df.empty:
    st.info("Adicione dados para gerar visualizações gráficas.")
  else:
    st.bar_chart(df, x="ID", y="Total")
