import gspread
import streamlit as st

# Converte os segredos num dicionário e corrige as quebras de linha da chave privada
creds_dict = dict(st.secrets["gsheets"])
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

# Estabelece a ligação com o gspread de forma segura
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
)
worksheet = sh.sheet1  # ou sh.worksheet("materias") se a folha se chamar assim
