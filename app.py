import streamlit as st

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
.login-box {
    background: white;
    border-radius: 15px;
    padding: 25px;
    color: black;
    text-align: left;
    max-width: 500px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS SIMPLES ---
if 'usuarios_liberados' not in st.session_state:
    st.session_state.usuarios_liberados = ["admin@admin.com"] # Admin inicial
if 'solicitacoes' not in st.session_state:
    st.session_state.solicitacoes = []
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'email_logado' not in st.session_state:
    st.session_state.email_logado = ""
if 'gavetas' not in st.session_state:
    st.session_state.gavetas = {i: (i % 2 == 1) for i in range(1, 21)}
if 'selecionada' not in st.session_state:
    st.session_state.selecionada = None
if 'campos' not in st.session_state:
    st.session_state.campos = {}

# --- TELA DE LOGIN DENTRO DA GAVETA RETANGULAR ---
if not st.session_state.logado:
    st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS<br><span style="font-size:18px">Acesso Restrito</span></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login Administrador", "📝 Cadastro para Liberação"])

    with tab1:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("Login")
        email = st.text_input("Email cadastrado", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        # Senha admin padrão: 123456
        if st.button("Entrar", type="primary", use_container_width=True):
            if email in st.session_state.usuarios_liberados and senha == "123456":
                st.session_state.logado = True
                st.session_state.email_logado = email
                st.success("Login liberado!")
                st.rerun()
            else:
                st.error("Email não liberado ou senha incorreta. Senha padrão admin é 123456")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("Solicitar Acesso")
        st.caption("Seu email será enviado para o administrador liberar")
        nome_cad = st.text_input("Seu nome")
        email_cad = st.text_input("Seu email para liberação")

        if st.button("Solicitar Liberação", use_container_width=True):
            if email_cad:
                if email_cad not in st.session_state.usuarios_liberados:
                    st.session_state.solicitacoes.append({"nome": nome_cad, "email": email_cad})
                    st.success(f"Solicitação enviada! Aguarde liberação do email {email_cad}")
                    st.info("Administrador precisa liberar seu email na área admin")
                else:
                    st.warning("Este email já está liberado, faça login")
            else:
                st.error("Digite um email válido")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- USUARIO LOGADO - MOSTRA INTERFACE GRAFICA QUE VOCE JA APROVOU ---
    st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS</div>', unsafe_allow_html=True)
    st.sidebar.success(f"Logado: {st.session_state.email_logado}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # AREA DO ADMIN PARA LIBERAR EMAILS
    if st.session_state.email_logado == "admin@admin.com":
        with st.expander("👑 PAINEL ADMIN - Liberar acessos por email"):
            st.write("Emails liberados:", st.session_state.usuarios_liberados)
            if st.session_state.solicitacoes:
                st.write("Solicitações pendentes:")
                for i, sol in enumerate(st.session_state.solicitacoes):
                    c1, c2, c3 = st.columns([2,2,1])
                    c1.write(sol['nome'])
                    c2.write(sol['email'])
                    if c3.button("Liberar", key=f"lib_{i}"):
                        st.session_state.usuarios_liberados.append(sol['email'])
                        st.session_state.solicitacoes.pop(i)
                        st.rerun()
            else:
                st.info("Nenhuma solicitação pendente")

            st.divider()
            novo_email = st.text_input("Liberar email manualmente")
            if st.button("Liberar Email"):
                if novo_email:
                    st.session_state.usuarios_liberados.append(novo_email)
                    st.success(f"{novo_email} liberado!")
                    st.rerun()

    # SUA INTERFACE GRAFICA EXCELENTE MANTIDA
    total = len(st.session_state.gavetas)
    st.markdown(f"### Gavetas ({total})")
    cols = st.columns(5)
    for i in sorted(st.session_state.gavetas.keys()):
        col = cols[(i-1) % 5]
        liberada = st.session_state.gavetas[i]
        with col:
            if st.button(f"{'✅' if liberada else '🔒'} Gaveta {i:02d}", key=f"g_{i}", use_container_width=True):
                st.session_state.selecionada = i
                st.rerun()

    if st.session_state.selecionada is not None:
        sel = st.session_state.selecionada
        st.divider()
        st.subheader(f"📦 Gaveta {sel:02d}")

        if sel not in st.session_state.campos:
            st.session_state.campos[sel] = []

        for idx, campo in enumerate(st.session_state.campos[sel]):
            c1, c2, c3 = st.columns([3, 5, 1])
            with c1:
                novo_nome = st.text_input("Nome", value=campo['nome'], key=f"nome_{sel}_{idx}", label_visibility="collapsed")
                st.session_state.campos[sel][idx]['nome'] = novo_nome
            with c2:
                novo_valor = st.text_input("Valor", value=campo['valor'], key=f"valor_{sel}_{idx}", label_visibility="collapsed")
                st.session_state.campos[sel][idx]['valor'] = novo_valor
            with c3:
                if st.button("🗑️", key=f"del_{sel}_{idx}"):
                    st.session_state.campos[sel].pop(idx)
                    st.rerun()

        with st.form(key=f"form_{sel}", clear_on_submit=True):
            cn, cv = st.columns(2)
            nome_novo = cn.text_input("Nome do campo", placeholder="Ex: Produto")
            valor_novo = cv.text_input("Valor", placeholder="Ex: Tijolo")
            if st.form_submit_button("➕ Criar Campo", type="primary", use_container_width=True):
                if nome_novo:
                    st.session_state.campos[sel].append({"nome": nome_novo, "valor": valor_novo})
                    st.rerun()
