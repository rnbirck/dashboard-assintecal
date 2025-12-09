"""
Página de Verticais do Dashboard Assintecal
"""

import streamlit as st
from src.utils import (
    display_comex_vertical_analise,
    titulo_centralizado,
)


def show_page_vertical(
    df_exp_vertical,
    df_exp_vertical_pais,
    df_exp_vertical_sh6,
    df_imp_vertical,
    df_imp_vertical_pais,
    df_imp_vertical_sh6,
):
    """
    Página principal de análise das verticais de calçados.

    Args:
        df_exp_vertical: DataFrame com exportações agregadas por vertical
        df_exp_vertical_pais: DataFrame com exportações por vertical e país
        df_exp_vertical_sh6: DataFrame com exportações por vertical e SH6
        df_imp_vertical: DataFrame com importações agregadas por vertical
        df_imp_vertical_pais: DataFrame com importações por vertical e país
        df_imp_vertical_sh6: DataFrame com importações por vertical e SH6
    """

    # =======================
    # SEÇÃO DE EXPORTAÇÕES
    # =======================
    titulo_centralizado("Dashboard de Verticais", 1)
    st.info("Clique nos menus abaixo para explorar os dados das Verticais.")
    display_comex_vertical_analise(
        df_comex=df_exp_vertical,
        df_comex_pais=df_exp_vertical_pais,
        df_comex_sh6=df_exp_vertical_sh6,
        titulo_expander="Exportações por Vertical",
        titulo_kpi="Exportações",
        state_key_prefix="exp_vertical",
        categoria_kpi="Exportação",
        set_expander_open=None,
        expander_state_key="exp_vertical_expander_state",
        coluna_tipo="vertical",
        usar_expander=True,
    )

    # =======================
    # SEÇÃO DE IMPORTAÇÕES
    # =======================
    display_comex_vertical_analise(
        df_comex=df_imp_vertical,
        df_comex_pais=df_imp_vertical_pais,
        df_comex_sh6=df_imp_vertical_sh6,
        titulo_expander="Importações por Vertical",
        titulo_kpi="Importações",
        state_key_prefix="imp_vertical",
        categoria_kpi="Importação",
        set_expander_open=None,
        expander_state_key="imp_vertical_expander_state",
        coluna_tipo="vertical",
        usar_expander=True,
    )
