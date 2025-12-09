# app.py

# ==============================================================================
# BLOCO 1: IMPORTS DE TERCEIROS (PIP)
# ==============================================================================
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv()
# ==============================================================================
# BLOCO 2: IMPORTS DA APLICAÇÃO (SRC)
# ==============================================================================

from views.calcados import show_page_calcados  # noqa: E402
from views.couro import show_page_couro  # noqa: E402
from views.vertical import show_page_vertical  # noqa: E402
from views.componente import show_page_componente  # noqa: E402
from views.macroeconomia import show_page_macroeconomia  # noqa: E402
from views.home import show_page_home  # noqa: E402
from views.dados import show_page_dados  # noqa: E402


from src.utils import carregar_css  # noqa: E402
from src.utils import manter_posicao_scroll  # noqa: E402


from src.data_loader import (  # noqa: E402
    carregar_dados_producao,
    carregar_dados_vendas,
    carregar_dados_exp_calcados,
    carregar_dados_imp_calcados,
    carregar_dados_emprego_calcados,
    carregar_dados_ipca_calcados,
    carregar_dados_exp_couro,
    carregar_dados_imp_couro,
    carregar_dados_emprego_couro,
    carregar_dados_exp_vertical,
    carregar_dados_exp_vertical_pais,
    carregar_dados_exp_vertical_sh6,
    carregar_dados_imp_vertical,
    carregar_dados_imp_vertical_pais,
    carregar_dados_imp_vertical_sh6,
    carregar_dados_exp_componente,
    carregar_dados_exp_componente_pais,
    carregar_dados_exp_componente_sh6,
    carregar_dados_imp_componente,
    carregar_dados_imp_componente_pais,
    carregar_dados_imp_componente_sh6,
    carregar_dados_ibc_br,
    carregar_dados_expectativas,
    carregar_dados_ipca_geral,
    carregar_dados_taxa_cambio,
    carregar_dados_ind_transformacao,
    carregar_dados_taxa_desemprego,
    carregar_dados_previsao_exportacao,
    carregar_dados_previsao_producao,
)

from src.config import anos_de_interesse  # noqa: E402


