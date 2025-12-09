# %%
import os
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client
import numpy as np


# --- CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env ---
load_dotenv()

# CONFIGURAÇÃO DA CONEXÃO LOCAL ---
DB_USUARIO = os.getenv("DB_USUARIO")
DB_SENHA = os.getenv("DB_SENHA")
DB_HOST = os.getenv("DB_HOST")
DB_BANCO = os.getenv("DB_BANCO")

try:
    local_engine = create_engine(
        f"postgresql+psycopg2://{DB_USUARIO}:{DB_SENHA}@{DB_HOST}/{DB_BANCO}"
    )
    print("✅ Conexão com o banco de dados local estabelecida com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar ao banco de dados local: {e}")
    exit()

# --- 2. CONFIGURAÇÃO DA CONEXÃO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(
        "❌ Erro: Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas no arquivo .env."
    )
    exit()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexão com o Supabase estabelecida com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar ao Supabase: {e}")
    exit()


def process_and_upload(
    query_string,
    target_table_name,
    engine,
    supabase_client,
    params=None,
    batch_size=500,
):
    """
    Executa uma query parametrizada no banco local, corrige os tipos
    de dados e insere em lotes numa tabela do Supabase.
    """
    print(f"\n--- Processando tabela: {target_table_name} ---")

    try:
        start_time = time.time()

        # Executar a query e carregar para o DataFrame
        print(
            f"1/4: Buscando dados do banco local (Parâmetros: {params is not None})..."
        )
        df = pd.read_sql_query(text(query_string), engine, params=params)

        if df.empty:
            print("(!) Aviso: A query não retornou dados. Tabela pulada.")
            return

        print(f"-> Encontrados {len(df)} registros.")

        # Corrigir os tipos de dados
        print("2/4: Corrigindo tipos de dados no DataFrame...")
        for col in df.columns:
            if pd.api.types.is_float_dtype(df[col]):
                if (df[col].dropna() % 1 == 0).all():
                    print(
                        f"   - Convertendo coluna float '{col}' para inteiro anulável (Int64)."
                    )
                    df[col] = df[col].astype("Int64")

        df.replace([np.inf, -np.inf], None, inplace=True)
        df = df.astype(object).where(pd.notna(df), None)

        # Apagar dados existentes na tabela de destino
        print(f"3/4: Limpando a tabela de destino '{target_table_name}' no Supabase...")
        # Deleta todos os dados existentes para garantir uma carga limpa
        supabase_client.table(target_table_name).delete().gt("ano", 0).execute()

        # Inserir dados em lotes
        print(f"4/4: Inserindo dados em lotes de {batch_size} registros...")
        total_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)

        for i, start in enumerate(range(0, len(df), batch_size)):
            end = start + batch_size
            batch_df = df.iloc[start:end]
            data_to_insert = batch_df.to_dict(orient="records")

            response = (
                supabase_client.table(target_table_name)
                .insert(data_to_insert)
                .execute()
            )

            if hasattr(response, "error") and response.error:
                print(f"   -> ERRO no lote {i + 1}/{total_batches}: {response.error}")
            else:
                print(f"   -> Lote {i + 1}/{total_batches} inserido com sucesso.")

        end_time = time.time()
        print(
            f"✅ Tabela '{target_table_name}' concluída com sucesso em {end_time - start_time:.2f} segundos."
        )

    except Exception as e:
        print(f"❌ ERRO GERAL ao processar a tabela '{target_table_name}': {e}")
        with open("log_erros.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Erro na tabela {target_table_name}: {e}\n")


# ===================================================================
# --- 3. DEFINIÇÃO DOS FILTROS ---
# ===================================================================

anos_de_interesse = tuple(range(2021, 2026))


# ===================================================================
#  QUERIES
# ===================================================================
QUERY_PRODUCAO = """
SELECT
    SPLIT_PART(date, '/', 2)::INT AS ano,
    SPLIT_PART(date, '/', 1)::INT AS mes,
    grupo,
    taxa_mensal,
    taxa_acumulado
FROM
    producao
WHERE SPLIT_PART(date, '/', 2)::INT IN :lista_anos
"""

QUERY_VENDAS = """
SELECT
    SPLIT_PART(date, '/', 2)::INT AS ano,
    SPLIT_PART(date, '/', 1)::INT AS mes,
    grupo,
    taxa_mensal,
    taxa_acumulado
FROM
    vendas_varejo_calcados
WHERE SPLIT_PART(date, '/', 2)::INT IN :lista_anos
"""

QUERY_EXP_CALCADOS = """
SELECT
    ano,
    mes,
    pares,
    valor,
    tipo,
    pais
FROM
    comex
WHERE
    fluxo = 'EXP' AND segmento = 'CALCADO' AND ano IN :lista_anos
"""

