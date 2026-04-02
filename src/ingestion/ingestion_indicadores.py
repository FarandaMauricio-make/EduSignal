import pandas as pd
import os
from sqlalchemy import create_engine

# --- CONEXÃO COM O DOCKER ---
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"
engine = create_engine(DB_URL)

def carregar_indicadores_rendimento():
    print("--- 📝 PROCESSANDO TAXAS DE RENDIMENTO 2021 (LINHA 9) ---")
    
    caminho_pasta = r'G:\Meu Drive\Projetos\EduSignal\src\data_raw\tx_rend_escolas_2021\tx_rend_escolas_2021'
    arquivo_nome = 'tx_rend_escolas_2021.xlsx'
    caminho_completo = os.path.join(caminho_pasta, arquivo_nome)

    try:
        print("⏳ Lendo Excel a partir da linha 9...")
        # skiprows=8 pula as 8 primeiras linhas. A linha 9 vira o cabeçalho.
        df_rend = pd.read_excel(caminho_completo, skiprows=8)

        # Converte nomes para string e limpa colunas vazias (Unnamed)
        df_rend.columns = [str(col) for col in df_rend.columns]
        df_rend = df_rend.loc[:, ~df_rend.columns.str.contains('Unnamed')]
        
        # --- DIAGNÓSTICO DE COLUNAS ---
        print("\n🔍 LISTA DAS PRIMEIRAS 20 COLUNAS ENCONTRADAS:")
        print(df_rend.columns.tolist()[:20])

        # Subindo para o banco
        print("\n🐘 Enviando indicadores para o PostgreSQL...")
        df_rend.to_sql('indicadores_rendimento_raw', engine, if_exists='replace', index=False)
        
        print(f"🚀 SUCESSO! {len(df_rend)} linhas carregadas.")

    except Exception as e:
        print(f"❌ Erro ao carregar indicadores: {e}")

if __name__ == "__main__":
    carregar_indicadores_rendimento()