def main():
    """Função principal que executa a aplicação Streamlit."""

    st.set_page_config(layout="wide", page_title="Dashboard Assintecal", page_icon="📊")

    carregar_css("assets/style.css")

    with st.spinner("Carregando todos os dados da aplicação... Por favor, aguarde."):
        df_producao = carregar_dados_producao(anos=anos_de_interesse)
        df_vendas = carregar_dados_vendas(anos=anos_de_interesse)
        df_exp_calcados = carregar_dados_exp_calcados(anos=anos_de_interesse)
        df_previsao_exportacao = carregar_dados_previsao_exportacao(
            anos=anos_de_interesse
        )
        df_previsao_producao = carregar_dados_previsao_producao(anos=anos_de_interesse)
        df_imp_calcados = carregar_dados_imp_calcados(anos=anos_de_interesse)
        df_emprego_calcados = carregar_dados_emprego_calcados(anos=anos_de_interesse)
        df_ipca_calcados = carregar_dados_ipca_calcados(anos=anos_de_interesse)
        df_exp_couro = carregar_dados_exp_couro(anos=anos_de_interesse)
        df_imp_couro = carregar_dados_imp_couro(anos=anos_de_interesse)
        df_emprego_couro = carregar_dados_emprego_couro(anos=anos_de_interesse)
        # Dados de Vertical
        df_exp_vertical = carregar_dados_exp_vertical(anos=anos_de_interesse)
        df_exp_vertical_pais = carregar_dados_exp_vertical_pais(anos=anos_de_interesse)
        df_exp_vertical_sh6 = carregar_dados_exp_vertical_sh6(anos=anos_de_interesse)
        df_imp_vertical = carregar_dados_imp_vertical(anos=anos_de_interesse)
        df_imp_vertical_pais = carregar_dados_imp_vertical_pais(anos=anos_de_interesse)
        df_imp_vertical_sh6 = carregar_dados_imp_vertical_sh6(anos=anos_de_interesse)
        # Dados de Componente
        df_exp_componente = carregar_dados_exp_componente(anos=anos_de_interesse)
        df_exp_componente_pais = carregar_dados_exp_componente_pais(
            anos=anos_de_interesse
        )
        df_exp_componente_sh6 = carregar_dados_exp_componente_sh6(
            anos=anos_de_interesse
        )
        df_imp_componente = carregar_dados_imp_componente(anos=anos_de_interesse)
        df_imp_componente_pais = carregar_dados_imp_componente_pais(
            anos=anos_de_interesse
        )
        df_imp_componente_sh6 = carregar_dados_imp_componente_sh6(
            anos=anos_de_interesse
        )
        # Dados de Macroeconomia
        df_ibc_br = carregar_dados_ibc_br(anos=anos_de_interesse)
        df_expectativas = carregar_dados_expectativas(anos=anos_de_interesse)
        df_ipca_geral = carregar_dados_ipca_geral(anos=anos_de_interesse)
        df_taxa_cambio = carregar_dados_taxa_cambio(anos=anos_de_interesse)
        df_ind_transformacao = carregar_dados_ind_transformacao(anos=anos_de_interesse)
        df_taxa_desemprego = carregar_dados_taxa_desemprego(anos=anos_de_interesse)

    with st.sidebar:
        pagina_selecionada = option_menu(
            menu_title="Menu",
            options=[
                "Home",
                "Calçados",
                "Couro",
                "Vertical",
                "Componente",
                "Macroeconomia",
                "Dados",
            ],
            icons=[
                "house",
                "box-seam",
                "layers",
                "bar-chart",
                "puzzle",
                "graph-up",
                "download",
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "icon": {"font-size": "14px"},
                "nav-link": {
                    "font-size": "14px",
                    "padding": "8px 15px",
                },
                "nav-link-selected": {"background-color": "#22B573"},
            },
        )
    # ==============================================================================
    # RENDERIZAÇÃO DAS PÁGINAS
    # ==============================================================================
    placeholder = st.empty()

    with placeholder.container():
        if pagina_selecionada == "Home":
            show_page_home(
                df_producao=df_producao,
                df_vendas=df_vendas,
                df_exp_calcados=df_exp_calcados,
                df_imp_calcados=df_imp_calcados,
                df_emprego_calcados=df_emprego_calcados,
                df_ipca_calcados=df_ipca_calcados,
                df_exp_couro=df_exp_couro,
                df_imp_couro=df_imp_couro,
                df_emprego_couro=df_emprego_couro,
                df_exp_vertical=df_exp_vertical,
                df_exp_componente=df_exp_componente,
                df_ibc_br=df_ibc_br,
                df_expectativas=df_expectativas,
                df_ipca_geral=df_ipca_geral,
                df_taxa_cambio=df_taxa_cambio,
                df_ind_transformacao=df_ind_transformacao,
                df_taxa_desemprego=df_taxa_desemprego,
            )
        if pagina_selecionada == "Calçados":
            show_page_calcados(
                df_producao=df_producao,
                df_vendas=df_vendas,
                df_exp_calcados=df_exp_calcados,
                df_imp_calcados=df_imp_calcados,
                df_emprego_calcados=df_emprego_calcados,
                df_ipca_calcados=df_ipca_calcados,
                df_previsao_exportacao=df_previsao_exportacao,
                df_previsao_producao=df_previsao_producao,
            )
        if pagina_selecionada == "Couro":
            show_page_couro(
                df_producao=df_producao,
                df_exp_couro=df_exp_couro,
                df_imp_couro=df_imp_couro,
                df_emprego_couro=df_emprego_couro,
            )
        if pagina_selecionada == "Vertical":
            show_page_vertical(
                df_exp_vertical=df_exp_vertical,
                df_exp_vertical_pais=df_exp_vertical_pais,
                df_exp_vertical_sh6=df_exp_vertical_sh6,
                df_imp_vertical=df_imp_vertical,
                df_imp_vertical_pais=df_imp_vertical_pais,
                df_imp_vertical_sh6=df_imp_vertical_sh6,
            )
        if pagina_selecionada == "Componente":
            show_page_componente(
                df_exp_componente=df_exp_componente,
                df_exp_componente_pais=df_exp_componente_pais,
                df_exp_componente_sh6=df_exp_componente_sh6,
                df_imp_componente=df_imp_componente,
                df_imp_componente_pais=df_imp_componente_pais,
                df_imp_componente_sh6=df_imp_componente_sh6,
            )
        if pagina_selecionada == "Macroeconomia":
            show_page_macroeconomia(
                df_ibc_br=df_ibc_br,
                df_expectativas=df_expectativas,
                df_ipca_geral=df_ipca_geral,
                df_taxa_cambio=df_taxa_cambio,
                df_ind_transformacao=df_ind_transformacao,
                df_taxa_desemprego=df_taxa_desemprego,
            )
        if pagina_selecionada == "Dados":
            show_page_dados(
                df_producao=df_producao,
                df_vendas=df_vendas,
                df_exp_calcados=df_exp_calcados,
                df_imp_calcados=df_imp_calcados,
                df_emprego_calcados=df_emprego_calcados,
                df_ipca_calcados=df_ipca_calcados,
                df_previsao_exportacao=df_previsao_exportacao,
                df_previsao_producao=df_previsao_producao,
                df_exp_couro=df_exp_couro,
                df_imp_couro=df_imp_couro,
                df_emprego_couro=df_emprego_couro,
                df_exp_vertical=df_exp_vertical,
                df_exp_vertical_pais=df_exp_vertical_pais,
                df_exp_vertical_sh6=df_exp_vertical_sh6,
                df_imp_vertical=df_imp_vertical,
                df_imp_vertical_pais=df_imp_vertical_pais,
                df_imp_vertical_sh6=df_imp_vertical_sh6,
                df_exp_componente=df_exp_componente,
                df_exp_componente_pais=df_exp_componente_pais,
                df_exp_componente_sh6=df_exp_componente_sh6,
                df_imp_componente=df_imp_componente,
                df_imp_componente_pais=df_imp_componente_pais,
                df_imp_componente_sh6=df_imp_componente_sh6,
                df_ibc_br=df_ibc_br,
                df_expectativas=df_expectativas,
                df_ipca_geral=df_ipca_geral,
                df_taxa_cambio=df_taxa_cambio,
                df_ind_transformacao=df_ind_transformacao,
                df_taxa_desemprego=df_taxa_desemprego,
            )

    manter_posicao_scroll()


if __name__ == "__main__":
    main()
