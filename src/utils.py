import plotly_express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import io

# =============================================================================
# CONSTANTES E DICIONÁRIOS
# =============================================================================

MESES_DIC = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def manter_posicao_scroll():
    """
    Esta função injeta JavaScript para salvar a posição do scroll no sessionStorage
    do navegador e restaurá-la após a re-execução do script pelo Streamlit.
    """
    # O JavaScript para salvar e restaurar a posição do scroll.
    # A função debounce evita que o evento de scroll seja disparado muitas vezes,
    # o que poderia causar problemas de performance.
    js_code = """
    <script>
        const scrollKey = "streamlit-scroll-position";

        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        const saveScrollPosition = debounce(() => {
            sessionStorage.setItem(scrollKey, window.scrollY);
        }, 100);

        window.addEventListener("scroll", saveScrollPosition);

        window.addEventListener("DOMContentLoaded", () => {
            const scrollY = sessionStorage.getItem(scrollKey);
            if (scrollY) {
                window.scrollTo(0, parseInt(scrollY, 10));
            }
        });
    </script>
    """
    # Usa st.components.v1.html para injetar o script na página
    st.components.v1.html(js_code, height=0)


# -- FUNCOES DE VISUALIZACAO ---
def carregar_css(caminho_arquivo):
    """
    Lê um arquivo CSS e o injeta na aplicação Streamlit.
    """
    with open(caminho_arquivo, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def to_excel(df: pd.DataFrame) -> bytes:
    """
    Converte um DataFrame do Pandas para um arquivo Excel em memória (bytes).

    Args:
        df (pd.DataFrame): O DataFrame a ser convertido.

    Returns:
        bytes: Os dados do arquivo Excel em bytes.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")

    # Pega o valor dos bytes do buffer de memória
    processed_data = output.getvalue()
    return processed_data


def titulo_centralizado(texto: str, level: int, cor: str = None):
    """
    Cria um título Markdown centralizado com um nível de heading específico (h1, h2, ...).

    Args:
        texto (str): O texto do título.
        level (int): O nível do heading (1 para <h1>, 2 para <h2>, etc.).
        cor (str, optional): A cor do texto (ex: 'gray', '#FF4B4B'). Defaults to None.
    """
    style = "text-align: center;"
    if cor:
        style += f" color: {cor};"

    st.markdown(f"<h{level} style='{style}'>{texto}</h{level}>", unsafe_allow_html=True)


def criar_grafico_barras(
    df,
    titulo,
    label_y,
    barmode="group",
    height=400,
    data_label_format=",.2f",
    hover_label_format=",.2f",
    color_map=None,
    color_sequence=None,
    showlegend=False,
):
    """
    Cria um gráfico de barras customizado e reutilizável com Plotly Express.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" - ".join(map(str, col)).strip() for col in df.columns.values]

    index_name = df.index.name if df.index.name is not None else "index"
    df_reset = df.reset_index()
    index_name = df_reset.columns[0]

    df_long = df_reset.melt(id_vars=index_name, var_name="series", value_name="value")

    df_long["hover_value_formatted"] = df_long["value"].apply(
        lambda x: f"{x:{hover_label_format}}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    df_long["data_label_formatted"] = df_long["value"].apply(
        lambda x: f"{x:{data_label_format}}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    color_seq = color_sequence if color_sequence is not None else ["#000000"]

    fig = px.bar(
        df_long,
        x=index_name,
        y="value",
        color="series",
        labels={"value": label_y, index_name: "", "series": ""},
        barmode=barmode,
        height=height,
        custom_data=["hover_value_formatted", "data_label_formatted"],
        color_discrete_map=color_map,
        color_discrete_sequence=color_seq,
    )

    xaxis_config = {}
    if pd.api.types.is_numeric_dtype(df.index):
        xaxis_config = dict(tickmode="linear", dtick=1)

    # If legend will be shown, place it horizontally at the top center and
    # increase the top margin to avoid overlap with the title.
    legend_layout = dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
    )

    fig.update_layout(
        margin=dict(t=80 if showlegend else 50),
        title_text=titulo,
        title_font_size=20,
        xaxis_title="",
        xaxis=xaxis_config,
        showlegend=showlegend,
        legend=legend_layout,
    )

    fig.update_traces(
        texttemplate="%{customdata[1]}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            f"<b>{index_name.title()}</b>: %{{x}}<br>"
            "<b>Valor</b>: %{customdata[0]}"
            "<extra></extra>"
        ),
    )

    return fig


@st.cache_data
def calcular_yoy(df, tipo, ultimo_mes, ultimo_ano, coluna, round):
    """
    Calcula a variação ano-a-ano (YoY) para um indicador específico.
    'tipo' pode ser "mensal" ou "acumulado".
    """
    df_filtrado = None

    if tipo == "mensal":
        df_filtrado = df[df["mes"] == ultimo_mes].groupby("ano")[coluna].sum()

    elif tipo == "acumulado":
        df_filtrado = df[df["mes"] <= ultimo_mes].groupby("ano")[coluna].sum()

    else:
        return None

    df_filtrado = df_filtrado.to_frame(name=coluna).sort_index()

    # Cria a coluna "ano_anterior" usando shift()
    df_filtrado[f"{coluna}_ano_anterior"] = df_filtrado[f"{coluna}"].shift(1)

    if ultimo_ano not in df_filtrado.index:
        return None

    dados_recentes = df_filtrado.loc[ultimo_ano]
    valor_atual = dados_recentes[coluna]
    valor_anterior = dados_recentes[f"{coluna}_ano_anterior"]

    # Calcula a variação percentual
    if pd.notna(valor_anterior) and valor_anterior > 0:
        variacao = ((valor_atual / valor_anterior) - 1) * 100
        return variacao.round(round)

    return None


def formatar_delta(valor_yoy):
    """Função auxiliar para formatar o delta para st.metric."""
    if valor_yoy is None:
        return None

    return f"{valor_yoy:,.1f}%".replace(".", ",")


# =============================================================================
# FUNÇÕES DE FORMATAÇÃO PARA TABELAS
# =============================================================================


def formatar_valor_br(x):
    """Formata número float para padrão BR (1.000.000) sem decimais para valores altos."""
    if pd.isna(x):
        return "-"
    return f"{x:,.0f}".replace(",", ".")


def formatar_pct_br(x):
    """Formata número float para percentual BR (+1.234,5%) com 1 casa decimal."""
    if pd.isna(x):
        return "-"
    # Formata como +1,234.5% e depois inverte pontuação
    return f"{x:+,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def style_saldo_variacao(val):
    """
    Aplica formatação condicional (background color) para valores numéricos.
    Pode ser usado tanto para Saldo (inteiros) quanto Variação (percentuais).

    Regra:
    - Valor > 0: Fundo Verde Claro (#c8e6c9), Texto Verde Escuro (#1b5e20)
    - Valor < 0: Fundo Vermelho Claro (#ffcdd2), Texto Vermelho Escuro (#b71c1c)
    - Zero/NaN : Sem formatação
    """
    if pd.isna(val):
        return ""
    if val > 0:
        return "background-color: #c8e6c9; color: #1b5e20"
    elif val < 0:
        return "background-color: #ffcdd2; color: #b71c1c"
    return ""


