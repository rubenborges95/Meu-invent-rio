import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="AMBULANCE LOG", page_icon="🚑", layout="centered")

# Estilo CSS
st.markdown(
    """
    <style>
    .main { background-color: #11141a; }
    h1 { color: #f1c40f !important; font-family: 'Arial', sans-serif; text-align: center; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 45px; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- Cabeçalho ---
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
  try:
    st.image("WhatsApp Image 2026-10-11 at 14.58.23.jpeg", width=90)
  except:
    pass

with col_titulo:
  st.markdown(
      "<h3 style='margin-top: 15px; color: #f1c40f; font-family: Arial,"
      " sans-serif;'>A.H. Bombeiros Voluntários Carrazedo de Montenegro</h3>",
      unsafe_allow_html=True,
  )

st.caption("Gestão de Stock Material Pré-Hospitalar")

# Função segura sem bloqueios de arranque
def obter_cliente_gsheets():
  import gspread
  try:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "credentials.json")
    if not os.path.exists(caminho_json):
      return None
    return gspread.service_account(filename=caminho_json)
  except Exception as e:
    return None

def carregar_dados_seguro():
  try:
    cliente = obter_cliente_gsheets()
    if not cliente:
      return pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"])
    url = "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
    sh = cliente.open_by_url(url)
    ws = sh.worksheet("materiais")
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    if df.empty or "id" not in df.columns:
      return pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"])
    df["id"] = df["id"].astype(int)
    df["quantidade"] = df["quantidade"].astype(int)
    df["limite_minimo"] = df["limite_minimo"].astype(int)
    return df
  except Exception:
    return pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"])

aba_inventario, aba_registo, aba_historico = st.tabs(
    ["📦 Inventário Ativo", "➕ Registar Novo", "📋 Ocorrências"]
)

# Carregamento protegido
df_materiais = carregar_dados_seguro()

# --- ABA 1: INVENTÁRIO ATIVO ---
with aba_inventario:
  if df_materiais.empty:
    st.warning("⚠️ A aplicação abriu com sucesso, mas não foi possível carregar os dados do Google Sheets (ou a folha está vazia/sem as abas corretas).")
    if st.button("🔄 Tentar Ligar Novamente"):
      st.rerun()
  else:
    pesquisa = st.text_input("🔍 Pesquisa rápida de material...", placeholder="Ex: Guedel, Sorocel...")
    for _, row in df_materiais.iterrows():
      id_m = int(row["id"])
      nome = str(row["nome"])
      qtd = int(row["quantidade"])
      limite = int(row["limite_minimo"])
      cat = str(row["categoria"])

      if pesquisa and (pesquisa.lower() not in nome.lower() and pesquisa.lower() not in cat.lower()):
        continue

      with st.container(border=True):
        st.markdown(f"**{nome}** ({qtd} unid.) | Categoria: {cat}")

# --- ABA 2: REGISTAR ---
with aba_registo:
  st.subheader("Entrada de Material")
  st.info("Funcionalidade ativa após validação da folha.")

# --- ABA 3: HISTÓRICO ---
with aba_historico:
  st.subheader("Ocorrências")
  st.info("Registo histórico disponível.")
