import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="BUILD STOCK BR",
    page_icon="📦",
    layout="wide",
)

# Inicializando Banco de Dados e Histórico na Sessão
if "estoque_df" not in st.session_state:
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

if "mov_df" not in st.session_state:
  st.session_state.mov_df = pd.DataFrame(
      columns=["Data/Hora", "ID", "Tipo", "Quantidade", "Responsável"]
  )

# Título Principal
st.title("📦 BUILD STOCK BR — Sistema de Gestão de Almoxarifado")
st.markdown("---")

# Menu Lateral Profissional
menu = [
    "📋 Painel & Estoque",
    "🆕 Cadastrar Lote",
    "🔄 Movimentações",
    "📊 Gráficos & Relatórios",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df
mov_df = st.session_state.mov_df

if escolha == "📋 Painel & Estoque":
  st.subheader("📊 Painel de Controle Geral")

  # Métricas (KPIs)
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric("Total de Lotes", len(df))
  with col2:
    total_volume = (
        f"{df['Total'].sum():,.2f}" if not df.empty else "0.00"
    )
    st.metric("Volume Total Geral", total_volume)
  with col3:
    st.metric(
        "Movimentações Registradas", len(mov_df) if not mov_df.empty else 0
    )
  with col4:
    st.metric("Status do Sistema", "Online 🟢")

  st.markdown("### 🗂️ Inventário Atual")
  if df.empty:
    st.info(
        "Nenhum item cadastrado. Vá em 'Cadastrar Lote' no menu lateral para"
        " comecar."
    )
  else:
    st.dataframe(df, use_container_width=True)

    # Botão de Exportação
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatório de Estoque (CSV)",
        data=csv,
        file_name="build_stock_br_relatorio.csv",
        mime="text/csv",
    )

elif escolha == "🆕 Cadastrar Lote":
  st.subheader("➕ Cadastro de Novo Lote de Insumo")

  with st.form("form_cadastro", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      id_prod = st.text_input("ID / Código do Produto *")
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
          "Quantidade Embalagem Externa (Paletes/Fardos)",
          min_value=0.0,
          value=1.0,
      )
    with c5:
      medida_int = st.number_input(
          "Medida por Unidade Interna (KG/Un/L)", min_value=0.0, value=25.0
      )
    with c6:
      un_final = st.selectbox("Unidade de Medida Final", ["KG", "UN", "L", "M"])

    calculo_total = emb_externa * medida_int
    st.info(f"💡 **Volume Total Calculado:** {calculo_total:.2f} {un_final}")

    enviar = st.form_submit_button("💾 Salvar e Registrar Lote")

    if enviar:
      if not id_prod or not descricao or not marca or not lote:
        st.error("❌ Preencha todos os campos obrigatórios marcados com *!")
      else:
        novo_dado = {
            "ID": id_prod,
            "Descrição": descricao.upper(),
            "Marca": marca.upper(),
            "Lote": lote,
            "Validade": str(fab_data),
            "Qtd Palete": emb_externa,
            "Medida Saco": medida_int,
            "Total": calculo_total,
            "Unidade": un_final,
        }
        st.session_state.estoque_df = pd.concat(
            [df, pd.DataFrame([novo_dado])], ignore_index=True
        )

        # Registra no histórico de movimentações como Entrada inicial
        nova_mov = pd.DataFrame([{
            "Data/Hora": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ID": id_prod,
            "Tipo": "📥 Cadastro Inicial",
            "Quantidade": calculo_total,
            "Responsável": "Sistema",
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        st.success(f"✅ Lote **{id_prod}** cadastrado e integrado com sucesso!")

elif escolha == "🔄 Movimentações":
  st.subheader("🔄 Controle de Entradas e Baixas de Estoque")
  if df.empty:
    st.warning("Cadastre produtos primeiro para poder movimentá-los.")
  else:
    item_op = st.selectbox(
        "Selecione o Insumo", df["ID"] + " - " + df["Descrição"]
    )
    id_escolhido = item_op.split(" - ")[0]

    c_m1, c_m2 = st.columns(2)
    with c_m1:
      tipo_mov = st.selectbox(
          "Tipo de Operação", ["📥 Entrada (Adicionar)", "📤 Baixa (Retirar)"]
      )
    with c_m2:
      qtd_mov = st.number_input("Quantidade da Movimentação", min_value=0.1, value=1.0)

    responsavel = st.text_input(
        "Responsável pela Operação", value="Almoxarife"
    )

    if st.button("Confirmar Movimentação"):
      idx = st.session_state.estoque_df.index[
          st.session_state.estoque_df["ID"] == id_escolhido
      ]
      if not idx.empty:
        i = idx[0]
        atual = st.session_state.estoque_df.loc[i, "Total"]

        if "Baixa" in tipo_mov:
          if qtd_mov > atual:
            st.error("❌ Erro: A quantidade de baixa é superior ao estoque atual!")
          else:
            st.session_state.estoque_df.loc[i, "Total"] -= qtd_mov
            st.session_state.estoque_df.loc[i, "Qtd Palete"] = max(
                0.0,
                st.session_state.estoque_df.loc[i, "Qtd Palete"]
                - (
                    qtd_mov
                    / st.session_state.estoque_df.loc[i, "Medida Saco"]
                ),
            )
            reg_tipo = "📤 Baixa"
        else:
          st.session_state.estoque_df.loc[i, "Total"] += qtd_mov
          st.session_state.estoque_df.loc[i, "Qtd Palete"] += (
              qtd_mov / st.session_state.estoque_df.loc[i, "Medida Saco"]
          )
          reg_tipo = "📥 Entrada"

        # Salvar histórico
        nova_mov = pd.DataFrame([{
            "Data/Hora": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ID": id_escolhido,
            "Tipo": reg_tipo,
            "Quantidade": qtd_mov,
            "Responsável": responsavel,
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )
        st.success(
            f"✅ Movimentação de **{reg_tipo}** registrada com sucesso para o ID"
            f" {id_escolhido}!"
        )
        st.rerun()

    st.markdown("### 📜 Histórico de Movimentações")
    if mov_df.empty:
      st.info("Nenhuma movimentação registrada até o momento.")
    else:
      st.dataframe(mov_df, use_container_width=True)

elif escolha == "📊 Gráficos & Relatórios":
  st.subheader("📊 Análise Gráfica de Insumos")
  if df.empty:
    st.info("Adicione dados para gerar gráficos inteligentes.")
  else:
    c_g1, c_g2 = st.columns(2)
    with c_g1:
      st.markdown("#### Volume Total por ID de Produto")
      st.bar_chart(df, x="ID", y="Total")
    with c_g2:
      st.markdown("#### Paletes Alocados por ID")
      st.bar_chart(df, x="ID", y="Qtd Palete")