def criar_grafico_barras_linha_comex(
    df_plot, coluna_y_principal, titulo_coluna_y, tipo_coluna
):
    """
    Cria um gráfico de combo (Barras + Linha) com eixo Y secundário.
    """
    cor_barras = "#000a11"
    cor_linha = "#22B573"

    # Mapeamento manual para garantir abreviações em PT-BR
    meses_abrev = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez",
    }

    x_labels = [f"{meses_abrev[d.month]}/{str(d.year)[2:]}" for d in df_plot["date"]]

    # Cria a figura com eixo Y secundário
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras (Eixo Primário)
    fig.add_trace(
        go.Bar(
            x=x_labels,  # Usamos a lista formatada
            y=df_plot[coluna_y_principal],
            name=titulo_coluna_y,
            marker_color=cor_barras,
            text=df_plot["valor_label"],
            texttemplate="%{text} M",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"<b>{tipo_coluna}</b>: %{{y:,.1f}} M<extra></extra>",
            textfont=dict(color=cor_barras),
        ),
        secondary_y=False,
    )

    # Linha (Eixo Secundário)
    fig.add_trace(
        go.Scatter(
            x=x_labels,  # Usamos a lista formatada
            y=df_plot["yoy"],
            name="Var. Ano a Ano (%)",
            line=dict(color=cor_linha, width=3),
            marker=dict(color=cor_linha, size=8),
            mode="lines+markers",
            hovertemplate="<b>Var. Ano a Ano</b>: %{y:,.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    # Annotations Manuais
    for label_data, (i, row) in zip(x_labels, df_plot.iterrows()):
        fig.add_annotation(
            x=label_data,  # Usa a string formatada como coordenada X
            y=row["yoy"],
            text=f"<span style='color: {cor_linha}'><b>{row['yoy_label']}%</b></span>",
            showarrow=False,
            yshift=12,
            xref="x",
            yref="y2",
            xanchor="center",
            yanchor="bottom",
            font=dict(size=11),
        )

    # Configurações dos Eixos
    fig.update_xaxes(
        title_text="",
        showgrid=False,
    )

    # Eixo Y Primário (Barras)
    fig.update_yaxes(
        title_text=titulo_coluna_y,
        secondary_y=False,
        ticksuffix=" M",
        title_font_color=cor_barras,
        tickfont=dict(color=cor_barras),
        rangemode="tozero",
        showgrid=True,
    )

    # Eixo Y Secundário (Linha)
    fig.update_yaxes(
        title_text="Var. Ano a Ano (%)",
        secondary_y=True,
        ticksuffix="%",
        title_font_color=cor_linha,
        tickfont=dict(color=cor_linha),
        showgrid=False,
        zeroline=False,
    )

    # Layout Final - criar_grafico_barras_linha_comex
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.1),
        hovermode="x unified",
        margin=dict(t=60, l=10, r=10, b=10),
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def criar_grafico_barras_linha_comex_acum(df_plot, titulo_coluna_y, tipo_coluna):
    """
    Cria um gráfico de combo (Barras + Linha) com eixo Y secundário para dados acumulados comparativos.
    Recebe um DataFrame com colunas: x_label, valor, yoy, valor_label, yoy_label
    """
    cor_barras = "#000a11"
    cor_linha = "#22B573"

    x_labels = df_plot["x_label"].tolist()

    # Cria a figura com eixo Y secundário
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras (Eixo Primário)
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=df_plot["valor"],
            name=titulo_coluna_y,
            marker_color=cor_barras,
            text=df_plot["valor_label"],
            texttemplate="%{text} M",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"<b>{tipo_coluna}</b>: %{{y:,.1f}} M<extra></extra>",
            textfont=dict(color=cor_barras),
        ),
        secondary_y=False,
    )

    # Linha (Eixo Secundário)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=df_plot["yoy"],
            name="Var. Ano a Ano (%)",
            line=dict(color=cor_linha, width=3),
            marker=dict(color=cor_linha, size=8),
            mode="lines+markers",
            hovertemplate="<b>Var. Ano a Ano</b>: %{y:,.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    # Annotations Manuais para os valores de YoY
    for i, row in df_plot.iterrows():
        if pd.notna(row["yoy"]):
            fig.add_annotation(
                x=row["x_label"],
                y=row["yoy"],
                text=f"<span style='color: {cor_linha}'><b>{row['yoy_label']}%</b></span>",
                showarrow=False,
                yshift=12,
                xref="x",
                yref="y2",
                xanchor="center",
                yanchor="bottom",
                font=dict(size=11),
            )

    # Configurações dos Eixos
    fig.update_xaxes(
        title_text="",
        showgrid=False,
    )

    # Eixo Y Primário (Barras)
    fig.update_yaxes(
        title_text=titulo_coluna_y,
        secondary_y=False,
        ticksuffix=" M",
        title_font_color=cor_barras,
        tickfont=dict(color=cor_barras),
        rangemode="tozero",
        showgrid=True,
    )

    # Eixo Y Secundário (Linha)
    fig.update_yaxes(
        title_text="Var. Ano a Ano (%)",
        secondary_y=True,
        ticksuffix="%",
        title_font_color=cor_linha,
        tickfont=dict(color=cor_linha),
        showgrid=False,
        zeroline=False,
    )

    # Layout Final - criar_grafico_barras_linha_comex_acum
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.1),
        hovermode="x unified",
        margin=dict(t=60, l=10, r=10, b=10),
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# =============================================================================
# FUNÇÕES DE PREPARAÇÃO DE DADOS - REUTILIZÁVEIS
# =============================================================================


@st.cache_data
def preparar_dados_comex_grafico(df, coluna):
    """
    Prepara os dados de comex, agregando por data e calculando o YoY.
    Reutilizável para qualquer setor (calçados, couros, etc.).
    """
    df_agg = df.groupby(["ano", "mes"])[coluna].sum().reset_index()

    df_agg["date"] = pd.to_datetime(
        df_agg[["ano", "mes"]]
        .assign(day=1)
        .rename(columns={"ano": "year", "mes": "month"})
    )
    df_agg = df_agg.set_index("date").sort_index()

    df_agg["yoy"] = df_agg[coluna].pct_change(12) * 100
    df_agg[coluna] = df_agg[coluna] / 1000000

    df_agg["valor_label"] = df_agg[coluna].apply(lambda x: f"{x:.1f}".replace(".", ","))
    df_agg["yoy_label"] = df_agg["yoy"].apply(lambda x: f"{x:.1f}".replace(".", ","))

    df_agg = df_agg.iloc[12:].reset_index()

    return df_agg


@st.cache_data
def preparar_dados_comex_acu_comparativo(df, coluna, ult_mes):
    """
    Prepara os dados de comex acumulados para comparação entre anos.
    Retorna um DataFrame com o acumulado até o mês atual para cada ano,
    incluindo a variação YoY.
    Reutilizável para qualquer setor (calçados, couros, etc.).
    """
    df = df.copy()

    # Filtra apenas meses até o último mês disponível
    df_filtrado = df[df["mes"] <= ult_mes]

    # Agrupa por ano e soma o valor da coluna
    df_acum = df_filtrado.groupby("ano")[coluna].sum().reset_index()
    df_acum.columns = ["ano", "valor"]

    # Calcula YoY
    df_acum["valor_anterior"] = df_acum["valor"].shift(1)
    df_acum["yoy"] = (df_acum["valor"] / df_acum["valor_anterior"] - 1) * 100

    # Converte para milhões
    df_acum["valor"] = df_acum["valor"] / 1_000_000

    # Formata labels
    df_acum["valor_label"] = df_acum["valor"].apply(
        lambda x: f"{x:.1f}".replace(".", ",")
    )
    df_acum["yoy_label"] = df_acum["yoy"].apply(
        lambda x: f"{x:.1f}".replace(".", ",") if pd.notna(x) else ""
    )

    # Cria o índice no formato "Jan-Mês/Ano"
    df_acum["x_label"] = (
        "Jan-" + MESES_DIC[ult_mes][:3] + "/" + df_acum["ano"].astype(str).str.slice(-2)
    )

    # Remove o primeiro ano (sem YoY)
    df_acum = df_acum.iloc[1:].reset_index(drop=True)

    return df_acum


