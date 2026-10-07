import streamlit as st
import pandas as pd
from utils import buscar_todas_parcelas, formatar_moeda

st.title("📑 Relatórios (Tabela Dinâmica)")

user_id = st.session_state.usuario_logado.id

st.subheader("🔍 Filtros")
col_f1, col_f2 = st.columns(2)

with col_f1:
    status_filtro = st.selectbox("Status das Parcelas:", ["TODOS", "PAGO", "EM ABERTO"], index=0, key="filtro_status_relatorio")

df_tudo = buscar_todas_parcelas(user_id)

if df_tudo.empty:
    st.warning("️ Nenhum dado encontrado no banco para gerar o relatório.")
else:
    if status_filtro != "TODOS":
        df_relatorio = df_tudo[df_tudo['Status'] == status_filtro].copy()
    else:
        df_relatorio = df_tudo.copy()
    
    df_relatorio['DataDT'] = pd.to_datetime(df_relatorio['Data Vencimento'])
    df_relatorio['Ano'] = df_relatorio['DataDT'].dt.year
    df_relatorio['Mes'] = df_relatorio['DataDT'].dt.month
    
    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    df_relatorio['Nome_Mes'] = df_relatorio['Mes'].map(meses_pt)
    
    anos_disponiveis = sorted(df_relatorio['Ano'].unique())
    
    with col_f2:
        anos_selecionados = st.multiselect("Selecione os Anos para Comparação:", options=anos_disponiveis, default=anos_disponiveis, key="anos_relatorio")
    
    st.divider()
    st.subheader(f"📊 Resumo Mensal ({status_filtro})")
    
    if not anos_selecionados:
        st.info("👈 Selecione pelo menos um ano acima para gerar a tabela.")
    else:
        dados_tabela = {}
        for ano in anos_selecionados:
            df_ano = df_relatorio[df_relatorio['Ano'] == ano]
            totais_ano = df_ano.groupby('Nome_Mes')['Valor Parcela'].sum()
            coluna_ano = [totais_ano.get(mes_nome, 0.0) for mes_nome in meses_pt.values()]
            dados_tabela[str(ano)] = coluna_ano
        
        df_final = pd.DataFrame(dados_tabela, index=list(meses_pt.values()))
        df_final.index.name = 'Mês'
        
        def formatar_coluna(valor): return f"R$ {formatar_moeda(valor)}"
        
        st.dataframe(df_final.map(formatar_coluna), use_container_width=True)
        
        st.subheader(" Total Anual")
        totais_gerais = [f"R$ {formatar_moeda(df_final[str(ano)].sum())}" for ano in anos_selecionados]
        df_totais = pd.DataFrame([totais_gerais], columns=[str(ano) for ano in anos_selecionados], index=['TOTAL GERAL'])
        st.dataframe(df_totais, use_container_width=True)