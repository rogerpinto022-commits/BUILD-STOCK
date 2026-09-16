import streamlit as st
import pandas as pd
import datetime
import pytz
from supabase import create_client

# CONFIG SUPABASE
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "SUA_URL_AQUI")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "SUA_KEY_AQUI")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BR_TZ = pytz.timezone('America/Sao_Paulo')
def now_brt(): return datetime.datetime.now(BR_TZ)
def fmt_brt(dt):
    if not dt: return "-"
    return pd.to_datetime(dt).tz_convert(BR_TZ).strftime("%d/%m/%Y %H:%M:%S BRT") if hasattr(dt,'tzinfo') else str(dt)

def validar_par(s):
    return len(s)==4 and s.isdigit() and all(c in '02468' for c in s)

# LOGIN ALMIR
if 'logado' not in st.session_state: st.session_state.logado=False
if not st.session_state.logado:
    st.title("🔐 ALMIR - ACESSO 4 PARES - BRT")
    st.text_input("NOME", value="ALMIR", disabled=True)
    senha = st.text_input("SENHA 4 PARES (0,2,4,6,8)", type="password", max_chars=4)
    if st.button("ENTRAR"):
        if validar_par(senha):
            st.session_state.logado=True
            supabase.table("historico_uso").insert({
                "usuario":"ALMIR","acao":"LOGIN","detalhe":f"Login ALMIR BRT {now_brt()}",
                "data": now_brt().isoformat()
            }).execute()
            st.rerun()
        else:
            st.error("Senha inválida. Use 4 pares. Ex: 2468")
    st.stop()

menu = st.sidebar.radio("MENU", ["ESTOQUE GERAL","GALPÃO","SALA ANEXA","OFICINA DE REVESTIMENTO DE CUBAS","GRÁFICOS POR ID","HISTÓRICO"])

def get_bases():
    res = supabase.table("produtos_base").select("*").execute()
    return res.data