@st.cache_data
def preparar_dados_graficos_prod_vendas(df, coluna):
    """
    Prepara dados de produção/vendas para gráficos.
    Reutilizável para qualquer setor.
    """
    df_hist = (
        df.assign(
            date=pd.to_datetime(
                df[["ano", "mes"]]
                .assign(day=1)
                .rename(columns={"ano": "year", "mes": "month"})
            )
        )
        .pivot_table(
            index="date",
            values=coluna,
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    return df_hist


@st.cache_data
def preparar_dados_emprego_grafico(df_emprego, coluna_grupo="subclasse"):
    """
    Prepara dados de emprego para gráficos.
    Reutilizável para qualquer setor.

    Args:
        df_emprego: DataFrame com dados de emprego
        coluna_grupo: Nome da coluna para agrupar (ex: 'subclasse' para calçados)
    """
    if df_emprego.empty:
        return None, None, None, None

    # Histórico Mensal Total
    df_hist_total = (
        df_emprego.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    # Histórico Mensal por Grupo
    df_hist_grupo = (
        df_emprego.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            columns=coluna_grupo,
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    ult_ano = df_emprego["ano"].max()
    ult_mes = df_emprego[df_emprego["ano"] == ult_ano]["mes"].max()

    # Acumulado Anual Total
    df_acum_total = (
        df_emprego[df_emprego["mes"] <= ult_mes]
        .pivot_table(
            index="ano",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    df_acum_total.index = (
        "Jan-"
        + MESES_DIC[ult_mes][:3]
        + "/"
        + df_acum_total.index.astype(str).str.slice(-2)
    )

    # Acumulado Anual por Grupo
    df_acum_grupo = (
        df_emprego[df_emprego["mes"] <= ult_mes]
        .pivot_table(
            index="ano",
            columns=coluna_grupo,
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    df_acum_grupo.index = (
        "Jan-"
        + MESES_DIC[ult_mes][:3]
        + "/"
        + df_acum_grupo.index.astype(str).str.slice(-2)
    )

    return df_hist_total, df_hist_grupo, df_acum_total, df_acum_grupo


@st.cache_data
def preparar_dados_ipca_grafico(df_ipca):
    """
    Prepara dados de IPCA para gráficos.
    Reutilizável para qualquer setor.
    """
    if df_ipca.empty:
        return None, None

    df_mes = (
        df_ipca.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            values="ipca_mes",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    df_12_meses = (
        df_ipca.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            values="ipca_12_meses",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    return df_mes, df_12_meses


@st.cache_data
def formatar_indice_grafico(df_filtrado):
    """
    Formata o índice do DataFrame para exibição no gráfico (ex: Jan/25).
    Reutilizável para qualquer setor.
    """
    if df_filtrado.empty:
        return df_filtrado

    df_plot = df_filtrado.copy()
    df_plot.index = [
        f"{MESES_DIC[date.month][:3]}/{str(date.year)[2:]}" for date in df_plot.index
    ]
    return df_plot


# =============================================================================
# FUNÇÕES DE DISPLAY DE KPIs - REUTILIZÁVEIS
# =============================================================================


def display_prod_vendas_kpi_cards(df, titulo_kpi, categoria_kpi, filtro):
    """
    Exibe os cards de KPI de Produção e Vendas.
    Reutilizável para qualquer setor.
    """
    titulo_centralizado(titulo_kpi, 3)
    with st.container(border=False):
        df = df.copy()
        df = df[df["grupo"] == filtro]
        ult_ano = df["ano"].max()
        ult_mes = df[df["ano"] == ult_ano]["mes"].max()

        df_ult = df[(df["ano"] == ult_ano) & (df["mes"] == ult_mes)]
        valor_ult_mes = df_ult["taxa_mensal"].sum()
        valor_acu_ano = df_ult["taxa_acumulado"].sum()

        col1, col2 = st.columns(2)
        col1.metric(
            label=f"{categoria_kpi} em {MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{valor_ult_mes:,.1f}%".replace(".", ","),
            help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
            border=True,
        )
        col2.metric(
            label=f"{categoria_kpi} no Acumulado Jan - {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{valor_acu_ano:,.1f}%".replace(".", ","),
            help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
            border=True,
        )


def display_comex_kpi_cards(df, titulo_kpi, categoria_kpi, coluna):
    """
    Exibe os cards de KPI de Comércio Exterior.
    Reutilizável para qualquer setor.
    """
    titulo_centralizado(titulo_kpi, 3)
    with st.container(border=False):
        df = df.copy()
        ult_ano = df["ano"].max()
        ult_mes = df[df["ano"] == ult_ano]["mes"].max()

        df_ult_mes = df[(df["ano"] == ult_ano) & (df["mes"] == ult_mes)]
        df_acumulado = df[(df["ano"] == ult_ano) & (df["mes"] <= ult_mes)]

        divisor = 1000000
        valor_ult_mes = df_ult_mes[coluna].sum() / divisor
        valor_acu_ano = df_acumulado[coluna].sum() / divisor

        yoy_mensal = calcular_yoy(
            df=df,
            tipo="mensal",
            ultimo_mes=ult_mes,
            ultimo_ano=ult_ano,
            coluna=coluna,
            round=1,
        )
        yoy_acumulado = calcular_yoy(
            df=df,
            tipo="acumulado",
            ultimo_mes=ult_mes,
            ultimo_ano=ult_ano,
            coluna=coluna,
            round=1,
        )

        delta_mensal = formatar_delta(yoy_mensal)
        delta_acumulado = formatar_delta(yoy_acumulado)

        sufixo_metrica = " Milhões" if coluna == "valor" else " Milhões de Pares"

        # Formatação BR: ponto como separador de milhar, vírgula como decimal
        valor_ult_mes_fmt = (
            f"{valor_ult_mes:,.1f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        valor_acu_ano_fmt = (
            f"{valor_acu_ano:,.1f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        col1, col2 = st.columns(2)
        col1.metric(
            label=f"{categoria_kpi} em {MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{valor_ult_mes_fmt}{sufixo_metrica}",
            delta=delta_mensal,
            help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
            border=True,
        )
        col2.metric(
            label=f"{categoria_kpi} no Acumulado Jan - {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{valor_acu_ano_fmt}{sufixo_metrica}",
            delta=delta_acumulado,
            help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
            border=True,
        )


def display_emprego_kpi_cards(df, titulo_kpi="Emprego"):
    """
    Exibe os cards de KPI de Emprego.
    Reutilizável para qualquer setor.
    """
    titulo_centralizado(titulo_kpi, 3)
    with st.container(border=False):
        df = df.copy()
        ult_ano = df["ano"].max()
        ult_mes = df[df["ano"] == ult_ano]["mes"].max()

        df_ult = df[(df["ano"] == ult_ano) & (df["mes"] == ult_mes)]
        saldo_ult_mes = df_ult["saldo_movimentacao"].sum()

        df_acumulado = df[(df["ano"] == ult_ano) & (df["mes"] <= ult_mes)]
        saldo_acu_ano = df_acumulado["saldo_movimentacao"].sum()

        col1, col2 = st.columns(2)
        col1.metric(
            label=f"Saldo de Emprego em {MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{saldo_ult_mes:,.0f}".replace(",", "."),
            border=True,
        )
        col2.metric(
            label=f"Saldo de Emprego no Acumulado Jan - {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{saldo_acu_ano:,.0f}".replace(",", "."),
            border=True,
        )


def display_ipca_kpi_cards(df, titulo_kpi="IPCA"):
    """
    Exibe os cards de KPI do IPCA.
    Reutilizável para qualquer setor.
    """
    titulo_centralizado(titulo_kpi, 3)
    with st.container(border=False):
        df = df.copy()
        ult_ano = df["ano"].max()
        ult_mes = df[df["ano"] == ult_ano]["mes"].max()

        df_ult = df[(df["ano"] == ult_ano) & (df["mes"] == ult_mes)]
        ipca_mes = df_ult["ipca_mes"].sum()
        ipca_12_meses = df_ult["ipca_12_meses"].sum()

        col1, col2 = st.columns(2)
        col1.metric(
            label=f"Inflação Mensal em {MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{ipca_mes:,.2f}%".replace(".", ","),
            border=True,
        )
        col2.metric(
            label=f"Inflação Acumulada em 12 Meses até {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{ipca_12_meses:,.2f}%".replace(".", ","),
            border=True,
        )


# =============================================================================
# FUNÇÕES DE DISPLAY DE GRÁFICOS - REUTILIZÁVEIS
# =============================================================================


def display_graficos_prod_vendas(
    df,
    titulo_expander,
    titulo_kpi,
    categoria_kpi,
    filtro_kpi,
    state_key_prefix,
    usar_expander=True,
    df_previsao=None,
):
    """
    Função auxiliar que renderiza um bloco de análise completo (KPI, Gráficos).
    Usa session_state para manter o expander aberto após interação.
    Reutilizável para qualquer setor.

    Args:
        usar_expander: Se True, envolve o conteúdo em um expander. Se False, exibe diretamente.
        df_previsao: DataFrame opcional com dados de previsão (colunas: ano, mes, variacao_verificada, prev_otimista, prev_pessimista)
    """
    expander_state_key = f"{state_key_prefix}_expander_state"
    select_key = f"{state_key_prefix}_ano"
    radio_key = f"{state_key_prefix}_view"

    if expander_state_key not in st.session_state:
        st.session_state[expander_state_key] = False

    def set_expander_open():
        st.session_state[expander_state_key] = True

    def render_content():
        display_prod_vendas_kpi_cards(
            df=df, titulo_kpi=titulo_kpi, categoria_kpi=categoria_kpi, filtro=filtro_kpi
        )

        df_hist_mensal = preparar_dados_graficos_prod_vendas(df, "taxa_mensal")
        df_hist_acumulado = preparar_dados_graficos_prod_vendas(df, "taxa_acumulado")

        anos_disponiveis = sorted(df["ano"].unique().tolist())

        ult_ano = anos_disponiveis[-1]
        if len(anos_disponiveis) >= 2:
            ano_anterior = anos_disponiveis[-2]
            default_range = (ano_anterior, ult_ano)
        else:
            default_range = (ult_ano, ult_ano)

        # Definir opções do pills baseado na disponibilidade de previsão
        opcoes_view = ["Mensal", "Acumulado no Ano"]
        if df_previsao is not None and not df_previsao.empty:
            opcoes_view.append("Previsão")

        # Exibir pills para seleção de visualização
        view_mode = st.pills(
            "Selecione a visualização:",
            opcoes_view,
            default="Mensal",
            selection_mode="single",
            key=radio_key,
        )

        # Exibir o slider apenas se NÃO for Previsão
        if view_mode != "Previsão":
            col1, _ = st.columns([0.45, 0.55])
            with col1:
                ANOS_SELECIONADOS = st.select_slider(
                    "Selecione o ano para o gráfico:",
                    options=anos_disponiveis,
                    value=default_range,
                    key=select_key,
                )
            start_year, end_year = ANOS_SELECIONADOS

            if start_year == end_year:
                periodo_str = f"em {start_year}"
            else:
                periodo_str = f"de {start_year} a {end_year}"

        if view_mode == "Previsão":
            # Exibir gráfico de previsão
            titulo = f"Projeção mensal de {titulo_kpi}"
            titulo_centralizado(titulo, 5)

            # Preparar dados de previsão
            df_prev = df_previsao.copy()
            # Multiplicar por 100 para representar percentual
            df_prev["variacao_verificada"] = df_prev["variacao_verificada"] * 100
            df_prev["prev_otimista"] = df_prev["prev_otimista"] * 100
            df_prev["prev_pessimista"] = df_prev["prev_pessimista"] * 100

            # Criar coluna de data para o eixo X
            df_prev["mes_ano_label"] = df_prev.apply(
                lambda row: f"{list(MESES_DIC.values())[int(row['mes']) - 1][:3]}/{str(int(row['ano']))[-2:]}"
                if pd.notna(row["mes"]) and pd.notna(row["ano"])
                else "",
                axis=1,
            )

            # Criar figura
            fig = go.Figure()

            # Adicionar barras de variação verificada (pretas)
            mask_verificada = df_prev["variacao_verificada"].notna()
            fig.add_trace(
                go.Bar(
                    x=df_prev.loc[mask_verificada, "mes_ano_label"],
                    y=df_prev.loc[mask_verificada, "variacao_verificada"],
                    name="Taxa de Variação Verificada",
                    marker_color="black",
                    width=0.8,
                    text=df_prev.loc[mask_verificada, "variacao_verificada"].apply(
                        lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                    ),
                    textposition="outside",
                    hovertemplate="<b>Verificada</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
                )
            )

            # Adicionar barras de previsão otimista (verde) e pessimista (vermelha)
            mask_prev = df_prev["prev_otimista"].notna()
            df_prev_filtered = df_prev.loc[mask_prev].copy()

            # Barra verde - Previsão Otimista
            fig.add_trace(
                go.Bar(
                    x=df_prev_filtered["mes_ano_label"],
                    y=df_prev_filtered["prev_otimista"],
                    name="Previsão Otimista",
                    marker_color="green",
                    text=df_prev_filtered["prev_otimista"].apply(
                        lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                    ),
                    textposition="outside",
                    hovertemplate="<b>Previsão Otimista</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
                    width=0.3,
                )
            )

            # Barra vermelha - Previsão Pessimista
            fig.add_trace(
                go.Bar(
                    x=df_prev_filtered["mes_ano_label"],
                    y=df_prev_filtered["prev_pessimista"],
                    name="Previsão Pessimista",
                    marker_color="red",
                    text=df_prev_filtered["prev_pessimista"].apply(
                        lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                    ),
                    textposition="outside",
                    hovertemplate="<b>Previsão Pessimista</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
                    width=0.3,
                )
            )

            # Garantir que categorias do eixo X sigam a ordem cronológica
            try:
                ordered = (
                    df_prev[["ano", "mes", "mes_ano_label"]]
                    .drop_duplicates()
                    .sort_values(["ano", "mes"])
                )
                ordered_labels = ordered["mes_ano_label"].tolist()
                fig.update_xaxes(
                    categoryorder="array",
                    categoryarray=ordered_labels,
                    tickangle=0,
                    automargin=True,
                )
            except Exception:
                # se falhar, mantém comportamento padrão
                pass

            # Configurar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Taxa de Variação (%)",
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                ),
                margin=dict(t=60, b=50, l=50, r=50),
                hovermode="x unified",
                barmode="group",
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            # Gráficos normais (Mensal ou Acumulado)
            if view_mode == "Mensal":
                titulo = f"Taxa de variação mensal de {titulo_kpi} {periodo_str}"
                df_base = df_hist_mensal
            else:
                titulo = f"Taxa de variação acumulada de {titulo_kpi} {periodo_str}"
                df_base = df_hist_acumulado

            df_filtrado = df_base[
                (df_base.index.year >= start_year) & (df_base.index.year <= end_year)
            ]

            df_plot = formatar_indice_grafico(df_filtrado)
            titulo_centralizado(titulo, 5)
            fig = criar_grafico_barras(
                df=df_plot,
                titulo="",
                label_y="Taxa de Variação (%)",
                data_label_format=",.1f",
                hover_label_format=",.1f",
            )
            st.plotly_chart(fig, use_container_width=True)

    if usar_expander:
        with st.expander(
            titulo_expander, expanded=st.session_state[expander_state_key]
        ):
            render_content()
    else:
        render_content()


def display_comex_grafico(
    df_comex,
    state_key_prefix,
    set_expander_open_callback,
    coluna_dados,
    coluna_tipo="tipo",
    df_previsao=None,
):
    """
    Exibe o slider de ano e o gráfico de combo para o comércio exterior.
    Reutilizável para qualquer setor.

    Args:
        df_comex: DataFrame com dados de comércio exterior
        state_key_prefix: Prefixo para chaves de session_state
        set_expander_open_callback: Callback para manter expander aberto
        coluna_dados: Nome da coluna de dados ('valor' ou 'pares')
        coluna_tipo: Nome da coluna de tipo/categoria (default: 'tipo')
        df_previsao: DataFrame opcional com dados de previsão
    """
    # Seletor de tipo no topo (compartilhado por todas as visualizações)
    opcoes_filtro = ["Total"] + sorted(list(df_comex[coluna_tipo].unique()))

    col_tipo, _ = st.columns(2)
    with col_tipo:
        tipo_selecionado = st.selectbox(
            "Selecione o tipo:",
            options=opcoes_filtro,
            key=f"{state_key_prefix}_selectbox_tipo",
        )

    # Filtrar dados pelo tipo selecionado
    if tipo_selecionado == "Total":
        df_filtrado = df_comex
    else:
        df_filtrado = df_comex[df_comex[coluna_tipo] == tipo_selecionado]

    # Definir opções de pills baseado na disponibilidade de previsão
    opcoes_pills = ["Histórico Mensal", "Acumulado no Ano", "Por País", "Por Tipo"]
    if df_previsao is not None and not df_previsao.empty and coluna_dados == "pares":
        opcoes_pills.append("Previsão")

    # Pills para seleção de visualização
    tab_selection = st.pills(
        "Selecione a visualização:",
        opcoes_pills,
        default="Histórico Mensal",
        selection_mode="single",
        key=f"{state_key_prefix}_pills",
    )

    # === VISUALIZAÇÃO DE PREVISÃO ===
    if tab_selection == "Previsão":
        titulo_centralizado("Projeção mensal da Exportação de Calçados em Pares", 5)

        # Preparar dados de previsão
        df_prev = df_previsao.copy()
        # Multiplicar por 100 para representar percentual
        df_prev["variacao_verificada"] = df_prev["variacao_verificada"] * 100
        df_prev["prev_otimista"] = df_prev["prev_otimista"] * 100
        df_prev["prev_pessimista"] = df_prev["prev_pessimista"] * 100

        # Criar coluna de data para o eixo X
        df_prev["mes_ano_label"] = df_prev.apply(
            lambda row: f"{list(MESES_DIC.values())[int(row['mes']) - 1][:3]}/{str(int(row['ano']))[-2:]}"
            if pd.notna(row["mes"]) and pd.notna(row["ano"])
            else "",
            axis=1,
        )

        # Criar figura
        fig = go.Figure()

        # Adicionar barras de variação verificada (pretas)
        mask_verificada = df_prev["variacao_verificada"].notna()
        fig.add_trace(
            go.Bar(
                x=df_prev.loc[mask_verificada, "mes_ano_label"],
                y=df_prev.loc[mask_verificada, "variacao_verificada"],
                name="Taxa de Variação Verificada",
                marker_color="black",
                width=0.8,
                text=df_prev.loc[mask_verificada, "variacao_verificada"].apply(
                    lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                ),
                textposition="outside",
                hovertemplate="<b>Verificada</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
            )
        )

        # Adicionar barras de previsão otimista (verde) e pessimista (vermelha)
        mask_prev = df_prev["prev_otimista"].notna()
        df_prev_filtered = df_prev.loc[mask_prev].copy()

        # Barra verde - Previsão Otimista
        fig.add_trace(
            go.Bar(
                x=df_prev_filtered["mes_ano_label"],
                y=df_prev_filtered["prev_otimista"],
                name="Previsão Otimista",
                marker_color="green",
                text=df_prev_filtered["prev_otimista"].apply(
                    lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                ),
                textposition="outside",
                hovertemplate="<b>Previsão Otimista</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
                width=0.3,
            )
        )

        # Barra vermelha - Previsão Pessimista
        fig.add_trace(
            go.Bar(
                x=df_prev_filtered["mes_ano_label"],
                y=df_prev_filtered["prev_pessimista"],
                name="Previsão Pessimista",
                marker_color="red",
                text=df_prev_filtered["prev_pessimista"].apply(
                    lambda x: f"{x:,.1f}".replace(".", ",") if pd.notna(x) else ""
                ),
                textposition="outside",
                hovertemplate="<b>Previsão Pessimista</b><br>%{x}<br><b>Valor</b>: %{y:.1f}<extra></extra>",
                width=0.3,
            )
        )

        # Garantir que categorias do eixo X sigam a ordem cronológica
        try:
            ordered = (
                df_prev[["ano", "mes", "mes_ano_label"]]
                .drop_duplicates()
                .sort_values(["ano", "mes"])
            )
            ordered_labels = ordered["mes_ano_label"].tolist()
            fig.update_xaxes(
                categoryorder="array",
                categoryarray=ordered_labels,
                tickangle=0,
                automargin=True,
            )
        except Exception:
            # se falhar, mantém comportamento padrão
            pass

        # Configurar layout
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Taxa de Variação",
            height=450,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            ),
            margin=dict(t=60, b=50, l=50, r=50),
            hovermode="x unified",
            barmode="group",
        )

        st.plotly_chart(fig, use_container_width=True)
        return

    # === VISUALIZAÇÃO POR PAÍS ===
    if tab_selection == "Por País":
        display_comex_pais_view(
            df_comex=df_filtrado,
            state_key_prefix=state_key_prefix,
            set_expander_open=set_expander_open_callback,
            coluna_dados=coluna_dados,
        )
        return

    # === VISUALIZAÇÃO POR TIPO ===
    if tab_selection == "Por Tipo":
        display_comex_tipo_view(
            df_comex=df_comex,  # Usa df original, não filtrado por tipo
            state_key_prefix=state_key_prefix,
            set_expander_open=set_expander_open_callback,
            coluna_dados=coluna_dados,
            coluna_tipo=coluna_tipo,
        )
        return

    # === VISUALIZAÇÕES HISTÓRICO MENSAL E ACUMULADO ===
    if tab_selection == "Histórico Mensal":
        df_preparado = preparar_dados_comex_grafico(df_filtrado, coluna_dados)

        if df_preparado.empty:
            st.info("Não há dados suficientes para o gráfico.")
            return

        anos_disponiveis = sorted(df_preparado["date"].dt.year.unique().tolist())

        if not anos_disponiveis:
            st.warning("Não há dados anuais disponíveis para este gráfico.")
            return

        ult_ano = anos_disponiveis[-1]
        if len(anos_disponiveis) >= 2:
            ano_anterior = anos_disponiveis[-2]
            default_range = (ano_anterior, ult_ano)
        else:
            default_range = (ult_ano, ult_ano)

        select_key = f"{state_key_prefix}_slider_grafico"

        col_slider, _ = st.columns(2)
        with col_slider:
            ANOS_SELECIONADOS = st.select_slider(
                "Selecione o período para o gráfico:",
                options=anos_disponiveis,
                value=default_range,
                key=select_key,
            )

        start_year, end_year = ANOS_SELECIONADOS

        df_plot = df_preparado[
            (df_preparado["date"].dt.year >= start_year)
            & (df_preparado["date"].dt.year <= end_year)
        ]

        if df_plot.empty:
            st.info("Não há dados para o período selecionado.")
            return

        if start_year == end_year:
            periodo_str = f"em {start_year}"
        else:
            periodo_str = f"de {start_year} a {end_year}"

        unidade_medida = (
            "Milhões de US$" if coluna_dados == "valor" else "Milhões de Pares"
        )
        tipo_titulo = "Valor" if coluna_dados == "valor" else "Pares"

        fluxo = "Exportação" if "exp" in state_key_prefix else "Importação"

        titulo_centralizado(
            f"{fluxo} Mensal {periodo_str} - {unidade_medida} - {tipo_selecionado}",
            5,
        )

        fig = criar_grafico_barras_linha_comex(
            df_plot, coluna_dados, unidade_medida, tipo_titulo
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tab_selection == "Acumulado no Ano":
        ult_ano = df_filtrado["ano"].max()
        ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()

        df_preparado_acum = preparar_dados_comex_acu_comparativo(
            df_filtrado, coluna_dados, ult_mes
        )

        fluxo = "Exportação" if "exp" in state_key_prefix else "Importação"
        unidade_medida = (
            "Milhões de US$" if coluna_dados == "valor" else "Milhões de Pares"
        )
        tipo_titulo = "Valor" if coluna_dados == "valor" else "Pares"

        titulo_centralizado(
            f"{fluxo} Acumulado de Janeiro a {MESES_DIC[ult_mes]} - {unidade_medida} - {tipo_selecionado}",
            5,
        )

        fig_acum = criar_grafico_barras_linha_comex_acum(
            df_preparado_acum, unidade_medida, tipo_titulo
        )
        st.plotly_chart(fig_acum, use_container_width=True)


def display_comex_analise(
    df_comex,
    coluna_dados,
    titulo_expander,
    titulo_kpi,
    state_key_prefix,
    categoria_kpi,
    set_expander_open,
    expander_state_key="comex_expander_state",
    coluna_tipo="tipo",
    usar_expander=True,
    df_previsao=None,
):
    """
    Função auxiliar para renderizar um bloco completo de Comércio Exterior.
    Reutilizável para qualquer setor.

    Args:
        df_comex: DataFrame com dados de comércio exterior
        coluna_dados: Nome da coluna de dados ('valor' ou 'pares')
        titulo_expander: Título do expander
        titulo_kpi: Título para os KPIs
        state_key_prefix: Prefixo para chaves de session_state
        categoria_kpi: Categoria para os KPIs (ex: 'Exportação')
        set_expander_open: Callback para manter expander aberto
        expander_state_key: Chave do session_state para o expander
        coluna_tipo: Nome da coluna de tipo/categoria (default: 'tipo')
        usar_expander: Se True, envolve o conteúdo em um expander. Se False, exibe diretamente.
        df_previsao: DataFrame opcional com dados de previsão (colunas: ano, mes, variacao_verificada, prev_otimista, prev_pessimista)
    """

    def render_content():
        display_comex_kpi_cards(
            df=df_comex,
            titulo_kpi=titulo_kpi,
            categoria_kpi=categoria_kpi,
            coluna=coluna_dados,
        )

        st.divider()
        display_comex_grafico(
            df_comex=df_comex,
            state_key_prefix=state_key_prefix,
            set_expander_open_callback=set_expander_open,
            coluna_dados=coluna_dados,
            coluna_tipo=coluna_tipo,
            df_previsao=df_previsao,
        )

    if usar_expander:
        with st.expander(
            titulo_expander,
            expanded=st.session_state.get(expander_state_key, False),
        ):
            render_content()
    else:
        render_content()


# =============================================================================
# FUNÇÕES PARA TABELA DE COMÉRCIO EXTERIOR POR PAÍS
# =============================================================================


@st.cache_data
def preparar_dados_comex_pais_pivot(
    df, coluna_valor, view_mode_tabela, metric_mode_tabela
):
    """
    Prepara e pivota os dados de comércio exterior por país.
    A ordenação é SEMPRE baseada no valor absoluto (maior para menor),
    independentemente da métrica selecionada.

    Args:
        df: DataFrame com colunas ano, mes, pais, valor, pares
        coluna_valor: 'valor' ou 'pares'
        view_mode_tabela: 'Mês' ou 'Acumulado no Ano'
        metric_mode_tabela: 'Valor', 'Pares' ou 'Variação (%)'

    Returns:
        DataFrame pivotado com países como índice e anos como colunas
    """
    if df.empty:
        return pd.DataFrame()

    df_filtrado = df.copy()

    if df_filtrado.empty:
        return pd.DataFrame()

    # --- LÓGICA DO MÊS DE REFERÊNCIA ---
    ultimo_ano_dados = df_filtrado["ano"].max()
    ult_mes_referencia = df_filtrado[df_filtrado["ano"] == ultimo_ano_dados][
        "mes"
    ].max()

    # Preparar dados baseado na visualização
    if view_mode_tabela == "Mês":
        # Agregar valores apenas do mês específico para todos os anos
        df_view = df_filtrado[df_filtrado["mes"] == ult_mes_referencia].copy()
        df_grouped = df_view.groupby(["pais", "ano"])[coluna_valor].sum().reset_index()
        prefixo_col = f"{MESES_DIC[ult_mes_referencia][:3]}"
    else:  # Acumulado no Ano
        # Agregar valores de jan até o mês de referência para cada ano
        df_acum = df_filtrado[df_filtrado["mes"] <= ult_mes_referencia].copy()
        df_grouped = df_acum.groupby(["pais", "ano"])[coluna_valor].sum().reset_index()
        prefixo_col = f"Jan-{MESES_DIC[ult_mes_referencia][:3]}"

    if df_grouped.empty:
        return pd.DataFrame()

    # 4. Pivotar valores absolutos (para exibição e/ou ordenação)
    pivot_valores = df_grouped.pivot_table(
        index="pais",
        columns="ano",
        values=coluna_valor,
        aggfunc="sum",
        fill_value=0,
    )

    # Garantir que não há colunas duplicadas
    pivot_valores = pivot_valores.loc[:, ~pivot_valores.columns.duplicated()]

    # Ordenação pelo maior valor do ano mais recente (pela coluna do contexto)
    if not pivot_valores.empty and len(pivot_valores.columns) > 0:
        ultimo_ano_col = pivot_valores.columns.max()
        pivot_valores = pivot_valores.sort_values(by=ultimo_ano_col, ascending=False)

    # 5. Calcular o DataFrame Final
    if metric_mode_tabela in ["Valor", "Pares"]:
        df_final = pivot_valores.copy()
    else:
        # Calcular variação percentual ano a ano
        pivot_perc = pivot_valores.pct_change(axis=1) * 100
        # Remover primeira coluna (não tem ano anterior para comparar)
        pivot_perc = pivot_perc.iloc[:, 1:]
        # Manter a mesma ordem (já ordenada por valor absoluto)
        df_final = pivot_perc

    # 6. Renomear Colunas (formato: Nov/24 ou Jan-Nov/24)
    df_final.columns = [f"{prefixo_col}/{str(ano)[2:]}" for ano in df_final.columns]

    # 7. Renomear índice
    df_final.index.name = "País"

    return df_final


def display_comex_pais_view(
    df_comex,
    state_key_prefix,
    set_expander_open,
    coluna_dados="valor",
):
    """
    Exibe a tabela de comércio exterior por país dentro de um expander existente.

    Args:
        df_comex: DataFrame com dados de comércio exterior (já filtrado por tipo)
        state_key_prefix: Prefixo para chaves de session_state
        set_expander_open: Callback para manter expander aberto
        coluna_dados: Nome da coluna de dados ('valor' ou 'pares')
    """
    # Controles de Visualização e Métrica
    col_view, col_metric = st.columns(2)

    with col_view:
        view_mode = st.segmented_control(
            "Visualização:",
            options=["Mês", "Acumulado no Ano"],
            default="Mês",
            key=f"{state_key_prefix}_pais_view_mode",
        )
        if not view_mode:
            view_mode = "Mês"

    # Determinar métrica baseado no contexto do expander (valor ou pares)
    metrica_base = "Valor" if coluna_dados == "valor" else "Pares"

    with col_metric:
        metric_mode = st.segmented_control(
            "Métrica:",
            options=[metrica_base, "Variação (%)"],
            default=metrica_base,
            key=f"{state_key_prefix}_pais_metric_mode",
        )
        if not metric_mode:
            metric_mode = metrica_base

    # Coluna de dados é fixa baseada no contexto do expander
    coluna_valor = coluna_dados

    # Campo de busca
    texto_busca = st.text_input(
        "🔍 Pesquisar País:",
        key=f"{state_key_prefix}_pais_busca",
        placeholder="Ex: Estados Unidos, China",
    )

    # Preparar e exibir tabela
    df_pivot = preparar_dados_comex_pais_pivot(
        df_comex, coluna_valor, view_mode, metric_mode
    )

    if not df_pivot.empty:
        if texto_busca:
            df_pivot = df_pivot[
                df_pivot.index.str.contains(texto_busca, case=False, na=False)
            ]

        styler = df_pivot.style
        if metric_mode == "Variação (%)":
            styler = styler.format(formatar_pct_br).map(style_saldo_variacao)
        else:
            styler = styler.format(formatar_valor_br)
            # Usar cor verde - quanto maior o valor na coluna, mais verde
            styler = styler.background_gradient(cmap="Greens", axis=0)

        st.dataframe(styler, use_container_width=True)
    else:
        st.info("Sem dados para a seleção atual.")


# =============================================================================
# FUNÇÕES PARA TABELA DE COMÉRCIO EXTERIOR POR TIPO
# =============================================================================


@st.cache_data
def preparar_dados_comex_tipo_pivot(
    df, coluna_valor, coluna_tipo, view_mode_tabela, metric_mode_tabela
):
    """
    Prepara e pivota os dados de comércio exterior por tipo.
    Calcula a participação percentual de cada tipo no total.

    Args:
        df: DataFrame com colunas ano, mes, tipo, valor, pares
        coluna_valor: 'valor' ou 'pares'
        coluna_tipo: Nome da coluna de tipo (default: 'tipo')
        view_mode_tabela: 'Mês' ou 'Acumulado no Ano'
        metric_mode_tabela: 'Valor', 'Pares', 'Participação (%)' ou 'Variação (%)'

    Returns:
        DataFrame pivotado com tipos como índice e anos como colunas
    """
    if df.empty:
        return pd.DataFrame()

    df_filtrado = df.copy()

    if df_filtrado.empty:
        return pd.DataFrame()

    # --- LÓGICA DO MÊS DE REFERÊNCIA ---
    ultimo_ano_dados = df_filtrado["ano"].max()
    ult_mes_referencia = df_filtrado[df_filtrado["ano"] == ultimo_ano_dados][
        "mes"
    ].max()

    # Preparar dados baseado na visualização
    if view_mode_tabela == "Mês":
        # Agregar valores apenas do mês específico para todos os anos
        df_view = df_filtrado[df_filtrado["mes"] == ult_mes_referencia].copy()
        df_grouped = (
            df_view.groupby([coluna_tipo, "ano"])[coluna_valor].sum().reset_index()
        )
        prefixo_col = f"{MESES_DIC[ult_mes_referencia][:3]}"
    else:  # Acumulado no Ano
        # Agregar valores de jan até o mês de referência para cada ano
        df_acum = df_filtrado[df_filtrado["mes"] <= ult_mes_referencia].copy()
        df_grouped = (
            df_acum.groupby([coluna_tipo, "ano"])[coluna_valor].sum().reset_index()
        )
        prefixo_col = f"Jan-{MESES_DIC[ult_mes_referencia][:3]}"

    if df_grouped.empty:
        return pd.DataFrame()

    # 4. Pivotar valores absolutos
    pivot_valores = df_grouped.pivot_table(
        index=coluna_tipo,
        columns="ano",
        values=coluna_valor,
        aggfunc="sum",
        fill_value=0,
    )

    # Garantir que não há colunas duplicadas
    pivot_valores = pivot_valores.loc[:, ~pivot_valores.columns.duplicated()]

    # Ordenação pelo maior valor do ano mais recente
    if not pivot_valores.empty and len(pivot_valores.columns) > 0:
        ultimo_ano_col = pivot_valores.columns.max()
        pivot_valores = pivot_valores.sort_values(by=ultimo_ano_col, ascending=False)

    # 5. Calcular o DataFrame Final baseado na métrica
    if metric_mode_tabela in ["Valor", "Pares"]:
        df_final = pivot_valores.copy()
    elif metric_mode_tabela == "Participação (%)":
        # Calcular participação percentual de cada tipo no total do ano
        totais_por_ano = pivot_valores.sum(axis=0)
        df_final = (pivot_valores / totais_por_ano * 100).round(1)
    else:  # Variação (%)
        # Calcular a variação percentual ano a ano
        df_final = pivot_valores.pct_change(axis=1) * 100
        # Remover a primeira coluna (não tem YoY)
        if len(df_final.columns) > 1:
            df_final = df_final.iloc[:, 1:]

    if df_final.empty:
        return pd.DataFrame()

    # 6. Renomear Colunas (formato: Nov/24 ou Jan-Nov/24)
    df_final.columns = [f"{prefixo_col}/{str(ano)[2:]}" for ano in df_final.columns]

    # 7. Renomear índice
    df_final.index.name = "Tipo"

    return df_final


def display_comex_tipo_view(
    df_comex,
    state_key_prefix,
    set_expander_open,
    coluna_dados="valor",
    coluna_tipo="tipo",
):
    """
    Exibe a tabela de comércio exterior por tipo dentro de um expander existente.

    Args:
        df_comex: DataFrame com dados de comércio exterior
        state_key_prefix: Prefixo para chaves de session_state
        set_expander_open: Callback para manter expander aberto
        coluna_dados: Nome da coluna de dados ('valor' ou 'pares')
        coluna_tipo: Nome da coluna de tipo (default: 'tipo')
    """
    # Controles de Visualização e Métrica
    col_view, col_metric = st.columns(2)

    with col_view:
        view_mode = st.segmented_control(
            "Visualização:",
            options=["Mês", "Acumulado no Ano"],
            default="Mês",
            key=f"{state_key_prefix}_tipo_view_mode",
        )
        if not view_mode:
            view_mode = "Mês"

    # Determinar métrica baseado no contexto do expander (valor ou pares)
    metrica_base = "Valor" if coluna_dados == "valor" else "Pares"

    with col_metric:
        metric_mode = st.segmented_control(
            "Métrica:",
            options=[metrica_base, "Participação (%)", "Variação (%)"],
            default="Participação (%)",
            key=f"{state_key_prefix}_tipo_metric_mode",
        )
        if not metric_mode:
            metric_mode = "Participação (%)"

    # Coluna de dados é fixa baseada no contexto do expander
    coluna_valor = coluna_dados

    # Preparar e exibir tabela
    df_pivot = preparar_dados_comex_tipo_pivot(
        df_comex, coluna_valor, coluna_tipo, view_mode, metric_mode
    )

    if not df_pivot.empty:
        styler = df_pivot.style
        if metric_mode == "Variação (%)":
            styler = styler.format(formatar_pct_br).map(style_saldo_variacao)
        elif metric_mode == "Participação (%)":
            styler = styler.format(
                lambda x: f"{x:,.1f}%".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if pd.notna(x)
                else "-"
            )
            styler = styler.background_gradient(cmap="Greens", axis=0)
        else:
            styler = styler.format(formatar_valor_br)
            styler = styler.background_gradient(cmap="Greens", axis=0)

        st.dataframe(styler, use_container_width=True)
    else:
        st.info("Sem dados para a seleção atual.")


# =============================================================================
# FUNÇÕES PARA TABELA DE COMÉRCIO EXTERIOR POR SH6
# =============================================================================


@st.cache_data
def preparar_dados_comex_sh6_pivot(
    df, coluna_valor, view_mode_tabela, metric_mode_tabela
):
    """
    Prepara e pivota os dados de comércio exterior por SH6.

    Args:
        df: DataFrame com colunas ano, mes, id_sh6, descricao_sh6, valor
        coluna_valor: 'valor'
        view_mode_tabela: 'Mês' ou 'Acumulado no Ano'
        metric_mode_tabela: 'Valor' ou 'Variação (%)'

    Returns:
        DataFrame pivotado com SH6 como índice e anos como colunas
    """
    if df.empty:
        return pd.DataFrame()

    df_filtrado = df.copy()

    # Criar coluna combinada SH6
    df_filtrado["sh6"] = (
        df_filtrado["id_sh6"].astype(str) + " - " + df_filtrado["descricao_sh6"]
    )

    if df_filtrado.empty:
        return pd.DataFrame()

    # --- LÓGICA DO MÊS DE REFERÊNCIA ---
    ultimo_ano_dados = df_filtrado["ano"].max()
    ult_mes_referencia = df_filtrado[df_filtrado["ano"] == ultimo_ano_dados][
        "mes"
    ].max()

    # Preparar dados baseado na visualização
    if view_mode_tabela == "Mês":
        df_view = df_filtrado[df_filtrado["mes"] == ult_mes_referencia].copy()
        df_grouped = df_view.groupby(["sh6", "ano"])[coluna_valor].sum().reset_index()
        prefixo_col = f"{MESES_DIC[ult_mes_referencia][:3]}"
    else:  # Acumulado no Ano
        df_acum = df_filtrado[df_filtrado["mes"] <= ult_mes_referencia].copy()
        df_grouped = df_acum.groupby(["sh6", "ano"])[coluna_valor].sum().reset_index()
        prefixo_col = f"Jan-{MESES_DIC[ult_mes_referencia][:3]}"

    if df_grouped.empty:
        return pd.DataFrame()

    # Pivotar valores absolutos
    pivot_valores = df_grouped.pivot_table(
        index="sh6",
        columns="ano",
        values=coluna_valor,
        aggfunc="sum",
        fill_value=0,
    )

    # Garantir que não há colunas duplicadas
    pivot_valores = pivot_valores.loc[:, ~pivot_valores.columns.duplicated()]

    # Ordenação pelo maior valor do ano mais recente
    if not pivot_valores.empty and len(pivot_valores.columns) > 0:
        ultimo_ano_col = pivot_valores.columns.max()
        pivot_valores = pivot_valores.sort_values(by=ultimo_ano_col, ascending=False)

    # Calcular o DataFrame Final
    if metric_mode_tabela == "Valor":
        df_final = pivot_valores.copy()
    else:  # Variação (%)
        df_final = pivot_valores.pct_change(axis=1) * 100
        if len(df_final.columns) > 1:
            df_final = df_final.iloc[:, 1:]

    if df_final.empty:
        return pd.DataFrame()

    # Renomear Colunas
    df_final.columns = [f"{prefixo_col}/{str(ano)[2:]}" for ano in df_final.columns]

    # Renomear índice
    df_final.index.name = "SH6"

    return df_final


def display_comex_sh6_view(
    df_comex,
    state_key_prefix,
    set_expander_open,
    coluna_dados="valor",
):
    """
    Exibe a tabela de comércio exterior por SH6.

    Args:
        df_comex: DataFrame com dados de comércio exterior (já filtrado)
        state_key_prefix: Prefixo para chaves de session_state
        set_expander_open: Callback para manter expander aberto
        coluna_dados: Nome da coluna de dados ('valor')
    """
    # Controles de Visualização e Métrica
    col_view, col_metric = st.columns(2)

    with col_view:
        view_mode = st.segmented_control(
            "Visualização:",
            options=["Mês", "Acumulado no Ano"],
            default="Mês",
            key=f"{state_key_prefix}_sh6_view_mode",
        )
        if not view_mode:
            view_mode = "Mês"

    with col_metric:
        metric_mode = st.segmented_control(
            "Métrica:",
            options=["Valor", "Variação (%)"],
            default="Valor",
            key=f"{state_key_prefix}_sh6_metric_mode",
        )
        if not metric_mode:
            metric_mode = "Valor"

    # Campo de busca
    texto_busca = st.text_input(
        "🔍 Pesquisar SH6:",
        key=f"{state_key_prefix}_sh6_busca",
        placeholder="Ex: 640399, calçado",
    )

    # Preparar e exibir tabela
    df_pivot = preparar_dados_comex_sh6_pivot(
        df_comex, coluna_dados, view_mode, metric_mode
    )

    if not df_pivot.empty:
        if texto_busca:
            df_pivot = df_pivot[
                df_pivot.index.str.contains(texto_busca, case=False, na=False)
            ]

        styler = df_pivot.style
        if metric_mode == "Variação (%)":
            styler = styler.format(formatar_pct_br).map(style_saldo_variacao)
        else:
            styler = styler.format(formatar_valor_br)
            styler = styler.background_gradient(cmap="Greens", axis=0)

        st.dataframe(styler, use_container_width=True)
    else:
        st.info("Sem dados para a seleção atual.")


# =============================================================================
# FUNÇÕES PARA COMÉRCIO EXTERIOR VERTICAL
# =============================================================================


def display_comex_vertical_grafico(
    df_comex,
    df_comex_pais,
    df_comex_sh6,
    df_filtrado,
    df_filtrado_pais,
    df_filtrado_sh6,
    tipo_selecionado,
    state_key_prefix,
    set_expander_open_callback,
    coluna_tipo="vertical",
):
    """
    Exibe o gráfico de comércio exterior para verticais.
    Inclui visualizações: Histórico Mensal, Acumulado no Ano, Por País, Por Vertical, Por SH6

    Args:
        df_comex: DataFrame com dados agregados por vertical (original, para view "Por Vertical")
        df_comex_pais: DataFrame com dados por vertical e país (original)
        df_comex_sh6: DataFrame com dados por vertical e SH6 (original)
        df_filtrado: DataFrame filtrado pela vertical selecionada
        df_filtrado_pais: DataFrame de país filtrado pela vertical
        df_filtrado_sh6: DataFrame de SH6 filtrado pela vertical
        tipo_selecionado: Vertical selecionada ("Total" ou nome da vertical)
        state_key_prefix: Prefixo para chaves de session_state
        set_expander_open_callback: Callback para manter expander aberto
        coluna_tipo: Nome da coluna de tipo/categoria (default: 'vertical')
    """
    coluna_dados = "valor"  # Vertical sempre usa valor

    # Definir labels dinâmicos baseados no tipo de análise
    tipo_label = (
        coluna_tipo.capitalize()
    )  # "vertical" -> "Vertical", "componente" -> "Componente"

    # Verificar se DataFrames filtrados estão vazios
    if df_filtrado.empty:
        st.warning("Não há dados disponíveis para exibição.")
        return

    # Pills para seleção de visualização
    tab_selection = st.pills(
        "Selecione a visualização:",
        [
            "Histórico Mensal",
            "Acumulado no Ano",
            "Por País",
            f"Por {tipo_label}",
            "Por SH6",
        ],
        default="Histórico Mensal",
        selection_mode="single",
        key=f"{state_key_prefix}_pills",
    )

    # === VISUALIZAÇÃO POR PAÍS ===
    if tab_selection == "Por País":
        if df_filtrado_pais.empty:
            st.info("Sem dados por país para a seleção atual.")
            return
        display_comex_pais_view(
            df_comex=df_filtrado_pais,
            state_key_prefix=state_key_prefix,
            set_expander_open=set_expander_open_callback,
            coluna_dados=coluna_dados,
        )
        return

    # === VISUALIZAÇÃO POR VERTICAL/COMPONENTE ===
    if tab_selection == f"Por {tipo_label}":
        display_comex_tipo_view(
            df_comex=df_comex,  # Usa df original, não filtrado por tipo
            state_key_prefix=state_key_prefix,
            set_expander_open=set_expander_open_callback,
            coluna_dados=coluna_dados,
            coluna_tipo=coluna_tipo,
        )
        return

    # === VISUALIZAÇÃO POR SH6 ===
    if tab_selection == "Por SH6":
        if df_filtrado_sh6.empty:
            st.info("Sem dados por SH6 para a seleção atual.")
            return
        display_comex_sh6_view(
            df_comex=df_filtrado_sh6,
            state_key_prefix=state_key_prefix,
            set_expander_open=set_expander_open_callback,
            coluna_dados=coluna_dados,
        )
        return

    # === VISUALIZAÇÕES HISTÓRICO MENSAL E ACUMULADO ===
    if tab_selection == "Histórico Mensal":
        df_preparado = preparar_dados_comex_grafico(df_filtrado, coluna_dados)

        if df_preparado.empty:
            st.info("Não há dados suficientes para o gráfico.")
            return

        anos_disponiveis = sorted(df_preparado["date"].dt.year.unique().tolist())

        if not anos_disponiveis:
            st.warning("Não há dados anuais disponíveis para este gráfico.")
            return

        ult_ano = anos_disponiveis[-1]
        if len(anos_disponiveis) >= 2:
            ano_anterior = anos_disponiveis[-2]
            default_range = (ano_anterior, ult_ano)
        else:
            default_range = (ult_ano, ult_ano)

        select_key = f"{state_key_prefix}_slider_grafico"

        col_slider, _ = st.columns(2)
        with col_slider:
            ANOS_SELECIONADOS = st.select_slider(
                "Selecione o período para o gráfico:",
                options=anos_disponiveis,
                value=default_range,
                key=select_key,
            )

        start_year, end_year = ANOS_SELECIONADOS

        df_plot = df_preparado[
            (df_preparado["date"].dt.year >= start_year)
            & (df_preparado["date"].dt.year <= end_year)
        ]

        if df_plot.empty:
            st.info("Não há dados para o período selecionado.")
            return

        if start_year == end_year:
            periodo_str = f"em {start_year}"
        else:
            periodo_str = f"de {start_year} a {end_year}"

        unidade_medida = "Milhões de US$"
        tipo_titulo = "Valor"

        fluxo = "Exportação" if "exp" in state_key_prefix else "Importação"

        titulo_centralizado(
            f"{fluxo} Mensal {periodo_str} - {unidade_medida} - {tipo_selecionado}",
            5,
        )

        fig = criar_grafico_barras_linha_comex(
            df_plot, coluna_dados, unidade_medida, tipo_titulo
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Acumulado no Ano
        ult_ano = df_filtrado["ano"].max()
        ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()

        df_preparado_acum = preparar_dados_comex_acu_comparativo(
            df_filtrado, coluna_dados, ult_mes
        )

        fluxo = "Exportação" if "exp" in state_key_prefix else "Importação"
        unidade_medida = "Milhões de US$"
        tipo_titulo = "Valor"

        titulo_centralizado(
            f"{fluxo} Acumulado de Janeiro a {MESES_DIC[ult_mes]} - {unidade_medida} - {tipo_selecionado}",
            5,
        )

        fig_acum = criar_grafico_barras_linha_comex_acum(
            df_preparado_acum, unidade_medida, tipo_titulo
        )
        st.plotly_chart(fig_acum, use_container_width=True)


def display_comex_vertical_analise(
    df_comex,
    df_comex_pais,
    df_comex_sh6,
    titulo_expander,
    titulo_kpi,
    state_key_prefix,
    categoria_kpi,
    set_expander_open,
    expander_state_key="vertical_comex_expander_state",
    coluna_tipo="vertical",
    usar_expander=True,
):
    """
    Função auxiliar para renderizar um bloco completo de Comércio Exterior Vertical.

    Args:
        df_comex: DataFrame com dados agregados
        df_comex_pais: DataFrame com dados por país
        df_comex_sh6: DataFrame com dados por SH6
        titulo_expander: Título do expander
        titulo_kpi: Título para os KPIs
        state_key_prefix: Prefixo para chaves de session_state
        categoria_kpi: Categoria para os KPIs (ex: 'Exportação')
        set_expander_open: Callback para manter expander aberto
        expander_state_key: Chave do session_state para o expander
        coluna_tipo: Nome da coluna de tipo/categoria (default: 'vertical')
        usar_expander: Se True, envolve o conteúdo em um expander. Se False, exibe diretamente.
    """

    def render_content():
        # Verificar se DataFrame está vazio
        if df_comex.empty:
            st.warning("Não há dados disponíveis para exibição.")
            return

        # Definir labels dinâmicos baseados no tipo de análise
        tipo_label = (
            coluna_tipo.capitalize()
        )  # "vertical" -> "Vertical", "componente" -> "Componente"
        tipo_plural = f"{tipo_label}s"  # "Verticais", "Componentes"

        # Seletor no topo (afeta cards e gráficos)
        opcoes_filtro = ["Total"] + sorted(list(df_comex[coluna_tipo].unique()))

        col_tipo, _ = st.columns(2)
        with col_tipo:
            tipo_selecionado = st.selectbox(
                f"Selecione {tipo_label.lower()[0] if tipo_label[0] in 'AEIOU' else 'o'} {tipo_label.lower()}:",
                options=opcoes_filtro,
                key=f"{state_key_prefix}_selectbox_tipo",
            )

        # Filtrar dados pelo tipo selecionado
        if tipo_selecionado == "Total":
            df_filtrado = df_comex
            df_filtrado_pais = df_comex_pais
            df_filtrado_sh6 = df_comex_sh6
            titulo_kpi_dinamico = f"{titulo_kpi} - Total dos {tipo_plural}"
        else:
            df_filtrado = df_comex[df_comex[coluna_tipo] == tipo_selecionado]
            df_filtrado_pais = (
                df_comex_pais[df_comex_pais[coluna_tipo] == tipo_selecionado]
                if not df_comex_pais.empty and coluna_tipo in df_comex_pais.columns
                else pd.DataFrame()
            )
            df_filtrado_sh6 = (
                df_comex_sh6[df_comex_sh6[coluna_tipo] == tipo_selecionado]
                if not df_comex_sh6.empty and coluna_tipo in df_comex_sh6.columns
                else pd.DataFrame()
            )
            titulo_kpi_dinamico = f"{titulo_kpi} - {tipo_selecionado}"

        # KPI Cards com dados filtrados
        display_comex_kpi_cards(
            df=df_filtrado,
            titulo_kpi=titulo_kpi_dinamico,
            categoria_kpi=categoria_kpi,
            coluna="valor",
        )

        st.divider()

        # Gráficos com dados filtrados
        display_comex_vertical_grafico(
            df_comex=df_comex,
            df_comex_pais=df_comex_pais,
            df_comex_sh6=df_comex_sh6,
            df_filtrado=df_filtrado,
            df_filtrado_pais=df_filtrado_pais,
            df_filtrado_sh6=df_filtrado_sh6,
            tipo_selecionado=tipo_selecionado,
            state_key_prefix=state_key_prefix,
            set_expander_open_callback=set_expander_open,
            coluna_tipo=coluna_tipo,
        )

    if usar_expander:
        with st.expander(
            titulo_expander,
            expanded=st.session_state.get(expander_state_key, False),
        ):
            render_content()
    else:
        render_content()
