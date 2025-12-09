"""
Página de Componentes do Dashboard Assintecal
"""

import streamlit as st
from src.utils import (
    display_comex_vertical_analise,
    titulo_centralizado,
)


def show_page_componente(
    df_exp_componente,
    df_exp_componente_pais,
    df_exp_componente_sh6,
    df_imp_componente,
    df_imp_componente_pais,
    df_imp_componente_sh6,
):
    """
    Página principal de análise dos componentes para calçados.

    Args:
        df_exp_componente: DataFrame com exportações agregadas por componente
        df_exp_componente_pais: DataFrame com exportações por componente e país
        df_exp_componente_sh6: DataFrame com exportações por componente e SH6
        df_imp_componente: DataFrame com importações agregadas por componente
        df_imp_componente_pais: DataFrame com importações por componente e país
        df_imp_componente_sh6: DataFrame com importações por componente e SH6
    """

    # =======================
    # SEÇÃO DE EXPORTAÇÕES
    # =======================
    titulo_centralizado("Dashboard de Componentes", 1)
    st.info("Clique nos menus abaixo para explorar os dados dos Componentes.")
    display_comex_vertical_analise(
        df_comex=df_exp_componente,
        df_comex_pais=df_exp_componente_pais,
        df_comex_sh6=df_exp_componente_sh6,
        titulo_expander="Exportações por Componente",
        titulo_kpi="Exportações",
        state_key_prefix="exp_componente",
        categoria_kpi="Exportação",
        set_expander_open=None,
        expander_state_key="exp_componente_expander_state",
        coluna_tipo="componente",
        usar_expander=True,
    )

    # =======================
    # SEÇÃO DE IMPORTAÇÕES
    # =======================
    display_comex_vertical_analise(
        df_comex=df_imp_componente,
        df_comex_pais=df_imp_componente_pais,
        df_comex_sh6=df_imp_componente_sh6,
        titulo_expander="Importações por Componente",
        titulo_kpi="Importações",
        state_key_prefix="imp_componente",
        categoria_kpi="Importação",
        set_expander_open=None,
        expander_state_key="imp_componente_expander_state",
        coluna_tipo="componente",
        usar_expander=True,
    )
