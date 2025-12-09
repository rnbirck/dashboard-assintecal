import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# CONFIGURAÇÃO DA CONEXÃO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client: Client = None

# Validação das variáveis de ambiente
if not SUPABASE_URL or not SUPABASE_KEY:
    print("Erro fatal: SUPABASE_URL or SUPABASE_KEY não estão definidas no ambiente.")
    st.error(
        "Erro de Configuração: As variáveis de ambiente SUPABASE_URL ou SUPABASE_KEY não foram encontradas."
    )
else:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Conexão com Supabase estabelecida para o data_loader.")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase no data_loader: {e}")
        st.error(
            f"Falha ao conectar ao Supabase: {e}. Verifique as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY."
        )


# FUNÇÕES AUXILIARES E CACHE

CACHE_TTL = 172800  # 48 horas

# --- FUNÇÕES DE CARREGAMENTO DE DADOS (SUPABASE) ---


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_producao(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_producao")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_vendas(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_vendas")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_calcados(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_calcados")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_calcados(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_calcados")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_calcados(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_emprego_calcados")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_ipca_calcados(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_ipca_calcados")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_couro(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_couro")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_couro(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_couro")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_couro(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_emprego_couro")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


# --- FUNÇÕES DE CARREGAMENTO DE DADOS VERTICAIS ---


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_vertical(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_vertical")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_vertical_pais(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_vertical_pais")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_vertical_sh6(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_vertical_sh6")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_vertical(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_vertical")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_vertical_pais(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_vertical_pais")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_vertical_sh6(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_vertical_sh6")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


# --- FUNÇÕES DE CARREGAMENTO DE DADOS COMPONENTES ---


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_componente(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_componente")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_componente_pais(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_componente_pais")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_exp_componente_sh6(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_exp_componente_sh6")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_componente(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_componente")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_componente_pais(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_componente_pais")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_imp_componente_sh6(anos):
    if not supabase_client:
        st.error("Conexão com Supabase não estabelecida.")
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_imp_componente_sh6")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_ipca_geral(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_ipca_geral")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_ind_transformacao(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_ind_transformacao")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_taxa_desemprego(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_taxa_desemprego")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_ibc_br(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_ibc_br")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_taxa_cambio(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_taxa_cambio")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_expectativas(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_expectativas")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_previsao_exportacao(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_previsao_exportacao")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_previsao_producao(anos):
    if not supabase_client:
        return pd.DataFrame()
    response = (
        supabase_client.table("assintecal_previsao_producao")
        .select("*")
        .in_("ano", list(anos))
        .execute()
    )
    return pd.DataFrame(response.data)