def movimentar(tipo, local_origem, id_prod, qtd_pal, marca, lote, dest_local=None, tipo_dest="Geral"):
    bases = {b['id']:b for b in get_bases()}
    base = bases.get(id_prod)
    if not base:
        st.error("ID não cadastrado"); return

    # SAIDA COM FIFO LOTE MAIS ANTIGO
    if tipo=="SAIDA":
        estoque = supabase.table("estoque").select("*").eq("id_produto", id_prod).eq("local", local_origem).order("data_fab").execute().data
        restante = qtd_pal
        for item in estoque:
            if restante<=0: break
            if item['qtd_paletes'] >= restante:
                supabase.table("estoque").update({"qtd_paletes": item['qtd_paletes']-restante}).eq("id", item['id']).execute()
                restante=0
            else:
                restante-=item['qtd_paletes']
                supabase.table("estoque").delete().eq("id", item['id']).execute()

        # ESPELHO
        if local_origem=="GALPÃO" and dest_local in ["SALA ANEXA","OFICINA DE REVESTIMENTO DE CUBAS"]:
            supabase.table("estoque").insert({
                "local":dest_local,"tipo_local":"Geral","id_produto":id_prod,"nome":base['nome'],
                "marca":marca,"lote":lote,"data_fab":now_brt().isoformat(),"qtd_paletes":qtd_pal,
                "entrada_em":now_brt().isoformat()
            }).execute()
            acao="TRANSFERÊNCIA AUTOMÁTICA"
            detalhe=f"SAÍDA Galpão -> ENTRADA {dest_local} | ID {id_prod} | {qtd_pal} pal | {fmt_brt(now_brt())}"
        elif local_origem=="SALA ANEXA" and dest_local=="OFICINA DE REVESTIMENTO DE CUBAS":
            supabase.table("estoque").insert({
                "local":dest_local,"tipo_local":"Geral","id_produto":id_prod,"nome":base['nome'],
                "marca":marca,"lote":lote,"data_fab":now_brt().isoformat(),"qtd_paletes":qtd_pal,
                "entrada_em":now_brt().isoformat()
            }).execute()
            acao="TRANSFERÊNCIA AUTOMÁTICA"
            detalhe=f"SAÍDA Sala -> ENTRADA Oficina | ID {id_prod} | {qtd_pal} pal"
        else:
            acao="SAÍDA"
            detalhe=f"SAÍDA {local_origem} | ID {id_prod} | {qtd_pal} pal | {'BAIXA DEFINITIVA' if local_origem=='OFICINA DE REVESTIMENTO DE CUBAS' else ''} | {fmt_brt(now_brt())}"
    else: # ENTRADA
        supabase.table("estoque").insert({
            "local":local_origem,"tipo_local":tipo_dest,"id_produto":id_prod,"nome":base['nome'],
            "marca":marca,"lote":lote,"data_fab":now_brt().isoformat(),"qtd_paletes":qtd_pal,
            "entrada_em":now_brt().isoformat()
        }).execute()
        if local_origem in ["SALA ANEXA","OFICINA DE REVESTIMENTO DE CUBAS"]:
            # baixa auto no galpão
            estoque_g = supabase.table("estoque").select("*").eq("id_produto", id_prod).eq("local","GALPÃO").order("data_fab").execute().data
            rest = qtd_pal
            for it in estoque_g:
                if rest<=0: break
                if it['qtd_paletes']>=rest:
                    supabase.table("estoque").update({"qtd_paletes": it['qtd_paletes']-rest}).eq("id", it['id']).execute()
                    rest=0
                else:
                    rest-=it['qtd_paletes']
                    supabase.table("estoque").delete().eq("id", it['id']).execute()
            acao="TRANSFERÊNCIA AUTOMÁTICA"
            detalhe=f"ENTRADA {local_origem} -> SAÍDA Galpão auto | ID {id_prod} | {qtd_pal} pal | BRT {fmt_brt(now_brt())}"
        else:
            acao="ENTRADA"
            detalhe=f"ENTRADA {local_origem} | ID {id_prod} | {qtd_pal} pal | {marca} | {lote} | BRT {fmt_brt(now_brt())}"

    supabase.table("historico_uso").insert({
        "usuario":"ALMIR","acao":acao,"id_produto":id_prod,"qtd":qtd_pal,"detalhe":detalhe,"data":now_brt().isoformat()
    }).execute()
    st.success(f"{acao} OK - {detalhe}")

# TELAS
if menu=="ESTOQUE GERAL":
    st.header("ESTOQUE GERAL = Galpão+Sala+Oficina BRT")
    res = supabase.table("estoque").select("*").execute()
    df = pd.DataFrame(res.data)
    st.metric("Total Paletes", df['qtd_paletes'].sum() if not df.empty else 0)
    if not df.empty: st.dataframe(df)