QUERY_EXP_COURO = """
SELECT
    ano,
    mes,
    valor,
    tipo,
    pais
FROM
    comex
WHERE
    fluxo = 'EXP' AND segmento = 'COURO' AND ano IN :lista_anos
"""

QUERY_EXP_COMPONENTE = """
SELECT
    ano,
    mes,
    componente,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano, 
    mes, 
    componente
"""

QUERY_EXP_COMPONENTE_PAIS = """
SELECT
    ano,
    mes,
    componente,
    pais,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    componente,
    pais
"""

QUERY_EXP_COMPONENTE_SH6 = """
SELECT
    ano,
    mes,
    componente,
    id_sh6,
    descricao_sh6,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    componente,
    id_sh6,
    descricao_sh6
"""

QUERY_EXP_VERTICAL = """
SELECT
    ano,
    mes,
    vertical,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano, 
    mes, 
    vertical
"""

QUERY_EXP_VERTICAL_PAIS = """
SELECT
    ano,
    mes,
    vertical,
    pais,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    vertical,
    pais
"""

QUERY_EXP_VERTICAL_SH6 = """
SELECT
    ano,
    mes,
    vertical,
    id_sh6,
    descricao_sh6,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'EXP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    vertical,
    id_sh6,
    descricao_sh6
"""

QUERY_IMP_CALCADOS = """
SELECT
    ano,
    mes,
    pares,
    valor,
    tipo,
    pais
FROM
    comex
WHERE
    fluxo = 'IMP' AND segmento = 'CALCADO' AND ano IN :lista_anos
"""

QUERY_IMP_COURO = """
SELECT
    ano,
    mes,
    valor,
    tipo,
    pais
FROM
    comex
WHERE
    fluxo = 'IMP' AND segmento = 'COURO' AND ano IN :lista_anos
"""

QUERY_IMP_COMPONENTE = """
SELECT
    ano,
    mes,
    componente,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano, 
    mes, 
    componente
"""

QUERY_IMP_COMPONENTE_PAIS = """
SELECT
    ano,
    mes,
    componente,
    pais,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    componente,
    pais
"""

QUERY_IMP_COMPONENTE_SH6 = """
SELECT
    ano,
    mes,
    componente,
    id_sh6,
    descricao_sh6,
    SUM(valor) AS valor
FROM
    comex_componente
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    componente,
    id_sh6,
    descricao_sh6
"""

QUERY_IMP_VERTICAL = """
SELECT
    ano,
    mes,
    vertical,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano, 
    mes, 
    vertical
"""

QUERY_IMP_VERTICAL_PAIS = """
SELECT
    ano,
    mes,
    vertical,
    pais,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    vertical,
    pais
"""

QUERY_IMP_VERTICAL_SH6 = """
SELECT
    ano,
    mes,
    vertical,
    id_sh6,
    descricao_sh6,
    SUM(valor) AS valor
FROM
    comex_vertical
WHERE
    fluxo = 'IMP' AND ano IN :lista_anos
GROUP BY
    ano,
    mes,
    vertical,
    id_sh6,
    descricao_sh6
"""

QUERY_EMPREGO_CALCADOS = """
SELECT ano,
       mes,
       subclasse,
       saldo_movimentacao
FROM emprego_calcados
WHERE ano IN :lista_anos
"""

QUERY_IPCA_CALCADOS = """
SELECT 
    ano,
    mes,
    ipca_mes,
    ipca_12_meses
FROM ipca_calcados
WHERE ano IN :lista_anos
"""

QUERY_EMPREGO_COURO = """
SELECT ano,
       mes,
       subclasse,
       saldo_movimentacao
FROM emprego_couro
WHERE ano IN :lista_anos
"""

QUERY_IPCA_GERAL = """
SELECT 
    ano,
    mes,
    ipca_mes_geral,
    ipca_12_meses_geral
FROM ipca_geral
WHERE ano IN :lista_anos
"""

QUERY_IND_TRANSFORMACAO = """
SELECT 
    ano,
    mes,
    descricao,
    taxa_mensal,
    taxa_acumulado
FROM ind_transformacao
WHERE ano IN :lista_anos
"""

QUERY_TAXA_DESEMPREGO = """
SELECT
    ano,
    mes,
    trimestre_movel,
    fora_forca_trabalho,
    forca_trabalho,
    forca_trabalho_desocupada,
    forca_trabalho_ocupada,
    total,
    (forca_trabalho_desocupada/forca_trabalho) * 100 AS taxa_desemprego
FROM tx_desemprego
WHERE ano IN :lista_anos
"""

