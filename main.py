@st.cache_resource
def obter_cliente_gsheets():
  import json
  from google.oauth2.service_account import Credentials
  import gspread

  escopos = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]

  try:
    if "gsheets" in st.secrets:
      creds_dict = dict(st.secrets["gsheets"])
      if "private_key" in creds_dict:
        pk = creds_dict["private_key"]
        # Corrige automaticamente se vier com \n em texto ou com quebras reais
        if "\\n" in pk:
          creds_dict["private_key"] = pk.replace("\\n", "\n")
      creds = Credentials.from_service_account_info(cred_dict, scopes=escopos)
      cliente = gspread.authorize(creds)
      return cliente
  except Exception as e:
    st.error(f"Erro na autenticação: {e}")

  return None
