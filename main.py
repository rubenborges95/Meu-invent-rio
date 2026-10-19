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
  import gspread

  try:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "credentials.json")
    
    # Método nativo e infalível do gspread para ficheiros de serviço locais
    cliente = gspread.service_account(filename=caminho_json)
    return cliente
  except Exception as e:
    st.error(f"Erro na autenticação Google: {e}")
    return None


def abrir_tabela():
  try:
    cliente = obter_cliente_gsheets()
    if not cliente:
      return None
    url = "https://docs.google.com/spreadsheets/d/1cxL--ifJ-2GGWeNFUA2k-g0TLbOVdPFzGQ-i6UJrYiA/edit?gid=0#gid=0"
    sh = cliente.open_by_url(url)
    return sh
  except Exception as e:
    st.error(f"Erro ao abrir folha de cálculo: {e}")
    return None


def carregar_materiais():
  try:
    sh = abrir_tabela()
    if not sh:
      return pd.DataFrame(
          columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]
      )
    ws = sh.worksheet("materiais")
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    if df.empty or "id" not in df.columns:
      return pd.DataFrame(
          columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]
      )
    df["id"] = df["id"].astype(int)
    df["quantidade"] = df["quantidade"].astype(int)
    df["limite_minimo"] = df["limite_minimo"].astype(int)
    return df
  except Exception as e:
    return pd.DataFrame(
        columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]
    )


def guardar_materiais(df):
  try:
    sh = abrir_tabela()
    if not sh:
      return
    ws = sh.worksheet("materiais")
    ws.clear()
    dados_para_escrever = [df.columns.tolist()] + df.values.tolist()
    ws.update(dados_para_escrever)
  except Exception as e:
    st.error(f"Erro ao guardar materiais: {e}")


def carregar_historico():
  try:
    sh = abrir_tabela()
    if not sh:
      return pd.DataFrame(
          columns=[
              "data_hora",
              "material",
              "tipo_acao",
              "quantidade_alterada",
              "quantidade_final",
          ]
      )
    ws = sh.worksheet("historico")
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
    if df.empty:
      return pd.DataFrame(
          columns=[
              "data_hora",
              "material",
              "tipo_acao",
              "quantidade_alterada",
              "quantidade_final",
          ]
      )
    return df
  except:
    return pd.DataFrame(
        columns=[
            "data_hora",
            "material",
            "tipo_acao",
            "quantidade_alterada",
            "quantidade_final",
        ]
    )


def registar_historico(material, tipo_acao, qtd_alt, qtd_final):
  try:
    sh = abrir_tabela()
    if not sh:
      return
    ws = sh.worksheet("historico")
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([
        agora,
        str(material),
        str(tipo_acao),
        int(qtd_alt),
        int(qtd_final),
    ])
  except Exception as e:
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
      "<h3 style='margin-top: 15px; color: #f1c40f; font-family: Arial,"
      " sans-serif;'>A.H. Bombeiros Voluntários Carrazedo de Montenegro</h3>",
      unsafe_allow_html=True,
  )

st.caption("Gestão de Stock Material Pré-Hospitalar")

aba_inventario, aba_registo, aba_historico = st.tabs(
    ["📦 Inventário Ativo", "➕ Registar Novo", "📋 Ocorrências"]
)

df_materiais = carregar_materiais()

# --- ABA 1: INVENTÁRIO ATIVO ---
with aba_inventario:
  pesquisa = st.text_input(
      "🔍 Pesquisa rápida de material...", placeholder="Ex: Guedel, Sorocel..."
  )

  if df_materiais.empty:
    st.info("Nenhum material registado no sistema.")
  else:
    for _, row in df_materiais.iterrows():
      id_m = int(row["id"])
      nome = str(row["nome"])
      qtd = int(row["quantidade"])
      limite = int(row["limite_minimo"])
      cat = str(row["categoria"])

      if pesquisa and (
          pesquisa.lower() not in nome.lower()
          and pesquisa.lower() not in cat.lower()
      ):
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
              df_materiais.loc[df_materiais["id"] == id_m, "quantidade"] = (
                  nova_qtd
              )
              guardar_materiais(df_materiais)
              registar_historico(nome, "Uso Material (-1)", 1, nova_qtd)
              st.rerun()
            else:
              st.error("Erro: Stock a zeros.")

        with col_mais:
          if st.button("📈 +1", key=f"mais_{id_m}"):
            nova_qtd = qtd + 1
            df_materiais.loc[df_materiais["id"] == id_m, "quantidade"] = (
                nova_qtd
            )
            guardar_materiais(df_materiais)
            registar_historico(nome, "Reposição (+1)", 1, nova_qtd)
            st.rerun()

# --- ABA 2: REGISTAR NOVO MATERIAL ---
with aba_registo:
  st.subheader("💊 Entrada de Novo Consumível")
  with st.form("form_cadastro", clear_on_submit=True):
    nome_novo = st.text_input("Designação do Material / Fármaco:")
    qtd_nova = st.number_input(
        "Quantidade Inicial em Stock:", min_value=0, step=1, value=5
    )
    limite_novo = st.number_input(
        "Alerta de Stock Mínimo Individual:", min_value=0, step=1, value=2
    )
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

        st.success(f"'{nome_novo}' adicionado!")
        st.rerun()
      else:
        st.warning("Preenche o nome do material.")

# --- ABA 3: HISTÓRICO E APAGAR ---
with aba_historico:
  st.subheader("📋 Relatório de Movimentações")
  df_hist = carregar_historico()

  if not df_hist.empty:
    df_hist_display = df_hist.rename(
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
      nome_produto = df_materiais.loc[
          df_materiais["id"] == id_eliminar, "nome"
      ].values[0]

      df_materiais = df_materiais[df_materiais["id"] != id_eliminar]
      guardar_materiais(df_materiais)
      registar_historico(nome_produto, "Abate Total", 0, 0)

      st.success(f"'{nome_produto}' foi removido do inventário!")
      st.rerun()
