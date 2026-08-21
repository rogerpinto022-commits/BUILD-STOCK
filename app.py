import streamlit as st
import re

st.set_page_config(layout="wide", page_title="Reforma de Fornos")

st.markdown("""
<style>
.gaveta-principal {
    background: linear-gradient(90deg, #5B8DEF, #3A6ED8);
    border: 3px solid #1E40AF;
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    color: white;
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 25px;
}
.total-box {
    background: #16A34A;
    color: white;
    padding: 15px;
    border-radius: 10px;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    margin-top: 15px;
}
.login-box { background: white; border-radius: 15px; padding: 25px; color: black; max-width: 500px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# ESTADO
if 'usuarios_liberados' not in st.session_state: st.session_state.usuarios_liberados = ["admin@admin.com"]
if 'solicitacoes' not in st.session_state: st.session_state.solicitacoes = []
if 'logado' not in st.session_state: st.session_state.logado = False
if 'email_logado' not in st.session_state: st.session_state.email_logado = ""
if 'gavetas' not in st.session_state: st.session_state.gavetas = {i: True for i in range(1, 21)}
if 'selecionada' not in st.session_state: st.session_state.selecionada = None
if 'campos' not in st.session_state: st.session_state.campos = {}

# --- LOGIN NA GAVETA RETANGULAR ---
if not st.session_state.logado:
    st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS<br><span style="font-size:18px">Acesso Restrito</span></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
    with tab1:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if email in st.session_state.usuarios_liberados and senha == "123456":
                st.session_state.logado = True
                st.session_state.email_logado = email
                st.rerun()
            else:
                st.error("Email não liberado ou senha incorreta (padrão 123456)")
    with tab2:
        nome_cad = st.text_input("Nome")
        email_cad = st.text_input("Email para liberação")
        if st.button("Solicitar Liberação", use_container_width=True):
            if email_cad:
                st.session_state.solicitacoes.append({"nome": nome_cad, "email": email_cad})
                st.success("Solicitação enviada!")
else:
    st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS</div>', unsafe_allow_html=True)
    st.sidebar.success(f"Logado: {st.session_state.email_logado}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    if st.session_state.email_logado == "admin@admin.com":
        with st.expander("👑 PAINEL ADMIN - Liberar emails"):
            for i, sol in enumerate(st.session_state.solicitacoes):
                c1, c2, c3 = st.columns([2,2,1])
                c1.write(sol['nome']); c2.write(sol['email'])
                if c3.button("Liberar", key=f"lib_{i}"):
                    st.session_state.usuarios_liberados.append(sol['email'])
                    st.session_state.solicitacoes.pop(i)
                    st.rerun()

    # GRID GAVETAS - MANTIDA
    st.markdown(f"### Gavetas ({len(st.session_state.gavetas)})")
    cols = st.columns(5)
    for i in sorted(st.session_state.gavetas.keys()):
        with cols[(i-1) % 5]:
            if st.button(f"{'✅' if st.session_state.gavetas[i] else '🔒'} Gaveta {i:02d}", key=f"g_{i}", use_container_width=True):
                st.session_state.selecionada = i
                st.rerun()

    # DENTRO DA GAVETA COM CALCULO AUTOMATICO
    if st.session_state.selecionada is not None:
        sel = st.session_state.selecionada
        st.divider()
        st.subheader(f"📦 Gaveta {sel:02d} - Produtos e Cálculo Automático")
        if sel not in st.session_state.campos: st.session_state.campos[sel] = []

        # AREA DOS CAMPOS EDITAVEIS
        st.markdown("**Campos criados (edite os valores que o cálculo atualiza sozinho):**")
        for idx, campo in enumerate(st.session_state.campos[sel]):
            # Campo do tipo calculado não deixa editar valor
            is_calc = campo.get('tipo') == 'Calculado'
            c1, c2, c3, c4 = st.columns([2, 2, 3, 1])
            with c1:
                nn = st.text_input("N", value=campo['nome'], key=f"n_{sel}_{idx}", label_visibility="collapsed")
                st.session_state.campos[sel][idx]['nome'] = nn
            with c2:
                st.caption(f"{campo.get('tipo','Texto')}")
            with c3:
                if is_calc:
                    st.text_input("V", value=f"= {campo['formula']} = {campo['valor']}", key=f"v_{sel}_{idx}_calc", disabled=True, label_visibility="collapsed")
                else:
                    nv = st.text_input("V", value=campo['valor'], key=f"v_{sel}_{idx}", label_visibility="collapsed")
                    st.session_state.campos[sel][idx]['valor'] = nv
            with c4:
                if st.button("🗑️", key=f"d_{sel}_{idx}"):
                    st.session_state.campos[sel].pop(idx)
                    st.rerun()

        # CALCULO AUTOMATICO - LER OS DADOS E ATUALIZAR
        # Cria dicionário com valores numéricos
        dados_numericos = {}
        total_geral = 0
        for campo in st.session_state.campos[sel]:
            if campo.get('tipo')!= 'Calculado':
                try:
                    # Tenta converter valor para numero (aceita virgula)
                    v = campo['valor'].replace(',','.').strip()
                    num = float(v) if v else 0
                    dados_numericos[campo['nome'].lower()] = num
                except:
                    dados_numericos[campo['nome'].lower()] = 0

        # Atualiza campos calculados
        for campo in st.session_state.campos[sel]:
            if campo.get('tipo') == 'Calculado':
                try:
                    formula = campo['formula'].lower()
                    # Substitui nomes dos campos por valores
                    for nome, valor in dados_numericos.items():
                        formula = formula.replace(nome, str(valor))
                    # Avalia seguro
                    resultado = eval(formula, {"__builtins__": {}}, {})
                    campo['valor'] = str(round(resultado, 2))
                except Exception as e:
                    campo['valor'] = "Erro"

        # Exibe TOTAL automático se tiver Qtd e Valor
        # Detecta automaticamente quantidade * valor unitário
        if dados_numericos:
            # Soma de todos os campos que parecem total
            for campo in st.session_state.campos[sel]:
                if 'total' in campo['nome'].lower() and campo.get('tipo')!= 'Calculado':
                    try:
                        total_geral += float(campo['valor'].replace(',','.'))
                    except:
                        pass

            # Se tiver campo calculado, mostra
            for campo in st.session_state.campos[sel]:
                if campo.get('tipo') == 'Calculado':
                    st.markdown(f'<div class="total-box">🧮 {campo["nome"]}: {campo["formula"]} = R$ {campo["valor"]}</div>', unsafe_allow_html=True)

        st.divider()

        # CRIAR CAMPO COM TIPO
        st.markdown("#### ➕ Criar Campo com Cálculo Automático")
        with st.form(key=f"form_{sel}", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 3])
            with c1:
                nome_novo = st.text_input("Nome do campo", placeholder="Ex: Quantidade, Valor Unitario")
            with c2:
                tipo_novo = st.selectbox("Tipo", ["Número", "Texto", "Calculado"])
            with c3:
                if tipo_novo == "Calculado":
                    formula_nova = st.text_input("Fórmula", placeholder="Ex: quantidade * valor unitario")
                    valor_novo = ""
                else:
                    formula_nova = ""
                    valor_novo = st.text_input("Valor", placeholder="Ex: 10")

            if st.form_submit_button("➕ Criar Campo", type="primary", use_container_width=True):
                if nome_novo:
                    if tipo_novo == "Calculado" and not formula_nova:
                        st.error("Digite a fórmula para campo calculado")
                    else:
                        st.session_state.campos[sel].append({"nome": nome_novo, "tipo": tipo_novo, "valor": valor_novo, "formula": formula_nova})
                        st.rerun()

        # Tabela resumo
        if st.session_state.campos[sel]:
            st.dataframe([{"Campo": c['nome'], "Tipo": c.get('tipo','Texto'), "Valor": c['valor'], "Fórmula": c.get('formula','')} for c in st.session_state.campos[sel]], use_container_width=True)

    st.divider()
    if st.button("➕ Nova Gaveta", type="primary"):
        nid = max(st.session_state.gavetas.keys()) + 1
        st.session_state.gavetas[nid] = True
        st.session_state.selecionada = nid
        st.rerun()
