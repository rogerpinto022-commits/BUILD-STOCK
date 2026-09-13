import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="WMS 3 Áreas - Final", layout="wide", page_icon="🏭")

DATA_FILE = "wms_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("estoque", []), d.get("movs", []), d.get("combos", [])
        except:
            return [], [], []
    return [], [], []

def save_data(estoque, movs, combos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"estoque": estoque, "movs": movs, "combos": combos}, f, ensure_ascii=False, indent=2)

if "estoque" not in st.session_state:
    est, movs, combos = load_data()
    st.session_state.estoque = est
    st.session_state.movs = movs
    st.session_state.combos = combos
    st.session_state.combo_temp = []
    st.session_state.outros_temp = []

estoque = st.session_state.estoque
movs = st.session_state.movs
combos = st.session_state.combos

st.markdown("## 🏭 WMS DEFINITIVO - 3 ÁREAS | 7 CHARS + OUTROS + MENSAL")
st.caption("ENTRADA sempre GALPÃO → SAÍDA GALPÃO→SALA/OFICINA → DEVOLUÇÃO vice-versa → PRODUÇÃO 7 chars + OUTROS + Mensal")

col1, col2, col3, col4, col5 = st.columns(5)
galpao = sum(e["saldo"] for e in estoque if e["local"]=="GALPÃO DE MATERIAIS")
sala = sum(e["saldo"] for e in estoque if e["local"]=="SALA ANEXA")
oficina = sum(e["saldo"] for e in estoque if e["local"]=="OFICINA DE REVESTIMENTO")
total_geral = sum(e["saldo"] for e in estoque)
prod_por_mes = defaultdict(float)
for m in movs:
    if "PRODUÇÃO" in m.get("tipo",""):
        prod_por_mes[m.get("mes","")] += m.get("qtd",0)
mes_atual = datetime.now().strftime("%m/%Y")
prod_mes = prod_por_mes.get(mes_atual, 0)

col1.metric("GALPÃO", galpao)
col2.metric("SALA ANEXA", sala)
col3.metric("OFICINA", oficina)
col4.metric("TOTAL GERAL", total_geral)
col5.metric(f"PROD {mes_atual}", int(prod_mes))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📥 ENTRADA GALPÃO", "📤 SAÍDA GALPÃO→ÁREA", "↩️ DEVOLUÇÃO", "🧩 COMBOS 7 CHARS", "🏭 PRODUZIR 7c + OUTROS", "📊 ESTOQUE + MENSAL"])

with tab1:
    st.subheader("📥 ENTRADA - Sempre no GALPÃO (atualiza geral auto)")
    c1, c2 = st.columns(2)
    mat = c1.text_input("Material *", key="e_mat")
    qtd = c2.number_input("Qtd *", min_value=0.0, key="e_qtd")
    if st.button("DAR ENTRADA NO GALPÃO", type="primary"):
        if not mat or qtd<=0:
            st.error("Material e Qtd obrigatórios")
        else:
            ach = next((e for e in estoque if e["local"]=="GALPÃO DE MATERIAIS" and e["nome"].lower()==mat.lower()), None)
            if ach:
                ach["saldo"]+=qtd
            else:
                estoque.append({"local":"GALPÃO DE MATERIAIS","nome":mat.strip(),"saldo":qtd,"un":"UN","ts":datetime.now().isoformat()})
            movs.insert(0,{"tipo":"ENTRADA","local":"GALPÃO DE MATERIAIS","mat":mat,"qtd":qtd,"data":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),"mes":mes_atual})
            save_data(estoque,movs,combos)
            st.success(f"Entrada: {mat} {qtd}")
            st.rerun()

