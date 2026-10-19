@st.cache_resource
def obter_cliente_gsheets():
  import gspread
  from google.oauth2.service_account import Credentials
  import google.auth.transport.requests
  import requests

  escopos = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  try:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "credentials.json")

    creds = Credentials.from_service_account_file(caminho_json, scopes=escopos)
    
    # Força a atualização do token ignorando pequenas desfasagens temporais
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    cliente = gspread.authorize(creds)
    return cliente
  except Exception as e:
    st.error(f"Erro na autenticação Google: {e}")
    return None
