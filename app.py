from datetime import datetime, timedelta
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
ESTOQUE_FILE = "build_stock_estoque_v10.csv"
MOV_FILE = "build_stock_movimentacoes_v10.csv"
PERMISSOES_FILE = "build_stock_permissoes_v10.csv"
COMBO_FILE = "build_stock_combos_v10.csv"

areas_reais = [
    "🏭 Galpão de Materiais Refratários",
    "🧱 Oficina de Revestimento",
    "🚪 Sala Anexa",
]


# CARGA INICIAL COM ESTOQUE ZERADO (APENAS PARA BASE DE ESTRUTURA)
def criar_carga_inicial_ltc():
  dados_iniciais = [
      {
          "ID": "ID-1",
          "Descrição": "CIMENTO LAFARGE FONDU",
          "Marca": "LAFARGE",
          "Lote": "09/07/25_1400",
          "Fabricação": "2025-07-09",
          "Validade": "2026-07-09",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 1400.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-1",
          "Descrição": "CIMENTO LAFARGE FONDU",
          "Marca": "LAFARGE",
          "Lote": "09/07/25_375",
          "Fabricação": "2025-07-09",
          "Validade": "2026-07-09",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 375.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-2",
          "Descrição": "CARBETO DE SILICIO",
          "Marca": "PADRÃO",
          "Lote": "LOTE-02",
          "Fabricação": "2026-01-01",
          "Validade": "2027-01-01",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 1000.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-3",
          "Descrição": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S",
          "Marca": "TECNOFIRE",
          "Lote": "LOTE-3A",
          "Fabricação": "2026-01-01",
          "Validade": "2027-01-01",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 1200.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-3",
          "Descrição": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S",
          "Marca": "TECNOFIRE",
          "Lote": "LOTE-3B",
          "Fabricação": "2026-01-01",
          "Validade": "2027-01-01",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 400.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-4",
          "Descrição": "CASTIBAR PSI UG",
          "Marca": "CASTIBAR",
          "Lote": "LOTE-4A",
          "Fabricação": "2026-01-01",
          "Validade": "2027-01-01",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Palete",
          "Qtd Interna por Externa": 1.0,
          "Emb Interna": "Saco",
          "Medida por Interna": 1250.0,
          "Unidade Final": "KG",
          "Total Geral": 0.0,
      },
      {
          "ID": "ID-5",
          "Descrição": "LÃ DE ROCHA IBAR SEM CORTE",
          "Marca": "IBAR",
          "Lote": "LOTE-5A",
          "Fabricação": "2026-01-01",
          "Validade": "2027-01-01",
          "Área": areas_reais[0],
          "Qtd Externa": 0.0,
          "Emb Externa": "Caixa",
          "Qtd Interna por Externa": 6.0,
          "Emb Interna": "PACOTE",
          "Medida por Interna": 1.0,
          "Unidade Final": "UN",
          "Total Geral": 0.0,
      },
  ]
  return pd.DataFrame(dados_iniciais)


# Carregamento com Persistência
if "estoque_df" not in st.session_state:
  if os.path.exists(ESTOQUE_FILE):
    st.session_state.estoque_df = pd.read_csv(ESTOQUE_FILE)
  else:
    st.session_state.estoque_df = criar_carga_inicial_ltc()

if "mov_df" not in st.session_state:
  if os.path.exists(MOV_FILE):
    st.session_state.mov_df = pd.read_csv(MOV_FILE)
  else:
    st.session_state.mov_df = pd.DataFrame(columns=[
        "Data/Hora",
        "ID",
        "Descrição",
        "Marca",
        "Lote",
        "Tipo",
        "Quantidade",
        "Origem",
        "Destino",
        "Responsável",
    ])

if "permissoes_df" not in st.session_state:
  if os.path.exists(PERMISSOES_FILE):
    st.session_state.permissoes_df = pd.read_csv(PERMISSOES_FILE)
  else:
    perm_list = []
    ids_unicos = st.session_state.estoque_df["ID"].unique()
    for i in ids_unicos:
      for a in areas_reais:
        perm_list.append({"ID": i, "Área": a, "Ativo": True})
    st.session_state.permissoes_df = pd.DataFrame(perm_list)

