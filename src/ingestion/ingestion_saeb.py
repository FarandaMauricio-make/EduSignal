import pandas as pd
import os
from sqlalchemy import create_engine

# --- MINHA CONEXÃO COM O DOCKER ---
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"
engine = create_engine(DB_URL)

def carregar_saeb_escola():
    print("--- 📝 PROCESSANDO RESULTADOS DO SAEB 2021 ---")
    
    # Caminho onde os arquivos do SAEB estão (ajustado para sua estrutura)
    caminho_pasta = r'G:\Meu Drive\Projetos\EduSignal\src\data_raw\microdados_censo_escolar_2021\microdados_saeb_2021_ensino_fundamental_e_medio\DADOS'
    arquivo_nome = 'TS_ESCOLA.csv' # Verifique se a extensão é .csv ou .txt
    
    caminho_completo = os.path.join(caminho_pasta, arquivo_nome)

    try:
        # Lendo os dados do Saeb
        # DICA: Arquivos do Saeb costumam usar vírgula ou ponto-e-vírgula. 
        # Vou usar sep=None para o pandas detectar automaticamente!
        print(f"⏳ Lendo arquivo: {arquivo_nome}")
        df_saeb = pd.read_csv(caminho_completo, sep=None, engine='python', encoding='latin1')

        # Mostrando as primeiras colunas para eu aprender o que tem dentro
        print(f"✅ Colunas encontradas: {list(df_saeb.columns[:10])}")

        # Subindo para o banco (Tabela: saeb_escolas_raw)
        print("🐘 Enviando para o PostgreSQL...")
        df_saeb.to_sql('saeb_escolas_raw', engine, if_exists='replace', index=False)
        
        print("🚀 SUCESSO! Agora temos as notas e a infraestrutura no banco.")

    except Exception as e:
        print(f"❌ Erro ao carregar SAEB: {e}")

if __name__ == "__main__":
    carregar_saeb_escola()