QUERY_IBC_BR = """
SELECT
    ano,
    mes,
    ibc_mensal,
    ibc_mes_anterior,
    ibc_acumulado
FROM ibc
WHERE ano IN :lista_anos
"""

QUERY_TAXA_CAMBIO = """
SELECT
    ano,
    mes,
    taxa_cambio,
    taxa_cambio_mensal,
    taxa_cambio_acumulado,
    taxa_cambio_mes_anterior,
    media_movel_3
FROM tx_cambio
WHERE ano IN :lista_anos
"""

QUERY_EXPECTATIVAS = """
SELECT
    ano,
    mes,
    expectativa_pib_25,
    expectativa_pib_26,
    expectativa_ipca_25,
    expectativa_ipca_26
FROM expectativas
WHERE ano IN :lista_anos
"""

QUERY_PREVISAO_EXP = """
SELECT
    ano,
    mes,
    variacao_verificada,
    prev_otimista,
    prev_pessimista
FROM previsao_exportacao
WHERE ano IN :lista_anos
"""

QUERY_PREVISAO_PRODUCAO = """
SELECT
    ano,
    mes,
    variacao_verificada,
    prev_otimista,
    prev_pessimista
FROM previsao_producao
WHERE ano IN :lista_anos
"""


def main():
    """
    Orquestra a execução de todas as tarefas de carga de dados
    com os parâmetros corretos.
    """

    # Parâmetros para queries de "lista" (Todos os Municípios)
    params = {
        "lista_anos": anos_de_interesse,
    }

    tasks = [
        # --- Queries  ---
        (QUERY_PRODUCAO, "assintecal_producao", params),
        (QUERY_VENDAS, "assintecal_vendas", params),
        (QUERY_EXP_CALCADOS, "assintecal_exp_calcados", params),
        (QUERY_IMP_CALCADOS, "assintecal_imp_calcados", params),
        (QUERY_EMPREGO_CALCADOS, "assintecal_emprego_calcados", params),
        (QUERY_IPCA_CALCADOS, "assintecal_ipca_calcados", params),
        (QUERY_EXP_COURO, "assintecal_exp_couro", params),
        (QUERY_IMP_COURO, "assintecal_imp_couro", params),
        (QUERY_EMPREGO_COURO, "assintecal_emprego_couro", params),
        (QUERY_EXP_VERTICAL, "assintecal_exp_vertical", params),
        (QUERY_EXP_VERTICAL_PAIS, "assintecal_exp_vertical_pais", params),
        (QUERY_EXP_VERTICAL_SH6, "assintecal_exp_vertical_sh6", params),
        (QUERY_IMP_VERTICAL, "assintecal_imp_vertical", params),
        (QUERY_IMP_VERTICAL_PAIS, "assintecal_imp_vertical_pais", params),
        (QUERY_IMP_VERTICAL_SH6, "assintecal_imp_vertical_sh6", params),
        (QUERY_EXP_COMPONENTE, "assintecal_exp_componente", params),
        (QUERY_EXP_COMPONENTE_PAIS, "assintecal_exp_componente_pais", params),
        (QUERY_EXP_COMPONENTE_SH6, "assintecal_exp_componente_sh6", params),
        (QUERY_IMP_COMPONENTE, "assintecal_imp_componente", params),
        (QUERY_IMP_COMPONENTE_PAIS, "assintecal_imp_componente_pais", params),
        (QUERY_IMP_COMPONENTE_SH6, "assintecal_imp_componente_sh6", params),
        (QUERY_IPCA_GERAL, "assintecal_ipca_geral", params),
        (QUERY_IND_TRANSFORMACAO, "assintecal_ind_transformacao", params),
        (QUERY_TAXA_DESEMPREGO, "assintecal_taxa_desemprego", params),
        (QUERY_IBC_BR, "assintecal_ibc_br", params),
        (QUERY_TAXA_CAMBIO, "assintecal_taxa_cambio", params),
        (QUERY_EXPECTATIVAS, "assintecal_expectativas", params),
        (QUERY_PREVISAO_EXP, "assintecal_previsao_exportacao", params),
        (QUERY_PREVISAO_PRODUCAO, "assintecal_previsao_producao", params),
    ]

    print("Iniciando script de carga de dados FILTRADOS para o Supabase.")

    total_tasks = len(tasks)
    for i, (query, table_name, params) in enumerate(tasks):
        print(
            f"\n==================== TAREFA {i + 1} de {total_tasks} ===================="
        )
        process_and_upload(query, table_name, local_engine, supabase, params=params)

    print("\nTodas as tarefas filtradas foram concluídas!")


if __name__ == "__main__":
    main()


# %%
