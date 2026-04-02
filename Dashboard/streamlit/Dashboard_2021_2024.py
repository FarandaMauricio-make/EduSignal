import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO ---
# Defino o layout wide para aproveitar o espaço lateral para os filtros e KPIs
st.set_page_config(page_title="EduSignal | Data Intelligence", layout="wide", initial_sidebar_state="expanded")

# --- UI/UX: CUSTOM DESIGN SYSTEM (PREMIUM DARK) ---
# Estilização em CSS
st.markdown("""
    <style>
    .main { background-color: #080a11; color: #e0e0e0; }
    div[data-testid="stMetricContainer"] {
        background-color: rgba(30, 33, 48, 0.8);
        border: 1px solid #3d425c;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }
    label[data-testid="stMetricLabel"] { color: #8892b0 !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 2.4rem !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { background-color: #161b22; border-radius: 10px 10px 0 0; color: #8892b0; }
    .stTabs [aria-selected="true"] { background-color: #00d4ff !important; color: #080a11 !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_historical_data():
    # Carregamento da Master Gold unificada de 2021 a 2024
    engine = create_engine("postgresql://admin:password123@localhost:5432/edusignal_dw")
    df = pd.read_sql("SELECT * FROM escolas_master_historica_gold", engine)
    
    # --- LÓGICA DE VALIDAÇÃO DE CONFIABILIDADE ---
    # Escolas com 100% de abandono podem ser anomalias de registro ou unidades desativadas
    def validar_registro(row):
        # Se tem internet e 100% de abandono, a probabilidade de erro de censo é alta
        if (row['abandono_9ef'] == 100 or row['abandono_1em'] == 100) and row['tem_internet'] == 1:
            return "Inconsistente (Anomalia)"
        return "Confiável"
    
    df['trust_score'] = df.apply(validar_registro, axis=1)
    return df

try:
    df_raw = load_historical_data()

    # --- SIDEBAR: GOVERNANÇA E FILTROS ---
    st.sidebar.title("🛂 Governança de Dados")
    
    # Filtros Temporais e Geográficos
    anos = sorted(df_raw['ano_referencia'].unique())
    selected_years = st.sidebar.multiselect("Série Temporal", anos, default=anos)
    
    ufs = sorted(df_raw['uf'].unique())
    selected_ufs = st.sidebar.multiselect("Estados Filtrados", ufs, default=ufs)

    # SEÇÃO DE VALIDAÇÃO (Explicando o "Oxi" dos 100%)
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Verificadores de Integridade")
    
    remove_100 = st.sidebar.checkbox("Expurgar Escolas com 100% de Abandono", value=False, 
                                     help="Remove escolas que perderam todos os alunos. Útil para limpar a média de erros de registro ou unidades fechadas.")
    
    # Aplicação da filtragem de integridade
    df = df_raw[(df_raw['ano_referencia'].isin(selected_years)) & (df_raw['uf'].isin(selected_ufs))]
    
    if remove_100:
        df = df[(df['abandono_9ef'] < 100) & (df['abandono_1em'] < 100)]

    # --- DASHBOARD HEADER ---
    st.title("🛡️ EduSignal: Inteligência e Retenção Escolar")
    st.markdown("### Análise Longitudinal e Validação de Fluxo (2021-2024)")

    # --- EXPLICAÇÃO TÉCNICA (STORYTELLING) ---
    with st.expander("ℹ️ Entendendo a Validação de Dados (Picos de 100%)"):
        st.write("""
            **Por que vemos 100% de abandono?** Identificamos escolas que atingem o teto de 100% de evasão em todos os anos. Isso ocorre por três fatores principais:
            1. **Escolas de Baixa Matrícula:** Unidades rurais ou indígenas com poucos alunos (ex: 5 alunos), onde a desistência de todos eleva a taxa ao máximo.
            2. **Unidades Desativadas:** Escolas que encerraram atividades mas ainda constam no processamento do Censo.
            3. **Erro de Registro:** Inconsistências na migração de alunos entre sistemas estaduais e o INEP.
            
            *O filtro na barra lateral permite que você visualize a média 'limpa' dessas anomalias.*
        """)

    # --- ABAS ---
    tab_9ano, tab_medio, tab_comparativo = st.tabs(["🏫 9º Ano Fundamental", "🚀 Ensino Médio", "🔄 Cruzamento Geral"])

    # --- ABA 1: FUNDAMENTAL ---
    with tab_9ano:
        st.subheader("Performance 9º Ano: Ciclo de Saída")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Abandono Médio", f"{df['abandono_9ef'].mean():.2f}%")
        k2.metric("Pico Identificado", f"{df['abandono_9ef'].max():.1f}%")
        k3.metric("Escolas Válidas", f"{len(df[df['abandono_9ef'] > 0]):,}")
        k4.metric("Queda vs 2021", f"{(df[df['ano_referencia']==2021]['abandono_9ef'].mean() - df[df['ano_referencia']==2024]['abandono_9ef'].mean()):.2f}%")

        st.divider()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            df_9_time = df.groupby(['ano_referencia', 'uf'])['abandono_9ef'].mean().reset_index()
            fig_9_line = px.line(df_9_time, x='ano_referencia', y='abandono_9ef', color='uf', markers=True, 
                                 title="Evolução Temporal por Estado", template="plotly_dark")
            st.plotly_chart(fig_9_line, use_container_width=True)
        with c2:
            st.markdown("#### 🔍 Dispersão de Outliers")
            fig_9_box = px.box(df, x='ano_referencia', y='abandono_9ef', template="plotly_dark", color_discrete_sequence=['#00d4ff'])
            st.plotly_chart(fig_9_box, use_container_width=True)

    # --- ABA 2: ENSINO MÉDIO ---
    with tab_medio:
        st.subheader("Performance Ensino Médio: Ciclo de Retenção")
        df['media_em_total'] = df[['abandono_1em', 'abandono_2em', 'abandono_3em']].mean(axis=1)
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Média Ciclo Médio", f"{df['media_em_total'].mean():.2f}%")
        k2.metric("Gargalo 1º EM", f"{df['abandono_1em'].mean():.2f}%")
        k3.metric("Média s/ Internet", f"{df[df['tem_internet']==0]['media_em_total'].mean():.2f}%")
        k4.metric("Status Dados", "Válidos" if not remove_100 else "Filtrados")

        st.divider()

        c1, c2 = st.columns([2, 1])
        with c1:
            # Evolução comparativa das 3 séries do médio
            df_em_evol = df.groupby('ano_referencia')[['abandono_1em', 'abandono_2em', 'abandono_3em']].mean().reset_index()
            fig_em_line = go.Figure()
            colors = ['#FF4B4B', '#FFA500', '#00d4ff']
            names = ['1º Ano (Crítico)', '2º Ano', '3º Ano']
            for i, col in enumerate(['abandono_1em', 'abandono_2em', 'abandono_3em']):
                fig_em_line.add_trace(go.Scatter(x=df_em_evol['ano_referencia'], y=df_em_evol[col], name=names[i], line=dict(color=colors[i], width=3)))
            fig_em_line.update_layout(template="plotly_dark", title="Tendência por Ano do Ensino Médio")
            st.plotly_chart(fig_em_line, use_container_width=True)
        with c2:
            st.markdown("#### 🚨 Escolas de Risco Máximo (100% Evasão)")
            st.dataframe(df[df['media_em_total'] == 100][['nome_escola', 'uf']].head(10), hide_index=True)

    # --- ABA 3: CRUZAMENTO ---
    with tab_comparativo:
        st.subheader("🔄 Comparativo de Transição: Fundamental vs Médio")
        df_comp = df.groupby('ano_referencia').agg({'abandono_9ef': 'mean', 'media_em_total': 'mean'}).reset_index()
        fig_total = px.bar(df_comp, x='ano_referencia', y=['abandono_9ef', 'media_em_total'], barmode='group', 
                          template="plotly_dark", color_discrete_map={'abandono_9ef': '#8892b0', 'media_em_total': '#00d4ff'})
        st.plotly_chart(fig_total, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Falha no Carregamento: {e}")

st.caption("EduSignal Intelligence System | v4.2.0 | Governança Aplicada (2021-2024)")