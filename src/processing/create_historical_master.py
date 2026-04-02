import pandas as pd
from sqlalchemy import create_engine, inspect

# --- MINHA CONEXÃO ---
engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

def gerar_master_historica():
    print("--- 🏆 CONSTRUINDO A MASTER HISTÓRICA FINAL (2021-2024) ---")
    
    anos = [2021, 2022, 2023, 2024]
    lista_queries = []
    inspector = inspect(engine)

    for ano in anos:
        # AJUSTE COM BASE NO SEU CHECK DE TABELAS:
        if ano == 2021:
            tabela_escolas = 'escolas_2021_raw'
            tabela_rend = 'indicadores_rendimento_raw'
        else:
            tabela_escolas = f'escolas_{ano}_raw'
            tabela_rend = f'indicadores_rendimento_{ano}_raw'

        # Verifico se as tabelas existem antes de tentar o JOIN
        if inspector.has_table(tabela_escolas) and inspector.has_table(tabela_rend):
            print(f"🔗 Unindo dados de {ano} (Tabelas: {tabela_escolas} + {tabela_rend})")
            
            sql = f"""
            SELECT 
                {ano} as ano_referencia,
                c."CO_ENTIDADE" as id_escola,
                c."NO_ENTIDADE" as nome_escola,
                c."SG_UF" as uf,
                c."IN_INTERNET" as tem_internet,
                -- Limpeza: transformando '--' em NULL e ',' em '.' para cálculos
                CAST(NULLIF(REPLACE(CAST(r."3_CAT_FUN_09" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_9ef,
                CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_01" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_1em,
                CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_02" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_2em,
                CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_03" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_3em
            FROM {tabela_escolas} c
            INNER JOIN {tabela_rend} r ON 
                CAST(c."CO_ENTIDADE" AS NUMERIC) = CAST(r."CO_ENTIDADE" AS NUMERIC)
            """
            lista_queries.append(sql)
        else:
            print(f"⚠️ Atenção: Tabelas de {ano} NÃO encontradas.")

    if not lista_queries:
        print("❌ Nenhuma query gerada. Verifique os nomes das tabelas.")
        return

    query_final = " UNION ALL ".join(lista_queries)

    try:
        print("⏳ Processando união massiva no Docker...")
        df_history = pd.read_sql(query_final, engine)
        
        # Só mantemos quem tem algum dado de abandono preenchido
        df_history = df_history.dropna(subset=['abandono_9ef', 'abandono_1em', 'abandono_2em', 'abandono_3em'], how='all')
        
        # Salvamos na tabela Gold que alimentará o Streamlit
        df_history.to_sql('escolas_master_historica_gold', engine, if_exists='replace', index=False)
        print(f"🚀 SUCESSO! Master Histórica criada com {len(df_history)} registros totais.")

    except Exception as e:
        print(f"❌ Erro na união histórica: {e}")

if __name__ == "__main__":
    gerar_master_historica()