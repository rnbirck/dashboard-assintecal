import streamlit as st
from src.utils import to_excel, titulo_centralizado


def show_page_dados(
    # --- DataFrames da Página Calçados ---
    df_producao,
    df_vendas,
    df_exp_calcados,
    df_imp_calcados,
    df_emprego_calcados,
    df_ipca_calcados,
    df_previsao_exportacao,
    df_previsao_producao,
    # --- DataFrames da Página Couro ---
    df_exp_couro,
    df_imp_couro,
    df_emprego_couro,
    # --- DataFrames da Página Vertical ---
    df_exp_vertical,
    df_exp_vertical_pais,
    df_exp_vertical_sh6,
    df_imp_vertical,
    df_imp_vertical_pais,
    df_imp_vertical_sh6,
    # --- DataFrames da Página Componente ---
    df_exp_componente,
    df_exp_componente_pais,
    df_exp_componente_sh6,
    df_imp_componente,
    df_imp_componente_pais,
    df_imp_componente_sh6,
    # --- DataFrames da Página Macroeconomia ---
    df_ibc_br,
    df_expectativas,
    df_ipca_geral,
    df_taxa_cambio,
    df_ind_transformacao,
    df_taxa_desemprego,
):
    """
    Renderiza a página de Download (Dados), com expanders para cada seção
    e botões para baixar os DataFrames em Excel.
    """
    titulo_centralizado("Página de Dados", 1)
    st.info(
        "Utilize os menus expansíveis abaixo para baixar os arquivos excel com os dados brutos do dashboard."
    )

    # 1. CALÇADOS
    with st.expander("Dados da Página: Calçados"):
        st.subheader("Dados do Setor Calçadista")
        st.markdown(
            "Dados mensais e anuais de produção, vendas, comércio exterior, emprego e inflação do setor de calçados."
        )

        col_calc_1, col_calc_2 = st.columns(2)
        with col_calc_1:
            st.download_button(
                label="📥 Produção Industrial de Calçados",
                data=to_excel(df_producao),
                file_name="calcados_producao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Vendas de Calçados",
                data=to_excel(df_vendas),
                file_name="calcados_vendas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Exportação de Calçados",
                data=to_excel(df_exp_calcados),
                file_name="calcados_exportacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação de Calçados",
                data=to_excel(df_imp_calcados),
                file_name="calcados_importacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_calc_2:
            st.download_button(
                label="📥 Emprego no Setor de Calçados",
                data=to_excel(df_emprego_calcados),
                file_name="calcados_emprego.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 IPCA Calçados",
                data=to_excel(df_ipca_calcados),
                file_name="calcados_ipca.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Previsão - Exportação de Calçados",
                data=to_excel(df_previsao_exportacao),
                file_name="calcados_previsao_exportacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Previsão - Produção de Calçados",
                data=to_excel(df_previsao_producao),
                file_name="calcados_previsao_producao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # 2. COURO
    with st.expander("Dados da Página: Couro"):
        st.subheader("Dados do Setor de Couro")
        st.markdown("Dados mensais de comércio exterior e emprego do setor de couro.")

        col_couro_1, col_couro_2 = st.columns(2)
        with col_couro_1:
            st.download_button(
                label="📥 Exportação de Couro",
                data=to_excel(df_exp_couro),
                file_name="couro_exportacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação de Couro",
                data=to_excel(df_imp_couro),
                file_name="couro_importacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_couro_2:
            st.download_button(
                label="📥 Emprego no Setor de Couro",
                data=to_excel(df_emprego_couro),
                file_name="couro_emprego.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # 3. VERTICAL
    with st.expander("Dados da Página: Vertical"):
        st.subheader("Dados de Exportação e Importação por Vertical")
        st.markdown(
            "Dados mensais de comércio exterior segmentados por vertical de calçados (Masculino, Feminino, Infantil, etc.)."
        )

        col_vert_1, col_vert_2 = st.columns(2)
        with col_vert_1:
            st.download_button(
                label="📥 Exportação por Vertical",
                data=to_excel(df_exp_vertical),
                file_name="vertical_exportacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Exportação por Vertical e País",
                data=to_excel(df_exp_vertical_pais),
                file_name="vertical_exportacao_pais.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Exportação por Vertical e SH6",
                data=to_excel(df_exp_vertical_sh6),
                file_name="vertical_exportacao_sh6.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_vert_2:
            st.download_button(
                label="📥 Importação por Vertical",
                data=to_excel(df_imp_vertical),
                file_name="vertical_importacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação por Vertical e País",
                data=to_excel(df_imp_vertical_pais),
                file_name="vertical_importacao_pais.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação por Vertical e SH6",
                data=to_excel(df_imp_vertical_sh6),
                file_name="vertical_importacao_sh6.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # 4. COMPONENTE
    with st.expander("Dados da Página: Componente"):
        st.subheader("Dados de Exportação e Importação de Componentes")
        st.markdown(
            "Dados mensais de comércio exterior de componentes para calçados (Solados, Cabedais, Palmilhas, etc.)."
        )

        col_comp_1, col_comp_2 = st.columns(2)
        with col_comp_1:
            st.download_button(
                label="📥 Exportação de Componentes",
                data=to_excel(df_exp_componente),
                file_name="componente_exportacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Exportação de Componentes por País",
                data=to_excel(df_exp_componente_pais),
                file_name="componente_exportacao_pais.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Exportação de Componentes por SH6",
                data=to_excel(df_exp_componente_sh6),
                file_name="componente_exportacao_sh6.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_comp_2:
            st.download_button(
                label="📥 Importação de Componentes",
                data=to_excel(df_imp_componente),
                file_name="componente_importacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação de Componentes por País",
                data=to_excel(df_imp_componente_pais),
                file_name="componente_importacao_pais.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Importação de Componentes por SH6",
                data=to_excel(df_imp_componente_sh6),
                file_name="componente_importacao_sh6.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # 5. MACROECONOMIA
    with st.expander("Dados da Página: Macroeconomia"):
        st.subheader("Dados Macroeconômicos")
        st.markdown(
            "Indicadores macroeconômicos que impactam o setor coureiro-calçadista brasileiro."
        )

        col_macro_1, col_macro_2 = st.columns(2)
        with col_macro_1:
            st.download_button(
                label="📥 IBC-Br (Índice de Atividade Econômica)",
                data=to_excel(df_ibc_br),
                file_name="macro_ibc_br.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Expectativas de Mercado (Focus)",
                data=to_excel(df_expectativas),
                file_name="macro_expectativas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 IPCA Geral",
                data=to_excel(df_ipca_geral),
                file_name="macro_ipca_geral.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_macro_2:
            st.download_button(
                label="📥 Taxa de Câmbio (R$/USD)",
                data=to_excel(df_taxa_cambio),
                file_name="macro_taxa_cambio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Produção Industrial (Indústria de Transformação)",
                data=to_excel(df_ind_transformacao),
                file_name="macro_industria_transformacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Taxa de Desemprego",
                data=to_excel(df_taxa_desemprego),
                file_name="macro_taxa_desemprego.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
