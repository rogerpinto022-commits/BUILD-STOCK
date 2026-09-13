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
ESTOQUE_FILE = "build_stock_estoque_v5.csv"
MOV_FILE = "build_stock_movimentacoes_v5.csv"
PERMISSOES_FILE = "build_stock_permissoes_v5.csv"
COMBO_FILE = "build_stock_combos_v5.csv"

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

if "permissoes_df" not in st.session_state:
  if os.path.exists(PERMISSOES_FILE):
    st.session_state.permissoes_df = pd.read_csv(PERMISSOES_FILE)
  else:
    st.session_state.permissoes_df = pd.DataFrame(
        columns=["ID", "Área", "Ativo"]
    )

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
st.title("📦 BUILD STOCK BR — Gestão de Almoxarifado Industrial & Expedição")
st.markdown("---")

# Menu Lateral
menu = [
    "📋 Painel & Soma Geral por ID",
    "⚙️ Habilitar / Desabilitar IDs por Área",
    "🆕 Cadastro Mestre (Galpão)",
    "🛠️ Cadastro de Combo (Produto Acabado)",
    "⚡ Baixa por Entrega / Produção (7 Caracteres)",
    "🔄 Movimentações Cruzadas",
    "📊 Gráficos & Linha do Tempo",
]
escolha = st.sidebar.selectbox("🧭 Navegação", menu)

df = st.session_state.estoque_df
mov_df = st.session_state.mov_df
perm_df = st.session_state.permissoes_df
combo_df = st.session_state.combo_df

if escolha == "📋 Painel & Soma Geral por ID":
  st.subheader("📊 Painel de Controle Consolidado e Soma Geral por ID")

  if df.empty:
    st.info("Nenhum material cadastrado no sistema.")
  else:
    st.markdown("### 📈 Soma Total Consolidada de Estoque por ID (Todas as Áreas)")
    soma_por_id = df.groupby(["ID", "Descrição", "Unidade Final"])[
        "Total Geral"
    ].sum().reset_index()
    st.dataframe(soma_por_id, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏢 Estoque Detalhado por Área e ID")
    area_filtro = st.selectbox(
        "Filtrar por Área Específica", ["TODAS AS ÁREAS"] + areas_reais
    )
    df_exibir = df.copy()
    if area_filtro != "TODAS AS ÁREAS":
      df_exibir = df_exibir[df_exibir["Área"] == area_filtro]

    st.dataframe(df_exibir, use_container_width=True)

    csv_data = df_exibir.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Relatório Atual (CSV)",
        data=csv_data,
        file_name="build_stock_relatorio_geral.csv",
        mime="text/csv",
    )

elif escolha == "⚙️ Habilitar / Desabilitar IDs por Área":
  st.subheader("⚙️ Controle de Visibilidade e Ativação de IDs por Área")
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
        "⚖️ Medida por Unidade Interna", min_value=0.01, value=25.0
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

        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_prod.upper(),
            "Descrição": descricao.upper(),
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
            f"✅ ID **{id_prod.upper()}** cadastrado com sucesso no Galpão!"
        )

