# macroeconomia.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.utils import (
    MESES_DIC,
    titulo_centralizado,
    criar_grafico_barras,
    formatar_indice_grafico,
    style_saldo_variacao,
    formatar_pct_br,
)


def display_ibc_br_analise(df_ibc_br):
    """
    Renderiza o bloco completo de análise do IBC-Br (Índice de Atividade Econômica do Banco Central).
    """

    if df_ibc_br.empty:
        st.info("Não há dados disponíveis para o IBC-Br.")
        return

    # Converter colunas para numérico
    df_ibc_br["ano"] = pd.to_numeric(df_ibc_br["ano"], errors="coerce")
    df_ibc_br["mes"] = pd.to_numeric(df_ibc_br["mes"], errors="coerce")
    df_ibc_br["ibc_mensal"] = pd.to_numeric(df_ibc_br["ibc_mensal"], errors="coerce")
    df_ibc_br["ibc_mes_anterior"] = pd.to_numeric(
        df_ibc_br["ibc_mes_anterior"], errors="coerce"
    )
    df_ibc_br["ibc_acumulado"] = pd.to_numeric(
        df_ibc_br["ibc_acumulado"], errors="coerce"
    )

    # Filtrar dados válidos
    df_ibc_br = df_ibc_br.dropna(subset=["ano", "mes"])

    # Identificar último mês/ano
    ultimo_ano = int(df_ibc_br["ano"].max())
    ultimo_mes = int(df_ibc_br[df_ibc_br["ano"] == ultimo_ano]["mes"].max())

    # KPIs
    titulo_centralizado("Indicadores de Atividade Econômica (IBC-Br)", 3)
    titulo_centralizado(
        f"Último dado disponível: {MESES_DIC[ultimo_mes]}/{ultimo_ano}", 6
    )

    st.divider()

    # Pegar valores mais recentes
    df_ultimo = df_ibc_br[
        (df_ibc_br["ano"] == ultimo_ano) & (df_ibc_br["mes"] == ultimo_mes)
    ]

    if not df_ultimo.empty:
        valor_mensal = df_ultimo["ibc_mensal"].iloc[0]
        valor_mes_anterior = df_ultimo["ibc_mes_anterior"].iloc[0]
        valor_acumulado = df_ultimo["ibc_acumulado"].iloc[0]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=f"Variação Mensal (vs. mesmo mês {ultimo_ano - 1})",
                value=f"{valor_mensal:,.2f}%".replace(".", ","),
                help=f"Variação do IBC-Br em relação ao mesmo mês do ano anterior ({MESES_DIC[ultimo_mes]}/{ultimo_ano})",
            )

        with col2:
            st.metric(
                label="Variação vs. Mês Anterior",
                value=f"{valor_mes_anterior:,.2f}%".replace(".", ","),
                help=f"Variação do IBC-Br em relação ao mês imediatamente anterior ({MESES_DIC[ultimo_mes]}/{ultimo_ano})",
            )

        with col3:
            st.metric(
                label="Variação Acumulada no Ano",
                value=f"{valor_acumulado:,.2f}%".replace(".", ","),
                help=f"Variação acumulada do IBC-Br no ano de {ultimo_ano}",
            )

    st.divider()

    # Preparar dados para gráfico
    df_ibc_br["data"] = pd.to_datetime(
        df_ibc_br["ano"].astype(str)
        + "-"
        + df_ibc_br["mes"].astype(str).str.zfill(2)
        + "-01"
    )

    # Anos disponíveis com base nos dados válidos de cada métrica
    anos_com_mensal = set(df_ibc_br[df_ibc_br["ibc_mensal"].notna()]["ano"].unique())
    anos_com_mes_anterior = set(
        df_ibc_br[df_ibc_br["ibc_mes_anterior"].notna()]["ano"].unique()
    )
    anos_com_acumulado = set(
        df_ibc_br[df_ibc_br["ibc_acumulado"].notna()]["ano"].unique()
    )

    # Interseção de todos os anos com dados válidos em todas as métricas
    anos_disponiveis = sorted(
        anos_com_mensal & anos_com_mes_anterior & anos_com_acumulado
    )

    col1, col3, col2 = st.columns([0.45, 0.05, 0.5])

    with col1:
        anos_selecionados = st.select_slider(
            "Selecione o período para o gráfico:",
            options=anos_disponiveis,
            value=(anos_disponiveis[-2], anos_disponiveis[-1])
            if len(anos_disponiveis) >= 2
            else (anos_disponiveis[0], anos_disponiveis[-1]),
            key="ibc_br_ano_select_slider",
        )

    with col2:
        view_mode = st.segmented_control(
            "Selecione a visualização:",
            options=["Mensal (vs. ano anterior)", "Mês Anterior", "Acumulado no Ano"],
            default="Mensal (vs. ano anterior)",
            key="ibc_br_view_mode_radio",
        )

    start_year, end_year = anos_selecionados

    # Filtrar dados pelo período selecionado
    df_filtrado = df_ibc_br[
        (df_ibc_br["ano"] >= start_year) & (df_ibc_br["ano"] <= end_year)
    ].copy()

    df_filtrado = df_filtrado.sort_values("data")
    df_filtrado = df_filtrado.set_index("data")

    if view_mode == "Mensal (vs. ano anterior)":
        titulo_centralizado(
            f"IBC-Br: Variação Mensal (vs. mesmo mês do ano anterior) de {start_year} a {end_year}",
            5,
        )
        df_plot = df_filtrado[["ibc_mensal"]].copy()
        df_plot = df_plot.dropna()  # Remove linhas com valores nulos
        df_plot_formatado = formatar_indice_grafico(df_plot)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y="Variação (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Mês Anterior":
        titulo_centralizado(
            f"IBC-Br: Variação em Relação ao Mês Anterior de {start_year} a {end_year}",
            5,
        )
        df_plot = df_filtrado[["ibc_mes_anterior"]].copy()
        df_plot = df_plot.dropna()  # Remove linhas com valores nulos
        df_plot_formatado = formatar_indice_grafico(df_plot)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y="Variação (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Acumulado no Ano
        titulo_centralizado(
            f"IBC-Br: Variação Acumulada no Ano de {start_year} a {end_year}",
            5,
        )
        df_plot = df_filtrado[["ibc_acumulado"]].copy()
        df_plot = df_plot.dropna()  # Remove linhas com valores nulos
        df_plot_formatado = formatar_indice_grafico(df_plot)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y="Variação Acumulada (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)


