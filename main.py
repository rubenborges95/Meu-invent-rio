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

@st.cache_resource
def obter_cliente_gsheets():
    import json
    import os
    import re
    import gspread
    from google.oauth2.service_account import Credentials
    
    try:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_json = os.path.join(diretorio_atual, "credentials.json")
        
        if not os.path.exists(caminho_json):
            st.error(f"Ficheiro 'credentials.json' não encontrado na pasta do projeto.")
            return None
            
        with open(caminho_json, "r", encoding="utf-8") as f:
            creds_dict = json.load(f)
            
        # Reconstrução total e blindada da chave privada para formato PEM válido
        if "private_key" in creds_dict:
            pk = str(creds_dict["private_key"])
            match = re.search(r"-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----", pk, re.DOTALL)
            if match:
                corpo = match.group(1)
                # Remove quaisquer espaços ou quebras inválidas antigas
                corpo_limpo = "".join(corpo.split())
                # Reorganiza exatamente em blocos de 64 carateres (padrão oficial PEM)
                linhas = [corpo_limpo[i:i+64] for i in range(0, len(corpo_limpo), 64)]
                pk_reconstruida = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(linhas) + "\n-----END PRIVATE KEY-----\n"
                creds_dict["private_key"] = pk_reconstruida
            
        escopos = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        return None

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
        ws.update(dados_para_escrever)
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

# Carregamento único e seguro de dados
df_materiais, df_historico = carregar_dados_seguro()

# --- ABA 1: INVENTÁRIO ATIVO ---
with aba_inventario:
    pesquisa = st.text_input("🔍 Pesquisa rápida de material...", placeholder="Ex: Guedel, Sorocel...")

    if df_materiais.empty:
        st.warning("A folha de cálculo está vazia ou sem ligação válida.")
        if st.button("🔄 Atualizar Dados"):
            st.rerun()
    else:
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
                registar_historico(nome_novo, "Registo Inicial", qtd_nova, qtd_nova)

                st.success(f"'{nome_novo}' adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Preenche o nome do material.")

# --- ABA 3: HISTÓRICO E APAGAR ---
with aba_historico:
    st.subheader("📋 Relatório de Movimentações")

    if not df_historico.empty:
        df_hist_display = df_historico.rename(
            columns={
                "data_hora": "Data/Hora",
                "material": "Material",
                "tipo_acao": "Ação",
                "quantidade_alterada": "Qtd Mod.",
                "quantidade_final": "Stock Final",
            }
        )
        st.dataframe(
            df_hist_display.tail(50).sort_index(ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sem histórico registado.")

    st.markdown("---")
    st.subheader("🗑️ Abate / Apagar Material do Sistema")

    if df_materiais.empty:
        st.caption("Não há materiais para eliminar.")
    else:
        opcoes = {
            f"{row['nome']} (ID: {row['id']})": row["id"]
            for _, row in df_materiais.iterrows()
        }
        produto_selecionado = st.selectbox(
            "Selecione o material que deseja apagar permanentemente:",
            list(opcoes.keys()),
        )

        if st.button("🗑️ APAGAR PRODUTO SELECIONADO", type="primary"):
            id_eliminar = opcoes[produto_selecionado]
            nome_produto = df_materiais.loc[df_materiais["id"] == id_eliminar, "nome"].values[0]

            df_materiais = df_materiais[df_materiais["id"] != id_eliminar]
            guardar_materiais(df_materiais)
            registar_historico(nome_produto, "Abate Total", 0, 0)

            st.success(f"'{nome_produto}' foi removido do inventário!")
            st.rerun()
