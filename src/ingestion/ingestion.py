import pandas as pd
import os
from sqlalchemy import create_engine

# --- MINHA CONEXÃO COM O BANCO ---
# Aqui eu defino o "endereço" do meu banco Postgres que está rodando no Docker.
# O padrão é: postgresql://usuario:senha@local:porta/nome_do_banco
DB_URL = "postgresql://admin:password123@localhost:5432/edusignal_dw"

# O engine é o "tradutor" que permite o Pandas conversar com o banco de dados.
engine = create_engine(DB_URL)

def carregar_dados_censo():
    print("--- 🚀 HORA DE SUBIR OS DADOS DO CENSO 2021 ---")
    
    # Este é o caminho exato que eu encontrei no meu computador.
    # Note que usei r'' (raw string) antes das aspas para o Windows não 
    # se confundir com as barras invertidas (\).
    caminho_pasta = r'G:\Meu Drive\Projetos\EduSignal\src\data_raw\microdados_censo_escolar_2021\microdados_ed_basica_2021\dados'
    nome_arquivo = 'microdados_ed_basica_2021.csv'
    
    # Junto a pasta e o nome do arquivo para ter o caminho completo
    caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
    
    # Verifico se eu realmente estou apontando para o lugar certo
    if not os.path.exists(caminho_completo):
        print(f"❌ Opa! Não achei o arquivo em: {caminho_completo}")
        print("Preciso conferir se o nome do arquivo .csv está certinho dentro daquela pasta.")
        return

    try:
        # --- LENDO O ARQUIVO ---
        # sep=';' -> No Censo 2021, os dados são separados por ponto e vírgula.
        # encoding='latin1' -> Uso esse para não quebrar os acentos (ç, á, õ).
        # nrows=10000 -> Vou subir só 10 mil linhas agora para testar se tudo funciona rápido.
        print("⏳ Lendo o CSV... (Isso pode demorar um pouco porque o arquivo é pesado)")
        
        # Agora leio o arquivo inteiro para garantir que o JOIN funcione!
        df = pd.read_csv(caminho_completo, sep=';', encoding='latin1', low_memory=False)
        
        # --- LIMPANDO OS DADOS ---
        # O INEP usa '-' quando não tem informação. Vou trocar por 'None' 
        # para o banco entender que é um valor nulo de verdade.
        df = df.replace('-', None)

        # --- MANDANDO PARA O DOCKER ---
        # 'escolas_2021_raw' é o nome da tabela que o Python vai criar para mim.
        # if_exists='replace' -> Se eu rodar de novo, ele apaga a tabela velha e cria uma nova.
        print("🐘 Enviando os dados para o PostgreSQL no Docker...")
        df.to_sql('escolas_2021_raw', engine, if_exists='replace', index=False)
        
        print(f"✅ CONCLUÍDO! Já tenho {len(df)} escolas no meu banco de dados.")

    except Exception as e:
        print(f"❌ Deu erro no processamento: {e}")

if __name__ == "__main__":
    # Primeiro testo se o banco está ouvindo
    try:
        with engine.connect() as conn:
            print("🔗 Conexão com o Docker: ESTABELECIDA!")
            carregar_dados_censo()
    except Exception as e:
        print(f"❌ Não consegui conectar no banco. O Docker está aberto?")
        print(f"Erro: {e}")