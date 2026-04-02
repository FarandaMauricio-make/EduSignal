import pandas as pd
import os
import glob
from sqlalchemy import create_engine

# --- MINHA CONEXÃO COM O BANCO ---
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"
engine = create_engine(DB_URL)

def buscar_arquivo(diretorio, padrao):
    """Função para encontrar um arquivo mesmo com subpastas variadas"""
    caminho_busca = os.path.join(diretorio, "**", padrao)
    arquivos = glob.glob(caminho_busca, recursive=True)
    return arquivos[0] if arquivos else None

def carregar_dados_por_ano(anos):
    pasta_base = r'G:\Meu Drive\Projetos\EduSignal\src\data_raw'
    
    for ano in anos:
        print(f"\n--- 📅 PROCESSANDO {ano} ---")
        diretorio_ano = os.path.join(pasta_base, str(ano))
        
        # 1. BUSCA FLEXÍVEL DO CENSO (.csv)
        path_censo = buscar_arquivo(diretorio_ano, f"microdados_ed_basica_{ano}.csv")
        
        # 2. BUSCA FLEXÍVEL DO RENDIMENTO (.xlsx)
        path_rend = buscar_arquivo(diretorio_ano, f"tx_rend_escolas_{ano}.xlsx")

        # --- PROCESSAMENTO DO CENSO ---
        if path_censo:
            try:
                print(f"⏳ Lendo Censo: {os.path.basename(path_censo)}")
                df_censo = pd.read_csv(path_censo, sep=';', encoding='latin1', low_memory=False)
                df_censo.to_sql(f'escolas_{ano}_raw', engine, if_exists='replace', index=False)
                print(f"✅ Censo {ano} enviado!")
            except Exception as e:
                print(f"❌ Erro no Censo {ano}: {e}")
        else:
            print(f"⚠️ Censo {ano} não encontrado em {diretorio_ano}")

        # --- PROCESSAMENTO DO RENDIMENTO ---
        if path_rend:
            try:
                print(f"⏳ Lendo Rendimento: {os.path.basename(path_rend)}")
                df_rend = pd.read_excel(path_rend, skiprows=8)
                df_rend.to_sql(f'indicadores_rendimento_{ano}_raw', engine, if_exists='replace', index=False)
                print(f"✅ Rendimento {ano} enviado!")
            except Exception as e:
                print(f"❌ Erro no Rendimento {ano}: {e}")
        else:
            print(f"⚠️ Rendimento {ano} não encontrado em {diretorio_ano}")

if __name__ == "__main__":
    meus_anos = [2022, 2023, 2024]
    carregar_dados_por_ano(meus_anos)