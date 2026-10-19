from datetime import datetime
import pandas as pd
import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="AMBULANCE LOG", page_icon="🚑", layout="centered")

st.write("A iniciar a aplicação...")

try:
  conn = st.connection("gsheets", type=GSheetsConnection)
  st.write("Ligação ao Google Sheets estabelecida com sucesso!")
except Exception as e:
  st.error(f"Erro na ligação: {e}")

try:
  df_mat = conn.read(worksheet="materiais", ttl=0)
  st.write("Dados de materiais lidos com sucesso:", df_mat)
except Exception as e:
  st.warning(
      "Aviso: Não foi possível ler a aba 'materiais'. Verifica se ela existe"
      f" na folha. Erro: {e}"
  )

st.write("Se estás a ver esta mensagem, o código correu todo!")