elif escolha == "🛠️ Cadastro de Combo (Produto Acabado)":
  st.subheader("🛠️ Cadastro de Combo / Ficha Técnica (Múltiplos IDs por Produto)")
  st.markdown(
      "Cadastre o código de 7 caracteres para identificar o produto acabado e"
      " defina os insumos consumidos da Oficina de Revestimento."
  )

  if df.empty:
    st.warning("Cadastre materiais no Cadastro Mestre primeiro.")
  else:
    with st.form("form_combo"):
      codigo_7 = st.text_input(
          "🔑 Código do Combo (Exatamente 7 Caracteres: Ex: PA00001, ABC1234) *"
      )
      nome_produto = st.text_input("📝 Nome do Produto Acabado *")

      st.markdown("### Selecione os Insumos e Quantidades Usadas")
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
              "❌ O código do combo deve conter exatamente **7 caracteres**"
              f" (digitados: {len(codigo_limpo)})."
          )
        elif not nome_produto:
          st.error("❌ Informe o nome do produto acabado.")
        else:
          combo_df = combo_df[combo_df["Codigo_Combo"] != codigo_limpo]

          novas_linhas = []
          selecoes = [(id1, qtd1), (id2, qtd2), (id3, qtd3), (id4, qtd4)]
          for iid, q in selecoes:
            if iid != "NENHUM" and q > 0:
              novas_linhas.append({
                  "Codigo_Combo": codigo_limpo.upper(),
                  "Nome_Produto_Acabado": nome_produto.upper(),
                  "ID_Insumo": iid,
                  "Qtd_Utilizada": q,
              })

          if not novas_linhas:
            st.error(
                "❌ Selecione pelo menos um insumo válido com quantidade maior"
                " que zero."
            )
          else:
            df_novos_combos = pd.DataFrame(novas_linhas)
            st.session_state.combo_df = pd.concat(
                [combo_df, df_novos_combos], ignore_index=True
            )
            salvar_dados()
            st.success(
                f"✅ Combo **{codigo_limpo.upper()} ({nome_produto})** cadastrado"
                " com sucesso!"
            )

  st.markdown("---")
  st.markdown("### 📋 Combos Cadastrados Atualmente")
  if not combo_df.empty:
    st.dataframe(combo_df, use_container_width=True)
  else:
    st.info("Nenhum combo cadastrado.")

