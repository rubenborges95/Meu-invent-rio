import streamlit as st

st.set_page_config(page_title="TESTE", page_icon="🚑", layout="centered")

st.title("A.H. Bombeiros Voluntários Carrazedo de Montenegro")
st.success("Se estás a ver esta mensagem, o Streamlit arrancou com sucesso!")

# Teste simples do ficheiro de credenciais
import os

if os.path.exists("credentials.json"):
  st.info("O ficheiro credentials.json foi detetado na pasta!")
else:
  st.error("O ficheiro credentials.json NÃO foi encontrado na pasta do GitHub!")
