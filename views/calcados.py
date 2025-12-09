# calcados.py
import streamlit as st
import plotly_express as px

from src.utils import (
    MESES_DIC,
    titulo_centralizado,
    criar_grafico_barras,
    # Funções de preparação de dados
    preparar_dados_emprego_grafico,
    preparar_dados_ipca_grafico,
    formatar_indice_grafico,
    # Funções de display de KPIs
    display_emprego_kpi_cards,
    display_ipca_kpi_cards,
    # Funções de display de gráficos
    display_graficos_prod_vendas,
    display_comex_analise,
)


def expander_calcados_callback():
    """Garante que o expander permaneça aberto após a interação."""
    st.session_state.calcados_expander_state = True


# =============================================================================
# FUNÇÕES ESPECÍFICAS DE CALÇADOS
# =============================================================================


def display_emprego_analise_calcados(df_emprego_calcados, set_expander_open):
    """
    Função auxiliar para renderizar um bloco completo de Emprego no Setor de Calçados.
    """

    # KPIs
    display_emprego_kpi_cards(df=df_emprego_calcados)

    st.divider()

    # Preparar dados
    (
        df_hist_total,
        df_hist_subclasse,
        df_acum_total,
        df_acum_subclasse,
    ) = preparar_dados_emprego_grafico(df_emprego_calcados)

    if df_hist_total.empty:
        st.info("Não há dados suficientes para análise de emprego.")
        return

    # Lista de anos disponível a partir do índice do histórico mensal
    anos_disponiveis = sorted(df_hist_total.index.year.unique().tolist())
    ult_ano = df_emprego_calcados["ano"].max()
    ult_mes = df_emprego_calcados[df_emprego_calcados["ano"] == ult_ano]["mes"].max()
    tab_selection = st.pills(
        "Selecione a visualização:",
        ["Histórico Mensal", "Acumulado no Ano"],
        default="Histórico Mensal",
        selection_mode="single",
        key="emprego_pills",
    )

    if tab_selection == "Histórico Mensal":
        col1, col3, col2 = st.columns([0.45, 0.05, 0.5])
        with col2:
            view_mode = st.segmented_control(
                "Selecione a Análise para o Gráfico",
                options=["Total", "CNAE Subclasse"],
                default="Total",
                key="emprego_view_mode_mes_radio",
                on_change=set_expander_open,
            )

        with col1:
            if view_mode == "Total":
                ANOS_SELECIONADOS = st.select_slider(
                    "Selecione o ano para o gráfico:",
                    options=anos_disponiveis,
                    value=(anos_disponiveis[-2], anos_disponiveis[-1]),
                    key="emprego_hist_select_slider",
                )
                start_year, end_year = ANOS_SELECIONADOS
            else:
                ANO_SELECIONADO = st.selectbox(
                    "Selecione o ano para o gráfico:",
                    options=reversed(anos_disponiveis),
                    index=0,
                    key="emprego_hist_selectbox",
                )
                start_year = end_year = ANO_SELECIONADO

        df_hist_total = df_hist_total[
            (df_hist_total.index.year >= start_year)
            & (df_hist_total.index.year <= end_year)
        ]
        df_hist_subclasse = df_hist_subclasse[
            (df_hist_subclasse.index.year >= start_year)
            & (df_hist_subclasse.index.year <= end_year)
        ]

        if view_mode == "Total":
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
            # Gráfico Histórico por Subclasse
            titulo_centralizado(
                f"Histórico Mensal do Saldo de Emprego por CNAE Subclasse em {start_year}",
                5,
            )
            df_plot_hist_subclasse = formatar_indice_grafico(df_hist_subclasse)
            fig_hist_subclasse = criar_grafico_barras(
                df=df_plot_hist_subclasse,
                titulo="",
                label_y="Saldo de Emprego",
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_sequence=px.colors.qualitative.Plotly,
                showlegend=True,
            )
            st.plotly_chart(fig_hist_subclasse, use_container_width=True)
    else:
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            view_mode_acum = st.segmented_control(
                "Selecione a Análise para o Gráfico",
                options=["Total", "CNAE Subclasse"],
                default="Total",
                key="emprego_view_mode_acum_radio",
                on_change=set_expander_open,
            )

        if view_mode_acum == "Total":
            # Gráfico Acumulado Total
            titulo_centralizado(
                f"Saldo de Emprego de Janeiro a {MESES_DIC[ult_mes]}", 5
            )
            df_plot_acum_total = df_acum_total.copy()
            fig_acum_total = criar_grafico_barras(
                df=df_plot_acum_total,
                titulo="",
                label_y="Saldo de Emprego",
                data_label_format=",.0f",
                hover_label_format=",.0f",
            )
            st.plotly_chart(fig_acum_total, use_container_width=True)

        else:
            # Gráfico Acumulado por Subclasse
            titulo_centralizado(
                f"Saldo de Emprego por CNAE Subclasse de Janeiro a {MESES_DIC[ult_mes]}",
                5,
            )
            df_plot_acum_subclasse = df_acum_subclasse.copy()
            fig_acum_subclasse = criar_grafico_barras(
                df=df_plot_acum_subclasse,
                titulo="",
                label_y="Saldo de Emprego",
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_sequence=px.colors.qualitative.Plotly,
                showlegend=True,
            )
            st.plotly_chart(fig_acum_subclasse, use_container_width=True)


