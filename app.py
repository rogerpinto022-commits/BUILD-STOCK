import plotly.express as px

# --- 1. CONVERTE DATA ---
df['data'] = pd.to_datetime(df['data'])
df['mes'] = df['data'].dt.to_period('M').astype(str)
df['semestre'] = df['data'].dt.year.astype(str) + "-S" + ((df['data'].dt.month-1)//6 + 1).astype(str)
df['ano'] = df['data'].dt.year

# --- 2. GRÁFICOS DE ESTOQUE ATUAL ---
st.subheader("📦 Estoque Atual por Local")
col1, col2, col3 = st.columns(3)
with col1:
    fig_barracao = px.bar(df[df['local']=='Barracão'].groupby('produto')['quantidade'].sum().reset_index(), x='produto', y='quantidade', title="Barracão")
    st.plotly_chart(fig_barracao)
with col2:
    fig_sala = px.bar(df[df['local']=='Sala Anexa'].groupby('produto')['quantidade'].sum().reset_index(), x='produto', y='quantidade', title="Sala Anexa")
    st.plotly_chart(fig_sala)
with col3:
    df_total = df.groupby('produto')['quantidade'].sum().reset_index()
    fig_total = px.pie(df_total, values='quantidade', names='produto', title="TOTAL GERAL")
    st.plotly_chart(fig_total)

# --- 3. GRÁFICOS DE MOVIMENTAÇÃO ---
st.subheader("📈 Entradas x Saídas")

# MENSAL
mensal = df.groupby(['mes', 'tipo_mov'])['quantidade'].sum().reset_index()
fig_mensal = px.line(mensal, x='mes', y='quantidade', color='tipo_mov', markers=True, title="MENSAL - Entradas x Saídas")
st.plotly_chart(fig_mensal, use_container_width=True)

# SEMESTRAL
semestral = df.groupby(['semestre', 'tipo_mov'])['quantidade'].sum().reset_index()
fig_sem = px.bar(semestral, x='semestre', y='quantidade', color='tipo_mov', barmode='group', title="SEMESTRAL - Entradas x Saídas")
st.plotly_chart(fig_sem, use_container_width=True)

# ANUAL
anual = df.groupby(['ano', 'tipo_mov'])['quantidade'].sum().reset_index()
fig_anual = px.bar(anual, x='ano', y='quantidade', color='tipo_mov', barmode='group', title="ANUAL - Entradas x Saídas")
st.plotly_chart(fig_anual, use_container_width=True)
