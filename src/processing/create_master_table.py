import pandas as pd
from sqlalchemy import create_engine

# --- CONEXÃO ---
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"
engine = create_engine(DB_URL)

def criar_tabela_mestre_final():
    print("--- 🏆 CONSTRUINDO A TABELA MASTER EDUSIGNAL (FUNDAMENTAL + MÉDIO) ---")
    
    query = """
    SELECT 
        c."CO_ENTIDADE" as id_escola,
        c."NO_ENTIDADE" as nome_escola,
        c."SG_UF" as uf,
        c."IN_INTERNET" as tem_internet,
        -- Ensino Fundamental (9º ano)
        CAST(NULLIF(REPLACE(CAST(r."3_CAT_FUN_09" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_9ef,
        -- Ensino Médio (1º, 2º e 3º ano)
        CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_01" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_1em,
        CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_02" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_2em,
        CAST(NULLIF(REPLACE(CAST(r."3_CAT_MED_03" AS TEXT), ',', '.'), '--') AS NUMERIC) as abandono_3em
    FROM escolas_2021_raw c
    INNER JOIN indicadores_rendimento_raw r ON 
        CAST(c."CO_ENTIDADE" AS NUMERIC) = CAST(r."CO_ENTIDADE" AS NUMERIC)
    """
    
    try:
        print("⏳ Cruzando dados e limpando caracteres especiais...")
        df_master = pd.read_sql(query, engine)
        
        # AJUSTE: Removemos apenas linhas onde TODAS as taxas de abandono estão vazias
        # Assim mantemos escolas que só têm Fundamental ou só têm Médio.
        colunas_abandono = ['abandono_9ef', 'abandono_1em', 'abandono_2em', 'abandono_3em']
        df_master = df_master.dropna(subset=colunas_abandono, how='all')
        
        print(f"✅ SUCESSO! Master Table criada com {len(df_master)} escolas.")
        
        # Salvando a versão GOLD
        df_master.to_sql('escolas_master_gold', engine, if_exists='replace', index=False)
        print("🚀 EduSignal: Dados unificados e prontos para análise multissérie!")

    except Exception as e:
        print(f"❌ Erro na união: {e}")

if __name__ == "__main__":
    criar_tabela_mestre_final()

"""

Este script é para listar o nome real das colunas nas tabelas 'escolas_2021_raw' e 'saeb_escolas_raw' do banco de dados 'edusignal_dw'.

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

# Vamos listar o nome real das colunas no banco
for tabela in ['escolas_2021_raw', 'saeb_escolas_raw']:
    colunas = pd.read_sql(f"SELECT * FROM {tabela} LIMIT 0", engine).columns.tolist()
    print(f"Colunas na tabela {tabela}: {colunas}")

"""
