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
ESTOQUE_FILE = "build_stock_estoque_v2.csv"
MOV_FILE = "build_stock_movimentacoes_v2.csv"
PERMISSOES_FILE = "build_stock_permissoes.csv"

areas_reais = [
    "🏭 Galpão de Materiais Refratários",
    "🧱 Oficina de Revestimento",
    "🚪 Sala Anexa",
]

# 1. CARREGAMENTO COM PERSISTÊNCIA REAL
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
        "Qtd Externa",
        "Emb Externa",
        "Qtd Interna por Externa",
        "Emb Interna",
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

# Matriz de Habilitação por Área (True = Habilitado por padrão para novos IDs)
if "permissoes_df" not in st.session_state:
  if os.path.exists(PERMISSOES_FILE):
    st.session_state.permissoes_df = pd.read_csv(PERMISSOES_FILE)
  else:
    st.session_state.permissoes_df = pd.DataFrame(
        columns=["ID", "Área", "Ativo"]
    )


def salvar_dados():
  st.session_state.estoque_df.to_csv(ESTOQUE_FILE, index=False)
  st.session_state.mov_df.to_csv(MOV_FILE, index=False)
  st.session_state.permissoes_df.to_csv(PERMISSOES_FILE, index=False)


def garantir_permissao(id_prod, area):
  df_p = st.session_state.permissoes_df
  if (
      df_p.empty
      or not ((df_p["ID"] == id_prod) & (df_p["Área"] == area)).any()
  ):
    nova_perm = pd.DataFrame([{"ID": id_prod, "Área": area, "Ativo": True}])
    st.session_state.permissoes_df = pd.concat(
        [df_p, nova_perm], ignore_index=True
    )
    salvar_dados()


# Título Principal
st.title("📦 BUILD STOCK BR — Gestão Inteligente de Almoxarifado Industrial")
st.markdown("---")

