import streamlit as st

st.set_page_config(layout="wide", page_title="Reforma de Fornos")

# CSS da interface
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
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
.gaveta-card {
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 12px;
    background: white;
    margin-bottom: 10px;
}
.liberada { background: #16A34A; color: white; padding: 2px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; }
.trancada { background: #DC2626; color: white; padding: 2px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# INICIO - GAVETA PRINCIPAL COM TEXTO DENTRO
st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS</div>', unsafe_allow_html=True)

# Estado padrão das gavetas (igual ao que já roda no seu app)
if 'gavetas' not in st.session_state:
    st.session_state.gavetas = {i: (i % 2 == 1) for i in range(1, 21)} # True=Liberada, False=Trancada

liberadas = sum(1 for v in st.session_state.gavetas.values() if v)
trancadas = 20 - liberadas

st.markdown(f"### Gavetas (20) — Status: {liberadas} Liberadas • {trancadas} Trancadas")
st.caption("Gerencie o acesso às gavetas do forno. Liberadas podem ser abertas. Trancadas permanecem fechadas.")

# GRID DE GAVETAS
cols = st.columns(5)
for i in range(1, 21):
    col = cols[(i-1) % 5]
    status = st.session_state.gavetas[i]
    with col:
        cor = "LIBERADA" if status else "TRANCADA"
        classe = "liberada" if status else "trancada"
        icone = "✅" if status else "🔒"
        st.markdown(f"""
        <div class="gaveta-card">
            <b>{i:02d} — {'Liberada' if status else 'Trancada'}</b><br>
            {icone} <span class="{classe}">{cor}</span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# BOTOES NA PARTE INFERIOR - COMO VOCE PEDIU
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("🔓 Liberar", use_container_width=True, type="primary"):
        st.session_state.gavetas[1] = True
        st.rerun()
with c2:
    if st.button("🔒 Trancar", use_container_width=True):
        st.session_state.gavetas[1] = False
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
    if st.button("➕ Criar Nova Gaveta Automatico", use_container_width=True, type="primary"):
        novo_id = max(st.session_state.gavetas.keys()) + 1
        st.session_state.gavetas[novo_id] = True
        st.rerun()
