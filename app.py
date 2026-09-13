from datetime import datetime
import os
import pandas as pd
import pytz
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="BUILD STOCK BR",
    page_icon="📦",
    layout="wide",
)

# Fuso Horário de Brasília
BR_TZ = pytz.timezone("America/Sao_Paulo")


def get_now_br():
  return datetime.now(BR_TZ).strftime("%Y-%m-%d %H:%M:%S")


# Arquivos de Persistência Local (CSV)
ESTOQUE_FILE = "build_stock_estoque.csv"
MOV_FILE = "build_stock_movimentacoes.csv"

# 1. CARREGAMENTO COM PERSISTÊNCIA REAL (NÃO APAGA MAIS)
if "estoque_df" not in st.session_state:
  if os.path.exists(ESTOQUE_FILE):
    st.session_state.estoque_df = pd.read_csv(ESTOQUE_FILE)
  else:
    st.session_state.estoque_df = pd.DataFrame(columns=[
        "ID",
        "Descrição",
        "Marca",
        "Lote",
        "Fabricação",
        "Validade",
        "Área",
        "Emb Externa Tipo",
        "Qtd Externa",
        "Emb Interna Tipo",
        "Qtd Interna por Externa",
        "Medida por Interna",
        "Unidade Final",
        "Total Geral",
    ])

if "mov_df" not in st.session_state:
  if os.path.exists(MOV_FILE):
    st.session_state.mov_df = pd.read_csv(MOV_FILE)
  else:
    st.session_state.mov_df = pd.DataFrame(columns=[
        "Data/Hora",
        "ID",
        "Descrição",
        "Lote",
        "Tipo",
        "Quantidade",
        "Origem",
        "Destino",
        "Responsável",
    ])


def salvar_dados():
  st.session_state.estoque_df.to_csv(ESTOQUE_FILE, index=False)
  st.session_state.mov_df.to_csv(MOV_FILE, index=False)


# Título Principal
st.title("📦 BUILD STOCK BR — Sistema Inteligente de Almoxarifado")
st.markdown("---")

# Menu Lateral com as 3 Áreas Reais
menu = [
    "📋 Painel & Áreas",
    "🆕 Cadastro Mestre",
    "🔄 Transferência & Movimentação",
    "📊 Gráficos & Linha do Tempo",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df
mov_df = st.session_state.mov_df
areas_reais = [
    "🏭 Galpão de Materiais Refratários",
    "🚪 Sala Anexa",
    "🧱 Oficina de Revestimento",
]

if escolha == "📋 Painel & Áreas":
  st.subheader("📊 Visão Geral Consolidada por Área")

  # Métricas Principais
  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.metric("Total de Lotes Ativos", len(df))
  with c2:
    vol_geral = f"{df['Total Geral'].sum():,.2f}" if not df.empty else "0.00"
    st.metric("Volume Global em Estoque", vol_geral)
  with c3:
    st.metric("Áreas Monitoradas", len(areas_reais))
  with c4:
    st.metric("Sistema de Persistência", "Ativo 🟢 (CSV)")

  st.markdown("---")

  # Soma por Área
  if not df.empty:
    st.markdown("### 📈 Soma de Volume por Área")
    soma_area = (
        df.groupby("Área")["Total Geral"].sum().reset_index()
    )
    st.dataframe(soma_area, use_container_width=True)

  # Visão por Área Específica
  st.markdown("### 🔍 Inventário Detalhado por Local")
    
  area_filtro = st.selectbox("Selecione a Área para Auditoria", areas_reais)
  df_filtrado = df[df["Área"] == area_filtro]

  if df_filtrado.empty:
    st.info(f"Nenhum item alocado no momento em: **{area_filtro}**.")
  else:
    st.dataframe(df_filtrado, use_container_width=True)

    # Botão para Baixar CSV da Área
    csv_area = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Baixar Relatório de {area_filtro} (CSV)",
        data=csv_area,
        file_name=f"estoque_{area_filtro.replace(' ', '_').lower()}.csv",
        mime="text/csv",
    )