elif escolha == "⚡ Baixa por Entrega / Produção (7 Caracteres)":
  st.subheader(
      "⚡ Baixa de Expedição e Produção (Leitura de 7 Caracteres) — Insumos"
      " Retirados Definitivamente do Estoque"
  )
  st.markdown(
      "Digite ou bipe o código de **7 caracteres** do produto acabado entregue."
      " O sistema baixará os insumos da **Oficina de Revestimento**, os"
      " retirará do estoque geral e registrará a expedição."
  )

  if combo_df.empty:
    st.warning("Cadastre ao menos um Combo na aba anterior primeiro.")
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
          st.error(
              "❌ O código informado possui "
              f"{len(cod_limpo)} caractere(s). O sistema exige exatamente"
              " **7 caracteres**."
          )
        elif cod_limpo not in combos_cadastrados:
          st.error(
              f"❌ O código **{cod_limpo}** não foi encontrado nos combos"
              " cadastrados."
          )
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
            saldo_atual_oficina = (
                estoque_oficina_item["Total Geral"].sum()
                if not estoque_oficina_item.empty
                else 0.0
            )

            if saldo_atual_oficina < qtd_nec:
              falta_saldo = True
              msg_erro += (
                  f"<br>• ID **{ins_id}**: Necessário {qtd_nec:,.2f} | Disponível"
                  f" na Oficina: {saldo_atual_oficina:,.2f}"
              )

          if falta_saldo:
            st.error(
                "❌ **Saldo insuficiente na Oficina de Revestimento para"
                f" entregar {nome_prod_acabado}!**"
                f"{msg_erro}"
            )
          else:
            # Baixa definitiva da Oficina de Revestimento (sai do estoque geral)
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

              # Registra movimentação de saída definitiva por entrega do produto acabado
              nova_mov = pd.DataFrame([{
                  "Data/Hora": get_now_br(),
                  "ID": ins_id,
                  "Descrição": (
                      f"Entrega de Produto Acabado: {nome_prod_acabado} (Combo"
                      f" {cod_limpo})"
                  ),
                  "Lote": lote_fab,
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
                f"✅ Produto acabado **{nome_prod_acabado}** entregue com"
                f" sucesso (Código: **{cod_limpo}**)! Os insumos foram"
                " retirados definitivamente do estoque geral por ID."
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
      st.warning(
          f"Nenhum ID habilitado ou com saldo disponível na área"
          f" **{area_operacao}**."
      )
    else:
      item_op = st.selectbox(
          "Selecione o Material / Lote",
          df_disponivel["ID"]
          + " - "
          + df_disponivel["Descrição"]
          + " (Lote: "
          + df_disponivel["Lote"]
          + ")",
      )

      id_sel = item_op.split(" - ")[0]
      lote_sel = item_op.split("Lote: ")[1].split(")")[0]

      reg_item = df[
          (df["ID"] == id_sel)
          & (df["Lote"] == lote_sel)
          & (df["Área"] == area_operacao)
      ].iloc[0]
      max_qtd = reg_item["Total Geral"]
      unidade = reg_item["Unidade Final"]

      st.info(
          f"📍 **Origem Atual:** {area_operacao} | 📦 **Saldo Disponível no"
          f" Lote:** {max_qtd:,.2f} {unidade}"
      )

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
            & (df["Lote"] == lote_sel)
            & (df["Área"] == area_operacao)
        ].index[0]

        galpao_nome = areas_reais[0]
        oficina_nome = areas_reais[1]
        sala_anexa_nome = areas_reais[2]

        if "Saída" in tipo_op:
          if qtd_mov > max_qtd:
            st.error("❌ Erro: Quantidade solicitada excede o saldo atual!")
            st.stop()

          df.loc[idx_origem, "Total Geral"] -= qtd_mov

          if area_operacao == galpao_nome:
            destino_automatico = oficina_nome
          elif area_operacao == sala_anexa_nome:
            destino_automatico = oficina_nome
          else:
            destino_automatico = galpao_nome

          ja_existe_dest = df[
              (df["ID"] == id_sel)
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

          tipo_hist = f"📤 Saída de {area_operacao} ➔ 📥 Entrada Automática em {destino_automatico}"
          destino_reg = destino_automatico

        elif "Entrada" in tipo_op:
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          if area_operacao == oficina_nome:
            galpao_item = df[
                (df["ID"] == id_sel)
                & (df["Lote"] == lote_sel)
                & (df["Área"] == galpao_nome)
            ]
            if not galpao_item.empty:
              idx_g = galpao_item.index[0]
              df.loc[idx_g, "Total Geral"] = max(
                  0.0, df.loc[idx_g, "Total Geral"] - qtd_mov
              )

          tipo_hist = "📥 Entrada com Ajuste Automático"
          destino_reg = area_operacao
          area_operacao = "Fornecedor / Ajuste"

        else:
          df.loc[idx_origem, "Total Geral"] += qtd_mov
          tipo_hist = "↩️ Devolução"
          destino_reg = area_operacao
          area_operacao = "Setor Consumidor"

        st.session_state.estoque_df = df

        nova_mov = pd.DataFrame([{
            "Data/Hora": get_now_br(),
            "ID": id_sel,
            "Descrição": reg_item["Descrição"],
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
        st.success(f"✅ Operação cruzada executada com sucesso!")
        st.rerun()

  st.markdown("---")
  st.markdown("### 📜 Histórico de Auditoria Cruzada")
  if mov_df.empty:
    st.info("Nenhuma movimentação registrada.")
  else:
    st.dataframe(mov_df, use_container_width=True)

elif escolha == "📊 Gráficos & Linha do Tempo":
  st.subheader("📊 Gráficos Analíticos e Soma Geral por ID")
  if df.empty:
    st.info("Cadastre dados para visualizar os relatórios.")
  else:
    c_g1, c_g2 = st.columns(2)
    with c_g1:
      st.markdown("#### 📊 Volume Total Consolidado por ID")
      df_chart = df.groupby("ID")["Total Geral"].sum().reset_index()
      st.bar_chart(df_chart, x="ID", y="Total Geral")

    with c_g2:
      st.markdown("#### 🏢 Soma de Estoque por Área")
      df_area_chart = df.groupby("Área")["Total Geral"].sum().reset_index()
      st.bar_chart(df_area_chart, x="Área", y="Total Geral")

    st.markdown("---")
    st.markdown("### 🕒 Linha do Tempo por ID")
    if not mov_df.empty:
      id_timeline = st.selectbox(
          "Selecione o ID para auditoria cronológica", mov_df["ID"].unique()
      )
      df_tl = mov_df[mov_df["ID"] == id_timeline]
      st.dataframe(df_tl, use_container_width=True)
    else:
      st.info("Sem movimentações para gerar linha do tempo.")
