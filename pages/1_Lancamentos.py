import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import (subcategorias, regras_parcelas, formas_pagamento, 
                   buscar_todas_parcelas, buscar_parcelas_abertas, buscar_historico_vendas, 
                   salvar_venda, atualizar_status_parcela, formatar_moeda)

# DEFINIR VARIÁVEIS DE DATA
hoje = datetime.now()
mes_atual = hoje.month
ano_atual = hoje.year

# Pega o ID do usuário logado
user_id = st.session_state.usuario_logado.id

st.title(" Menu Lançamentos")

# 1. KPIs REAIS
st.subheader("📊 KPIs - Resumo Financeiro")
df_tudo = buscar_todas_parcelas(user_id)

if df_tudo.empty:
    total_mes_atual = total_ano_atual = total_ano_passado = 0.0
else:
    df_pago = df_tudo[df_tudo['Status'] == 'PAGO']
    if not df_pago.empty:
        df_pago['Mes_Pag'] = pd.to_datetime(df_pago['Data Pagamento']).dt.month
        df_pago['Ano_Pag'] = pd.to_datetime(df_pago['Data Pagamento']).dt.year
        total_mes_atual = df_pago[(df_pago['Mes_Pag'] == mes_atual) & (df_pago['Ano_Pag'] == ano_atual)]['Valor Parcela'].sum()
        total_ano_atual = df_pago[df_pago['Ano_Pag'] == ano_atual]['Valor Parcela'].sum()
        total_ano_passado = df_pago[df_pago['Ano_Pag'] == (ano_atual - 1)]['Valor Parcela'].sum()
    else:
        total_mes_atual = total_ano_atual = total_ano_passado = 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Recebido Mensal ({hoje.strftime('%B/%Y').upper()})", f"R$ {formatar_moeda(total_mes_atual)}")
col2.metric(f"Recebido Mensal ({ano_atual - 1})", f"R$ {formatar_moeda(0.00)}", "0.0%")
col3.metric(f"Recebido Anual ({ano_atual})", f"R$ {formatar_moeda(total_ano_atual)}")
col4.metric(f"Recebido Anual ({ano_atual - 1})", f"R$ {formatar_moeda(total_ano_passado)}")

st.divider()

# 2. Formulário
st.subheader(" Novo Lançamento de Venda")
if 'form_limpo' not in st.session_state: st.session_state.form_limpo = 0
if 'categoria_atual' not in st.session_state: st.session_state.categoria_atual = list(subcategorias.keys())[0]

key_suffix = f"_{st.session_state.form_limpo}"

col1, col2, col3 = st.columns(3)
with col1:
    data_venda = st.date_input("Data da Venda", datetime.now(), format="DD/MM/YYYY", key=f"data_venda{key_suffix}")
with col2:
    cat_principal = st.selectbox("Categoria", list(subcategorias.keys()), 
                                 index=list(subcategorias.keys()).index(st.session_state.categoria_atual),
                                 key=f"cat{key_suffix}")
with col3:
    sub_cat = st.selectbox("Subcategoria", subcategorias[cat_principal], key=f"subcat{key_suffix}")

col4, col5, col6 = st.columns(3)
with col4:
    valor_negociado = st.number_input("Valor Negociado (R$)", min_value=0.0, format="%.2f", key=f"valor{key_suffix}")
with col5:
    forma_pagto = st.selectbox("Forma de Pagamento", list(formas_pagamento.keys()), key=f"forma{key_suffix}")
with col6:
    descricao = st.text_input("Descrição / Observações", key=f"desc{key_suffix}")

if cat_principal != st.session_state.categoria_atual:
    st.session_state.categoria_atual = cat_principal
    st.rerun()

if sub_cat and sub_cat in regras_parcelas:
    regra = regras_parcelas[sub_cat]
    valor_parcela_1 = valor_negociado * (regra["percentuais"][0] / 100) if valor_negociado > 0 else 0
    col_conf1, col_conf2 = st.columns(2)
    with col_conf1: st.info(f"📦 Número de Parcelas: **{regra['total_parcelas']}**")
    with col_conf2: st.info(f"💰 Valor da Parcela 1: **R$ {formatar_moeda(valor_parcela_1)}**")

st.divider()

# BOTÃO COM KEY ÚNICA
if st.button("💾 Salvar Lançamento", type="primary", use_container_width=True, key="btn_salvar_lancamento"):
    if valor_negociado > 0 and sub_cat:
        with st.spinner("💾 Salvando..."): 
            salvar_venda(data_venda, sub_cat, valor_negociado, forma_pagto, descricao, user_id)
        st.success(f"✅ Venda de R$ {formatar_moeda(valor_negociado)} lançada!")
        st.session_state.form_limpo += 1
        st.rerun()
    else:
        st.error("❌ Preencha o valor e selecione uma subcategoria válida.")

