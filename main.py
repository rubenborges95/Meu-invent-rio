@st.cache_resource
def obter_cliente_gsheets():
  import gspread
  from google.oauth2.service_account import Credentials

  escopos = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  try:
    # Obtém a pasta exata onde o main.py está a correr
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "credentials.json")

    creds = Credentials.from_service_account_file(caminho_json, scopes=escopos)
    cliente = gspread.authorize(creds)
    return cliente
  except Exception as e:
    st.error(f"Erro a carregar as credenciais: {e}")
    return None
