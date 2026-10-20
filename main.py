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

@st.cache_resource
def obter_cliente_gsheets():
    import gspread
    import os
    from google.oauth2.service_account import Credentials
    
    try:
        # Lê as credenciais diretamente das Variáveis de Ambiente do Render
        creds_dict = {
            "type": "service_account",
            "project_id": "stock-bombeiros",
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID", "ee3317924b8f107e0290fc00742d1ee82273094e"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL", "bombeiros-app@stock-bombeiros.iam.gserviceaccount.com"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID", "102395152982852761363"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bombeiros-app%40stock-bombeiros.iam.gserviceaccount.com"
        }
            
        escopos = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro de autenticação: {e}")
        return None

@st.cache_data(ttl=60, show_spinner=False)
def carregar_dados_seguro():
    try:
        cliente = obter_cliente_gsheets()
        if not cliente:
            return pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]), pd.DataFrame()
            
        url = "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
        sh = cliente.open_by_url(url)
        
        # Carregar Materiais
        ws_mat = sh.worksheet("materiais")
        dados_mat = ws_mat.get_all_records()
        df_mat = pd.DataFrame(dados_mat)
        
        if not df_mat.empty and "id" in df_mat.columns:
            df_mat = df_mat.dropna(subset=["id", "nome"])
            df_mat["id"] = df_mat["id"].astype(int)
            df_mat["quantidade"] = df_mat["quantidade"].astype(int)
            df_mat["limite_minimo"] = df_mat["limite_minimo"].astype(int)
        else:
            df_mat = pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"])
            
        # Carregar Histórico
        try:
            ws_hist = sh.worksheet("historico")
            dados_hist = ws_hist.get_all_records()
            df_hist = pd.DataFrame(dados_hist)
        except:
            df_hist = pd.DataFrame(columns=["data_hora", "material", "tipo_acao", "quantidade_alterada", "quantidade_final"])
            
        return df_mat, df_hist
    except Exception as e:
        st.error(f"Erro ao comunicar com o Google Sheets: {e}")
        return pd.DataFrame(columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]), pd.DataFrame()


def guardar_materiais(df):
    try:
        cliente = obter_cliente_gsheets()
        if not cliente:
            return
        url = "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
        sh = cliente.open_by_url(url)
        ws = sh.worksheet("materiais")
        ws.clear()
        dados_para_escrever = [df.columns.tolist()] + df.values.tolist()
        ws.update(values=dados_para_escrever, range_name="A1")
        st.cache_data.clear() # Limpa a cache para refletir as alterações imediatamente
    except Exception as e:
        st.error(f"Erro ao guardar materiais: {e}")


def registar_historico(material, tipo_acao, qtd_alt, qtd_final):
    try:
        cliente = obter_cliente_gsheets()
        if not cliente:
            return
        url = "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
        sh = cliente.open_by_url(url)
        ws = sh.worksheet("historico")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([agora, str(material), str(tipo_acao), int(qtd_alt), int(qtd_final)])
        st.cache_data.clear()
    except Exception:
        pass


# --- Cabeçalho ---
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
    try:
        st.image("WhatsApp Image 2026-10-11 at 14.58.23.jpeg", width=90)
    except:
        pass

with col_titulo:
    st.markdown(
        "<h3 style='margin-top: 15px; color: #f1c40f; font-family: Arial, sans-serif;'>A.H. Bombeiros Voluntários Carrazedo de Montenegro</h3>",
        unsafe_allow_html=True,
    )

st.caption("Gestão de Stock Material Pré-Hospitalar")

aba_inventario, aba_registo, aba_historico = st.tabs(
    ["📦 Inventário Ativo", "➕ Registar Novo", "📋 Ocorrências"]
)

# Carregamento único e seguro de dados com cache
df_materiais, df_historico = carregar_dados_seguro()

# --- ABA 1: INVENTÁRIO ATIVO ---
with aba_inventario:
    pesquisa = st.text_input("🔍 Pesquisa rápida de material...", placeholder="Ex: Guedel, Sorocel...")

    if df_materiais.empty:
        st.warning("A folha de cálculo está vazia ou sem ligação válida.")
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
    else:
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
            
        for _, row in df_materiais.iterrows():
            id_m = int(row["id"])
            nome = str(row["nome"])
            qtd = int(row["quantidade"])
            limite = int(row["limite_minimo"])
            cat = str(row["categoria"])

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
                            df_materiais.loc[df_materiais["id"] == id_m, "quantidade"] = nova_qtd
                            guardar_materiais(df_materiais)
                            registar_historico(nome, "Uso Material (-1)", 1, nova_qtd)
                            st.rerun()
                        else:
                            st.error("Erro: Stock a zeros.")

                with col_mais:
                    if st.button("📈 +1", key=f"mais_{id_m}"):
                        nova_qtd = qtd + 1
                        df_materiais.loc[df_materiais["id"] == id_m, "quantidade"] = nova_qtd
                        guardar_materiais(df_materiais)
                        registar_historico(nome, "Reposição (+1)", 1, nova_qtd)
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
                novo_id = (
                    int(df_materiais["id"].max()) + 1
                    if not df_materiais.empty and pd.notna(df_materiais["id"].max())
                    else 1
                )

                novo_registo = pd.DataFrame([{
                    "id": novo_id,
                    "nome": nome_novo,
                    "quantidade": qtd_nova,
                    "categoria": cat_final,
                    "limite_minimo": limite_novo,
                }])

                df_materiais = pd.concat([df_materiais, novo_registo], ignore_index=True)
                guardar_materiais(df_materiais)
                registar_historico(nome_novo, "Novo Material Adicionado", qtd_nova, qtd_nova)
                
                st.success(f"Material '{nome_novo}' registado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha a designação do material.")

# --- ABA 3: OCORRÊNCIAS ---
with aba_historico:
    st.subheader("📋 Histórico de Movimentos e Ocorrências")
    if df_historico.empty:
        st.info("Ainda não existem registos de histórico.")
    else:
        st.dataframe(df_historico, use_container_width=True)
        if st.button("🔄 Atualizar Histórico"):
            st.cache_data.clear()
            st.rerun()