def display_expectativas_analise(df_expectativas):
    """
    Renderiza o bloco completo de análise das Expectativas de Mercado (PIB e Inflação).
    """

    if df_expectativas.empty:
        st.info("Não há dados disponíveis para as Expectativas.")
        return

    # Converter colunas para numérico
    df_expectativas["ano"] = pd.to_numeric(df_expectativas["ano"], errors="coerce")
    df_expectativas["mes"] = pd.to_numeric(df_expectativas["mes"], errors="coerce")
    df_expectativas["expectativa_pib_25"] = pd.to_numeric(
        df_expectativas["expectativa_pib_25"], errors="coerce"
    )
    df_expectativas["expectativa_pib_26"] = pd.to_numeric(
        df_expectativas["expectativa_pib_26"], errors="coerce"
    )
    df_expectativas["expectativa_ipca_25"] = pd.to_numeric(
        df_expectativas["expectativa_ipca_25"], errors="coerce"
    )
    df_expectativas["expectativa_ipca_26"] = pd.to_numeric(
        df_expectativas["expectativa_ipca_26"], errors="coerce"
    )

    # Filtrar dados válidos
    df_expectativas = df_expectativas.dropna(subset=["ano", "mes"])

    # Criar coluna de data
    df_expectativas["data"] = pd.to_datetime(
        df_expectativas["ano"].astype(str)
        + "-"
        + df_expectativas["mes"].astype(str).str.zfill(2)
        + "-01"
    )

    # Filtrar apenas os dois últimos anos
    anos_disponiveis = sorted(df_expectativas["ano"].unique())
    if len(anos_disponiveis) >= 2:
        ultimos_dois_anos = anos_disponiveis[-2:]
    else:
        ultimos_dois_anos = anos_disponiveis

    df_filtrado = df_expectativas[df_expectativas["ano"].isin(ultimos_dois_anos)].copy()
    df_filtrado = df_filtrado.sort_values("data")

    titulo_centralizado("Expectativas de Mercado", 3)

    col1, col3, col2 = st.columns([0.45, 0.05, 0.5])

    with col1:
        view_mode = st.segmented_control(
            "Selecione a visualização:",
            options=["PIB", "Inflação (IPCA)"],
            default="PIB",
            key="expectativas_view_mode_radio",
        )

    if view_mode == "PIB":
        titulo_centralizado(
            f"Expectativas de Crescimento do PIB para 2025 e 2026 ({ultimos_dois_anos[0]}-{ultimos_dois_anos[-1]})",
            5,
        )

        # Criar gráfico de linhas
        fig = go.Figure()

        # Linha para 2025 (preto)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["data"],
                y=df_filtrado["expectativa_pib_25"],
                mode="lines+markers+text",
                name="2025",
                line=dict(color="#000000", width=2),
                marker=dict(size=6),
                text=[
                    f"{val:.1f}%".replace(".", ",")
                    for val in df_filtrado["expectativa_pib_25"]
                ],
                textposition="top center",
                textfont=dict(size=10, color="#000000"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Expectativa 2025:</b> %{y:.2f}%<extra></extra>",
            )
        )

        # Linha para 2026 (verde)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["data"],
                y=df_filtrado["expectativa_pib_26"],
                mode="lines+markers+text",
                name="2026",
                line=dict(color="#22B573", width=2),
                marker=dict(size=6),
                text=[
                    f"{val:.1f}%".replace(".", ",")
                    for val in df_filtrado["expectativa_pib_26"]
                ],
                textposition="bottom center",
                textfont=dict(size=10, color="#22B573"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Expectativa 2026:</b> %{y:.2f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="Expectativa de Crescimento do PIB (%)",
            hovermode="x unified",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.00, xanchor="center", x=0.5
            ),
            margin=dict(t=80),
        )

        # Formatar eixo X para padrão português
        fig.update_xaxes(
            ticktext=[
                f"{MESES_DIC[d.month][:3]}/{str(d.year)[2:]}"
                for d in df_filtrado["data"]
            ],
            tickvals=df_filtrado["data"].tolist(),
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # Inflação (IPCA)
        titulo_centralizado(
            f"Expectativas de Inflação (IPCA) para 2025 e 2026 ({ultimos_dois_anos[0]}-{ultimos_dois_anos[-1]})",
            5,
        )

        # Criar gráfico de linhas
        fig = go.Figure()

        # Linha para 2025 (preto)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["data"],
                y=df_filtrado["expectativa_ipca_25"],
                mode="lines+markers+text",
                name="2025",
                line=dict(color="#000000", width=2),
                marker=dict(size=6),
                text=[
                    f"{val:.1f}%".replace(".", ",")
                    for val in df_filtrado["expectativa_ipca_25"]
                ],
                textposition="top center",
                textfont=dict(size=10, color="#000000"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Expectativa 2025:</b> %{y:.2f}%<extra></extra>",
            )
        )

        # Linha para 2026 (verde)
        fig.add_trace(
            go.Scatter(
                x=df_filtrado["data"],
                y=df_filtrado["expectativa_ipca_26"],
                mode="lines+markers+text",
                name="2026",
                line=dict(color="#22B573", width=2),
                marker=dict(size=6),
                text=[
                    f"{val:.1f}%".replace(".", ",")
                    for val in df_filtrado["expectativa_ipca_26"]
                ],
                textposition="bottom center",
                textfont=dict(size=10, color="#22B573"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Expectativa 2026:</b> %{y:.2f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="Expectativa de Inflação - IPCA (%)",
            hovermode="x unified",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.00, xanchor="center", x=0.5
            ),
            margin=dict(t=80),
        )

        # Formatar eixo X para padrão português
        fig.update_xaxes(
            ticktext=[
                f"{MESES_DIC[d.month][:3]}/{str(d.year)[2:]}"
                for d in df_filtrado["data"]
            ],
            tickvals=df_filtrado["data"].tolist(),
        )

        st.plotly_chart(fig, use_container_width=True)


def display_ipca_geral_analise(df_ipca_geral):
    """
    Renderiza o bloco completo de análise do IPCA - Geral.
    """

    if df_ipca_geral.empty:
        st.info("Não há dados disponíveis para o IPCA - Geral.")
        return

    # Converter colunas para numérico
    df_ipca_geral["ano"] = pd.to_numeric(df_ipca_geral["ano"], errors="coerce")
    df_ipca_geral["mes"] = pd.to_numeric(df_ipca_geral["mes"], errors="coerce")
    df_ipca_geral["ipca_12_meses_geral"] = pd.to_numeric(
        df_ipca_geral["ipca_12_meses_geral"], errors="coerce"
    )
    df_ipca_geral["ipca_mes_geral"] = pd.to_numeric(
        df_ipca_geral["ipca_mes_geral"], errors="coerce"
    )

    # Filtrar dados válidos
    df_ipca_geral = df_ipca_geral.dropna(subset=["ano", "mes"])

    # Criar coluna de data
    df_ipca_geral["data"] = pd.to_datetime(
        df_ipca_geral["ano"].astype(str)
        + "-"
        + df_ipca_geral["mes"].astype(str).str.zfill(2)
        + "-01"
    )

    # Identificar último mês/ano
    ultimo_ano = int(df_ipca_geral["ano"].max())
    ultimo_mes = int(df_ipca_geral[df_ipca_geral["ano"] == ultimo_ano]["mes"].max())

    # Pegar valores mais recentes
    df_ultimo = df_ipca_geral[
        (df_ipca_geral["ano"] == ultimo_ano) & (df_ipca_geral["mes"] == ultimo_mes)
    ]

    if df_ultimo.empty:
        st.warning("Não há dados disponíveis para o período mais recente.")
        return

    ipca_12_meses = df_ultimo["ipca_12_meses_geral"].values[0]
    ipca_mes = df_ultimo["ipca_mes_geral"].values[0]

    # KPIs
    titulo_centralizado("IPCA - Geral (Acumulado 12 meses)", 3)
    titulo_centralizado(
        f"Último dado disponível: {MESES_DIC[ultimo_mes]}/{ultimo_ano}", 6
    )

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric(
        label="IPCA Acumulado 12 Meses",
        value=f"{ipca_12_meses:.2f}%".replace(".", ","),
        help="Inflação acumulada nos últimos 12 meses",
        border=True,
    )
    col2.metric(
        label=f"Variação Mensal em {MESES_DIC[ultimo_mes]}",
        value=f"{ipca_mes:.2f}%".replace(".", ","),
        help="Variação em relação ao mês imediatamente anterior",
        border=True,
    )

    st.divider()

    # Filtrar apenas os últimos 3 anos disponíveis
    todos_anos = sorted(df_ipca_geral["ano"].unique())
    anos_disponiveis = todos_anos[-3:] if len(todos_anos) >= 3 else todos_anos

    col1, col3, col2 = st.columns([0.45, 0.05, 0.5])

    with col1:
        ult_ano = anos_disponiveis[-1]
        if len(anos_disponiveis) >= 2:
            ano_anterior = anos_disponiveis[-2]
            default_range = (ano_anterior, ult_ano)
        else:
            default_range = (ult_ano, ult_ano)

        ANOS_SELECIONADOS = st.select_slider(
            "Selecione o intervalo de anos:",
            options=anos_disponiveis,
            value=default_range,
            key="ipca_geral_12_meses_ano_slider",
        )

    with col2:
        view_mode = st.segmented_control(
            "Selecione a visualização:",
            options=["IPCA 12 Meses", "Variação Mensal"],
            default="IPCA 12 Meses",
            key="ipca_geral_view_mode_radio",
        )

    if view_mode == "IPCA 12 Meses":
        start_year, end_year = ANOS_SELECIONADOS

        # Filtrar dados pelo intervalo de anos
        df_plot = df_ipca_geral[
            (df_ipca_geral["ano"] >= start_year) & (df_ipca_geral["ano"] <= end_year)
        ].copy()
        df_plot = df_plot.sort_values("data")

        # Criar gráfico de linhas
        fig = go.Figure()

        # Linha IPCA 12 meses (preto) com rótulos
        fig.add_trace(
            go.Scatter(
                x=df_plot["data"],
                y=df_plot["ipca_12_meses_geral"],
                mode="lines+markers+text",
                name="IPCA - 12 meses",
                line=dict(color="#000000", width=3),
                marker=dict(size=6, color="#000000"),
                text=[
                    f"{val:.2f}%".replace(".", ",")
                    for val in df_plot["ipca_12_meses_geral"]
                ],
                textposition="top center",
                textfont=dict(size=10, color="#000000"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>IPCA 12 meses:</b> %{y:.2f}%<extra></extra>",
            )
        )

        # Linhas de referência com legendas
        # Tolerância Alta - Vermelho
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Tolerância Alta",
                line=dict(color="#FF0000", width=2, dash="dash"),
                showlegend=True,
            )
        )
        fig.add_hline(
            y=4.5,
            line_dash="dash",
            line_color="#FF0000",
            annotation_text="",
        )

        # Meta - Verde
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Meta",
                line=dict(color="#00AA00", width=2, dash="dash"),
                showlegend=True,
            )
        )
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="#00AA00",
            annotation_text="",
        )

        # Tolerância Baixa - Azul Claro
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Tolerância Baixa",
                line=dict(color="#87CEEB", width=2, dash="dash"),
                showlegend=True,
            )
        )
        fig.add_hline(
            y=1.5,
            line_dash="dash",
            line_color="#87CEEB",
            annotation_text="",
        )

        titulo_centralizado(
            f"IPCA - Geral (Acumulado 12 meses) - {start_year} a {end_year}",
            5,
        )

        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="IPCA Acumulado 12 Meses (%)",
            hovermode="x unified",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            ),
            margin=dict(t=80),
        )

        # Formatar eixo X para padrão português
        fig.update_xaxes(
            ticktext=[
                f"{MESES_DIC[d.month][:3]}/{str(d.year)[2:]}" for d in df_plot["data"]
            ],
            tickvals=df_plot["data"].tolist(),
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # Variação Mensal
        start_year, end_year = ANOS_SELECIONADOS

        # Filtrar dados pelo intervalo de anos
        df_filtrado = df_ipca_geral[
            (df_ipca_geral["ano"] >= start_year) & (df_ipca_geral["ano"] <= end_year)
        ].copy()

        df_filtrado = df_filtrado.sort_values("data")
        df_filtrado = df_filtrado.set_index("data")

        titulo_centralizado(
            f"IPCA - Geral: Variação Mensal de {start_year} a {end_year}",
            5,
        )
        df_plot = df_filtrado[["ipca_mes_geral"]].copy()
        df_plot = df_plot.dropna()  # Remove linhas com valores nulos
        df_plot_formatado = formatar_indice_grafico(df_plot)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y="Variação (%)",
            data_label_format=",.2f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)


def display_taxa_cambio_analise(df_taxa_cambio):
    """
    Renderiza o bloco completo de análise da Taxa de Câmbio.
    """

    if df_taxa_cambio.empty:
        st.info("Não há dados disponíveis para a Taxa de Câmbio.")
        return

    # Converter colunas para numérico
    df_taxa_cambio["ano"] = pd.to_numeric(df_taxa_cambio["ano"], errors="coerce")
    df_taxa_cambio["mes"] = pd.to_numeric(df_taxa_cambio["mes"], errors="coerce")
    df_taxa_cambio["taxa_cambio"] = pd.to_numeric(
        df_taxa_cambio["taxa_cambio"], errors="coerce"
    )
    df_taxa_cambio["media_movel_3"] = pd.to_numeric(
        df_taxa_cambio["media_movel_3"], errors="coerce"
    )
    df_taxa_cambio["taxa_cambio_mensal"] = pd.to_numeric(
        df_taxa_cambio["taxa_cambio_mensal"], errors="coerce"
    )
    df_taxa_cambio["taxa_cambio_mes_anterior"] = pd.to_numeric(
        df_taxa_cambio["taxa_cambio_mes_anterior"], errors="coerce"
    )
    df_taxa_cambio["taxa_cambio_acumulado"] = pd.to_numeric(
        df_taxa_cambio["taxa_cambio_acumulado"], errors="coerce"
    )

    # Filtrar dados válidos
    df_taxa_cambio = df_taxa_cambio.dropna(subset=["ano", "mes"])

    # Criar coluna de data
    df_taxa_cambio["data"] = pd.to_datetime(
        df_taxa_cambio["ano"].astype(str)
        + "-"
        + df_taxa_cambio["mes"].astype(str).str.zfill(2)
        + "-01"
    )

    # Identificar último mês/ano
    ultimo_ano = int(df_taxa_cambio["ano"].max())
    ultimo_mes = int(df_taxa_cambio[df_taxa_cambio["ano"] == ultimo_ano]["mes"].max())

    # Pegar valor mais recente
    df_ultimo = df_taxa_cambio[
        (df_taxa_cambio["ano"] == ultimo_ano) & (df_taxa_cambio["mes"] == ultimo_mes)
    ]

    if df_ultimo.empty:
        st.warning("Não há dados disponíveis para o período mais recente.")
        return

    taxa_cambio_valor = df_ultimo["taxa_cambio"].values[0]

    # KPIs
    titulo_centralizado("Taxa de Câmbio (R$/USD)", 3)
    titulo_centralizado(
        f"Último dado disponível: {MESES_DIC[ultimo_mes]}/{ultimo_ano}", 6
    )

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric(
        label="Taxa de Câmbio",
        value=f"R$ {taxa_cambio_valor:.2f}".replace(".", ","),
        help="Cotação do dólar em reais",
        border=True,
    )
    taxa_mes_anterior = df_ultimo["taxa_cambio_mes_anterior"].values[0]
    col2.metric(
        label="Variação vs. Mês Anterior",
        value=f"{taxa_mes_anterior:.2f}%".replace(".", ","),
        help="Variação da taxa de câmbio em relação ao mês imediatamente anterior",
        border=True,
    )

    st.divider()

    col1, col3, col2 = st.columns([0.35, 0.05, 0.6])

    # Filtrar apenas os últimos 3 anos disponíveis
    todos_anos = sorted(df_taxa_cambio["ano"].unique())
    anos_disponiveis = todos_anos[-3:] if len(todos_anos) >= 3 else todos_anos

    ult_ano = anos_disponiveis[-1]
    if len(anos_disponiveis) >= 2:
        ano_anterior = anos_disponiveis[-2]
        default_range = (ano_anterior, ult_ano)
    else:
        default_range = (ult_ano, ult_ano)

    with col1:
        ANOS_SELECIONADOS = st.select_slider(
            "Selecione o intervalo de anos:",
            options=anos_disponiveis,
            value=default_range,
            key="taxa_cambio_ano_slider",
        )

    with col2:
        view_mode = st.segmented_control(
            "Selecione a visualização:",
            options=[
                "Taxa de Câmbio (R$/USD)",
                "Variação Mensal",
                "Variação Mês Anterior",
                "Acumulado no Ano",
            ],
            default="Taxa de Câmbio (R$/USD)",
            key="taxa_cambio_view_mode_radio",
        )

    start_year, end_year = ANOS_SELECIONADOS

    # Filtrar dados pelo intervalo de anos
    df_plot = df_taxa_cambio[
        (df_taxa_cambio["ano"] >= start_year) & (df_taxa_cambio["ano"] <= end_year)
    ].copy()
    df_plot = df_plot.sort_values("data")

    if view_mode == "Taxa de Câmbio (R$/USD)":
        # Criar gráfico de linhas
        fig = go.Figure()

        # Linha Taxa de Câmbio (preto)
        fig.add_trace(
            go.Scatter(
                x=df_plot["data"],
                y=df_plot["taxa_cambio"],
                mode="lines+markers+text",
                name="Taxa de Câmbio",
                line=dict(color="#000000", width=3),
                marker=dict(size=6, color="#000000"),
                text=[
                    f"R$ {valor:.2f}".replace(".", ",")
                    for valor in df_plot["taxa_cambio"]
                ],
                textposition="top center",
                textfont=dict(size=10, color="#000000"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Taxa:</b> R$ %{y:.2f}<extra></extra>",
            )
        )

        # Linha Média Móvel 3 meses (pontilhada, verde)
        fig.add_trace(
            go.Scatter(
                x=df_plot["data"],
                y=df_plot["media_movel_3"],
                mode="lines+markers",
                name="Média Móvel 3 Meses",
                line=dict(color="#22B573", width=2, dash="dash"),
                marker=dict(size=5, color="#22B573"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Média Móvel:</b> R$ %{y:.2f}<extra></extra>",
            )
        )

        titulo_centralizado(
            f"Taxa de Câmbio (R$/USD) - {start_year} a {end_year}",
            5,
        )

        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="Taxa de Câmbio (R$/USD)",
            hovermode="x unified",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            ),
            margin=dict(t=80),
        )

        # Formatar eixo X para padrão português
        fig.update_xaxes(
            ticktext=[
                f"{MESES_DIC[d.month][:3]}/{str(d.year)[2:]}" for d in df_plot["data"]
            ],
            tickvals=df_plot["data"].tolist(),
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        df_filtrado = df_plot.copy()
        df_filtrado = df_filtrado.set_index("data")

        if view_mode == "Variação Mensal":
            titulo_centralizado(
                f"Taxa de Câmbio: Variação Mensal (vs. mesmo mês do ano anterior) de {start_year} a {end_year}",
                5,
            )
            df_plot = df_filtrado[["taxa_cambio_mensal"]].copy()
            label_y = "Variação (%)"
        elif view_mode == "Variação Mês Anterior":
            titulo_centralizado(
                f"Taxa de Câmbio: Variação em Relação ao Mês Anterior de {start_year} a {end_year}",
                5,
            )
            df_plot = df_filtrado[["taxa_cambio_mes_anterior"]].copy()
            label_y = "Variação (%)"
        else:  # Acumulado no Ano
            titulo_centralizado(
                f"Taxa de Câmbio: Variação Acumulada no Ano de {start_year} a {end_year}",
                5,
            )
            df_plot = df_filtrado[["taxa_cambio_acumulado"]].copy()
            label_y = "Variação Acumulada (%)"

        df_plot = df_plot.dropna()  # Remove linhas com valores nulos
        df_plot_formatado = formatar_indice_grafico(df_plot)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y=label_y,
            data_label_format=",.1f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)


def display_ind_transformacao_analise(df_ind_transformacao):
    """
    Renderiza o bloco completo de análise da Produção Industrial - Indústria de Transformação.
    """

    if df_ind_transformacao.empty:
        st.info("Não há dados disponíveis para a Indústria de Transformação.")
        return

    # Converter colunas para numérico
    df_ind_transformacao["ano"] = pd.to_numeric(
        df_ind_transformacao["ano"], errors="coerce"
    )
    df_ind_transformacao["mes"] = pd.to_numeric(
        df_ind_transformacao["mes"], errors="coerce"
    )
    df_ind_transformacao["taxa_mensal"] = pd.to_numeric(
        df_ind_transformacao["taxa_mensal"], errors="coerce"
    )
    df_ind_transformacao["taxa_acumulado"] = pd.to_numeric(
        df_ind_transformacao["taxa_acumulado"], errors="coerce"
    )

    # Filtrar dados válidos
    df_ind_transformacao = df_ind_transformacao.dropna(subset=["ano", "mes"])

    # Criar coluna de data
    df_ind_transformacao["data"] = pd.to_datetime(
        df_ind_transformacao["ano"].astype(str)
        + "-"
        + df_ind_transformacao["mes"].astype(str).str.zfill(2)
        + "-01"
    )

    # Identificar último mês/ano
    ultimo_ano = int(df_ind_transformacao["ano"].max())
    ultimo_mes = int(
        df_ind_transformacao[df_ind_transformacao["ano"] == ultimo_ano]["mes"].max()
    )

    # Filtrar dados de "Indústrias de transformação" para KPIs
    df_transformacao = df_ind_transformacao[
        df_ind_transformacao["descricao"] == "Indústrias de transformação"
    ].copy()

    # Pegar valores mais recentes
    df_ultimo = df_transformacao[
        (df_transformacao["ano"] == ultimo_ano)
        & (df_transformacao["mes"] == ultimo_mes)
    ]

    if df_ultimo.empty:
        st.warning("Não há dados disponíveis para o período mais recente.")
        return

    taxa_mensal = df_ultimo["taxa_mensal"].values[0]
    taxa_acumulado = df_ultimo["taxa_acumulado"].values[0]

    # KPIs
    titulo_centralizado("Produção Industrial - Indústria de Transformação", 3)
    titulo_centralizado(
        f"Último dado disponível: {MESES_DIC[ultimo_mes]}/{ultimo_ano}", 6
    )

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric(
        label="Variação Mensal (vs. mesmo mês ano anterior)",
        value=f"{taxa_mensal:.2f}%".replace(".", ","),
        help="Variação da produção industrial em relação ao mesmo mês do ano anterior",
        border=True,
    )
    col2.metric(
        label="Variação Acumulada no Ano",
        value=f"{taxa_acumulado:.2f}%".replace(".", ","),
        help="Variação acumulada da produção industrial no ano",
        border=True,
    )

    st.divider()

    # Filtrar apenas os últimos 3 anos disponíveis
    todos_anos = sorted(df_ind_transformacao["ano"].unique())
    anos_disponiveis = todos_anos[-3:] if len(todos_anos) >= 3 else todos_anos

    col1, col3, col2 = st.columns([0.45, 0.05, 0.5])

    with col2:
        view_mode = st.segmented_control(
            "Selecione a visualização:",
            options=["Evolução Mensal", "Acumulado no Ano", "Por Categoria"],
            default="Evolução Mensal",
            key="ind_transformacao_view_mode_radio",
        )

    # Seletor de anos - sempre usar selectbox para evitar rerender
    with col1:
        ano_selecionado = st.selectbox(
            "Selecione o ano:",
            options=anos_disponiveis,
            index=len(anos_disponiveis) - 1,
            key="ind_transformacao_ano_select",
        )

    if view_mode in ["Evolução Mensal", "Acumulado no Ano"]:
        # Filtrar apenas "Indústrias de transformação" pelo ano selecionado
        df_plot = df_transformacao[df_transformacao["ano"] == ano_selecionado].copy()
        df_plot = df_plot.sort_values("data")
        df_plot = df_plot.set_index("data")

        if view_mode == "Evolução Mensal":
            titulo_centralizado(
                f"Produção Industrial: Variação Mensal (vs. mesmo mês ano anterior) - {ano_selecionado}",
                5,
            )
            df_plot_final = df_plot[["taxa_mensal"]].copy()
            label_y = "Variação (%)"
        else:  # Acumulado no Ano
            titulo_centralizado(
                f"Produção Industrial: Variação Acumulada no Ano - {ano_selecionado}",
                5,
            )
            df_plot_final = df_plot[["taxa_acumulado"]].copy()
            label_y = "Variação Acumulada (%)"

        df_plot_final = df_plot_final.dropna()
        df_plot_formatado = formatar_indice_grafico(df_plot_final)
        fig = criar_grafico_barras(
            df=df_plot_formatado,
            titulo="",
            label_y=label_y,
            data_label_format=",.1f",
            hover_label_format=",.2f",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Por Categoria
        # Filtrar dados pelo ano selecionado
        df_filtrado = df_ind_transformacao[
            df_ind_transformacao["ano"] == ano_selecionado
        ].copy()

        # Pegar o último mês disponível no ano selecionado
        ultimo_mes_ano = int(df_filtrado["mes"].max())

        # Filtrar apenas o último mês
        df_ultimo_mes = df_filtrado[df_filtrado["mes"] == ultimo_mes_ano].copy()

        # Montar string de período acumulado (Jan-Mes/Ano)
        mes_inicio = "Jan"
        mes_fim_abrev = MESES_DIC[ultimo_mes_ano][:3]  # Primeiras 3 letras
        periodo_acumulado = f"{mes_inicio}-{mes_fim_abrev}/{str(ano_selecionado)[-2:]}"

        # Montar string do mês de variação mensal (Mes/Ano)
        periodo_mensal = f"{mes_fim_abrev}/{str(ano_selecionado)[-2:]}"

        titulo_centralizado(
            f"Produção Industrial por Categoria - {MESES_DIC[ultimo_mes_ano]}/{ano_selecionado}",
            5,
        )

        # Criar tabela com Categoria, Variação Mensal e Acumulado no Ano
        df_tabela = df_ultimo_mes[["descricao", "taxa_mensal", "taxa_acumulado"]].copy()
        df_tabela = df_tabela.rename(
            columns={
                "descricao": "Categoria",
                "taxa_mensal": f"Variação Mensal em {periodo_mensal} (%)",
                "taxa_acumulado": f"Acumulado de {periodo_acumulado} (%)",
            }
        )
        df_tabela = df_tabela.set_index("Categoria")

        # Aplicar estilo
        styled_df = df_tabela.style.applymap(style_saldo_variacao).format(
            lambda x: formatar_pct_br(x) if pd.notna(x) else "-"
        )

        st.dataframe(styled_df, use_container_width=True, height=500)


def display_taxa_desemprego_analise(df_taxa_desemprego):
    """
    Renderiza o bloco completo de análise da Taxa de Desemprego no Trimestre.
    """

    if df_taxa_desemprego.empty:
        st.info("Não há dados disponíveis para a Taxa de Desemprego.")
        return

    # Converter colunas para numérico
    df_taxa_desemprego["ano"] = pd.to_numeric(
        df_taxa_desemprego["ano"], errors="coerce"
    )
    df_taxa_desemprego["mes"] = pd.to_numeric(
        df_taxa_desemprego["mes"], errors="coerce"
    )
    df_taxa_desemprego["taxa_desemprego"] = pd.to_numeric(
        df_taxa_desemprego["taxa_desemprego"], errors="coerce"
    )

    # Filtrar dados válidos
    df_taxa_desemprego = df_taxa_desemprego.dropna(
        subset=["ano", "mes", "trimestre_movel"]
    )

    # Pegar os últimos 3 anos disponíveis
    anos_disponiveis = sorted(df_taxa_desemprego["ano"].unique())
    if len(anos_disponiveis) >= 3:
        anos_ultimos_3 = anos_disponiveis[-3:]
    else:
        anos_ultimos_3 = anos_disponiveis

    df_filtrado = df_taxa_desemprego[
        df_taxa_desemprego["ano"].isin(anos_ultimos_3)
    ].copy()

    # Ordenar por ano e mês
    df_filtrado = df_filtrado.sort_values(["ano", "mes"])

    # Filtrar apenas os meses que representam o fim de cada trimestre móvel
    # Trimestres móveis não se sobrepõem: Jan-Fev-Mar (mes=3), Abr-Mai-Jun (mes=6), Jul-Ago-Set (mes=9), Out-Nov-Dez (mes=12)
    # Manter apenas os meses finais de cada trimestre
    df_filtrado = df_filtrado[df_filtrado["mes"].isin([3, 6, 9, 12])].copy()

    # Identificar último trimestre/ano
    ultimo_ano = int(df_filtrado["ano"].max())
    ultimo_mes = int(df_filtrado[df_filtrado["ano"] == ultimo_ano]["mes"].max())
    ultimo_trimestre = df_filtrado[
        (df_filtrado["ano"] == ultimo_ano) & (df_filtrado["mes"] == ultimo_mes)
    ]["trimestre_movel"].iloc[0]

    # KPI
    titulo_centralizado("Taxa de Desemprego no Trimestre Móvel", 3)
    titulo_centralizado(f"Último trimestre disponível: {ultimo_trimestre}", 6)

    # Seletor de visualização
    view_mode = st.segmented_control(
        "Selecione a visualização:",
        options=["Taxa de Desemprego no Trimestre", "Por Categoria"],
        default="Taxa de Desemprego no Trimestre",
        key="taxa_desemprego_view_mode",
    )

    if view_mode == "Taxa de Desemprego no Trimestre":
        # Gráfico de barras
        titulo_centralizado(
            f"Taxa de Desemprego no Trimestre - Últimos 3 Anos ({anos_ultimos_3[0]}-{anos_ultimos_3[-1]})",
            5,
        )

        fig = go.Figure()

        # Formatar valores com vírgula como separador decimal
        valores_formatados = [
            f"{val:.2f}%".replace(".", ",") for val in df_filtrado["taxa_desemprego"]
        ]

        fig.add_trace(
            go.Bar(
                x=df_filtrado["trimestre_movel"],
                y=df_filtrado["taxa_desemprego"],
                text=valores_formatados,
                textposition="outside",
                textfont=dict(size=10),
                marker=dict(color="#000000"),
                name="Taxa de Desemprego",
            )
        )

        fig.update_layout(
            xaxis_title="Trimestre Móvel",
            yaxis_title="Taxa de Desemprego (%)",
            hovermode="x unified",
            showlegend=False,
            height=500,
            xaxis=dict(
                tickangle=-45,
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # Por Categoria
        titulo_centralizado(
            f"Dados por Categoria da Força de Trabalho - Últimos 3 Anos ({anos_ultimos_3[0]}-{anos_ultimos_3[-1]})",
            5,
        )

        # Preparar tabela com os últimos 3 anos
        df_tabela = df_filtrado[
            [
                "ano",
                "mes",
                "trimestre_movel",
                "forca_trabalho_ocupada",
                "forca_trabalho_desocupada",
                "fora_forca_trabalho",
                "total",
                "taxa_desemprego",
            ]
        ].copy()

        # Ordenar por ano e mês (descendente) para mostrar da data mais recente para trás
        df_tabela = df_tabela.sort_values(["ano", "mes"], ascending=False)

        # Remover colunas auxiliares ano e mes antes de exibir
        df_tabela = df_tabela.drop(columns=["ano", "mes"])

        # Renomear colunas
        df_tabela = df_tabela.rename(
            columns={
                "trimestre_movel": "Trimestre",
                "forca_trabalho_ocupada": "Força de Trabalho - Ocupada",
                "forca_trabalho_desocupada": "Força de Trabalho - Desocupada",
                "fora_forca_trabalho": "Fora da Força de Trabalho",
                "total": "Total",
                "taxa_desemprego": "Taxa de Desemprego",
            }
        )

        df_tabela = df_tabela.set_index("Trimestre")

        # Formatar apenas a coluna Taxa de Desemprego como percentual
        def formatar_coluna(val, col_name):
            if pd.isna(val):
                return "-"
            if col_name == "Taxa de Desemprego":
                return f"{val:.1f}%".replace(".", ",")
            else:
                # Formatar números grandes com separador de milhares
                return f"{int(val):,}".replace(",", ".")

        # Aplicar formatação
        styled_df = df_tabela.style.format(
            {col: lambda x, c=col: formatar_coluna(x, c) for col in df_tabela.columns}
        )

        st.dataframe(styled_df, use_container_width=True, height=400)


def show_page_macroeconomia(
    df_ibc_br,
    df_expectativas,
    df_ipca_geral,
    df_taxa_cambio,
    df_ind_transformacao,
    df_taxa_desemprego,
):
    """Função principal que renderiza a página de Macroeconomia."""

    titulo_centralizado("Dashboard de Macroeconomia", 1)
    st.info("Clique nos menus abaixo para explorar os indicadores macroeconômicos.")

    with st.expander(
        "IBC-Br (Índice de Atividade Econômica do Banco Central)",
        expanded=False,
    ):
        display_ibc_br_analise(
            df_ibc_br=df_ibc_br,
        )

    with st.expander(
        "Expectativas de Mercado (PIB e Inflação)",
        expanded=False,
    ):
        display_expectativas_analise(
            df_expectativas=df_expectativas,
        )

    with st.expander(
        "IPCA - Geral",
        expanded=False,
    ):
        display_ipca_geral_analise(
            df_ipca_geral=df_ipca_geral,
        )

    with st.expander(
        "Taxa de Câmbio (R$/USD)",
        expanded=False,
    ):
        display_taxa_cambio_analise(
            df_taxa_cambio=df_taxa_cambio,
        )

    with st.expander(
        "Produção Industrial - Indústria de Transformação",
        expanded=False,
    ):
        display_ind_transformacao_analise(
            df_ind_transformacao=df_ind_transformacao,
        )

    with st.expander(
        "Taxa de Desemprego no Trimestre",
        expanded=False,
    ):
        display_taxa_desemprego_analise(
            df_taxa_desemprego=df_taxa_desemprego,
        )
