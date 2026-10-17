import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Configuração da página para telemóvel e tema escuro
st.set_page_config(page_title="AMBULANCE LOG", page_icon="🚑", layout="centered")

# Estilização do Tema Pré-Hospitalar (CSS)
st.markdown("""
    <style>
    .main { background-color: #11141a; }
    h1 { color: #f1c40f !important; font-family: 'Arial', sans-serif; text-align: center; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 45px; }
    </style>
""", unsafe_allow_html=True)

def ligar_bd():
    # Cria a base de dados local no servidor cloud de forma automática
    return sqlite3.connect("inventario_central.db")

def inicializar_bd():
    conn = ligar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            categoria TEXT,
            limite_minimo INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            material TEXT,
            tipo_acao TEXT,
            quantidade_alterada INTEGER,
            quantidade_final INTEGER
        )
    """)
    conn.commit()
    conn.close()

inicializar_bd()

st.title("🚨 GESTÃO DE STOCK PRÉ-HOSPITALAR")
st.caption("Central de Controlo de Material Médico - Ambulância")

aba_inventario, aba_registo, aba_historico = st.tabs(["📦 Inventário Ativo", "➕ Registar Novo", "📋 Ocorrências"])

# --- ABA 1: INVENTÁRIO ATIVO ---
with aba_inventario:
    pesquisa = st.text_input("🔍 Pesquisa rápida de material...", placeholder="Ex: Guedel, Sorocel...")
    
    conn = ligar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, quantidade, limite_minimo, categoria FROM materiais")
    todos_materiais = cursor.fetchall()
    conn.close()
    
    if not todos_materiais:
        st.info("Nenhum material registado no sistema.")
    else:
        for mat in todos_materiais:
            id_m, nome, qtd, limite, cat = mat
            
            if pesquisa and (pesquisa.lower() not in nome.lower() and pesquisa.lower() not in cat.lower()):
                continue
            
            if qtd == 0:
                alerta_status = f"🔴 **RUTURA TOTAL** ({qtd} unid.)"
            elif qtd <= limite:
                alerta_status = f"🟠 **STOCK CRÍTICO** ({qtd} unid. / Mín: {limite})"
            else:
                alerta_status = f"🟢 Disponível ({qtd} unid.)"
                
            with st.container(border=True):
                col_info, col_menos, col_mais = st.columns([2, 1, 1])
                
                with col_info:
                    st.markdown(f"**{nome}**")
                    st.caption(f"Local: {cat} | Status: {alerta_status}")
                
                with col_menos:
                    if st.button("📉 -1", key=f"menos_{id_m}"):
                        if qtd > 0:
                            nova_qtd = qtd - 1
                            conn = ligar_bd()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE materiais SET quantidade = ? WHERE id = ?", (nova_qtd, id_m))
                            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute("INSERT INTO historico (data_hora, material, tipo_acao, quantidade_alterada, quantidade_final) VALUES (?, ?, ?, ?, ?)",
                                           (agora, nome, "Uso Material (-1)", 1, nova_qtd))
                            conn.commit()
                            conn.close()
                            st.rerun()
                        else:
                            st.error("Erro: Stock a zeros.")
                            
                with col_mais:
                    if st.button("📈 +1", key=f"mais_{id_m}"):
                        nova_qtd = qtd + 1
                        conn = ligar_bd()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE materiais SET quantidade = ? WHERE id = ?", (nova_qtd, id_m))
                        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("INSERT INTO historico (data_hora, material, tipo_acao, quantidade_alterada, quantidade_final) VALUES (?, ?, ?, ?, ?)",
                                       (agora, nome, "Reposição (+1)", 1, nova_qtd))
                        conn.commit()
                        conn.close()
                        st.rerun()

# --- ABA 2: REGISTAR NOVO MATERIAL ---
with aba_registo:
    st.subheader("💊 Entrada de Novo Consumível")
    with st.form("form_cadastro", clear_on_submit=True):
        nome_novo = st.text_input("Designação do Material / Fármaco:")
        qtd_nova = st.number_input("Quantidade Inicial em Stock:", min_value=0, step=1, value=5)
        limite_novo = st.number_input("Alerta de Stock Mínimo Individual:", min_value=0, step=1, value=2)
        cat_nova = st.text_input("Localização na Viatura (Ex: Saco Trauma):")
        
        btn_submeter = st.form_submit_button("➕ Gravar no Inventário")
        
        if btn_submeter:
            if nome_novo:
                cat_final = cat_nova if cat_nova else "Não Especificado"
                conn = ligar_bd()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO materiais (nome, quantidade, categoria, limite_minimo) VALUES (?, ?, ?, ?)",
                               (nome_novo, qtd_nova, cat_final, limite_novo))
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO historico (data_hora, material, tipo_acao, quantidade_alterada, quantidade_final) VALUES (?, ?, ?, ?, ?)",
                               (agora, nome_novo, "Registo Inicial", qtd_nova, qtd_nova))
                conn.commit()
                conn.close()
                st.success(f"'{nome_novo}' adicionado!")
                st.rerun()
            else:
                st.warning("Preenche o nome do material.")

# --- ABA 3: HISTÓRICO ---
with aba_historico:
    st.subheader(" Relatório de Movimentações")
    conn = ligar_bd()
    try:
        df_hist = pd.read_sql_query("SELECT data_hora as 'Data/Hora', material as 'Material', tipo_acao as 'Ação', quantidade_alterada as 'Qtd Mod.', quantidade_final as 'Stock Final' FROM historico ORDER BY id DESC LIMIT 50", conn)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    except:
        st.info("Sem histórico registado.")
    conn.close()
