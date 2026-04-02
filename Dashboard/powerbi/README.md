# 📈 Dashboard de Business Intelligence - EduSignal

Esta pasta contém a documentação e os registros visuais da camada de BI do projeto. O dashboard foi desenvolvido no **Power BI Desktop** e consome dados diretamente do Data Warehouse local (**PostgreSQL/Docker**).

## 🔍 Foco da Análise
O objetivo deste painel é fornecer uma visão geoespacial e analítica das taxas de abandono escolar, segmentadas por:
* **Série:** 1º, 2º e 3º ano do Ensino Médio.
* **Tipo de Rede:** Estadual, Federal, Municipal e Privada.
* **Localização:** Filtros dinâmicos por Estado (UF) e Município.

## 🛠️ Recursos Implementados
* **Análise Geoespacial:** Mapa de bolhas identificando a densidade de abandono em todo o território nacional.
* **KPIs de Desempenho:** Cartões com taxas médias dinâmicas e total de matrículas.
* **Gráficos de Tendência:** Comparativo de abandono entre as séries para identificar o maior gargalo (1º Ano do EM).
* **Treemap de Matrículas:** Proporção de alunos por tipo de rede de ensino.

## 🖼️ Visualização
> **Nota:** Devido ao limite de tamanho do GitHub (100MB), o arquivo `.pbix` original (~197MB) não está disponível para download direto. Abaixo está o registro visual da interface:

![Dashboard EduSignal Analytics](visual_inicial.png)

## 🚀 Como Replicar
1. Suba a infraestrutura de banco de dados usando o `docker-compose.yml` na pasta `/database`.
2. Execute o script `src/processing/create_master_table.py` para gerar a tabela `escolas_master_gold`.
3. No Power BI, utilize o conector do PostgreSQL apontando para `localhost:5432` com as credenciais configuradas no projeto.
