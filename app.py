from datetime import datetime
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Reforma de Fornos - Build Stock", layout="wide")

# Estilização Visual Customizada
st.markdown(
    """
<style>
.main {
    background-color: #f8f6f0;
}
.gaveta-retangular {
    background: linear-gradient(180deg, #e6f0ff 0%, #b3d1ff 100%);
    border: 4px solid #0055a4;
    border-radius: 6px;
    height: 85px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-bottom: 10px;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.2), 0 0 15px #00aaff;
}
.gaveta-retangular:before {
    content: ''; position: absolute; left: -8px; top: 15px; bottom: 15px;
    width: 20px; background: linear-gradient(90deg, #666, #aaa);
    border-radius: 4px; border: 2px solid #333;
}
.gaveta-retangular:after {
    content: ''; position: absolute; right: -8px; top: 15px; bottom: 15px;
    width: 20px; background: linear-gradient(90deg, #aaa, #666);
    border-radius: 4px; border: 2px solid #333;
}
.texto-reforma { font-size: 26px; font-weight: 900; color: #001a4d; letter-spacing: 3px; }
h1, h2, h3 { color: #3b2716 !important; font-family: 'Georgia', serif; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO (SESSION STATE)
# -------------------------------------------------------------
if "gavetas" not in st.session_state:
  st.session_state.gavetas = {i: "LIBERADA" for i in range(1, 21)}
  for i in [3, 6, 9, 12, 15, 18]:
    st.session_state.gavetas[i] = "TRANCADA"

if "materiais_gaveta" not in st.session_state:
  st.session_state.materiais_gaveta = pd.DataFrame(
      columns=[
          "Gaveta_ID",
          "ID_ITEM",
          "DESCRIÇÃO",
          "MARCA",
          "LOTE",
          "VALIDADE",
          "QTD/PALETE",
          "ENTRADA",
          "PESO UNITÁRIO",
          "TOTAL",
          "UNIDADE DE MEDIDA",
          "DATA HORA",
      ]
  )
  st.session_state.materiais_gaveta.loc[0] = [
      1,
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
      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  ]

if "gaveta_selecionada_detalhe" not in st.session_state:
  st.session_state.gaveta_selecionada_detalhe = None

# -------------------------------------------------------------
# TÍTULO E CABEÇALHO DO PAINEL
# -------------------------------------------------------------
st.markdown(
    '<div class="gaveta-retangular"><div class="texto-reforma">🔥 REFORMA DE'
    " FORNOS - BUILD STOCK 🔥</div></div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# VISUALIZAÇÃO DE UMA GAVETA ESPECÍFICA (DETALHES E MATERIAIS)
# -------------------------------------------------------------
if st.session_state.gaveta_selecionada_detalhe is not None:
  gav_num = st.session_state.gaveta_selecionada_detalhe
  status_atual = st.session_state.gavetas.get(gav_num, "LIBERADA")

  if st.button("⬅️ Voltar para o Painel Geral de Gavetas"):
    st.session_state.gaveta_selecionada_detalhe = None
    st.rerun()

  st.markdown("---")
  st.subheader(
      f"📂 Gerenciamento de Materiais — Gaveta {gav_num:02d} ({status_atual})"
  )

  # Adicionar Novo Lançamento na Gaveta Atual
  with st.expander("➕ Adicionar Novo Lançamento de Material nesta Gaveta"):
    with st.form(f"form_mat_{gav_num}"):
      c1, c2, c3 = st.columns(3)
      with c1:
        id_mat = st.text_input("ID do Item", value="1")
        descricao = st.text_input("DESCRIÇÃO", value="CIMENTO")
        marca = st.text_input("MARCA", value="FONDU")
      with c2:
        lote = st.text_input("LOTE", value="010101")
        validade = st.date_input("VALIDADE")
        unidade_medida = st.selectbox(
            "UNIDADE DE MEDIDA",
            ["KG", "TON", "SACOS", "UNIDADES", "LITROS", "M²"],
        )
      with c3:
        qtd_palete = st.number_input(
            "QTD/PALETE", value=56.0, min_value=0.0
        )
        entrada = st.number_input("ENTRADA (Paletes)", value=10.0, min_value=0.0)
        peso_unitario = st.number_input(
            "PESO UNITÁRIO", value=25.0, min_value=0.0
        )

      btn_salvar = st.form_submit_button(
          "💾 Salvar Lançamento na Gaveta Selecionada"
      )
      if btn_salvar:
        total_calculado = (
            float(qtd_palete) * float(entrada) * float(peso_unitario)
        )
        
        # Garante que todas as colunas existentes (inclusive as customizadas criadas pelo usuário) recebam valor vazio no novo item
        novo_dicionario = {
            "Gaveta_ID": gav_num,
            "ID_ITEM": str(id_mat),
            "DESCRIÇÃO": descricao.upper(),
            "MARCA": marca.upper(),
            "LOTE": lote,
            "VALIDADE": str(validade),
            "QTD/PALETE": float(qtd_palete),
            "ENTRADA": float(entrada),
            "PESO UNITÁRIO": float(peso_unitario),
            "TOTAL": float(total_calculado),
            "UNIDADE DE MEDIDA": unidade_medida,
            "DATA HORA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for col in st.session_state.materiais_gaveta.columns:
            if col not in novo_dicionario:
                novo_dicionario[col] = ""

        novo_registro = pd.DataFrame([novo_dicionario])
        st.session_state.materiais_gaveta = pd.concat(
            [st.session_state.materiais_gaveta, novo_registro],
            ignore_index=True,
        )
        st.success("Lançamento adicionado com sucesso!")
        st.rerun()

  # Criar Nova Coluna Customizada na Tabela
  with st.expander("🛠️ Criar Novo Campo / Coluna Personalizada"):
    with st.form("form_nova_coluna_gaveta"):
      nome_nova_coluna = st.text_input("Nome da Nova Coluna (Ex: OBSERVAÇÃO, FORNECEDOR)")
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
  st.subheader("📊 Tabela de Materiais da Gaveta")

  df_gav = st.session_state.materiais_gaveta[
      st.session_state.materiais_gaveta["Gaveta_ID"] == gav_num
  ].copy()

  if not df_gav.empty:
    unidades_disponiveis = df_gav["UNIDADE DE MEDIDA"].unique().tolist() if "UNIDADE DE MEDIDA" in df_gav.columns else []
    if unidades_disponiveis:
        filtro_unidade = st.multiselect(
            "🔍 Filtrar por UNIDADE DE MEDIDA:",
            options=unidades_disponiveis,
            default=unidades_disponiveis,
        )
        if filtro_unidade:
          df_gav = df_gav[df_gav["UNIDADE DE MEDIDA"].isin(filtro_unidade)]

    colunas_exibicao = [
        c for c in st.session_state.materiais_gaveta.columns if c != "Gaveta_ID"
    ]
    df_editado = st.data_editor(
        df_gav[colunas_exibicao], use_container_width=True, num_rows="dynamic"
    )

    if st.button("💾 Salvar Alterações na Tabela"):
      df_atualizado = df_editado.copy()
      if (
          "QTD/PALETE" in df_atualizado.columns
          and "ENTRADA" in df_atualizado.columns
          and "PESO UNITÁRIO" in df_atualizado.columns
          and "TOTAL" in df_atualizado.columns
      ):
        df_atualizado["TOTAL"] = (
            df_atualizado["QTD/PALETE"]
            * df_atualizado["ENTRADA"]
            * df_atualizado["PESO UNITÁRIO"]
        )
      df_atualizado["Gaveta_ID"] = gav_num

      st.session_state.materiais_gaveta = st.session_state.materiais_gaveta[
          st.session_state.materiais_gaveta["Gaveta_ID"] != gav_num
      ]
      st.session_state.materiais_gaveta = pd.concat(
          [
              st.session_state.materiais_gaveta,
              df_atualizado[st.session_state.materiais_gaveta.columns],
          ],
          ignore_index=True,
      )
      st.success("Alterações salvas com sucesso!")
      st.rerun()
  else:
    st.info(
        "Nenhum material cadastrado nesta gaveta com esse filtro ou ainda vazia."
    )

# -------------------------------------------------------------
# PAINEL GERAL DE GAVETAS (EM GRADE DE 5 COLUNAS)
# -------------------------------------------------------------
else:
  st.caption("✅ LIBERADA • Ativa • Clique em 'Abrir Gaveta' para gerenciar os itens e adicionar campos")
  st.subheader(f"GAVETAS DO ARMÁRIO ({len(st.session_state.gavetas)})")

  # Exibição em grade de 5 colunas
  items = list(st.session_state.gavetas.items())
  num_cols = 5
  linhas = [items[i : i + num_cols] for i in range(0, len(items), num_cols)]

  for linha in linhas:
    cols = st.columns(num_cols)
    for idx, (i, status) in enumerate(linha):
      with cols[idx]:
        with st.container(border=True):
          st.markdown(f"**GAVETA {i:02d}**")
          if status == "LIBERADA":
            st.success("LIBERADA")
          else:
            st.error("TRANCADA")

          if st.button(f"📂 Abrir Gaveta {i:02d}", key=f"abrir_{i}", use_container_width=True):
            st.session_state.gaveta_selecionada_detalhe = i
            st.rerun()

  st.divider()

  # =============================================================
  # CONTROLES DO OPERADOR NA PARTE INFERIOR
  # =============================================================
  st.subheader("⚙️ Controles do Operador - Parte Inferior")

  numero = st.text_input(
      "Digite o número da gaveta",
      placeholder="Ex: 5 ou 5,6,7,8 - deixe vazio para todas",
  )

  b1, b2, b3, b4, b5 = st.columns(5)

  with b1:
    if st.button("🔓 Liberar", use_container_width=True, type="primary"):
      if numero.strip() == "":
        for k in st.session_state.gavetas:
          st.session_state.gavetas[k] = "LIBERADA"
      else:
        for n in numero.split(","):
          try:
            n = int(n.strip())
            if n in st.session_state.gavetas:
              st.session_state.gavetas[n] = "LIBERADA"
          except:
            pass
      st.rerun()

  with b2:
    if st.button("🔒 Trancar", use_container_width=True):
      if numero.strip() == "":
        for k in st.session_state.gavetas:
          st.session_state.gavetas[k] = "TRANCADA"
      else:
        for n in numero.split(","):
          try:
            n = int(n.strip())
            if n in st.session_state.gavetas:
              st.session_state.gavetas[n] = "TRANCADA"
          except:
            pass
      st.rerun()

  with b3:
    if st.button("🔓 Liberar Todas", use_container_width=True):
      for k in st.session_state.gavetas:
        st.session_state.gavetas[k] = "LIBERADA"
      st.rerun()

  with b4:
    if st.button("🔒 Trancar Todas", use_container_width=True):
      for k in st.session_state.gavetas:
        st.session_state.gavetas[k] = "TRANCADA"
      st.rerun()

  with b5:
    if st.button(
        "✨ Criar Nova Gaveta (Automático)",
        use_container_width=True,
        type="primary",
    ):
      novo = len(st.session_state.gavetas) + 1
      st.session_state.gavetas[novo] = "LIBERADA"
      st.toast(f"Gaveta {novo} criada automaticamente!")
      st.rerun()

  st.info(
      f"Total visível: {len(st.session_state.gavetas)} gavetas | Liberadas:"
      f" {sum(1 for v in st.session_state.gavetas.values() if v=='LIBERADA')}"
  )