# Menu Lateral Profissional
menu = [
    "📋 Painel & Soma Geral",
    "⚙️ Habilitar / Desabilitar IDs por Área",
    "🆕 Cadastro Mestre (Galpão)",
    "🔄 Movimentações & Transferências",
    "📊 Gráficos & Linha do Tempo",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df
mov_df = st.session_state.mov_df
perm_df = st.session_state.permissoes_df

if escolha == "📋 Painel & Soma Geral":
  st.subheader("📊 Painel de Controle e Soma Geral Consolidada")

  if df.empty:
    st.info("Nenhum material cadastrado no sistema.")
  else:
    # Métricas Principais
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.metric("Total de Registros", len(df))
    with c2:
      vol_total_geral = df["Total Geral"].sum()
      st.metric("Soma Geral das 3 Áreas", f"{vol_total_geral:,.2f}")
    with c3:
      st.metric("Áreas Ativas", len(areas_reais))
    with c4:
      st.metric("Persistência CSV", "Ativo 🟢")

    st.markdown("---")

    # Soma por Área
    st.markdown("### 📈 Consolidado de Volume por Área")
    soma_por_area = df.groupby("Área")["Total Geral"].sum().reset_index()
    st.dataframe(soma_por_area, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Rastreio e Estoque Detalhado por ID")

    # Filtro por ID
    ids_unicos = ["TODOS OS IDS"] + list(df["ID"].unique())
    filtro_id = st.selectbox("Selecione o ID Rastreador", ids_unicos)

    area_filtro = st.selectbox(
        "Filtrar por Área", ["TODAS AS ÁREAS"] + areas_reais
    )

    df_exibir = df.copy()
    if filtro_id != "TODOS OS IDS":
      df_exibir = df_exibir[df_exibir["ID"] == filtro_id]
    if area_filtro != "TODAS AS ÁREAS":
      df_exibir = df_exibir[df_exibir["Área"] == area_filtro]

    st.dataframe(df_exibir, use_container_width=True)

    # Botão de Download
    csv_data = df_exibir.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatório Atual (CSV)",
        data=csv_data,
        file_name="build_stock_relatorio.csv",
        mime="text/csv",
    )

elif escolha == "⚙️ Habilitar / Desabilitar IDs por Área":
  st.subheader("⚙️ Controle de Visibilidade de IDs por Área")
  st.markdown(
      "Ative ou desative quais IDs aparecem ou podem ser movimentados em cada"
      " área (ex: Sala Anexa com apenas 2 itens habilitados)."
  )

  if df.empty:
    st.warning("Cadastre itens no Cadastro Mestre primeiro.")
  else:
    ids_cadastrados = df["ID"].unique()

    area_config = st.selectbox("Selecione a Área para Configurar", areas_reais)

    st.markdown(f"### Matriz de Ativação para: **{area_config}**")

    for id_p in ids_cadastrados:
      garantir_permissao(id_p, area_config)
      idx_p = perm_df[
          (perm_df["ID"] == id_p) & (perm_df["Área"] == area_config)
      ].index

      if not idx_p.empty:
        status_atual = bool(perm_df.loc[idx_p[0], "Ativo"])
        novo_status = st.checkbox(
            f"ID: {id_p} (Habilitado nesta área)",
            value=status_atual,
            key=f"chk_{area_config}_{id_p}",
        )
        if novo_status != status_atual:
          perm_df.loc[idx_p[0], "Ativo"] = novo_status
          salvar_dados()
          st.rerun()

elif escolha == "🆕 Cadastro Mestre (Galpão)":
  st.subheader(
      "➕ Cadastro Mestre de Novo Material (Entrada Inicial no Galpão de"
      " Materiais Refratários)"
  )

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
    c4, c5, c6, c7 = st.columns(4)
    with c4:
      qtd_ext = st.number_input("Qtd Externa", min_value=0.1, value=1.0)
    with c5:
      emb_ext = st.selectbox(
          "Tipo Emb Externa", ["Palete", "Caixa", "Fardo", "Tambor"]
      )
    with c6:
      qtd_int_ext = st.number_input(
          "Qtd Interna por Externa", min_value=0.1, value=40.0
      )
    with c7:
      emb_int = st.selectbox(
          "Tipo Emb Interna", ["Saco", "Rolo", "M²", "M", "PÇ", "Galão", "UN"]
      )

    medida_int = st.number_input(
        "⚖️ Medida por Unidade Interna (KG/M/L)", min_value=0.01, value=25.0
    )
    un_final = st.selectbox("📏 Unidade Final", ["KG", "UN", "L", "M", "M²"])

    total_calculado = qtd_ext * qtd_int_ext * medida_int
    st.info(
        f"💡 **Volume Calculado Inicial no Galpão:** {total_calculado:,.2f}"
        f" {un_final}"
    )

    salvar_btn = st.form_submit_button("💾 Salvar Cadastro no Galpão")

    if salvar_btn:
      if not id_prod or not descricao or not marca or not lote:
        st.error("❌ Preencha todos os campos obrigatórios com *!")
      else:
        galpao_nome = areas_reais[0]  # Galpão de Materiais Refratários

        # Verifica se já existe o registro exato no galpão
        novo_reg = pd.DataFrame([{
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
            "Marca": marca.upper(),
            "Lote": lote.upper(),
            "Fabricação": str(fab_data),
            "Validade": str(
                pd.to_datetime(fab_data)
                + pd.Timedelta(days=int(validade_dias))
            ).split()[0],
            "Área": galpao_nome,
            "Qtd Externa": qtd_ext,
            "Emb Externa": emb_ext,
            "Qtd Interna por Externa": qtd_int_ext,
            "Emb Interna": emb_int,
            "Medida por Interna": medida_int,
            "Unidade Final": un_final,
            "Total Geral": total_calculado,
        }])

        st.session_state.estoque_df = pd.concat(
            [df, novo_reg], ignore_index=True
        )

        # Habilita automaticamente para todas as áreas inicialmente
        for ar in areas_reais:
          garantir_permissao(id_prod.upper(), ar)

        # Registra no histórico de movimentações
        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
            "Lote": lote.upper(),
            "Tipo": "📥 Entrada Inicial (Cadastro)",
            "Quantidade": total_calculado,
            "Origem": "Fornecedor Externo",
            "Destino": galpao_nome,
            "Responsável": "Almoxarife",
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        salvar_dados()
        st.success(
            f"✅ ID **{id_prod.upper()}** cadastrado com sucesso no **{galpao_nome}**"
            " e disponível para as demais áreas!"
        )

elif escolha == "🔄 Movimentações & Transferências":
  st.subheader(
      "🔄 Movimentações por Área (Entrada, Saída, Devolução e Transferência"
      " Automática)"
  )

  if df.empty:
    st.warning("Não há materiais cadastrados.")
  else:
    area_operacao = st.selectbox("Selecione a Área da Operação", areas_reais)

    # Filtra IDs habilitados para esta área
    ids_habilitados = perm_df[
        (perm_df["Área"] == area_operacao) & (perm_df["Ativo"] == True)
    ]["ID"].unique()

    df_area_permitida = df[
        (df["Área"] == area_operacao) & (df["ID"].isin(ids_habilitados))
    ]

    # Se a área for a Oficina e o item não existir fisicamente lá ainda mas estiver habilitado no catálogo global, permite puxar do galpão
    df_disponivel_mov = df[df["ID"].isin(ids_habilitados)]

    if df_disponivel_mov.empty:
      st.warning(
          f"Nenhum ID habilitado ou com estoque disponível para a área"
          f" **{area_operacao}**. Verifique a aba de Habilitação de IDs."
      )
    else:
      item_op = st.selectbox(
          "Selecione o Material / Lote",
          df_disponivel_mov["ID"]
          + " - "
          + df_disponivel_mov["Descrição"]
          + " (Lote: "
          + df_disponivel_mov["Lote"]
          + " | Área Atual: "
          + df_disponivel_mov["Área"]
          + ")",
      )

      id_sel = item_op.split(" - ")[0]
      lote_sel = item_op.split("Lote: ")[1].split(" | ")[0]
      area_atual_item = item_op.split("Área Atual: ")[1].split(")")[0]

      reg_item = df[
          (df["ID"] == id_sel)
          & (df["Lote"] == lote_sel)
          & (df["Área"] == area_atual_item)
      ].iloc[0]
      max_qtd = reg_item["Total Geral"]
      unidade = reg_item["Unidade Final"]

      st.info(
          f"📍 **Localização Atual:** {area_atual_item} | 📦 **Saldo no Lote:**"
          f" {max_qtd:,.2f} {unidade}"
      )

      c_m1, c_m2 = st.columns(2)
      with c_m1:
        tipo_op = st.selectbox(
            "Tipo de Movimentação",
            [
                "📤 Saída (Com Transferência Automática entre Áreas)",
                "📥 Entrada Direta na Área",
                "↩️ Devolução para a Área",
            ],
        )
      with c_m2:
        qtd_mov = st.number_input(
            f"Quantidade ({unidade})", min_value=0.01, value=1.0
        )

      destino_transf = None
      if "Saída" in tipo_op:
        destinos_possiveis = [a for a in areas_reais if a != area_atual_item]
        destino_transf = st.selectbox(
            "Destino Automático da Saída",
            destinos_possiveis if destinos_possiveis else areas_reais,
        )

      responsavel = st.text_input("👤 Responsável pela Operação", value="Almoxarife")

      if st.button("⚡ Executar Operação"):
        idx_origem = df[
            (df["ID"] == id_sel)
            & (df["Lote"] == lote_sel)
            & (df["Área"] == area_atual_item)
        ].index[0]

        if "Saída" in tipo_op:
          if qtd_mov > max_qtd:
            st.error("❌ Erro: Quantidade solicitada excede o saldo atual!")
            st.stop()

          # Subtrai da origem
          df.loc[idx_origem, "Total Geral"] -= qtd_mov

          # Adiciona/Atualiza automaticamente no destino
          ja_existe_dest = df[
              (df["ID"] == id_sel)
              & (df["Lote"] == lote_sel)
              & (df["Área"] == destino_transf)
          ]
          if not ja_existe_dest.empty:
            idx_d = ja_existe_dest.index[0]
            df.loc[idx_d, "Total Geral"] += qtd_mov
          else:
            nova_linha_d = reg_item.copy()
            nova_linha_d["Área"] = destino_transf
            nova_linha_d["Total Geral"] = qtd_mov
            df = pd.concat([df, pd.DataFrame([nova_linha_d])], ignore_index=True)

          tipo_hist = "🚀 Saída com Transferência Automática"
          destino_reg = destino_transf

        elif "Entrada" in tipo_op:
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          tipo_hist = "📥 Entrada Direta"
          destino_reg = area_atual_item
          area_atual_item = "Fornecedor / Externo"

        else:  # Devolução
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          tipo_hist = "↩️ Devolução"
          destino_reg = area_atual_item
          area_atual_item = "Setor Consumidor / Obra"

        st.session_state.estoque_df = df

        # Registra auditoria
        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_sel,
            "Descrição": reg_item["Descrição"],
            "Lote": lote_sel,
            "Tipo": tipo_hist,
            "Quantidade": qtd_mov,
            "Origem": area_atual_item,
            "Destino": destino_reg,
            "Responsável": responsavel,
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )

        salvar_dados()
        st.success(
            f"✅ Operação **{tipo_hist}** realizada com sucesso! Saldo"
            " atualizado."
        )
        st.rerun()

  st.markdown("---")
  st.markdown("### 📜 Histórico Completo de Auditoria")
  if mov_df.empty:
    st.info("Nenhuma movimentação registrada.")
  else:
    st.dataframe(mov_df, use_container_width=True)

elif escolha == "📊 Gráficos & Linha do Tempo":
  st.subheader("📊 Gráficos Analíticos e Linha do Tempo por ID")

  if df.empty:
    st.info("Cadastre dados para visualizar os relatórios.")
  else:
    c_g1, c_g2 = st.columns(2)
    with c_g1:
      st.markdown("#### 📊 Volume Total por ID (Soma Geral)")
      df_chart = df.groupby("ID")["Total Geral"].sum().reset_index()
      st.bar_chart(df_chart, x="ID", y="Total Geral")

    with c_g2:
      st.markdown("#### 🏢 Soma de Estoque por Área")
      df_area_chart = df.groupby("Área")["Total Geral"].sum().reset_index()
      st.bar_chart(df_area_chart, x="Área", y="Total Geral")

    st.markdown("---")
    st.markdown("### 🕒 Linha do Tempo de Movimentações por ID")
    if not mov_df.empty:
      id_timeline = st.selectbox(
          "Selecione o ID para auditoria cronológica", mov_df["ID"].unique()
      )
      df_tl = mov_df[mov_df["ID"] == id_timeline]
      st.dataframe(df_tl, use_container_width=True)
    else:
      st.info("Sem movimentações para gerar linha do tempo.")