elif escolha == "🆕 Cadastro Mestre":
  st.subheader("➕ Cadastro Mestre com Auto Preenchimento e Conversão Flexível")

  with st.form("form_mestre", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      id_prod = st.text_input("🔖 ID Rastreador / Código *")
      descricao = st.text_input("📝 Descrição do Material *")
    with c2:
      marca = st.text_input("🏷️ Marca / Fabricante *")
      lote = st.text_input("📦 Número do Lote *")
    with c3:
      fab_data = st.date_input("📅 Data de Fabricação")
      validade_dias = st.number_input(
          "⏳ Validade (Dias)", min_value=1, value=365
      )

    st.markdown("---")
    c4, c5 = st.columns(2)
    with c4:
      area_inicial = st.selectbox("📍 Área de Destino Inicial", areas_reais)
    with c5:
      un_final = st.selectbox(
          "📏 Unidade de Medida Final",
          ["KG", "UN", "L", "M", "M²", "PÇ", "Saco", "Rolo", "Galão"],
      )

    st.markdown("### 🔄 Configuração de Embalagens e Fatores de Conversão")
    c6, c7, c8, c9 = st.columns(4)
    with c6:
      emb_ext_tipo = st.selectbox(
          "Embalagem Externa", ["Palete", "Caixa", "Fardo"]
      )
    with c7:
      qtd_externa = st.number_input(
          "Qtd Externa (Ex: 2 Paletes)", min_value=0.1, value=1.0
      )
    with c8:
      emb_int_tipo = st.selectbox(
          "Embalagem Interna",
          ["Saco", "Rolo", "M²", "M", "UND", "PÇ", "Galão"],
      )
    with c9:
      qtd_int_por_ext = st.number_input(
          "Qtd Interna por Externa (Ex: 40 sacos)", min_value=0.1, value=40.0
      )

    medida_por_int = st.number_input(
        "⚖️ Medida por Unidade Interna (Ex: 25kg por saco, 10m por rolo)",
        min_value=0.01,
        value=25.0,
    )

    # Cálculo Automático: Ex: 2 paletes x 40 sacos x 25kg = 2000kg
    total_calculado = qtd_externa * qtd_int_por_ext * medida_por_int
    st.info(
        f"💡 **Cálculo Automático de Volume:** {qtd_externa} {emb_ext_tipo}(s)"
        f" × {qtd_int_por_ext} {emb_int_tipo}(s) × {medida_por_int} ="
        f" **{total_calculado:,.2f} {un_final}**"
    )

    salvar_btn = st.form_submit_button("💾 Salvar Cadastro Mestre")

    if salvar_btn:
      if not id_prod or not descricao or not marca or not lote:
        st.error("❌ Preencha todos os campos obrigatórios marcados com *!")
      else:
        novo_registro = pd.DataFrame([{
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
            "Marca": marca.upper(),
            "Lote": lote.upper(),
            "Fabricação": str(fab_data),
            "Validade": str(
                pd.to_datetime(fab_data)
                + pd.Timedelta(days=int(validade_dias))
            ).split()[0],
            "Área": area_inicial,
            "Emb Externa Tipo": emb_ext_tipo,
            "Qtd Externa": qtd_externa,
            "Emb Interna Tipo": emb_int_tipo,
            "Qtd Interna por Externa": qtd_int_por_ext,
            "Medida por Interna": medida_por_int,
            "Unidade Final": un_final,
            "Total Geral": total_calculado,
        }])

        st.session_state.estoque_df = pd.concat(
            [df, novo_registro], ignore_index=True
        )

        # Registra Movimentação de Entrada Inicial
        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
            "Lote": lote.upper(),
            "Tipo": "📥 Entrada Inicial (Cadastro)",
            "Quantidade": total_calculado,
            "Origem": "Fornecedor Externo",
            "Destino": area_inicial,
            "Responsável": "Almoxarife",
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        salvar_dados()
        st.success(
            f"✅ Cadastro do ID **{id_prod.upper()}** efetuado com sucesso na área"
            f" **{area_inicial}**!"
        )

elif escolha == "🔄 Transferência & Movimentação":
  st.subheader(
      "🔄 Transferência Automática Inteligente (Galpão ⇄ Oficina / Sala)"
  )

  if df.empty:
    st.warning("⚠️ Não há lotes cadastrados para movimentar.")
  else:
    # Seleção do item
    item_op = st.selectbox(
        "Selecione o Insumo para Movimentação",
        df["ID"] + " - " + df["Descrição"] + " (Lote: " + df["Lote"] + ")",
    )
    id_escolhido = item_op.split(" - ")[0]
    lote_escolhido = item_op.split("Lote: ")[1].split(")")[0]

    # Filtra os lotes disponíveis deste ID
    lotes_disponiveis = df[
        (df["ID"] == id_escolhido) & (df["Lote"] == lote_escolhido)
    ]

    if not lotes_disponiveis.empty:
      item_atual = lotes_disponiveis.iloc[0]
      origem_atual = item_atual["Área"]
      max_qtd = item_atual["Total Geral"]
      unidade_item = item_atual["Unidade Final"]

      st.info(
          f"📍 **Localização Atual (Origem):** {origem_atual} | 📦 **Estoque"
          f" Disponível:** {max_qtd:,.2f} {unidade_item}"
      )

      c_m1, c_m2, c_m3 = st.columns(3)
      with c_m1:
        tipo_mov = st.selectbox(
            "Tipo de Operação",
            [
                "🚀 Transferência Automática (Saída Origem ➔ Entrada Destino)",
                "📤 Baixa/Saída Direta",
                "📥 Entrada Direta",
            ],
        )
      with c_m2:
        qtd_mov = st.number_input(
            f"Quantidade a movimentar ({unidade_item})",
            min_value=0.01,
            max_value=float(max_qtd)
            if "Transferência" in tipo_mov or "Baixa" in tipo_mov
            else 1000000.0,
            value=min(1.0, float(max_qtd)),
        )
      with c_m3:
        # Define destino padrão se for transferência automática
        destinos_possiveis = [a for a in areas_reais if a != origem_atual]
        destino_alvo = st.selectbox(
            "Destino Efetivo da Movimentação",
            destinos_possiveis if destinos_possiveis else areas_reais,
        )

      resp = st.text_input("👤 Responsável pela Operação", value="Almoxarife")

      if st.button("⚡ Executar Movimentação & FIFO"):
        idx_alvo = df[
            (df["ID"] == id_escolhido) & (df["Lote"] == lote_escolhido)
        ].index[0]

        if "Baixa" in tipo_mov or "Transferência" in tipo_mov:
          if qtd_mov > max_qtd:
            st.error(
                "❌ Erro: Quantidade solicitada é maior que o estoque atual"
                " disponível!"
            )
            st.stop()

        # Executa lógica de acordo com o tipo
        if "Transferência" in tipo_mov:
          # Subtrai da origem
          df.loc[idx_alvo, "Total Geral"] -= qtd_mov

          # Verifica se o lote já existe no destino para somar, senão cria cópia na nova área
          ja_existe_no_destino = df[
              (df["ID"] == id_escolhido)
              & (df["Lote"] == lote_escolhido)
              & (df["Área"] == destino_alvo)
          ]

          if not ja_existe_no_destino.empty:
            idx_dest = ja_existe_no_destino.index[0]
            df.loc[idx_dest, "Total Geral"] += qtd_mov
          else:
            nova_linha_dest = df.loc[idx_alvo].copy()
            nova_linha_dest["Área"] = destino_alvo
            nova_linha_dest["Total Geral"] = qtd_mov
            df = pd.concat(
                [df, pd.DataFrame([nova_linha_dest])], ignore_index=True
            )

          reg_tipo = "🔄 Transferência Automática"

        elif "Baixa" in tipo_mov:
          df.loc[idx_alvo, "Total Geral"] -= qtd_mov
          reg_tipo = "📤 Baixa/Saída"
          destino_alvo = "Consumo Externo / Obra"

        else:
          df.loc[idx_alvo, "Total Geral"] += qtd_mov
          reg_tipo = "📥 Entrada Direta"
          origem_atual = "Fornecedor / Ajuste"

        # Remove linhas com estoque zerado se necessário ou mantém
        st.session_state.estoque_df = df

        # Registra no histórico com data/hora fuso Brasília
        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_escolhido,
            "Descrição": item_atual["Descrição"],
            "Lote": lote_escolhido,
            "Tipo": reg_tipo,
            "Quantidade": qtd_mov,
            "Origem": origem_atual,
            "Destino": destino_alvo,
            "Responsável": resp,
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        salvar_dados()
        st.success(
            f"✅ Operação de **{reg_tipo}** realizada com sucesso de"
            f" **{origem_atual}** para **{destino_alvo}**!"
        )
        st.rerun()

  st.markdown("---")
  st.markdown("### 📜 Histórico Completo de Auditoria e Movimentações")
  if mov_df.empty:
    st.info("Nenhuma movimentação registrada.")
  else:
    st.dataframe(mov_df, use_container_width=True)

elif escolha == "📊 Gráficos & Linha do Tempo":
  st.subheader("📊 Gráficos Analíticos, FIFO por Fabricação e Linha do Tempo")

  if df.empty:
    st.info("Cadastre dados para visualizar os relatórios gráficos.")
  else:
    # 1. Regra FIFO por Fabricação
    st.markdown(
        "### ⏳ Alerta FIFO: Lotes Recomendados para Saída (Mais Antigos"
        " Primeiro)"
    )
    df_fifo = df.sort_values(by="Fabricação", ascending=True)
    st.dataframe(
        df_fifo[[
            "ID",
            "Descrição",
            "Lote",
            "Fabricação",
            "Validade",
            "Área",
            "Total Geral",
            "Unidade Final",
        ]],
        use_container_width=True,
    )

    st.markdown("---")

    c_g1, c_g2 = st.columns(2)
    with c_g1:
      st.markdown("#### 📊 Volume Total por ID de Produto")
      if not df.empty:
        df_chart = df.groupby("ID")["Total Geral"].sum().reset_index()
        st.bar_chart(df_chart, x="ID", y="Total Geral")

    with c_g2:
      st.markdown("#### 🏢 Distribuição de Estoque por Área")
      if not df.empty:
        df_area_chart = df.groupby("Área")["Total Geral"].sum().reset_index()
        st.bar_chart(df_area_chart, x="Área", y="Total Geral")

    st.markdown("---")
    st.markdown("### 🕒 Linha do Tempo de Movimentações por ID")
    if not mov_df.empty:
      id_linha_tempo = st.selectbox(
          "Filtrar Linha do Tempo por ID", mov_df["ID"].unique()
      )
      df_timeline = mov_df[mov_df["ID"] == id_linha_tempo]
      st.dataframe(df_timeline, use_container_width=True)
    else:
      st.info("Sem movimentações suficientes para gerar linha do tempo.")
