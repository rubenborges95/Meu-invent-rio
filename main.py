from datetime import datetime
import pandas as pd
import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="AMBULANCE LOG", page_icon="🚑", layout="centered")

# Ligar ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)


def carregar_materiais():
  try:
    df = conn.read(worksheet="materiais", ttl=0)
    if df.empty or "id" not in df.columns:
      return pd.DataFrame(
          columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]
      )
    df["id"] = df["id"].astype(int)
    df["quantidade"] = df["quantidade"].astype(int)
    df["limite_minimo"] = df["limite_minimo"].astype(int)
    return df
  except:
    return pd.DataFrame(
        columns=["id", "nome", "quantidade", "categoria", "limite_minimo"]
    )


def guardar_materiais(df):
  conn.update(worksheet="materiais", data=df)


def carregar_historico():
  try:
    df = conn.read(worksheet="historico", ttl=0)
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
  df_hist = carregar_historico()
  agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  novo_reg = pd.DataFrame([{
      "data_hora": agora,
      "material": material,
      "tipo_acao": tipo_acao,
      "quantidade_alterada": int(qtd_alt),
      "quantidade_final": int(qtd_final),
  }])
  df_atualizado = pd.concat([df_hist, novo_reg], ignore_index=True)
  conn.update(worksheet="historico", data=df_atualizado)


st.markdown(
    "<h3 style='color: #f1c40f; text-align: center;'>A.H. Bombeiros"
    " Voluntários Carrazedo de Montenegro</h3>",
    unsafe_allow_html=True,
)
st.caption("Gestão de Stock Material Pré-Hospitalar")

df_materiais = carregar_materiais()

pesquisa = st.text_input("🔍 Pesquisa rápida...")

if df_materiais.empty:
  st.info("Nenhum material registado.")
else:
  for _, row in df_materiais.iterrows():
    st.write(f"**{row['nome']}** - Quantidade: {row['quantidade']}")