with tab2:
    st.subheader("📤 SAÍDA GALPÃO → SALA / OFICINA (auto)")
    c1,c2,c3 = st.columns(3)
    mat_s = c1.text_input("Material *", key="s_mat")
    qtd_s = c2.number_input("Qtd *", min_value=0.0, key="s_qtd")
    dest = c3.selectbox("Destino *", ["SALA ANEXA","OFICINA DE REVESTIMENTO"])
    if mat_s:
        total_g = sum(e["saldo"] for e in estoque if e["local"]=="GALPÃO DE MATERIAIS" and e["nome"].lower()==mat_s.lower())
        st.info(f"No GALPÃO tem {total_g}")
    if st.button("TRANSFERIR GALPÃO ➡️ ÁREA", type="primary"):
        total = sum(e["saldo"] for e in estoque if e["local"]=="GALPÃO DE MATERIAIS" and e["nome"].lower()==mat_s.lower())
        if total < qtd_s:
            st.error(f"Só tem {total}")
        else:
            precisa = qtd_s
            for e in [x for x in estoque if x["local"]=="GALPÃO DE MATERIAIS" and x["nome"].lower()==mat_s.lower()]:
                tirar = min(e["saldo"], precisa)
                e["saldo"]-=tirar
                precisa-=tirar
            st.session_state.estoque = [e for e in estoque if e["saldo"]>0]
            estoque = st.session_state.estoque
            d = next((e for e in estoque if e["local"]==dest and e["nome"].lower()==mat_s.lower()), None)
            if d:
                d["saldo"]+=qtd_s
            else:
                estoque.append({"local":dest,"nome":mat_s.strip(),"saldo":qtd_s,"un":"UN","ts":datetime.now().isoformat()})
            movs.insert(0,{"tipo":"SAIDA","local":f"GALPÃO ➡️ {dest}","mat":mat_s,"qtd":qtd_s,"data":datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
            save_data(estoque,movs,combos)
            st.success(f"Transferido GALPÃO ➡️ {dest}")
            st.rerun()

with tab3:
    st.subheader("↩️ DEVOLUÇÃO Vice-versa")
    c1,c2,c3,c4 = st.columns(4)
    orig = c1.selectbox("Origem", ["SALA ANEXA","OFICINA DE REVESTIMENTO","GALPÃO DE MATERIAIS"], key="d_orig")
    dest_d = c2.selectbox("Destino", ["GALPÃO DE MATERIAIS","SALA ANEXA","OFICINA DE REVESTIMENTO"], key="d_dest")
    mat_d = c3.text_input("Material", key="d_mat")
    qtd_d = c4.number_input("Qtd", min_value=0.0, key="d_qtd")
    if st.button("DEVOLVER E ATUALIZAR"):
        if orig==dest_d:
            st.error("Origem != destino")
        else:
            total = sum(e["saldo"] for e in estoque if e["local"]==orig and e["nome"].lower()==mat_d.lower())
            if total < qtd_d:
                st.error(f"Só tem {total} em {orig}")
            else:
                precisa=qtd_d
                for e in [x for x in estoque if x["local"]==orig and x["nome"].lower()==mat_d.lower()]:
                    tirar=min(e["saldo"],precisa)
                    e["saldo"]-=tirar
                    precisa-=tirar
                st.session_state.estoque=[e for e in estoque if e["saldo"]>0]
                estoque=st.session_state.estoque
                dd = next((e for e in estoque if e["local"]==dest_d and e["nome"].lower()==mat_d.lower()), None)
                if dd:
                    dd["saldo"]+=qtd_d
                else:
                    estoque.append({"local":dest_d,"nome":mat_d.strip(),"saldo":qtd_d,"un":"UN","ts":datetime.now().isoformat()})
                movs.insert(0,{"tipo":"DEVOLUÇÃO","local":f"{orig} ➡️ {dest_d}","mat":mat_d,"qtd":qtd_d,"data":datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
                save_data(estoque,movs,combos)
                st.success("Devolvido!")
                st.rerun()

with tab4:
    st.subheader("🧩 COMBOS 7 chars - Pode ser AAAAAAA, 1111111 - EDITÁVEL")
    c1,c2 = st.columns(2)
    code = c1.text_input("Código 7 chars *", max_chars=7, key="c_code")
    nome = c2.text_input("Nome produto *", key="c_nome")
    cc1,cc2,cc3 = st.columns([2,1,1])
    mat_c = cc1.text_input("Material", key="c_mat")
    qtd_c = cc2.number_input("Qtd p/1", min_value=0.0, key="c_qtd_m")
    if cc3.button(" + Add"):
        if mat_c and qtd_c>0:
            st.session_state.combo_temp.append({"mat":mat_c.strip(),"qtd":qtd_c})
    if st.session_state.combo_temp:
        st.write(st.session_state.combo_temp)
    if st.button("💾 SALVAR COMBO 7 CHARS", type="primary"):
        if len(code)!=7:
            st.error("Precisa 7 chars!")
        elif not nome or not st.session_state.combo_temp:
            st.error("Nome e receita")
        else:
            combos = [c for c in combos if c["code"]!=code]
            combos.append({"code":code,"nome":nome.strip(),"receita":list(st.session_state.combo_temp)})
            st.session_state.combos=combos
            st.session_state.combo_temp=[]
            save_data(estoque,movs,combos)
            st.success(f"Combo {code} salvo!")
            st.rerun()
    for c in combos:
        col_a,col_b,col_c = st.columns([3,1,1])
        col_a.write(f"**{c['code']}** - {c['nome']} | {', '.join([f'{r['mat']}({r['qtd']})' for r in c['receita']])}")
        if col_b.button("EDITAR", key=f"edit_{c['code']}"):
            st.session_state.combo_temp = list(c["receita"])
            st.session_state["c_code"] = c["code"]
            st.session_state["c_nome"] = c["nome"]
            st.rerun()
        if col_c.button("APAGAR", key=f"del_{c['code']}"):
            st.session_state.combos = [x for x in combos if x["code"]!=c["code"]]
            save_data(estoque,st.session_state.movs,st.session_state.combos)
            st.rerun()

with tab5:
    st.subheader("🏭 PRODUZIR - PADRÃO 7 chars OU OUTROS")
    modo = st.radio("Modo", ["📦 PADRÃO (7 chars)","🔧 OUTROS"], horizontal=True)
    if "PADRÃO" in modo:
        code_p = st.text_input("Digite 7 chars", max_chars=7, key="p_code")
        qtd_p = st.number_input("Qtd produzir", min_value=1.0, value=1.0, key="p_qtd")
        combo_sel = next((c for c in combos if c["code"]==code_p), None) if len(code_p)==7 else None
        if len(code_p)==7:
            if combo_sel:
                st.success(f"{combo_sel['code']} - {combo_sel['nome']}")
                for r in combo_sel["receita"]:
                    total_of = sum(e["saldo"] for e in estoque if e["local"]=="OFICINA DE REVESTIMENTO" and e["nome"].lower()==r["mat"].lower())
                    st.write(f"• {r['mat']}: precisa {r['qtd']*qtd_p} | tem {total_of} OFICINA")
                if st.button("⚡ PRODUZIR PADRÃO + MENSAL", type="primary"):
                    falta=[]
                    for r in combo_sel["receita"]:
                        tot = sum(e["saldo"] for e in estoque if e["nome"].lower()==r["mat"].lower())
                        if tot < r["qtd"]*qtd_p:
                            falta.append(r["mat"])
                    if falta:
                        st.error(f"Falta {','.join(falta)}")
                    else:
                        for r in combo_sel["receita"]:
                            precisa=r["qtd"]*qtd_p
                            for e in [x for x in estoque if x["nome"].lower()==r["mat"].lower()]:
                                if precisa<=0: break
                                tirar=min(e["saldo"],precisa)
                                e["saldo"]-=tirar
                                precisa-=tirar
                        st.session_state.estoque=[e for e in estoque if e["saldo"]>0]
                        movs.insert(0,{"tipo":"PRODUÇÃO","local":f"OFICINA ➡️ {combo_sel['code']}","mat":combo_sel["nome"],"qtd":qtd_p,"code":combo_sel["code"],"data":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),"mes":mes_atual})
                        save_data(st.session_state.estoque,movs,combos)
                        st.success(f"Produzido! Mês {mes_atual}")
                        st.rerun()
            else:
                st.error(f"Código {code_p} não existe. Use OUTROS")
    else:
        nome_o = st.text_input("Nome OUTROS *", key="o_nome")
        oc1,oc2,oc3 = st.columns([2,1,1])
        mat_o = oc1.text_input("Material", key="o_mat")
        qtd_o = oc2.number_input("Qtd p/1", min_value=0.0, key="o_qtd_o")
        if oc3.button(" + Add OUTROS"):
            if mat_o and qtd_o>0:
                st.session_state.outros_temp.append({"mat":mat_o.strip(),"qtd":qtd_o})
        if st.session_state.outros_temp:
            st.write(st.session_state.outros_temp)
        qtd_prod_o = st.number_input("Qtd OUTROS", min_value=1.0, value=1.0, key="o_qtd_prod")
        if st.button("⚡ PRODUZIR OUTROS + MENSAL", type="primary"):
            if not nome_o or not st.session_state.outros_temp:
                st.error("Nome e receita")
            else:
                for r in st.session_state.outros_temp:
                    precisa=r["qtd"]*qtd_prod_o
                    for e in [x for x in estoque if x["nome"].lower()==r["mat"].lower()]:
                        if precisa<=0: break
                        tirar=min(e["saldo"],precisa)
                        e["saldo"]-=tirar
                        precisa-=tirar
                st.session_state.estoque=[e for e in estoque if e["saldo"]>0]
                movs.insert(0,{"tipo":"PRODUÇÃO OUTROS","local":"OFICINA OUTROS","mat":nome_o,"qtd":qtd_prod_o,"code":"OUTROS","data":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),"mes":mes_atual})
                st.session_state.outros_temp=[]
                save_data(st.session_state.estoque,movs,combos)
                st.success("Produzido OUTROS!")
                st.rerun()

with tab6:
    st.subheader("📊 Estoque + Mensal")
    if prod_por_mes:
        df_mensal = pd.DataFrame([{"Mês":k,"Qtd":v} for k,v in sorted(prod_por_mes.items())])
        st.bar_chart(df_mensal, x="Mês", y="Qtd")
        st.dataframe(df_mensal, use_container_width=True)
    if estoque:
        df = pd.DataFrame(estoque)
        st.dataframe(df.groupby(["local","nome"])["saldo"].sum().reset_index(), use_container_width=True)
        st.bar_chart(df.groupby("local")["saldo"].sum().reset_index(), x="local", y="saldo")
    if movs:
        st.dataframe(pd.DataFrame(movs).head(50), use_container_width=True)
