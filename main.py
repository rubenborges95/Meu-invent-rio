from datetime import datetime
import gspread
import pandas as pd
import streamlit as st

# Configuração da página para telemóvel e tema escuro
st.set_page_config(page_title="AMBULANCE LOG", page_icon="🚑", layout="centered")

# Estilização do Tema Pré-Hospitalar (CSS)
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


# Função para estabelecer ligação ao Google Sheets via gspread e st.secrets
def obter_conexao_gsheets():
  # Lê o link dos secrets do Streamlit
  url = st.secrets["connections"]["gsheets"]["spreadsheet"]
  gc = gspread.service_account_from_dict(
      dict(st.secrets["connections"]["gsheets"])
  )
  # Se usares credenciais por JSON nos segredos, o gspread liga-se diretamente:
  # Em alternativa, se a folha for aberta por link público com gspread:
  # Para simplificar com o link do spreadsheet:
  return gc.open_by_url(url)
