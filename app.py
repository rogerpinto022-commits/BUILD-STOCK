import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

st.set_page_config(layout="wide", page_title="Reforma Fornos - Alerta Compra")
st.markdown("""
<style>
.gaveta-principal { background: linear-gradient(90deg, #5B8DEF, #3A6ED8); border: 3px solid #1E40AF; border-radius: 12px; padding: 20px; text-align: center; color: white; font-size: 26px; font-weight: 800; margin-bottom: 15px; }
.gaveta-aberta { background: #FFFFFF; border: 4px solid #16A34A; border-top: 12px solid #16A34A; border-radius: 0 0 15px 15px; padding: 20px; margin-top: -10px; }
.alerta-compra { background: #DC2626; color: white; padding: 20px; border-radius: 12px; font-size: 20px; font-weight: 800; animation: pulse 2s infinite; }
.alerta-ok { background: #16A34A; color: white; padding: 15px; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'gavetas' not in st.session_state: st.session_state.gavetas = {i: True for i in range(1, 21)}
if 'selecionada' not in st.session_state: st.session_state.selecionada = None
if 'tabelas' not in st.session_state: st.session_state.tabelas = {}
if 'historico' not in st.session_state: st.session_state.historico = []
if 'estoque_min' not in st.session_state: st.session_state.estoque_min = {i: 1000 for i in range(1, 21)} # KG mínimo por gaveta
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuarios_liberados' not in st.session_state: st.session_state.usuarios_liberados = ["admin@admin.com"]

if not st.session_state.logado:
    st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS - LOGIN</div>', unsafe_allow_html=True)
    e = st.text_input("Email"); s = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if e in st.session_state.usuarios_liberados and s=="123456":
            st.session_state.logado=True; st.rerun()
    st.stop()

st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS - ALERTA DE COMPRA</div>', unsafe_allow_html=True)

# --- CALCULA ESTOQUE ATUAL POR GAVETA ---
estoque_atual = {}
for gid in st.session_state.gavetas.keys():
    entradas = sum([h["Total KG"] for h in st.session_state.historico if h["Gaveta"]==gid and h["Tipo"]=="ENTRADA"])
    saidas = sum([h["Total KG"] for h in st.session_state.historico if h["Gaveta"]==gid and h["Tipo"]=="SAIDA"])
    # Se não tem histórico, usa o total da tabela como estoque inicial
    if entradas==0 and saidas==0 and gid in st.session_state.tabelas and not st.session_state.tabelas[gid].empty:
        df = st.session_state.tabelas[gid]
        estoque_atual[gid] = (df["Paletes"] * df["Unitários p/ Palete"] * df["Kilos p/ Unitário"]).sum()
    else:
        estoque_atual[gid] = entradas - saidas

# --- ALERTA DE COMPRA INTELIGENTE ---
st.subheader("🚨 ALERTA DE COMPRA AUTOMÁTICO")
alertas = []
for gid, estoque in estoque_atual.items():
    minimo = st.session_state.estoque_min.get(gid, 1000)
    # Verifica validade vencida na gaveta
    vencidos_kg = 0
    if gid in st.session_state.tabelas and not st.session_state.tabelas[gid].empty:
        df = st.session_state.tabelas[gid].copy()
        df["Data Validade"] = pd.to_datetime(df["Data Validade"])
        df_venc = df[df["Data Validade"] < pd.to_datetime(date.today())]
        if not df_venc.empty:
            vencidos_kg = (df_venc["Paletes"] * df_venc["Unitários p/ Palete"] * df_venc["Kilos p/ Unitário"]).sum()

    if estoque <= minimo:
        falta = minimo*2 - estoque # Sugere comprar até 2x o mínimo
        alertas.append({"Gaveta": gid, "Motivo": "ESTOQUE BAIXO", "Estoque": estoque, "Mínimo": minimo, "Comprar": falta, "Urgência": "🔴 ALTA"})
    elif vencidos_kg > 0:
        alertas.append({"Gaveta": gid, "Motivo": f"VENCIDOS {vencidos_kg:.0f} KG", "Estoque": estoque, "Mínimo": minimo, "Comprar": vencidos_kg, "Urgência": "🟡 REPOSIÇÃO POR VENCIMENTO"})
    elif estoque <= minimo*1.3:
        alertas.append({"Gaveta": gid, "Motivo": "ESTOQUE EM ATENÇÃO", "Estoque": estoque, "Mínimo": minimo, "Comprar": minimo - estoque, "Urgência": "🟡 MÉDIA"})

if alertas:
    df_alertas = pd.DataFrame(alertas)
    for _, row in df_alertas.iterrows():
        st.markdown(f'<div class="alerta-compra">🚨 GAVETA {row["Gaveta"]:02d} - {row["Motivo"]} - Estoque: {row["Estoque"]:.0f} KG | Mín: {row["Mínimo"]:.0f} KG | ➡️ COMPRAR: {row["Comprar"]:.0f} KG - {row["Urgência"]}</div>', unsafe_allow_html=True)
    st.divider()
    st.dataframe(df_alertas, use_container_width=True)

    # Gráfico de alertas
    fig_alerta = px.bar(df_alertas, x="Gaveta", y="Comprar", color="Urgência", title="O QUE COMPRAR - por Gaveta", color_discrete_map={"🔴 ALTA":"#DC2626","🟡 MÉDIA":"#F59E0B","🟡 REPOSIÇÃO POR VENCIMENTO":"#F59E0B"})
    st.plotly_chart(fig_alerta, use_container_width=True)

    if st.button("📧 Gerar Pedido de Compra"):
        pedido_txt = "\n".join([f"Gaveta {r['Gaveta']:02d}: {r['Comprar']:.0f} KG - Motivo: {r['Motivo']}" for _, r in df_alertas.iterrows()])
        st.text_area("Pedido Gerado - Copie e envie", f"PEDIDO DE COMPRA - {date.today()}\n{pedido_txt}\nTotal Geral: {df_alertas['Comprar'].sum():.0f} KG", height=200)
else:
    st.markdown('<div class="alerta-ok">✅ NENHUM ALERTA - Todos os estoques estão dentro do mínimo</div>', unsafe_allow_html=True)

# DASHBOARD HISTORICO
if st.session_state.historico:
    df_h = pd.DataFrame(st.session_state.historico)
    df_h["Data"] = pd.to_datetime(df_h["Data"])
    c1,c2 = st.columns([3,1])
    with c1:
        periodo = st.selectbox("Histórico por:", ["Diário","Semanal","Mensal","Semestral","Anual"])
        # Simplificado para exemplo - Mensal
        df_h["MesAno"] = df_h["Data"].dt.to_period("M").astype(str)
        df_res = df_h.groupby(["MesAno","Tipo"])["Total KG"].sum().reset_index()
        fig = px.bar(df_res, x="MesAno", y="Total KG", color="Tipo", barmode="group", title=f"Entradas x Saídas - {periodo}", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        saldo_total = sum(estoque_atual.values())
        st.metric("Saldo Total Todas Gavetas", f"{saldo_total:,.0f} KG")

st.divider()

# GRID GAVETAS
cols = st.columns(5)
for i in sorted(st.session_state.gavetas.keys()):
    with cols[(i-1) % 5]:
        # Mostra alerta visual na gaveta
        estoque = estoque_atual.get(i, 0)
        minimo = st.session_state.estoque_min.get(i, 1000)
        cor = "🔴" if estoque <= minimo else ("🟡" if estoque <= minimo*1.3 else "📦")
        tipo = "primary" if st.session_state.selecionada == i else "secondary"
        if st.button(f"{cor} Gaveta {i:02d} ({estoque:.0f} KG)", key=f"g_{i}", use_container_width=True, type=tipo):
            st.session_state.selecionada = None if st.session_state.selecionada == i else i
            st.rerun()

if st.session_state.selecionada is not None:
    sel = st.session_state.selecionada
    if sel not in st.session_state.tabelas:
        st.session_state.tabelas[sel] = pd.DataFrame([{"Paletes": 1, "Unitários p/ Palete": 56, "Kilos p/ Unitário": 25.0, "Unidade": "KG", "Data Fabricação": date.today(), "Tempo Validade Dias": 90, "Data Validade": date.today()+timedelta(days=90)}])

    st.markdown('<div class="gaveta-aberta">', unsafe_allow_html=True)
    st.markdown(f"### 📂 GAVETA {sel:02d} - Estoque: {estoque_atual.get(sel,0):.0f} KG")

    c_min1, c_min2 = st.columns(2)
    with c_min1:
        novo_min = st.number_input(f"Estoque Mínimo KG Gaveta {sel}", value=st.session_state.estoque_min.get(sel,1000), step=100, key=f"min_{sel}")
        st.session_state.estoque_min[sel] = novo_min
    with c_min2:
        st.metric("Estoque Atual", f"{estoque_atual.get(sel,0):.0f} KG", delta=f"{estoque_atual.get(sel,0)-novo_min:.0f} KG vs mínimo")

    df_edit = st.data_editor(st.session_state.tabelas[sel], num_rows="dynamic", use_container_width=True, key=f"edit_{sel}")
    df_edit["Data Fabricação"] = pd.to_datetime(df_edit["Data Fabricação"])
    df_edit["Data Validade"] = df_edit["Data Fabricação"] + pd.to_timedelta(df_edit["Tempo Validade Dias"], unit="D")
    df_edit["Total KG"] = df_edit["Paletes"] * df_edit["Unitários p/ Palete"] * df_edit["Kilos p/ Unitário"]
    st.session_state.tabelas[sel] = df_edit[["Paletes","Unitários p/ Palete","Kilos p/ Unitário","Unidade","Data Fabricação","Tempo Validade Dias","Data Validade"]]

    st.markdown("#### 🔄 Registrar ENTRADA / SAÍDA")
    cm1, cm2, cm3, cm4 = st.columns(4)
    with cm1: tipo_mov = st.selectbox("Tipo", ["ENTRADA","SAIDA"], key=f"tipo_{sel}")
    with cm2: qtd_paletes_mov = st.number_input("Qtd Paletes", min_value=1, value=1, key=f"qtd_{sel}")
    with cm3: data_mov = st.date_input("Data", value=date.today(), key=f"data_{sel}")
    with cm4:
        if st.button("✅ Confirmar", type="primary", use_container_width=True, key=f"conf_{sel}"):
            media_unit = df_edit["Unitários p/ Palete"].mean() if not df_edit.empty else 56
            media_kg = df_edit["Kilos p/ Unitário"].mean() if not df_edit.empty else 25
            total_kg_mov = qtd_paletes_mov * media_unit * media_kg
            st.session_state.historico.append({"Data": datetime.combine(data_mov, datetime.min.time()), "Gaveta": sel, "Tipo": tipo_mov, "Paletes": qtd_paletes_mov, "Total KG": total_kg_mov})
            st.success(f"{tipo_mov} {total_kg_mov:.0f} KG registrada!"); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if st.button("➕ Nova Gaveta"):
    nid=max(st.session_state.gavetas.keys())+1
    st.session_state.gavetas[nid]=True
    st.session_state.estoque_min[nid]=1000
    st.rerun()
