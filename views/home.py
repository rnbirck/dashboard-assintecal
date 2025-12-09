# %%
import streamlit as st
from src.utils import MESES_DIC, titulo_centralizado


# ==============================================================================
# FUNÇÕES DA PÁGINA HOME
# ==============================================================================
def go_to_page(page_name):
    """Atualiza o estado da sessão para mudar a página selecionada."""
    st.session_state.selected_page = page_name


def show_page_home(
    df_producao,
    df_vendas,
    df_exp_calcados,
    df_imp_calcados,
    df_emprego_calcados,
    df_ipca_calcados,
    df_exp_couro,
    df_imp_couro,
    df_emprego_couro,
    df_exp_vertical,
    df_exp_componente,
    df_ibc_br,
    df_expectativas,
    df_ipca_geral,
    df_taxa_cambio,
    df_ind_transformacao,
    df_taxa_desemprego,
):
    """
    Renderiza a página inicial do dashboard com instruções, informações e datas de atualização.
    """

    titulo_centralizado("📊 Dashboard Assintecal", 1)
    st.markdown("---")
    titulo_centralizado("Bem-vindo(a) ao painel de visualização de dados!", 2)
    st.markdown(
        """
        ##### Este dashboard foi desenvolvido para apresentar indicadores econômicos e de mercado do **setor coureiro-calçadista brasileiro**, reunindo dados de produção, comércio exterior, emprego e indicadores macroeconômicos relevantes.
        """
    )
    st.markdown("---")
    st.subheader("🧭 Como Utilizar o Dashboard")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            #### 1. Menu de Navegação
            Na barra lateral à esquerda, você encontra o menu principal com todas as páginas disponíveis. Clique em uma opção para acessar os dados específicos de cada setor ou tema.
            """
        )

    with col2:
        st.markdown(
            """
            #### 2. Menus de Análise (Seções Expansíveis)
            Em cada página, os dados são organizados em seções recolhíveis. Clique em qualquer seção para expandir e ver as análises detalhadas.
            """
        )

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown(
            """
            #### 3. Seletores de Período
            Dentro de alguns menus, você encontrará **seletores de ano** que permitem escolher o período específico que deseja analisar.
            """
        )

    with col4:
        st.markdown(
            """
            #### 4. Alternar Visualizações
            Em algumas seções, você encontrará controles que permitem alternar a visualização dos dados (ex: "Mensal" vs "Acumulado no Ano"), oferecendo diferentes perspectivas.
            """
        )

    st.markdown("---")
    st.subheader("📂 Sobre as Páginas e Atualizações")

    # --- Obter datas de atualização dos dataframes ---

    # Produção e Vendas
    try:
        ult_ano_prod = int(df_producao["ano"].max())
        ult_mes_prod = int(df_producao[df_producao["ano"] == ult_ano_prod]["mes"].max())
        data_producao = f"{MESES_DIC[ult_mes_prod]} de {ult_ano_prod}"
    except Exception:
        data_producao = "Não disponível"

    try:
        ult_ano_vendas = int(df_vendas["ano"].max())
        ult_mes_vendas = int(df_vendas[df_vendas["ano"] == ult_ano_vendas]["mes"].max())
        data_vendas = f"{MESES_DIC[ult_mes_vendas]} de {ult_ano_vendas}"
    except Exception:
        data_vendas = "Não disponível"

    # Comércio Exterior Calçados
    try:
        ult_ano_exp_calc = int(df_exp_calcados["ano"].max())
        ult_mes_exp_calc = int(
            df_exp_calcados[df_exp_calcados["ano"] == ult_ano_exp_calc]["mes"].max()
        )
        data_comex_calcados = f"{MESES_DIC[ult_mes_exp_calc]} de {ult_ano_exp_calc}"
    except Exception:
        data_comex_calcados = "Não disponível"

    # Emprego Calçados
    try:
        ult_ano_emp_calc = int(df_emprego_calcados["ano"].max())
        ult_mes_emp_calc = int(
            df_emprego_calcados[df_emprego_calcados["ano"] == ult_ano_emp_calc][
                "mes"
            ].max()
        )
        data_emprego_calcados = f"{MESES_DIC[ult_mes_emp_calc]} de {ult_ano_emp_calc}"
    except Exception:
        data_emprego_calcados = "Não disponível"

    # IPCA Calçados
    try:
        ult_ano_ipca_calc = int(df_ipca_calcados["ano"].max())
        ult_mes_ipca_calc = int(
            df_ipca_calcados[df_ipca_calcados["ano"] == ult_ano_ipca_calc]["mes"].max()
        )
        data_ipca_calcados = f"{MESES_DIC[ult_mes_ipca_calc]} de {ult_ano_ipca_calc}"
    except Exception:
        data_ipca_calcados = "Não disponível"

    # Comércio Exterior Couro
    try:
        ult_ano_exp_couro = int(df_exp_couro["ano"].max())
        ult_mes_exp_couro = int(
            df_exp_couro[df_exp_couro["ano"] == ult_ano_exp_couro]["mes"].max()
        )
        data_comex_couro = f"{MESES_DIC[ult_mes_exp_couro]} de {ult_ano_exp_couro}"
    except Exception:
        data_comex_couro = "Não disponível"

    # Emprego Couro
    try:
        ult_ano_emp_couro = int(df_emprego_couro["ano"].max())
        ult_mes_emp_couro = int(
            df_emprego_couro[df_emprego_couro["ano"] == ult_ano_emp_couro]["mes"].max()
        )
        data_emprego_couro = f"{MESES_DIC[ult_mes_emp_couro]} de {ult_ano_emp_couro}"
    except Exception:
        data_emprego_couro = "Não disponível"

    # Verticais
    try:
        ult_ano_vertical = int(df_exp_vertical["ano"].max())
        ult_mes_vertical = int(
            df_exp_vertical[df_exp_vertical["ano"] == ult_ano_vertical]["mes"].max()
        )
        data_vertical = f"{MESES_DIC[ult_mes_vertical]} de {ult_ano_vertical}"
    except Exception:
        data_vertical = "Não disponível"

    # Componentes
    try:
        ult_ano_componente = int(df_exp_componente["ano"].max())
        ult_mes_componente = int(
            df_exp_componente[df_exp_componente["ano"] == ult_ano_componente][
                "mes"
            ].max()
        )
        data_componente = f"{MESES_DIC[ult_mes_componente]} de {ult_ano_componente}"
    except Exception:
        data_componente = "Não disponível"

    # Macroeconomia - IBC-Br
    try:
        ult_ano_ibc = int(df_ibc_br["ano"].max())
        ult_mes_ibc = int(df_ibc_br[df_ibc_br["ano"] == ult_ano_ibc]["mes"].max())
        data_ibc = f"{MESES_DIC[ult_mes_ibc]} de {ult_ano_ibc}"
    except Exception:
        data_ibc = "Não disponível"

    # Expectativas
    try:
        ult_ano_expect = int(df_expectativas["ano"].max())
        ult_mes_expect = int(
            df_expectativas[df_expectativas["ano"] == ult_ano_expect]["mes"].max()
        )
        data_expectativas = f"{MESES_DIC[ult_mes_expect]} de {ult_ano_expect}"
    except Exception:
        data_expectativas = "Não disponível"

    # IPCA Geral
    try:
        ult_ano_ipca = int(df_ipca_geral["ano"].max())
        ult_mes_ipca = int(
            df_ipca_geral[df_ipca_geral["ano"] == ult_ano_ipca]["mes"].max()
        )
        data_ipca_geral = f"{MESES_DIC[ult_mes_ipca]} de {ult_ano_ipca}"
    except Exception:
        data_ipca_geral = "Não disponível"

    # Taxa de Câmbio
    try:
        ult_ano_cambio = int(df_taxa_cambio["ano"].max())
        ult_mes_cambio = int(
            df_taxa_cambio[df_taxa_cambio["ano"] == ult_ano_cambio]["mes"].max()
        )
        data_cambio = f"{MESES_DIC[ult_mes_cambio]} de {ult_ano_cambio}"
    except Exception:
        data_cambio = "Não disponível"

    # Indústria de Transformação
    try:
        ult_ano_ind = int(df_ind_transformacao["ano"].max())
        ult_mes_ind = int(
            df_ind_transformacao[df_ind_transformacao["ano"] == ult_ano_ind][
                "mes"
            ].max()
        )
        data_ind_transf = f"{MESES_DIC[ult_mes_ind]} de {ult_ano_ind}"
    except Exception:
        data_ind_transf = "Não disponível"

    # Taxa de Desemprego
    try:
        ult_ano_desemp = int(df_taxa_desemprego["ano"].max())
        ult_mes_desemp = int(
            df_taxa_desemprego[df_taxa_desemprego["ano"] == ult_ano_desemp]["mes"].max()
        )
        data_desemprego = f"{MESES_DIC[ult_mes_desemp]} de {ult_ano_desemp}"
    except Exception:
        data_desemprego = "Não disponível"

    # --- Exibição das páginas ---
    col_a, col_b = st.columns(2, gap="large")

    # --- COLUNA A ---
    with col_a:
        st.markdown(
            f"""
            #### 👟 Calçados
            Consolida dados do setor calçadista brasileiro, incluindo **produção industrial**, **volume de vendas**, **comércio exterior** (exportações e importações em valor e pares), **emprego formal (CAGED)**, **inflação setorial (IPCA)** e **previsões** para produção e exportação em pares.
            
            *Fontes: **IBGE (PIM-PF/PMC)**, **Comexstat**, **CAGED**, **IPCA***
            
            *Últimos dados:*
            - *Produção: **{data_producao}***
            - *Vendas: **{data_vendas}***
            - *Comércio Exterior: **{data_comex_calcados}***
            - *Emprego: **{data_emprego_calcados}***
            - *IPCA: **{data_ipca_calcados}***
            """
        )
        st.button(
            "Explorar Calçados ➔",
            on_click=go_to_page,
            args=("Calçados",),
            key="btn_home_calcados",
        )
        st.markdown("---")

        st.markdown(
            f"""
            #### 🐄 Couro
            Apresenta indicadores do setor de couro, incluindo **produção industrial**, **comércio exterior** (exportações e importações) e dados de **emprego formal (CAGED)**.
            
            *Fontes: **IBGE (PIM-PF)**, **Comexstat**, **CAGED***
            
            *Últimos dados:*
            - *Produção: **{data_producao}***
            - *Comércio Exterior: **{data_comex_couro}***
            - *Emprego: **{data_emprego_couro}***
            """
        )
        st.button(
            "Explorar Couro ➔",
            on_click=go_to_page,
            args=("Couro",),
            key="btn_home_couro",
        )
        st.markdown("---")

        st.markdown(
            f"""
            #### 📊 Vertical
            Análise detalhada das **exportações e importações** por vertical (Moda, Máquinas, Químicos para Couro, Tecnologia), permitindo visualização por **valor**, **país de destino/origem** e **código SH6**.
            
            *Fonte: **Comexstat***
            
            *Últimos dados: **{data_vertical}***
            """
        )
        st.button(
            "Explorar Vertical ➔",
            on_click=go_to_page,
            args=("Vertical",),
            key="btn_home_vertical",
        )

    # --- COLUNA B ---
    with col_b:
        st.markdown(
            f"""
            #### 🧩 Componente
            Análise das **exportações e importações** de componentes para calçados (Acessórios, Cabedal, Ferramentaria, Insumos, etc.), com visualização por **valor**, **país** e **código SH6**.
            
            *Fonte: **Comexstat***
            
            *Últimos dados: **{data_componente}***
            """
        )
        st.button(
            "Explorar Componente ➔",
            on_click=go_to_page,
            args=("Componente",),
            key="btn_home_componente",
        )
        st.markdown("---")

        st.markdown(
            f"""
            #### 📈 Macroeconomia
            Reúne os principais indicadores macroeconômicos que impactam o setor:
            
            - **IBC-Br**: Índice de Atividade Econômica do Banco Central
            - **Expectativas de Mercado**: Projeções do Focus para PIB e IPCA
            - **IPCA Geral**: Inflação oficial do país
            - **Taxa de Câmbio**: Cotação R$/USD
            - **Produção Industrial**: Indústria de Transformação
            - **Taxa de Desemprego**: PNAD Contínua
            
            *Fontes: **BCB**, **IBGE**, **Focus/BCB***
            
            *Últimos dados:*
            - *IBC-Br: **{data_ibc}***
            - *Expectativas: **{data_expectativas}***
            - *IPCA Geral: **{data_ipca_geral}***
            - *Taxa de Câmbio: **{data_cambio}***
            - *Ind. Transformação: **{data_ind_transf}***
            - *Desemprego: **{data_desemprego}***
            """
        )
        st.button(
            "Explorar Macroeconomia ➔",
            on_click=go_to_page,
            args=("Macroeconomia",),
            key="btn_home_macro",
        )
