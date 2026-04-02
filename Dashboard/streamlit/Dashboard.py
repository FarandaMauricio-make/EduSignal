import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EduSignal: Inteligência Educacional", layout="wide")

# --- UI/UX: CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="stMetricValue"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3d425c;
        color: #00d4ff !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] {
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ccd1d1 !important;
    }
    .stMarkdown h3 { color: #00d4ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1e2130;
        border-radius: 10px 10px 0px 0px;
        color: white;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00d4ff; color: #0e1117; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")
    return pd.read_sql("SELECT * FROM escolas_master_gold", engine)

try:
    df_raw = carregar_dados()

    # --- BARRA LATERAL: FILTROS ---
    st.sidebar.title("⚙️ Configurações")
    ufs_disponiveis = sorted(df_raw['uf'].unique())
    uf_selecionada = st.sidebar.multiselect("Filtrar por UF:", options=ufs_disponiveis, default=ufs_disponiveis)
    df = df_raw[df_raw['uf'].isin(uf_selecionada)]

    # --- CABEÇALHO ---
    st.title("🎓 EduSignal: A Crise Invisível de 2021")
    st.markdown("### Monitoramento de Evasão Escolar Pós-Pandemia")
    
    # --- ORGANIZAÇÃO POR ABAS ---
    tab_geral, tab_9ano, tab_medio = st.tabs(["📊 Visão Integrada", "🏫 9º Ano Fundamental", "🚀 Ensino Médio"])

    # ---------------------------------------------------------
    # ABA 1: VISÃO INTEGRADA
    # ---------------------------------------------------------
    with tab_geral:
        st.markdown("## 🔍 Panorama Geral: O Salto do Abandono")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Escolas Analisadas", len(df))

        # KPI 2: Infraestrutura Crítica
        col2.metric("Escolas sem Internet", df[df['tem_internet'] == 0].shape[0])
        
        # KPI 3: Média do Fundamental
        col3.metric("Média Abandono 9º EF", f"{df['abandono_9ef'].mean():.2f}%")
        
        # KPI 4: Média Global do Ensino Médio (1º, 2º e 3º anos)
        media_em_global = df[['abandono_1em', 'abandono_2em', 'abandono_3em']].mean(axis=1).mean()
        col4.metric("Média Abandono Médio", f"{media_em_global:.2f}%")
        
        st.markdown("""
        #### 💡 Insight Central: A Jornada do Abandono
        O gráfico abaixo revela a 'quebra' de vínculo conforme o aluno avança. O **1º ano do Ensino Médio** é o maior gargalo nacional, 
        onde a pressão para ingressar no mercado de trabalho e o choque de complexidade pós-pandemia resultaram em picos de evasão.
        """)

        medias_series = pd.DataFrame({
            'Série': ['9º Fundamental', '1º Médio', '2º Médio', '3º Médio'],
            'Taxa de Abandono (%)': [df['abandono_9ef'].mean(), df['abandono_1em'].mean(), 
                                     df['abandono_2em'].mean(), df['abandono_3em'].mean()]
        })
        
        fig_jornada = px.line(medias_series, x='Série', y='Taxa de Abandono (%)', markers=True, template="plotly_dark")
        fig_jornada.update_traces(line_color='#00d4ff', marker=dict(size=12))
        st.plotly_chart(fig_jornada, use_container_width=True)

    # ---------------------------------------------------------
    # ABA 2: 9º ANO FUNDAMENTAL
    # ---------------------------------------------------------
    with tab_9ano:
        st.header("🏫 9º Ano: A Transição Crítica")
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.subheader("🌐 O Abismo Digital no Fundamental")
            df_plot_9 = df.groupby('tem_internet')['abandono_9ef'].mean().reset_index()
            df_plot_9['Status'] = df_plot_9['tem_internet'].map({1: 'Com Internet', 0: 'Sem Internet'})
            fig9 = px.bar(df_plot_9, x='Status', y='abandono_9ef', color='Status', template="plotly_dark",
                          color_discrete_map={'Com Internet': '#00d4ff', 'Sem Internet': '#FF4B4B'}, text_auto='.2f')
            st.plotly_chart(fig9, use_container_width=True)
        
        with c2:
            st.markdown("""
            #### 💡 O Alerta do 9º Ano
            No final do ciclo fundamental, o abandono em escolas **sem internet** é visivelmente superior. 
            Em 2021, a falta de conectividade isolou alunos que estavam prestes a mudar de ciclo, facilitando a desistência.
            """)

        st.subheader("📍 Dispersão por Estado (9º Ano)")
        fig_box_9 = px.box(df, x='uf', y='abandono_9ef', color='uf', template="plotly_dark")
        st.plotly_chart(fig_box_9, use_container_width=True)

        # TABELA DE PRIORIZAÇÃO ADICIONADA PARA 9º ANO
        st.subheader("🚨 Priorização Fundamental: Escolas com Abandono 9º ano > 10%")
        df_prioridade_9 = df[df['abandono_9ef'] > 10].sort_values('abandono_9ef', ascending=False)
        st.dataframe(df_prioridade_9[['nome_escola', 'uf', 'abandono_9ef', 'tem_internet']], use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # ABA 3: ENSINO MÉDIO
    # ---------------------------------------------------------
    with tab_medio:
        st.header("🚀 Ensino Médio: O Desafio da Permanência")
        
        st.markdown("""
        #### 💡 Análise por Série do Médio
        Observe como o abandono no **1º ano (1EM)** é desproporcional. Políticas de combate à evasão precisam focar 
        imediatamente na recepção deste aluno que vem do Fundamental.
        """)

        df_med_net = df.groupby('tem_internet')[['abandono_1em', 'abandono_2em', 'abandono_3em']].mean().reset_index()
        df_med_net['Status'] = df_med_net['tem_internet'].map({1: 'Com Internet', 0: 'Sem Internet'})
        df_melted = df_med_net.melt(id_vars='Status', value_vars=['abandono_1em', 'abandono_2em', 'abandono_3em'],
                                     var_name='Série', value_name='Taxa de Abandono')

        fig_compare = px.bar(df_melted, x='Série', y='Taxa de Abandono', color='Status', barmode='group',
                             template="plotly_dark", color_discrete_map={'Com Internet': '#00d4ff', 'Sem Internet': '#FF4B4B'})
        st.plotly_chart(fig_compare, use_container_width=True)

        # TABELA DE PRIORIZAÇÃO ATUALIZADA COM OS 3 ANOS DO ENSINO MÉDIO
        st.subheader("🚨 Priorização Médio: Escolas com alto índice de abandono")
        st.markdown("Filtro aplicado: Escolas onde pelo menos uma série do Ensino Médio possui Abandono > 20%")
        
        df_prioridade_med = df[
            (df['abandono_1em'] > 20) | (df['abandono_2em'] > 20) | (df['abandono_3em'] > 20)
        ].sort_values('abandono_1em', ascending=False)
        
        st.dataframe(
            df_prioridade_med[['nome_escola', 'uf', 'abandono_1em', 'abandono_2em', 'abandono_3em', 'tem_internet']], 
            use_container_width=True, 
            hide_index=True
        )

except Exception as e:
    st.error(f"Erro ao carregar dashboard: {e}")

st.caption("EduSignal 2026 | Tecnologia a serviço da Educação Brasileira")