elif menu in ["GALPÃO","SALA ANEXA","OFICINA DE REVESTIMENTO DE CUBAS"]:
    local=menu
    st.header(f"{local} - {fmt_brt(now_brt())}")
    bases = get_bases()
    if local=="GALPÃO":
        with st.expander("CADASTRO BASE - Só Galpão"):
            with st.form("cad"):
                id_c=st.text_input("ID 01-17","01")
                nome_c=st.text_input("Nome","CIMENTO TOK-70")
                marcas_c=st.text_input("Marcas vírgula","TOK, Refrasil")
                qtd_p=st.number_input("QTD/palete",1,1000,40)
                uni=st.selectbox("Unidade",["sacos","tijolos","kg","m²","bags"])
                if st.form_submit_button("Cadastrar"):
                    supabase.table("produtos_base").upsert({
                        "id":id_c,"nome":nome_c,"marcas":[m.strip() for m in marcas_c.split(",")],
                        "qtd_por_palete":qtd_p,"unidade":uni
                    }).execute()
                    supabase.table("historico_uso").insert({"usuario":"ALMIR","acao":"CADASTRO","id_produto":id_c,"detalhe":f"Cadastro ID {id_c}","data":now_brt().isoformat()}).execute()
                    st.success("Cadastrado! Agora habilite nos outros locais.")

    # Lista IDs
    ids_disp=[b['id'] for b in bases]
    tipo_mov=st.selectbox("TIPO", ["ENTRADA","SAÍDA"])
    id_sel=st.selectbox("ID", ids_disp) if ids_disp else None
    qtd_pal=st.number_input("QTD PALETES",1,1000,1)
    with st.expander("OUTROS"):
        base_sel=next((b for b in bases if b['id']==id_sel),None)
        marcas_opt=base_sel['marcas'] if base_sel else ["-"]
        marca_sel=st.selectbox("Marca", marcas_opt)
        lote_sel=st.text_input("Lote", f"LOTE-{now_brt().strftime('%d%m%Y')}")
        if local=="GALPÃO" and tipo_mov=="SAÍDA":
            dest=st.selectbox("Destino", ["SALA ANEXA","OFICINA DE REVESTIMENTO DE CUBAS"])
        elif local=="SALA ANEXA" and tipo_mov=="SAÍDA":
            dest=st.selectbox("Destino", ["OFICINA DE REVESTIMENTO DE CUBAS","FINAL"])
        else:
            dest=st.selectbox("Tipo", ["Geral","Segregado"])

    if st.button("CONFIRMAR FIFO lote mais antigo"):
        if id_sel:
            # pega lote mais antigo auto para saída
            est = supabase.table("estoque").select("*").eq("id_produto",id_sel).eq("local",local).order("data_fab").execute().data
            lote_auto = est[0]['lote'] if est and tipo_mov=="SAÍDA" else lote_sel
            movimentar(tipo_mov, local, id_sel, qtd_pal, marca_sel, lote_auto, dest_local=dest if 'SALA' in dest or 'OFICINA' in dest else None, tipo_dest=dest)

elif menu=="GRÁFICOS POR ID":
    st.header("GRÁFICOS 4 Modelos Coloridos")
    bases=get_bases()
    ids_all=[b['id'] for b in bases]
    if ids_all:
        id_g=st.selectbox("ID", ids_all)
        res=supabase.table("estoque").select("*").eq("id_produto",id_g).execute()
        df=pd.DataFrame(res.data)
        st.metric("Paletes", df['qtd_paletes'].sum() if not df.empty else 0)
        hist=supabase.table("historico_uso").select("*").eq("id_produto",id_g).order("data", desc=True).limit(1).execute()
        if hist.data: st.info(f"Última: {hist.data[0]['detalhe']} por {hist.data[0]['usuario']}")
        modelo=st.selectbox("Modelo", ["1-Barra Horizontal","2-Pizza","3-Coluna Vertical","4-Cards"])
        if not df.empty:
            import matplotlib.pyplot as plt
            por=df.groupby('local')['qtd_paletes'].sum()
            fig, ax = plt.subplots()
            if "1" in modelo: ax.barh(por.index, por.values, color=['green','blue','orange'])
            elif "2" in modelo: ax.pie(por.values, labels=por.index, autopct='%1.1f%%')
            else: ax.bar(por.index, por.values, color=['#2ecc71','#3498db','#e67e22'])
            st.pyplot(fig)

elif menu=="HISTÓRICO":
    st.header("HISTÓRICO ALMIR - BRT")
    res=supabase.table("historico_uso").select("*").order("data", desc=True).execute()
    df=pd.DataFrame(res.data)
    if not df.empty:
        df['data_brt']=pd.to_datetime(df['data']).dt.tz_convert(BR_TZ).dt.strftime("%d/%m/%Y %H:%M:%S BRT")
        st.dataframe(df[['data_brt','usuario','acao','detalhe']])
        txt="\n".join([f"{r['data_brt']} - {r['usuario']} - {r['acao']} - {r['detalhe']}" for _,r in df.iterrows()])
        st.text_area("Export WhatsApp BRT", txt, height=300)