if "combo_df" not in st.session_state:
  if os.path.exists(COMBO_FILE):
    st.session_state.combo_df = pd.read_csv(COMBO_FILE)
  else:
    st.session_state.combo_df = pd.DataFrame(
        columns=[
            "Codigo_Combo",
            "Nome_Produto_Acabado",
            "ID_Insumo",
            "Qtd_Utilizada",
        ]
    )


def salvar_dados():
  st.session_state.estoque_df.to_csv(ESTOQUE_FILE, index=False)
  st.session_state.mov_df.to_csv(MOV_FILE, index=False)
  st.session_state.permissoes_df.to_csv(PERMISSOES_FILE, index=False)
  st.session_state.combo_df.to_csv(COMBO_FILE, index=False)


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
st.title("📦 BUILD STOCK BR — Gestão Industrial Avançada por ID e Local")
st.markdown("---")

# Menu Lateral
menu = [
    "📋 Painel & Soma Geral",
    "📊 Visão por ID, Locais, Gráficos & Histórico",
    "⚙️ Habilitar / Desabilitar IDs por Área",
    "🆕 Cadastro Mestre (Galpão)",
    "🛠️ Cadastro de Combo (Produto Acabado)",
    "⚡ Baixa por Entrega / Produção (7 Caracteres)",
    "🔄 Movimentações Cruzadas",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df
mov_df = st.session_state.mov_df
perm_df = st.session_state.permissoes_df
combo_df = st.session_state.combo_df

if escolha == "📋 Painel & Soma Geral":
  st.subheader("📊 Painel de Controle Consolidado")
  if df.empty:
    st.info("Nenhum material cadastrado.")
  else:
    st.markdown("### 📈 Soma Total Consolidada de Estoque por ID")
    soma_por_id = df.groupby(["ID", "Descrição", "Unidade Final"])[
        "Total Geral"
    ].sum().reset_index()
    st.dataframe(soma_por_id, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏢 Estoque Detalhado")
    st.dataframe(df, use_container_width=True)

elif escolha == "📊 Visão por ID, Locais, Gráficos & Histórico":
  st.subheader(
      "📊 Consulta Dinâmica: Seleção Múltipla de IDs, Gráficos Horizontais &"
      " Histórico"
  )

  if df.empty:
    st.info("Nenhum dado cadastrado.")
  else:
    lista_ids = sorted(df["ID"].unique())

    st.markdown("### 🔍 Selecione as IDs para Exibir no Gráfico e Relatório")
    ids_selecionadas = st.multiselect(
        "Escolha uma ou mais IDs:",
        lista_ids,
        format_func=lambda x: f"{x} — {df[df['ID'] == x]['Descrição'].iloc[0]}",
    )

    if not ids_selecionadas:
      st.info(
          "👆 Selecione ao menos uma ID acima para carregar os gráficos e os"
          " dados detalhados."
      )
    else:
      df_ids_estoque = df[df["ID"].isin(ids_selecionadas)]

      st.markdown("---")
      st.markdown(
          "### 📊 Gráfico de Barras Horizontal: Saldo por ID, Marca e Lote"
      )

      if not df_ids_estoque.empty:
        df_ids_estoque["ID_Marca_Lote_Area"] = (
            "["
            + df_ids_estoque["ID"]
            + "] "
            + df_ids_estoque["Marca"]
            + " | Lote: "
            + df_ids_estoque["Lote"]
            + " ("
            + df_ids_estoque["Área"]
            + ")"
        )

        import altair as alt

        chart_data = (
            df_ids_estoque.groupby("ID_Marca_Lote_Area")["Total Geral"]
            .sum()
            .reset_index()
        )

        alt_chart = (
            alt.Chart(chart_data)
            .mark_bar(color="#1f77b4", cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Total Geral:Q", title="Saldo Total (Unidade do Material)"
                ),
                y=alt.Y(
                    "ID_Marca_Lote_Area:N",
                    sort="-x",
                    title="ID, Marca, Lote & Área",
                ),
                tooltip=["ID_Marca_Lote_Area", "Total Geral"],
            )
            .properties(height=300)
        )

        st.altair_chart(alt_chart, use_container_width=True)
        st.caption(
            "💡 *Este gráfico de barras horizontal exibe de forma clara e"
            " lúdica o saldo separado por Marca, Lote e Área para todas as IDs"
            " selecionadas.*"
        )

      st.markdown("---")

      # MÉTRICAS DE SALDO GERAL POR ID SELECIONADA
      st.markdown("### 🌟 Saldo Geral Consolidado por ID")
      cols_metricas = st.columns(min(len(ids_selecionadas), 4))
      for i, id_sel in enumerate(ids_selecionadas):
        df_um_id = df_ids_estoque[df_ids_estoque["ID"] == id_sel]
        desc_mat = df_um_id["Descrição"].iloc[0]
        unidade_mat = df_um_id["Unidade Final"].iloc[0]
        saldo_total_id = df_um_id["Total Geral"].sum()

        with cols_metricas[i % len(cols_metricas)]:
          st.metric(
              label=f"ID: {id_sel} ({unidade_mat})",
              value=f"{saldo_total_id:,.2f}",
              delta=desc_mat,
          )

      st.markdown("---")

      # TABELA DETALHADA
      crypto_detalhe = (
          df_ids_estoque.groupby(
              ["ID", "Descrição", "Área", "Marca", "Lote", "Unidade Final"]
          )["Total Geral"]
          .sum()
          .reset_index()
      )
      st.markdown("### 🏢 Estoque Detalhado das IDs Selecionadas")
      st.dataframe(crypto_detalhe, use_container_width=True)

      st.markdown("---")

      # HISTÓRICO DE MOVIMENTAÇÕES PARA AS IDS SELECIONADAS
      st.markdown("### 🕒 Histórico de Movimentações das IDs Selecionadas")
      if mov_df.empty:
        st.info("Nenhuma movimentação registrada no sistema.")
      else:
        mov_ids = mov_df[mov_df["ID"].isin(ids_selecionadas)].copy()

        if mov_ids.empty:
          st.info(
              "Nenhuma movimentação registrada para as IDs selecionadas."
          )
        else:
          mov_ids["Data/Hora_dt"] = pd.to_datetime(
              mov_ids["Data/Hora"], errors="coerce"
          )
          agora = datetime.now(BR_TZ)

          periodo_filtro = st.selectbox(
              "📅 Selecione o Período do Histórico",
              [
                  "Todos os Registros",
                  "Diário (Últimas 24 Horas)",
                  "Semanal (Últimos 7 Dias)",
                  "Mensal (Últimos 30 Dias)",
                  "Anual (Último Ano)",
              ],
          )

          if periodo_filtro == "Diário (Últimas 24 Horas)":
            limite_data = agora - timedelta(days=1)
            mov_ids = mov_ids[mov_ids["Data/Hora_dt"] >= limite_data]
          elif periodo_filtro == "Semanal (Últimos 7 Dias)":
            limite_data = agora - timedelta(days=7)
            mov_ids = mov_ids[mov_ids["Data/Hora_dt"] >= limite_data]
          elif periodo_filtro == "Mensal (Últimos 30 Dias)":
            limite_data = agora - timedelta(days=30)
            mov_ids = mov_ids[mov_ids["Data/Hora_dt"] >= limite_data]
          elif periodo_filtro == "Anual (Último Ano)":
            limite_data = agora - timedelta(days=365)
            mov_ids = mov_ids[mov_ids["Data/Hora_dt"] >= limite_data]

          if mov_ids.empty:
            st.warning(
                "Nenhuma movimentação encontrada para o período selecionado."
            )
          else:
            colunas_exibir = [
                "Data/Hora",
                "ID",
                "Tipo",
                "Marca",
                "Lote",
                "Quantidade",
                "Origem",
                "Destino",
                "Responsável",
            ]
            mov_ids_exibir = mov_ids[colunas_exibir].sort_values(
                by="Data/Hora", ascending=False
            )

            st.dataframe(mov_ids_exibir, use_container_width=True)

            csv_hist = mov_ids_exibir.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Baixar Histórico Filtrado (CSV)",
                data=csv_hist,
                file_name="historico_ids_selecionadas.csv",
                mime="text/csv",
            )

