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

# Carregamento com Persistência
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
    "📋 Painel & Estoque por ID",
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

if escolha == "📋 Painel & Estoque por ID":
  st.subheader("📊 Painel de Controle e Rastreabilidade por ID")

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
    st.metric("Persistência CSV", "Ativo 🟢")

  st.markdown("---")

  if df.empty:
    st.info("Nenhum item cadastrado no sistema.")
  else:
    # FILTRO RÁPIDO DE RASTREIO POR ID
    st.markdown("### 🔍 Rastreamento Direto por ID / Código")
    ids_unicos = ["TODOS OS IDS"] + list(df["ID"].unique())
    filtro_id_escolhido = st.selectbox(
        "Selecione ou digite para rastrear o ID específico", ids_unicos
    )

    if filtro_id_escolhido != "TODOS OS IDS":
      df_exibir = df[df["ID"] == filtro_id_escolhido]
    else:
      df_exibir = df

    # Filtro por Área
    area_filtro = st.selectbox("Filtrar por Área Específica", ["TODAS AS ÁREAS"] + areas_reais)
    if area_filtro != "TODAS AS ÁREAS":
      df_exibir = df_exibir[df_exibir["Área"] == area_filtro]

    st.markdown("### 📦 Estoque Atual Detalhado")
    st.dataframe(df_exibir, use_container_width=True)

    # Botão para Baixar CSV Filtrado
    csv_filtrado = df_exibir.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatório Filtrado (CSV)",
        data=csv_filtrado,
        file_name="build_stock_estoque_filtrado.csv",
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
          "Qtd Externa", min_value=0.1, value=1.0
      )
    with c8:
      emb_int_tipo = st.selectbox(
          "Embalagem Interna",
          ["Saco", "Rolo", "M²", "M", "UND", "PÇ", "Galão"],
      )
    with c9:
      qtd_int_por_ext = st.number_input(
          "Qtd Interna por Externa", min_value=0.1, value=40.0
      )

    medida_por_int = st.number_input(
        "⚖️ Medida por Unidade Interna",
        min_value=0.01,
        value=25.0,
    )

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

        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
            "Lote": lote.upper(),
            "Tipo": "📥 Entrada Inicial",
            "Quantidade": total_calculado,
            "Origem": "Fornecedor",
            "Destino": area_inicial,
            "Responsável": "Almoxarife",
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        salvar_dados()
        st.success(f"✅ ID **{id_prod.upper()}** cadastrado com sucesso!")

elif escolha == "🔄 Transferência & Movimentação":
  st.subheader("🔄 Transferência Automática Inteligente")

  if df.empty:
    st.warning("⚠️ Não há lotes cadastrados para movimentar.")
  else:
    item_op = st.selectbox(
        "Selecione o Insumo",
        df["ID"] + " - " + df["Descrição"] + " (Lote: " + df["Lote"] + " | Área: " + df["Área"] + ")",
    )
    id_escolhido = item_op.split(" - ")[0]
    lote_escolhido = item_op.split("Lote: ")[1].split(" | ")[0]
    area_origem_item = item_op.split("Área: ")[1].split(")")[0]

    lotes_disponiveis = df[
        (df["ID"] == id_escolhido) & (df["Lote"] == lote_escolhido) & (df["Área"] == area_origem_item)
    ]

    if not lotes_disponiveis.empty:
      item_atual = lotes_disponiveis.iloc[0]
      max_qtd = item_atual["Total Geral"]
      unidade_item = item_atual["Unidade Final"]

      st.info(
          f"📍 **Origem:** {area_origem_item} | 📦 **Estoque Disponível no ID:** {max_qtd:,.2f} {unidade_item}"
      )

      c_m1, c_m2, c_m3 = st.columns(3)
      with c_m1:
        tipo_mov = st.selectbox(
            "Tipo de Operação",
            [
                "🚀 Transferência Automática",
                "📤 Baixa/Saída Direta",
                "📥 Entrada Direta",
            ],
        )
      with c_m2:
        qtd_mov = st.number_input(
            f"Quantidade ({unidade_item})",
            min_value=0.01,
            max_value=float(max_qtd) if "Transferência" in tipo_mov or "Baixa" in tipo_mov else 1000000.0,
            value=min(1.0, float(max_qtd)),
        )
      with c_m3:
        destinos_possiveis = [a for a in areas_reais if a != area_origem_item]
        destino_alvo = st.selectbox(
            "Destino Efetivo",
            destinos_possiveis if destinos_possiveis else areas_reais,
        )

      resp = st.text_input("👤 Responsável", value="Almoxarife")

      if st.button("⚡ Executar Movimentação"):
        idx_alvo = df[
            (df["ID"] == id_escolhido) & (df["Lote"] == lote_escolhido) & (df["Área"] == area_origem_item)
        ].index[0]

        if "Transferência" in tipo_mov:
          df.loc[idx_alvo, "Total Geral"] -= qtd_mov

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
            df = pd.concat([df, pd.DataFrame([nova_linha_dest])], ignore_index=True)

          reg_tipo = "🔄 Transferência Automática"

        elif "Baixa" in tipo_mov:
          df.loc[idx_alvo, "Total Geral"] -= qtd_mov
          reg_tipo = "📤 Baixa/Saída"
          destino_alvo = "Consumo Externo"

        else:
          df.loc[idx_alvo, "Total Geral"] += qtd_mov
          reg_tipo = "📥 Entrada Direta"
          area_origem_item = "Fornecedor"

        st.session_state.estoque_df = df

        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_escolhido,
            "Descrição": item_atual["Descrição"],
            "Lote": lote_escolhido,
            "Tipo": reg_tipo,
            "Quantidade": qtd_mov,
            "Origem": area_origem_item,
            "Destino": destino_alvo,
            "Responsável": resp,
        }])
        st.session_state.mov_df = pd.concat([mov_df, nova_mov], ignore_index=True)

        salvar_dados()
        st.success(f"✅ Operação de **{reg_tipo}** realizada com sucesso!")
        st.rerun()

  st.markdown("---")
  st.markdown("### 📜 Histórico Completo de Auditoria")
  if mov_df.empty:
    st.info("Nenhuma movimentação registrada.")
  else:
    st.dataframe(mov_df, use_container_width=True)

elif escolha == "📊 Gráficos & Linha do Tempo":
  st.subheader("📊 Gráficos Analíticos e FIFO por Fabricação")

  if df.empty:
    st.info("Cadastre dados para visualizar os relatórios.")
  else:
    st.markdown("### ⏳ Alerta FIFO: Lotes Mais Antigos Primeiro")
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
      st.markdown("#### 📊 Volume Total por ID")
      df_chart = df.groupby("ID")["Total Geral"].sum().reset_index()
      st.bar_chart(df_chart, x="ID", y="Total Geral")

    with c_g2:
      st.markdown("#### 🏢 Estoque por Área")
      df_area_chart = df.groupby("Área")["Total Geral"].sum().reset_index()
      st.bar_chart(df_area_chart, x="Área", y="Total Geral")

    st.markdown("---")
    st.markdown("### 🕒 Linha do Tempo por ID")
    if not mov_df.empty:
      id_linha_tempo = st.selectbox("Filtrar Linha do Tempo por ID", mov_df["ID"].unique())
      df_timeline = mov_df[mov_df["ID"] == id_linha_tempo]
      st.dataframe(df_timeline, use_container_width=True)
    else:
      st.info("Sem movimentações para gerar linha do tempo.")
