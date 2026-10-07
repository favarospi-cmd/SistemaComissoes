import streamlit as st
import pandas as pd
import plotly.express as px
from utils import buscar_todas_parcelas, formatar_moeda

st.title(" Dashboards & Análises")

user_id = st.session_state.usuario_logado.id
df_tudo = buscar_todas_parcelas(user_id)

if df_tudo.empty:
    st.warning("⚠️ Nenhum dado encontrado no banco para gerar os dashboards. Faça lançamentos primeiro.")
else:
    total_geral = df_tudo['Valor Parcela'].sum()
    total_pago = df_tudo[df_tudo['Status'] == 'PAGO']['Valor Parcela'].sum()
    total_aberto = df_tudo[df_tudo['Status'] == 'EM ABERTO']['Valor Parcela'].sum()
    total_atrasado = df_tudo[df_tudo['Status'] == 'ATRASADO']['Valor Parcela'].sum()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Total Geral (Bruto)", f"R$ {formatar_moeda(total_geral)}")
    kpi2.metric("✅ Total Recebido", f"R$ {formatar_moeda(total_pago)}", f"{(total_pago/total_geral*100) if total_geral > 0 else 0:.1f}% do total")
    kpi3.metric(" A Receber (Em Aberto)", f"R$ {formatar_moeda(total_aberto)}")
    kpi4.metric("⚠️ Atrasado", f"R$ {formatar_moeda(total_atrasado)}")
    
    st.divider()
    
    st.subheader("🥧 Distribuição por Status")
    df_status = df_tudo.groupby('Status')['Valor Parcela'].sum().reset_index()
    fig_pizza = px.pie(df_status, values='Valor Parcela', names='Status', 
                       color_discrete_map={'PAGO': '#2ecc71', 'EM ABERTO': '#f1c40f', 'ATRASADO': '#e74c3c'},
                       hole=0.4)
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pizza, use_container_width=True)
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📊 Faturamento por Categoria")
        df_cat = df_tudo.groupby('Categoria')['Valor Parcela'].sum().reset_index()
        fig_barra = px.bar(df_cat, x='Categoria', y='Valor Parcela', color='Categoria', text_auto='.2s')
        fig_barra.update_layout(showlegend=False)
        st.plotly_chart(fig_barra, use_container_width=True)
        
    with col_graf2:
        st.subheader("🏢 Faturamento por Tipo")
        df_tipo = df_tudo.groupby('Tipo')['Valor Parcela'].sum().reset_index()
        fig_barra2 = px.bar(df_tipo, x='Tipo', y='Valor Parcela', color='Tipo', text_auto='.2s')
        fig_barra2.update_layout(showlegend=False)
        st.plotly_chart(fig_barra2, use_container_width=True)
        
    st.subheader("📅 Previsão de Recebimento (Próximos Meses)")
    df_aberto_graf = df_tudo[df_tudo['Status'] == 'EM ABERTO'].copy()
    df_aberto_graf['Mes_Venc'] = pd.to_datetime(df_aberto_graf['Data Vencimento']).dt.to_period('M').astype(str)
    df_previsao = df_aberto_graf.groupby('Mes_Venc')['Valor Parcela'].sum().reset_index()
    
    fig_linha = px.line(df_previsao, x='Mes_Venc', y='Valor Parcela', markers=True)
    fig_linha.update_traces(line_color='#3b82f6', marker_size=10)
    st.plotly_chart(fig_linha, use_container_width=True)