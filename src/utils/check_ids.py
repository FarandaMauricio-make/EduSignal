import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")

print("--- 🔍 DIAGNÓSTICO DE FORMATO DE ID ---")

# Verificando 3 exemplos do Censo
censo = pd.read_sql('SELECT "CO_ENTIDADE" FROM escolas_2021_raw LIMIT 3', engine)
print(f"Exemplos Censo (CO_ENTIDADE): \n{censo['CO_ENTIDADE'].tolist()}")

# Verificando 3 exemplos do SAEB
saeb = pd.read_sql('SELECT "ID_ESCOLA" FROM saeb_escolas_raw LIMIT 3', engine)
print(f"Exemplos SAEB (ID_ESCOLA): \n{saeb['ID_ESCOLA'].tolist()}")