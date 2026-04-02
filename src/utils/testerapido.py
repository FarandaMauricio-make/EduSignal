from sqlalchemy import create_engine, inspect

# Conectando ao seu banco no Docker
engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")
inspector = inspect(engine)

print("--- 📋 TABELAS ENCONTRADAS NO BANCO ---")
for table_name in inspector.get_table_names():
    print(f"🔹 {table_name}")

"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

# Vamos listar o nome de TODAS as colunas que o Excel gerou no banco
colunas = pd.read_sql('SELECT * FROM indicadores_rendimento_raw LIMIT 0', engine).columns.tolist()

print("--- 🔍 COLUNAS ENCONTRADAS NA TABELA DE INDICADORES ---")
for col in colunas:
    # Filtro para mostrar apenas as que parecem ser de ABANDONO ou APROVAÇÃO
    if 'ABANDONO' in col or 'APROVACAO' in col or 'ENTIDADE' in col:
        print(f"-> {col}")
"""

"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

def inspecao_por_nome():
    print("--- 🔍 BUSCANDO ESCOLAS PELO NOME PARA DESVENDAR O ID ---")
    
    # Pegamos uma amostra de nomes do Censo
    df_censo = pd.read_sql('SELECT "CO_ENTIDADE", "NO_ENTIDADE" FROM escolas_2021_raw LIMIT 500', engine)
    
    # Pegamos uma amostra do SAEB (buscando colunas que pareçam nomes)
    # Vou listar todas as colunas do SAEB de novo para garantir
    cols_saeb = pd.read_sql('SELECT * FROM saeb_escolas_raw LIMIT 0', engine).columns.tolist()
    print(f"Colunas disponíveis no SAEB: {cols_saeb}")

    # Tentativa de encontrar uma escola específica em ambas as tabelas
    # Vamos listar 10 escolas do SAEB para você comparar visualmente com o Censo
    amostra_saeb = pd.read_sql('SELECT "ID_ESCOLA", "ID_MUNICIPIO" FROM saeb_escolas_raw LIMIT 10', engine)
    
    print("\n📋 AMOSTRA DE DADOS DO SAEB:")
    print(amostra_saeb)
    
    print("\n📋 AMOSTRA DE DADOS DO CENSO:")
    print(df_censo.head(10))

if __name__ == "__main__":
    inspecao_por_nome()

"""    

"""

Verficando quais estados aparecem no arquivo do SAEB

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

# Vamos ver quais estados aparecem no seu arquivo do SAEB
ufs_saeb = pd.read_sql('SELECT DISTINCT "ID_UF" FROM saeb_escolas_raw', engine)
print(f"Estados (IDs) presentes no SAEB: {ufs_saeb['ID_UF'].tolist()}")

"""

"""
Este script é um teste rápido para verificar se os IDs das escolas do SAEB realmente existem no Censo Escolar.

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

print("--- 🧐 BUSCANDO INTERSECÇÃO REAL ---")

# Vamos pegar TODOS os IDs do SAEB e ver se algum existe no Censo
ids_saeb = pd.read_sql('SELECT DISTINCT "ID_ESCOLA" FROM saeb_escolas_raw', engine)
ids_censo = pd.read_sql('SELECT DISTINCT "CO_ENTIDADE" FROM escolas_2021_raw', engine)

# Transformamos em conjuntos (sets) para comparar
set_saeb = set(ids_saeb['ID_ESCOLA'])
set_censo = set(ids_censo['CO_ENTIDADE'])

interseccao = set_saeb.intersection(set_censo)

print(f"📍 IDs no SAEB: {len(set_saeb)}")
print(f"📍 IDs no Censo: {len(set_censo)}")
print(f"🤝 Escolas encontradas em AMBOS: {len(interseccao)}")

if len(interseccao) > 0:
    print(f"Exemplos de IDs que batem: {list(interseccao)[:3]}")

"""