st.divider()

# 3. Grid de Comissões a Receber
st.subheader("📅 Comissões a Receber (Em Aberto)")
df_aberto = buscar_parcelas_abertas(user_id)

if not df_aberto.empty:
    df_aberto['DataVencDT'] = pd.to_datetime(df_aberto['DataVencRaw'])
    df_aberto['MesAno'] = df_aberto['DataVencDT'].dt.to_period('M')
    
    def limpar_e_converter(valor_str):
        try:
            return float(str(valor_str).replace('.', '').replace(',', '.'))
        except:
            return 0.0

    df_aberto['Valor_Limpo'] = df_aberto['Valor Parcela'].apply(limpar_e_converter)
    totais_por_mes = df_aberto.groupby('MesAno')['Valor_Limpo'].sum()
    
    meses_futuros = [pd.Period(hoje, freq='M') + i for i in range(6)]
    cols_kpi = st.columns(6)
    meses_pt = {'JANUARY': 'JANEIRO', 'FEBRUARY': 'FEVEREIRO', 'MARCH': 'MARÇO', 'APRIL': 'ABRIL', 'MAY': 'MAIO', 'JUNE': 'JUNHO', 'JULY': 'JULHO', 'AUGUST': 'AGOSTO', 'SEPTEMBER': 'SETEMBRO', 'OCTOBER': 'OUTUBRO', 'NOVEMBER': 'NOVEMBRO', 'DECEMBER': 'DEZEMBRO'}
    
    for i, mes in enumerate(meses_futuros):
        valor = totais_por_mes.get(mes, 0.0)
        nome_mes = mes.strftime('%B/%Y').upper()
        for eng, pt in meses_pt.items(): nome_mes = nome_mes.replace(eng, pt)
        
        with cols_kpi[i]:
            st.markdown(f"""<div style="background:#f8fafc; border-left:4px solid #3b82f6; padding:10px; border-radius:6px; text-align:center;">
                <div style="font-size:12px; color:#64748b; font-weight:bold;">📅 {nome_mes}</div>
                <div style="font-size:16px; color:#1e3a8a; font-weight:bold; margin-top:5px;">R$ {formatar_moeda(valor)}</div>
            </div>""", unsafe_allow_html=True)
    st.divider()

    df_exibir = df_aberto.drop(columns=['DataVencRaw', 'DataVencDT', 'MesAno', 'Valor_Limpo'], errors='ignore')
    
    column_config = {
        "ID": st.column_config.NumberColumn("ID", disabled=True, width="small"),
        "Data Venda": st.column_config.TextColumn("Data Venda", disabled=True, width="small"),
        "Categoria": st.column_config.TextColumn("Categoria", disabled=True),
        "Subcategoria": st.column_config.TextColumn("Subcategoria", disabled=True),
        "Tipo": st.column_config.TextColumn("Tipo", disabled=True, width="small"),
        "Valor Negociado": st.column_config.TextColumn("Valor Negociado", disabled=True),
        "Parcela": st.column_config.TextColumn("Parcela", disabled=True, width="small"),
        "% Parcela": st.column_config.TextColumn("% Parcela", disabled=True, width="small"),
        "Valor Parcela": st.column_config.TextColumn("Valor Parcela", disabled=True),
        "Vencimento": st.column_config.TextColumn("Vencimento", disabled=True, width="small"),
        "Forma Pgto": st.column_config.TextColumn("Forma Pgto", disabled=True, width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=["EM ABERTO", "PAGO", "ATRASADO"], required=True)
    }
    
    edited_df = st.data_editor(df_exibir, column_config=column_config, num_rows="fixed", use_container_width=True, hide_index=True, key="editor_parcelas")
    
    # BOTÃO COM KEY ÚNICA
    if st.button("💾 Salvar Alterações de Status", type="primary", use_container_width=True, key="btn_salvar_status"):
        changes_made = False
        for index, row in edited_df.iterrows():
            if df_exibir.loc[index, "Status"] != row["Status"]:
                atualizar_status_parcela(row["ID"], row["Status"], user_id)
                changes_made = True
        if changes_made: 
            st.success("✅ Status atualizados!")
            st.rerun()
        else: 
            st.info("Nenhuma alteração detectada.")
else:
    st.info("Nenhuma parcela em aberto no momento.")

st.divider()

# 4. Grid de Histórico de Vendas
st.subheader("📋 Histórico de Vendas")
df_historico = buscar_historico_vendas(user_id)

if not df_historico.empty:
    st.dataframe(df_historico, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma venda registrada ainda.")