elif escolha == "⚙️ Habilitar / Desabilitar IDs por Área":
  st.subheader("⚙️ Controle de Visibilidade e Ativação de IDs por Área")
  if df.empty:
    st.warning("Cadastre itens primeiro.")
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
            f"ID: {id_p} (Habilitado)",
            value=status_atual,
            key=f"chk_{area_config}_{id_p}",
        )
        if novo_status != status_atual:
          perm_df.loc[idx_p[0], "Ativo"] = novo_status
          salvar_dados()
          st.rerun()

elif escolha == "🆕 Cadastro Mestre (Galpão)":
  st.subheader("➕ Cadastro Mestre de Novo Material (Galpão)")
  with st.form("form_mestre", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      id_prod = st.text_input("🔖 ID Rastreador / Código (Ex: ID-18) *")
      descricao = st.text_input("📝 Descrição do Material *")
    with c2:
      marca = st.text_input("🏷️ Marca / Fabricante (Editável) *", value="PADRÃO")
      lote = st.text_input("📦 Número do Lote *")
    with c3:
      fab_data = st.date_input("📅 Data de Fabricação")
      validade_dias = st.number_input(
          "⏳ Validade (Dias)", min_value=1, value=365
      )

    c4, c5, c6, c7 = st.columns(4)
    with c4:
      qtd_ext = st.number_input("Qtd Externa", min_value=0.0, value=0.0)
    with c5:
      emb_ext = st.selectbox(
          "Tipo Emb Externa", ["Palete", "Caixa", "Fardo", "Tambor", "UN"]
      )
    with c6:
      qtd_int_ext = st.number_input(
          "Qtd Interna por Externa", min_value=0.1, value=1.0
      )
    with c7:
      emb_int = st.selectbox(
          "Tipo Emb Interna", ["Saco", "Rolo", "M²", "M", "PÇ", "Galão", "UN"]
      )

    medida_int = st.number_input(
        "⚖️ Medida por Unidade Interna", min_value=0.01, value=1.0
    )
    un_final = st.selectbox("📏 Unidade Final", ["KG", "UN", "L", "M", "M²"])

    total_calculado = qtd_ext * qtd_int_ext * medida_int
    salvar_btn = st.form_submit_button("💾 Salvar Cadastro no Galpão")

    if salvar_btn:
      if not id_prod or not descricao or not marca or not lote:
        st.error("❌ Preencha todos os campos obrigatórios com *!")
      else:
        galpao_nome = areas_reais[0]
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

        for ar in areas_reais:
          garantir_permissao(id_prod.upper(), ar)

        if total_calculado > 0:
          nova_mov = pd.DataFrame([{
              "Data/Hora": get_now_br(),
              "ID": id_prod.upper(),
              "Descrição": descricao.upper(),
              "Marca": marca.upper(),
              "Lote": lote.upper(),
              "Tipo": "📥 Entrada Inicial (Galpão)",
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
            f"✅ ID **{id_prod.upper()}** (Marca: **{marca.upper()}**) cadastrado"
            " com sucesso!"
        )

elif escolha == "🛠️ Cadastro de Combo (Produto Acabado)":
  st.subheader("🛠️ Cadastro de Combo / Ficha Técnica")
  if df.empty:
    st.warning("Cadastre materiais no Cadastro Mestre primeiro.")
  else:
    with st.form("form_combo"):
      codigo_7 = st.text_input(
          "🔑 Código do Combo (Exatamente 7 Caracteres) *"
      )
      nome_produto = st.text_input("📝 Nome do Produto Acabado *")

      ids_disponiveis = df["ID"].unique()
      c1, c2 = st.columns(2)
      with c1:
        id1 = st.selectbox("Insumo 1 (ID)", ["NENHUM"] + list(ids_disponiveis))
        qtd1 = st.number_input("Qtd Insumo 1", min_value=0.0, value=0.0)
        id2 = st.selectbox("Insumo 2 (ID)", ["NENHUM"] + list(ids_disponiveis))
        qtd2 = st.number_input("Qtd Insumo 2", min_value=0.0, value=0.0)
      with c2:
        id3 = st.selectbox("Insumo 3 (ID)", ["NENHUM"] + list(ids_disponiveis))
        qtd3 = st.number_input("Qtd Insumo 3", min_value=0.0, value=0.0)
        id4 = st.selectbox("Insumo 4 (ID)", ["NENHUM"] + list(ids_disponiveis))
        qtd4 = st.number_input("Qtd Insumo 4", min_value=0.0, value=0.0)

      salvar_combo_btn = st.form_submit_button("💾 Salvar Ficha do Combo")
      if salvar_combo_btn:
        codigo_limpo = codigo_7.strip()
        if len(codigo_limpo) != 7:
          st.error(
              "❌ O código do combo deve conter exatamente **7 caracteres**."
          )
        elif not nome_produto:
          st.error("❌ Informe o nome do produto acabado.")
        else:
          combo_df = combo_df[combo_df["Codigo_Combo"] != codigo_limpo]
          novas_linhas = []
          for iid, q in [(id1, qtd1), (id2, qtd2), (id3, qtd3), (id4, qtd4)]:
            if iid != "NENHUM" and q > 0:
              novas_linhas.append({
                  "Codigo_Combo": codigo_limpo.upper(),
                  "Nome_Produto_Acabado": nome_produto.upper(),
                  "ID_Insumo": iid,
                  "Qtd_Utilizada": q,
              })
          if not novas_linhas:
            st.error("❌ Selecione pelo menos um insumo válido.")
          else:
            st.session_state.combo_df = pd.concat(
                [combo_df, pd.DataFrame(novas_linhas)], ignore_index=True
            )
            salvar_dados()
            st.success(
                f"✅ Combo **{codigo_limpo.upper()} ({nome_produto})**"
                " cadastrado com sucesso!"
            )

  if not combo_df.empty:
    st.dataframe(combo_df, use_container_width=True)

elif escolha == "⚡ Baixa por Entrega / Produção (7 Caracteres)":
  st.subheader("⚡ Baixa de Expedição e Produção (7 Caracteres)")
  if combo_df.empty:
    st.warning("Cadastre ao menos um Combo na aba anterior.")
  else:
    combos_cadastrados = combo_df["Codigo_Combo"].unique()
    with st.form("form_baixa_combo"):
      codigo_input = st.text_input(
          "🔍 Digite ou Escaneie o Código (Exatamente 7 Caracteres) *"
      )
      lote_fab = st.text_input(
          "📦 Lote de Produção / Expedição *", value="LOTE-EXPEDICAO-01"
      )
      responsavel_prod = st.text_input("👤 Responsável", value="Expedição")

      executar_baixa = st.form_submit_button(
          "🚀 Confirmar Entrega / Baixa Definitiva do Estoque"
      )
      if executar_baixa:
        cod_limpo = codigo_input.strip().upper()
        if len(cod_limpo) != 7:
          st.error("❌ O código exige exatamente **7 caracteres**.")
        elif cod_limpo not in combos_cadastrados:
          st.error(f"❌ O código **{cod_limpo}** não foi encontrado.")
        else:
          itens_combo = combo_df[combo_df["Codigo_Combo"] == cod_limpo]
          nome_prod_acabado = itens_combo["Nome_Produto_Acabado"].iloc[0]
          oficina_nome = areas_reais[1]
          falta_saldo = False
          msg_erro = ""

          for _, row in itens_combo.iterrows():
            ins_id = row["ID_Insumo"]
            qtd_nec = row["Qtd_Utilizada"]
            estoque_oficina_item = df[
                (df["ID"] == ins_id) & (df["Área"] == oficina_nome)
            ]
            saldo_atual = (
                estoque_oficina_item["Total Geral"].sum()
                if not estoque_oficina_item.empty
                else 0.0
            )
            if saldo_atual < qtd_nec:
              falta_saldo = True
              msg_erro += (
                  f"<br>• ID **{ins_id}**: Necessário {qtd_nec:,.2f} | Disponível"
                  f" na Oficina: {saldo_atual:,.2f}"
              )

          if falta_saldo:
            st.error(
                f"❌ **Saldo insuficiente na Oficina para {nome_prod_acabado}!**"
                f"{msg_erro}"
            )
          else:
            for _, row in itens_combo.iterrows():
              ins_id = row["ID_Insumo"]
              qtd_nec = row["Qtd_Utilizada"]
              restante_baixar = qtd_nec
              idxs_oficina = df[
                  (df["ID"] == ins_id)
                  & (df["Área"] == oficina_nome)
                  & (df["Total Geral"] > 0)
              ].index

              for idx in idxs_oficina:
                if restante_baixar <= 0:
                  break
                saldo_lote = df.loc[idx, "Total Geral"]
                if saldo_lote >= restante_baixar:
                  df.loc[idx, "Total Geral"] -= restante_baixar
                  restante_baixar = 0.0
                else:
                  restante_baixar -= saldo_lote
                  df.loc[idx, "Total Geral"] = 0.0

              marca_reg = (
                  df[df["ID"] == ins_id]["Marca"].iloc[0]
                  if not df[df["ID"] == ins_id].empty
                  else "PADRÃO"
              )
              lote_reg = (
                  df[df["ID"] == ins_id]["Lote"].iloc[0]
                  if not df[df["ID"] == ins_id].empty
                  else "LOTE"
              )

              nova_mov = pd.DataFrame([{
                  "Data/Hora": get_now_br(),
                  "ID": ins_id,
                  "Descrição": (
                      f"Entrega de Produto Acabado: {nome_prod_acabado} (Combo"
                      f" {cod_limpo})"
                  ),
                  "Marca": marca_reg,
                  "Lote": lote_reg,
                  "Tipo": "🚀 Saída Definitiva / Entrega (Expedição)",
                  "Quantidade": qtd_nec,
                  "Origem": oficina_nome,
                  "Destino": "Cliente / Externo (Entregue)",
                  "Responsável": responsavel_prod,
              }])
              st.session_state.mov_df = pd.concat(
                  [mov_df, nova_mov], ignore_index=True
              )

            st.session_state.estoque_df = df
            salvar_dados()
            st.success(
                f"✅ Produto acabado **{nome_prod_acabado}** entregue e insumos"
                " baixados com sucesso!"
            )
            st.rerun()

elif escolha == "🔄 Movimentações Cruzadas":
  st.subheader(
      "🔄 Movimentações Automáticas Cruzadas (Galpão ⇄ Oficina ⇄ Sala Anexa)"
  )
  if df.empty:
    st.warning("Não há materiais cadastrados.")
  else:
    area_operacao = st.selectbox(
        "Selecione a Área de Origem da Operação", areas_reais
    )
    ids_habilitados = perm_df[
        (perm_df["Área"] == area_operacao) & (perm_df["Ativo"] == True)
    ]["ID"].unique()
    df_disponivel = df[
        (df["Área"] == area_operacao) & (df["ID"].isin(ids_habilitados))
    ]

    if df_disponivel.empty:
      st.warning(f"Nenhum ID habilitado na área **{area_operacao}**.")
    else:
      df_disponivel["Opcao_Combo"] = (
          df_disponivel["ID"]
          + " — "
          + df_disponivel["Descrição"]
          + " | Marca: "
          + df_disponivel["Marca"]
          + " | Lote: "
          + df_disponivel["Lote"]
          + " | Saldo: "
          + df_disponivel["Total Geral"].astype(str)
      )

      item_op = st.selectbox(
          "Selecione o Material Específico (ID, Marca e Lote)",
          df_disponivel["Opcao_Combo"].unique(),
      )

      id_sel = item_op.split(" — ")[0]
      marca_sel = item_op.split(" | Marca: ")[1].split(" | Lote: ")[0]
      lote_sel = item_op.split(" | Lote: ")[1].split(" | Saldo: ")[0]

      reg_item = df[
          (df["ID"] == id_sel)
          & (df["Marca"] == marca_sel)
          & (df["Lote"] == lote_sel)
          & (df["Área"] == area_operacao)
      ].iloc[0]

      max_qtd = reg_item["Total Geral"]
      unidade = reg_item["Unidade Final"]

      c_m1, c_m2 = st.columns(2)
      with c_m1:
        tipo_op = st.selectbox(
            "Tipo de Operação",
            ["📤 Saída Direta", "📥 Entrada Direta", "↩️ Devolução"],
        )
      with c_m2:
        qtd_mov = st.number_input(
            f"Quantidade ({unidade})", min_value=0.01, value=1.0
        )
      responsavel = st.text_input("👤 Responsável pela Operação", value="Almoxarife")

      if st.button("⚡ Executar Operação Cruzada"):
        idx_origem = df[
            (df["ID"] == id_sel)
            & (df["Marca"] == marca_sel)
            & (df["Lote"] == lote_sel)
            & (df["Área"] == area_operacao)
        ].index[0]

        galpao_nome = areas_reais[0]
        oficina_nome = areas_reais[1]
        sala_anexa_nome = areas_reais[2]

        if "Saída" in tipo_op:
          if qtd_mov > max_qtd:
            st.error(
                "❌ Erro: Quantidade solicitada excede o saldo atual deste"
                " lote/marca!"
            )
            st.stop()
          df.loc[idx_origem, "Total Geral"] -= qtd_mov
          destino_automatico = (
              oficina_nome
              if area_operacao in [galpao_nome, sala_anexa_nome]
              else galpao_nome
          )

          ja_existe_dest = df[
              (df["ID"] == id_sel)
              & (df["Marca"] == marca_sel)
              & (df["Lote"] == lote_sel)
              & (df["Área"] == destino_automatico)
          ]
          if not ja_existe_dest.empty:
            idx_d = ja_existe_dest.index[0]
            df.loc[idx_d, "Total Geral"] += qtd_mov
          else:
            nova_linha_d = reg_item.copy()
            nova_linha_d["Área"] = destino_automatico
            nova_linha_d["Total Geral"] = qtd_mov
            df = pd.concat([df, pd.DataFrame([nova_linha_d])], ignore_index=True)

          tipo_hist = f"📤 Saída de {area_operacao} ➔ 📥 Entrada em {destino_automatico}"
          destino_reg = destino_automatico

        elif "Entrada" in tipo_op:
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          tipo_hist = "📥 Entrada com Ajuste Automático"
          destino_reg = area_operacao
        else:
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          type_hist = "↩️ Devolução"
          destino_reg = area_operacao

        st.session_state.estoque_df = df
        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_sel,
            "Descrição": reg_item["Descrição"],
            "Marca": marca_sel,
            "Lote": lote_sel,
            "Tipo": tipo_hist,
            "Quantidade": qtd_mov,
            "Origem": area_operacao,
            "Destino": destino_reg,
            "Responsável": responsavel,
        }])
        st.session_state.mov_df = pd.concat(
            [mov_df, nova_mov], ignore_index=True
        )
        salvar_dados()
        st.success("✅ Operação cruzada executada com sucesso!")
        st.rerun()

  st.markdown("---")
  st.markdown("### 📜 Histórico Geral de Auditoria")
  if not mov_df.empty:
    st.dataframe(mov_df, use_container_width=True)
