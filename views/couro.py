# couro.py
import streamlit as st

from src.utils import (
    MESES_DIC,
    titulo_centralizado,
    criar_grafico_barras,
    # Funções de preparação de dados
    preparar_dados_emprego_grafico,
    formatar_indice_grafico,
    # Funções de display de KPIs
    display_emprego_kpi_cards,
    # Funções de display de gráficos
    display_graficos_prod_vendas,
    display_comex_analise,
)


def display_emprego_analise_couro(df_emprego_couro, set_expander_open):
    """
    Função auxiliar para renderizar um bloco completo de Emprego no Setor de Couro.
    """

    # KPIs
    display_emprego_kpi_cards(df=df_emprego_couro)

    st.divider()

    # Preparar dados
    (
        df_hist_total,
        df_hist_subclasse,
        df_acum_total,
        df_acum_subclasse,
    ) = preparar_dados_emprego_grafico(df_emprego_couro)

    if df_hist_total.empty:
        st.info("Não há dados suficientes para análise de emprego.")
        return

    # Lista de anos disponível a partir do índice do histórico mensal
    anos_disponiveis = sorted(df_hist_total.index.year.unique().tolist())
    ult_ano = df_emprego_couro["ano"].max()
    ult_mes = df_emprego_couro[df_emprego_couro["ano"] == ult_ano]["mes"].max()

    tab_selection = st.pills(
        "Selecione a visualização:",
        ["Histórico Mensal", "Acumulado no Ano"],
        default="Histórico Mensal",
        selection_mode="single",
        key="couro_emprego_pills",
    )

    if tab_selection == "Histórico Mensal":
        col1, _ = st.columns(2)
        with col1:
            ANOS_SELECIONADOS = st.select_slider(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                value=(anos_disponiveis[-2], anos_disponiveis[-1]),
                key="couro_emprego_hist_select_slider",
                on_change=set_expander_open,
            )
            start_year, end_year = ANOS_SELECIONADOS

        df_hist_total = df_hist_total[
            (df_hist_total.index.year >= start_year)
            & (df_hist_total.index.year <= end_year)
        ]

        # Gráfico Histórico Total
        titulo_centralizado(
            f"Histórico Mensal do Saldo de Emprego de {start_year} a {end_year}", 5
        )
        df_plot_hist_total = formatar_indice_grafico(df_hist_total)
        fig_hist_total = criar_grafico_barras(
            df=df_plot_hist_total,
            titulo="",
            label_y="Saldo de Emprego",
            data_label_format=",.0f",
            hover_label_format=",.0f",
        )
        st.plotly_chart(fig_hist_total, use_container_width=True)
    else:
        # Gráfico Acumulado Total
        titulo_centralizado(f"Saldo de Emprego de Janeiro a {MESES_DIC[ult_mes]}", 5)
        df_plot_acum_total = df_acum_total.copy()
        fig_acum_total = criar_grafico_barras(
            df=df_plot_acum_total,
            titulo="",
            label_y="Saldo de Emprego",
            data_label_format=",.0f",
            hover_label_format=",.0f",
        )
        st.plotly_chart(fig_acum_total, use_container_width=True)


def show_page_couro(df_producao, df_exp_couro, df_imp_couro, df_emprego_couro):
    """Função principal que renderiza a página de Couro."""

    titulo_centralizado("Dashboard de Couro", 1)
    st.info("Clique nos menus abaixo para explorar os dados do setor de Couro.")

    with st.expander("Produção", expanded=False):
        display_graficos_prod_vendas(
            df=df_producao,
            titulo_expander="Produção",
            titulo_kpi="Produção Industrial de Couro",
            categoria_kpi="Produção",
            filtro_kpi="curtimento_couro",
            state_key_prefix="couro_prod",
            usar_expander=False,
        )

    with st.expander("Comércio Exterior - Exportação", expanded=False):
        display_comex_analise(
            df_comex=df_exp_couro,
            coluna_dados="valor",
            titulo_expander="Exportação em Valor (US$)",
            titulo_kpi="Exportação de Couro (US$)",
            state_key_prefix="couro_exp_valor",
            categoria_kpi="Exportação",
            set_expander_open=None,
            usar_expander=False,
        )

    with st.expander("Comércio Exterior - Importação", expanded=False):
        display_comex_analise(
            df_comex=df_imp_couro,
            coluna_dados="valor",
            titulo_expander="Importação em Valor (US$)",
            titulo_kpi="Importação de Couro (US$)",
            state_key_prefix="couro_imp_valor",
            categoria_kpi="Importação",
            set_expander_open=None,
            usar_expander=False,
        )

    with st.expander("Emprego", expanded=False):
        display_emprego_analise_couro(
            df_emprego_couro=df_emprego_couro,
            set_expander_open=None,
        )
