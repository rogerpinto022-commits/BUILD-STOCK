import streamlit as st

st.set_page_config(layout="wide", page_title="Reforma de Fornos")

st.markdown("""
<style>
.gaveta-principal {
    background: linear-gradient(90deg, #5B8DEF, #3A6ED8);
    border: 3px solid #1E40AF;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 25px;
}
.gaveta-aberta {
    border: 3px solid #16A34A;
    background: #F0FDF4;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}
.gaveta-fechada {
    border: 3px solid #DC2626;
    background: #FEF2F2;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS</div>', unsafe_allow_html=True)

if 'gavetas' not in st.session_state:
    st.session_state.gavetas = {i: (i % 2 == 1) for i in range(1, 21)}
if 'selecionada' not in st.session_state:
    st.session_state.selecionada = None

total = len(st.session_state.gavetas)
liberadas = sum(1 for v in st.session_state.gavetas.values() if v)

st.markdown(f"### Gavetas ({total}) — {liberadas} Liberadas")
st.caption("Clique em uma gaveta para ABRIR e ver o interior")

cols = st.columns(5)
for i in sorted(st.session_state.gavetas.keys()):
    col = cols[(i-1) % 5]
    liberada = st.session_state.gavetas[i]
    label = f"{'✅' if liberada else '🔒'} Gaveta {i:02d}"
    with col:
        if st.button(label, key=f"g_{i}", use_container_width=True):
            st.session_state.selecionada = i
            st.rerun()

# AREA QUE ABRE - ISSO QUE FALTAVA
if st.session_state.selecionada is not None:
    sel = st.session_state.selecionada
    liberada = st.session_state.gavetas[sel]

    if liberada:
        st.markdown(f"""
        <div class="gaveta-aberta">
            <h2>✅ GAVETA {sel:02d} ABERTA</h2>
            <p>Status: LIBERADA - Pode operar</p>
            <p>Conteúdo: Ferramentas de reforma, tijolos refratários, termopar</p>
        </div>
        """, unsafe_allow_html=True)
        st.success(f"Interior da gaveta {sel:02d} liberado para uso!")
    else:
        st.markdown(f"""
        <div class="gaveta-fechada">
            <h2>🔒 GAVETA {sel:02d} TRANCADA</h2>
            <p>Status: TRANCADA - Acesso negado</p>
            <p>Libere a gaveta para ver o interior</p>
        </div>
        """, unsafe_allow_html=True)
        st.error(f"Gaveta {sel:02d} está trancada!")

st.divider()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("🔓 Liberar Selecionada", use_container_width=True, type="primary"):
        if st.session_state.selecionada:
            st.session_state.gavetas[st.session_state.selecionada] = True
            st.rerun()
with c2:
    if st.button("🔒 Trancar Selecionada", use_container_width=True):
        if st.session_state.selecionada:
            st.session_state.gavetas[st.session_state.selecionada] = False
            st.rerun()
with c3:
    if st.button("✅ Liberar Todas", use_container_width=True):
        for k in st.session_state.gavetas: st.session_state.gavetas[k] = True
        st.rerun()
with c4:
    if st.button("🔒 Trancar Todas", use_container_width=True):
        for k in st.session_state.gavetas: st.session_state.gavetas[k] = False
        st.rerun()
with c5:
    if st.button("➕ Nova Gaveta", use_container_width=True, type="primary"):
        novo_id = max(st.session_state.gavetas.keys()) + 1
        st.session_state.gavetas[novo_id] = True
        st.session_state.selecionada = novo_id
        st.rerun()
