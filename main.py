@st.cache_resource
def obter_cliente_gsheets():
    import gspread
    from google.oauth2.service_account import Credentials

    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=escopos)
        cliente = gspread.authorize(creds)
        return cliente
    except Exception as e:
        st.error(f"Erro ao carregar o ficheiro credentials.json: {e}")
        return None