def display_ipca_analise(df_ipca, titulo_expander, set_expander_open):
    """
    Função auxiliar para renderizar um bloco completo de IPCA.
    """

    # KPIs
    display_ipca_kpi_cards(df_ipca)

    st.divider()

    # Preparar dados para gráfico
    df_ipca_mes, df_ipca_12_meses = preparar_dados_ipca_grafico(df_ipca)
    anos_disponiveis = sorted(df_ipca["ano"].unique().tolist())

    col1, col3, col2 = st.columns([0.45, 0.05, 0.5])
    with col1:
        ANOS_SELECIONADOS = st.select_slider(
            "Selecione o ano para o gráfico:",
            options=anos_disponiveis,
            value=(anos_disponiveis[-2], anos_disponiveis[-1]),
            key="ipca_ano_select_slider",
        )
    with col2:
        view_mode = st.segmented_control(
            "Selecione a visualização do IPCA:",
            options=["Mensal", "Acumulado 12 Meses"],
            default="Mensal",
            key="ipca_view_mode_radio",
            on_change=set_expander_open,
        )

    start_year, end_year = ANOS_SELECIONADOS

    df_ipca_mes = df_ipca_mes[
        (df_ipca_mes.index.year >= start_year) & (df_ipca_mes.index.year <= end_year)
    ]
    df_ipca_12_meses = df_ipca_12_meses[
        (df_ipca_12_meses.index.year >= start_year)
        & (df_ipca_12_meses.index.year <= end_year)
    ]

    if view_mode == "Mensal":
        # Gráfico IPCA Mensal
        titulo_centralizado(
            f"Inflação Mensal de Calçados e Acessórios de {start_year} a {end_year}", 5
        )
        df_plot_ipca_mes = formatar_indice_grafico(df_ipca_mes)
        fig_ipca_mes = criar_grafico_barras(
            df=df_plot_ipca_mes,
            titulo="",
            label_y="IPCA Mensal (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig_ipca_mes, use_container_width=True)
    else:
        # Gráfico IPCA Acumulado 12 Meses
        titulo_centralizado(
            f"Inflação Acumulada em 12 Meses de Calçados e Acessórios de {start_year} a {end_year}",
            5,
        )
        df_plot_ipca_12_meses = formatar_indice_grafico(df_ipca_12_meses)
        fig_ipca_12_meses = criar_grafico_barras(
            df=df_plot_ipca_12_meses,
            titulo="",
            label_y="IPCA Acumulado 12 Meses (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig_ipca_12_meses, use_container_width=True)


# =============================================================================
# FUNÇÕES PRINCIPAIS DA PÁGINA
# =============================================================================


def display_prod_vendas_expander(df_producao, df_vendas, df_previsao_producao):
    """Renderiza os dois blocos de análise (Produção e Vendas)."""

    display_graficos_prod_vendas(
        df=df_producao,
        titulo_expander="Produção",
        titulo_kpi="Produção Industrial de Calçados",
        categoria_kpi="Produção",
        filtro_kpi="fabricao_calcado",
        state_key_prefix="prod",
        df_previsao=df_previsao_producao,
    )

    display_graficos_prod_vendas(
        df=df_vendas,
        titulo_expander="Volume de Vendas",
        titulo_kpi="Volume de Vendas no Comércio de Tecidos, Vestuário e Calçados",
        categoria_kpi="Vendas",
        filtro_kpi="vestuario_calcados",
        state_key_prefix="vendas",
    )


def show_page_calcados(
    df_producao,
    df_vendas,
    df_exp_calcados,
    df_imp_calcados,
    df_emprego_calcados,
    df_ipca_calcados,
    df_previsao_exportacao,
    df_previsao_producao,
):
    """Função principal que renderiza a página de Calçados."""

    titulo_centralizado("Dashboard de Calçados", 1)
    st.info("Clique nos menus abaixo para explorar os dados do setor de Calçados.")

    with st.expander("Produção e Volume de Vendas", expanded=False):
        display_prod_vendas_expander(
            df_producao=df_producao,
            df_vendas=df_vendas,
            df_previsao_producao=df_previsao_producao,
        )

    with st.expander("Comércio Exterior - Exportação", expanded=False):
        display_comex_analise(
            df_comex=df_exp_calcados,
            coluna_dados="valor",
            titulo_expander="Exportação em Valor (US$)",
            titulo_kpi="Exportação de Calçados (US$)",
            state_key_prefix="exp_valor",
            categoria_kpi="Exportação",
            set_expander_open=None,
        )
        display_comex_analise(
            df_comex=df_exp_calcados,
            coluna_dados="pares",
            titulo_expander="Exportação em Pares",
            titulo_kpi="Exportação de Calçados em Pares",
            state_key_prefix="exp_pares",
            categoria_kpi="Exportação",
            set_expander_open=None,
            df_previsao=df_previsao_exportacao,
        )

    with st.expander("Comércio Exterior - Importação", expanded=False):
        display_comex_analise(
            df_comex=df_imp_calcados,
            coluna_dados="valor",
            titulo_expander="Importação em Valor (US$)",
            titulo_kpi="Importação de Calçados (US$)",
            state_key_prefix="imp_valor",
            categoria_kpi="Importação",
            set_expander_open=None,
        )
        display_comex_analise(
            df_comex=df_imp_calcados,
            coluna_dados="pares",
            titulo_expander="Importação em Pares",
            titulo_kpi="Importação de Calçados em Pares",
            state_key_prefix="imp_pares",
            categoria_kpi="Importação",
            set_expander_open=None,
        )

    with st.expander("Emprego", expanded=False):
        display_emprego_analise_calcados(
            df_emprego_calcados=df_emprego_calcados,
            set_expander_open=None,
        )

    with st.expander("Inflação (IPCA)", expanded=False):
        display_ipca_analise(
            df_ipca=df_ipca_calcados,
            titulo_expander="Inflação (IPCA) - Calçados e Acessórios",
            set_expander_open=None,
        )
