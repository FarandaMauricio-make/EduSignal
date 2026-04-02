import pandas as pd
from sqlalchemy import create_engine

# --- CONEXÃO COM O MEU DATA WAREHOUSE ---
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"
engine = create_engine(DB_URL)

def analise_infraestrutura_detalhada():
    print("--- 🏫 ANÁLISE DE INFRAESTRUTURA DAS ESCOLAS ---")
    
    # Vou selecionar colunas chave para o risco educacional
    # IN_LABORATORIO_INFORMATICA: Tem lab de TI?
    # IN_BIBLIOTECA: Tem biblioteca?
    # IN_AGUA_POTAVEL: Tem o básico (água)?
    # IN_ENERGIA_INEXISTENTE: A escola está no escuro?
    query = """
    SELECT 
        "IN_INTERNET",
        "IN_LABORATORIO_INFORMATICA",
        "IN_BIBLIOTECA",
        "IN_AGUA_POTAVEL",
        "IN_ENERGIA_INEXISTENTE"
    FROM escolas_2021_raw 
    LIMIT 1000
    """
    
    try:
        df = pd.read_sql(query, engine)
        total = len(df)

        # Vou criar um dicionário para automatizar as contas
        indicadores = {
            "Internet": "IN_INTERNET",
            "Laboratório de TI": "IN_LABORATORIO_INFORMATICA",
            "Biblioteca": "IN_BIBLIOTECA",
            "Água Potável": "IN_AGUA_POTAVEL"
        }

        print(f"\n📊 RESUMO DE INFRAESTRUTURA (Amostra: {total} escolas):")
        for nome, coluna in indicadores.items():
            qtd = df[coluna].sum()
            perc = (qtd / total) * 100
            print(f"- {nome}: {int(qtd)} escolas ({perc:.1f}%)")

        # Análise especial: Escolas sem energia
        sem_energia = df["IN_ENERGIA_INEXISTENTE"].sum()
        if sem_energia > 0:
            print(f"\n⚠️ ALERTA DE RISCO: {int(sem_energia)} escolas não possuem energia elétrica!")

    except Exception as e:
        print(f"❌ Erro na consulta: {e}")

if __name__ == "__main__":
    analise_infraestrutura_detalhada()