import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
from datetime import datetime
from utils import (supabase, carregar_regras, carregar_config_empresa, 
                   buscar_todas_parcelas, formatar_moeda, 
                   fazer_login, fazer_logout, get_usuario_atual)

# --- CONFIGURAÇÃO DE IDIOMA E PÁGINA ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

st.set_page_config(page_title="Controle de Comissões", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

st.markdown('<script>document.documentElement.lang = "pt-BR";</script>', unsafe_allow_html=True)

# CSS Global
st.markdown("""
<style>
    section[data-testid="stSidebar"] { width: 280px !important; }
    .banner-empresa {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 20px 30px; border-radius: 10px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .banner-empresa h1 { margin: 0; font-size: 26px; font-weight: bold; }
    .banner-empresa p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
    .card-resumo {
        background: white; border-radius: 8px; padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid #3b82f6;
    }
    .login-container {
        max-width: 400px; margin: 80px auto; padding: 40px;
        background: white; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LÓGICA DE SESSÃO E LOGIN
# ============================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = get_usuario_atual()

# ============================================================
# VITRINE DE VENDAS (Aparece para quem não está logado)
# ============================================================
if not st.session_state.usuario_logado:
    
    # Inicializa a variável de controle da tela
    if "mostrar_login" not in st.session_state:
        st.session_state.mostrar_login = False

    if not st.session_state.mostrar_login:
        # --- PÁGINA DE VENDAS (LANDING PAGE) ---
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h1 style="color: #1e3a8a; font-size: 42px; margin-bottom: 10px;">C&Q Sistemas Inteligentes</h1>
            <p style="font-size: 18px; color: #64748b;">Tecnologia que trabalha por você.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Hero Section
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
            <h2 style="font-size: 32px; margin-bottom: 15px;">💰 Sistema de Controle de Comissões</h2>
            <p style="font-size: 20px; line-height: 1.5;">Trabalha com comissão e quer saber exatamente o que vai cair no seu bolso este mês e nos próximos?<br><strong>Este é o sistema feito para você.</strong></p>
        </div>
        """, unsafe_allow_html=True)

        # Para quem é
        st.subheader("🎯 Ideal para:")
        col1, col2, col3 = st.columns(3)
        with col1: st.info("🏠 **Corretores de Imóveis**")
        with col2: st.info("🚗 **Vendedores de Veículos**")
        with col3: st.info("🤝 **Correspondentes e Autônomos**")

        st.markdown("---")

        # Benefícios
        st.subheader("🚀 Por que escolher a C&Q?")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("###  Previsibilidade Total")
            st.write("Saiba exatamente quanto vai receber no mês corrente e nos próximos meses. Chega de surpresas.")
        with b2:
            st.markdown("### 🎯 Metas vs Realizado")
            st.write("Acompanhe seu desempenho em tempo real. Bata suas metas com precisão cirúrgica.")
        with b3:
            st.markdown("### 🔒 100% Seguro e Privado")
            st.write("Seus dados de vendas e comissões são isolados e protegidos. Ninguém mais tem acesso.")

        st.markdown("---")

        # Contato e CTA
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #1e3a8a;">Quer levar o controle total das suas vendas?</h3>
            <p>Fale diretamente com <strong>Cesar</strong> e agende uma demonstração.</p>
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            # Link direto para o WhatsApp
            st.markdown(f'<a href="https://wa.me/5541999753534" target="_blank" style="text-decoration: none;"><button style="background-color: #25D366; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; width: 100%; cursor: pointer;"> Chamar no WhatsApp</button></a>', unsafe_allow_html=True)
        with col_btn2:
            if st.button("🔓 Já sou cliente? Fazer Login", use_container_width=True, type="primary"):
                st.session_state.mostrar_login = True
                st.rerun()

    else:
        # --- TELA DE LOGIN (Aparece quando clica no botão) ---
        st.markdown("""
        <div class="login-container">
            <h1>💰 Controle de Comissões</h1>
            <p>Acesse sua conta para gerenciar suas vendas</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            col1, col2 = st.columns(2)
            with col1:
                botao_entrar = st.form_submit_button(" Entrar", type="primary", use_container_width=True)
            with col2:
                botao_cadastro = st.form_submit_button("📝 Criar Conta", use_container_width=True)

        if botao_entrar:
            if email and senha:
                usuario = fazer_login(email, senha)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha incorretos.")
            else:
                st.warning("⚠️ Preencha todos os campos.")

        if botao_cadastro:
            if email and senha:
                try:
                    supabase.auth.sign_up({"email": email, "password": senha})
                    st.success("✅ Conta criada com sucesso! Agora faça o login.")
                except Exception as e:
                    st.error(f"Erro ao criar conta: {str(e)}")
            else:
                st.warning("⚠️ Preencha e-mail e senha.")
        
        # Botão para voltar para a vitrine
        if st.button("⬅️ Voltar para a página inicial"):
            st.session_state.mostrar_login = False
            st.rerun()

    st.stop() # Para a execução aqui e não carrega o resto do app

# ============================================================
# APLICATIVO PRINCIPAL (Só carrega se estiver logado)
# ============================================================
st.set_page_config(initial_sidebar_state="expanded")

formas_pagamento, subcategorias, regras_parcelas = carregar_regras()
user_id = st.session_state.usuario_logado.id
config_empresa = carregar_config_empresa(user_id)

# Banner da Empresa (APENAS UMA VEZ)
info_extra = []
if config_empresa.get('cnpj'): info_extra.append(f"CNPJ: {config_empresa['cnpj']}")
if config_empresa.get('telefone'): info_extra.append(f"Tel: {config_empresa['telefone']}")
info_texto = " | ".join(info_extra)

st.markdown(f"""
<div class="banner-empresa">
    <h1>💰 {config_empresa.get('nome_empresa', 'Sua Empresa')}</h1>
    <p>{config_empresa.get('slogan', '')} {('• ' + info_texto) if info_texto else ''}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar com Logout
st.sidebar.title(f"👤 {st.session_state.usuario_logado.email}")
if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
    fazer_logout()
    st.session_state.usuario_logado = None
    st.rerun()
st.sidebar.divider()
st.sidebar.info("Sistema v1.0 - Multi-tenant ativo!")

# ============================================================
# DASHBOARD INICIAL - PAINEL EXECUTIVO
# ============================================================
st.title("📊 Painel Executivo")

hoje = datetime.now()
mes_atual = hoje.month
ano_atual = hoje.year
meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

st.markdown(f"**📅 Data:** {hoje.strftime('%d/%m/%Y')} | **Período atual:** {meses_pt[mes_atual]}/{ano_atual}")
st.divider()

df_tudo = buscar_todas_parcelas(user_id)

if df_tudo.empty:
    st.warning("⚠️ Nenhum dado encontrado no sistema. Comece lançando vendas na página **Lançamentos**.")
    st.subheader("🚀 Acesso Rápido")
    col_ac1, col_ac2, col_ac3 = st.columns(3)
    with col_ac1: st.info("📝 **Lançamentos**\n\nRegistre novas vendas e comissões")
    with col_ac2: st.info("⚙️ **Parâmetros**\n\nConfigure metas, categorias e regras")
    with col_ac3: st.info("📈 **Dashboards**\n\nVisualize gráficos e análises")
else:
    st.subheader("📈 Visão Geral Financeira")
    
    total_geral = df_tudo['Valor Parcela'].sum()
    total_pago = df_tudo[df_tudo['Status'] == 'PAGO']['Valor Parcela'].sum()
    total_aberto = df_tudo[df_tudo['Status'] == 'EM ABERTO']['Valor Parcela'].sum()
    total_atrasado = df_tudo[df_tudo['Status'] == 'ATRASADO']['Valor Parcela'].sum()
    
    df_pago = df_tudo[df_tudo['Status'] == 'PAGO'].copy()
    if not df_pago.empty:
        df_pago['DataPagDT'] = pd.to_datetime(df_pago['Data Pagamento'])
        df_pago['MesPag'] = df_pago['DataPagDT'].dt.month
        df_pago['AnoPag'] = df_pago['DataPagDT'].dt.year
        recebido_mes = df_pago[(df_pago['MesPag'] == mes_atual) & (df_pago['AnoPag'] == ano_atual)]['Valor Parcela'].sum()
        recebido_ano = df_pago[df_pago['AnoPag'] == ano_atual]['Valor Parcela'].sum()
    else:
        recebido_mes = 0.0
        recebido_ano = 0.0
    
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("💰 Total Geral", f"R$ {formatar_moeda(total_geral)}")
    kpi2.metric("✅ Recebido (Mês)", f"R$ {formatar_moeda(recebido_mes)}")
    kpi3.metric("Em Aberto", f"R$ {formatar_moeda(total_aberto)}")
    kpi4.metric("⚠️ Atrasado", f"R$ {formatar_moeda(total_atrasado)}")
    kpi5.metric("📊 Recebido (Ano)", f"R$ {formatar_moeda(recebido_ano)}")
    
    st.divider()
    
    # --- GRÁFICOS ---
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("🥧 Distribuição por Status")
        df_status = df_tudo.groupby('Status')['Valor Parcela'].sum().reset_index()
        if not df_status.empty:
            fig_pizza = px.pie(df_status, values='Valor Parcela', names='Status', 
                               color_discrete_map={'PAGO': '#2ecc71', 'EM ABERTO': '#f1c40f', 'ATRASADO': '#e74c3c'}, hole=0.4)
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_graf2:
        st.subheader("📊 Faturamento por Categoria")
        df_cat = df_tudo.groupby('Categoria')['Valor Parcela'].sum().reset_index()
        if not df_cat.empty:
            fig_barra = px.bar(df_cat, x='Categoria', y='Valor Parcela', color='Categoria', text_auto='.2s')
            fig_barra.update_layout(showlegend=False)
            st.plotly_chart(fig_barra, use_container_width=True)
            
    st.divider()
    
    # --- DESEMPENHO VS METAS ---
    st.subheader("🎯 Desempenho vs Metas")
    try:
        metas_raw = supabase.table('metas').select('ano, mes, valor_meta, categorias(nome)').eq('user_id', user_id).execute().data
        if metas_raw:
            df_metas = pd.DataFrame([{"ano": m['ano'], "mes": m['mes'], "categoria": m['categorias']['nome'], "meta": m['valor_meta']} for m in metas_raw])
            df_metas_ano = df_metas[df_metas['ano'] == ano_atual]
            
            if not df_metas_ano.empty and not df_pago.empty:
                df_pago['DataVencDT'] = pd.to_datetime(df_pago['Data Vencimento'])
                df_pago['ano'] = df_pago['DataVencDT'].dt.year
                df_pago['mes'] = df_pago['DataVencDT'].dt.month
                
                realizado_por_mes = df_pago.groupby(['ano', 'mes', 'Categoria'])['Valor Parcela'].sum().reset_index()
                realizado_por_mes.columns = ['ano', 'mes', 'categoria', 'realizado']
                
                df_comparativo = pd.merge(df_metas_ano, realizado_por_mes, on=['ano', 'mes', 'categoria'], how='left')
                df_comparativo['realizado'] = df_comparativo['realizado'].fillna(0)
                df_comparativo['percentual'] = (df_comparativo['realizado'] / df_comparativo['meta'] * 100).round(2)
                
                categorias_unicas = sorted(df_comparativo['categoria'].unique())
                df_comparativo['mes_ano'] = df_comparativo.apply(lambda x: f"{meses_pt[int(x['mes'])]}/{x['ano']}", axis=1)
                meses_unicos = sorted(df_comparativo['mes_ano'].unique())
                
                html_tabela = '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse; font-size: 13px;"><thead><tr style="background-color: #1e3a8a; color: white;"><th rowspan="2" style="padding: 10px; border: 1px solid #ddd; text-align: left;">MESES / ANO</th>'
                for cat in categorias_unicas:
                    html_tabela += f'<th colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: center;">{cat}</th>'
                html_tabela += '<th colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: center; background-color: #0f2d6b;">TOTAL GERAL DO MÊS</th></tr><tr style="background-color: #3b82f6; color: white;">'
                for _ in categorias_unicas:
                    html_tabela += '<th style="padding: 8px; border: 1px solid #ddd;">Realizado</th><th style="padding: 8px; border: 1px solid #ddd;">Meta</th><th style="padding: 8px; border: 1px solid #ddd;">Percentual</th>'
                html_tabela += '<th style="padding: 8px; border: 1px solid #ddd; background-color: #2563eb;">Realizado</th><th style="padding: 8px; border: 1px solid #ddd; background-color: #2563eb;">Meta</th><th style="padding: 8px; border: 1px solid #ddd; background-color: #2563eb;">Percentual</th></tr></thead><tbody>'
                
                for mes_ano in meses_unicos:
                    df_mes = df_comparativo[df_comparativo['mes_ano'] == mes_ano]
                    total_realizado_mes = df_mes['realizado'].sum()
                    total_meta_mes = df_mes['meta'].sum()
                    total_percentual_mes = (total_realizado_mes / total_meta_mes * 100) if total_meta_mes > 0 else 0
                    
                    if total_percentual_mes >= 100: status_geral, cor_geral, icone_geral = "META ATINGIDA", "#2ecc71", "✅"
                    elif total_percentual_mes >= 70: status_geral, cor_geral, icone_geral = "QUASE LÁ", "#f39c12", "⚠️"
                    else: status_geral, cor_geral, icone_geral = "ABAIXO DA META", "#e74c3c", "❌"
                    
                    html_tabela += f'<tr style="background-color: #f8f9fa;"><td rowspan="2" style="padding: 10px; border: 1px solid #ddd; font-weight: bold; vertical-align: top;">{icone_geral} {mes_ano}<br><span style="font-size: 11px; color: {cor_geral};">{status_geral}</span></td>'
                    
                    for cat in categorias_unicas:
                        df_cat_mes = df_mes[df_mes['categoria'] == cat]
                        if not df_cat_mes.empty:
                            row = df_cat_mes.iloc[0]
                            cor_perc = "#2ecc71" if row['percentual'] >= 100 else "#f39c12" if row['percentual'] >= 70 else "#e74c3c"
                            html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">R$ {formatar_moeda(row["realizado"])}</td>'
                            html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">R$ {formatar_moeda(row["meta"])}</td>'
                            html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: {cor_perc}; font-weight: bold;">{row["percentual"]:.2f}%</td>'
                        else:
                            html_tabela += '<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">R$ 0,00</td><td style="padding: 8px; border: 1px solid #ddd; text-align: right;">R$ 0,00</td><td style="padding: 8px; border: 1px solid #ddd; text-align: center;">-</td>'
                    
                    cor_total = "#2ecc71" if total_percentual_mes >= 100 else "#f39c12" if total_percentual_mes >= 70 else "#e74c3c"
                    html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right; background-color: #f0f9ff;">R$ {formatar_moeda(total_realizado_mes)}</td>'
                    html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right; background-color: #f0f9ff;">R$ {formatar_moeda(total_meta_mes)}</td>'
                    html_tabela += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center; background-color: #f0f9ff; color: {cor_total}; font-weight: bold;">{total_percentual_mes:.2f}%</td></tr>'
                    html_tabela += f'<tr style="height: 5px;"><td colspan="{len(categorias_unicas) * 3 + 3}" style="border: none;"></td></tr>'
                
                html_tabela += '</tbody></table></div>'
                st.markdown(html_tabela, unsafe_allow_html=True)
                
                st.markdown("""<div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 12px;">
                    <strong>Legenda:</strong> <span style="color: #2ecc71;">■ Verde</span> = Meta Atingida (≥100%) | 
                    <span style="color: #f39c12;">■ Laranja</span> = Quase Lá (70-99%) | <span style="color: #e74c3c;">■ Vermelho</span> = Abaixo da Meta (<70%)
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Nenhum pagamento registrado ou nenhuma meta para este ano.")
        else:
            st.info("📌 Nenhuma meta cadastrada. Vá em **Parâmetros > Metas de Venda**.")
    except Exception as e:
        st.info("📌 Configure suas metas para acompanhar o desempenho.")
    
    st.divider()
    
    # --- PRÓXIMOS RECEBIMENTOS ---
    st.subheader("📅 Próximos Recebimentos (30 dias)")
    df_aberto = df_tudo[df_tudo['Status'] == 'EM ABERTO'].copy()
    if not df_aberto.empty:
        df_aberto['DataVencDT'] = pd.to_datetime(df_aberto['Data Vencimento'])
        limite = hoje + pd.Timedelta(days=30)
        df_proximos = df_aberto[(df_aberto['DataVencDT'] >= hoje) & (df_aberto['DataVencDT'] <= limite)]
        
        if not df_proximos.empty:
            df_proximos = df_proximos.sort_values('DataVencDT')
            
            # Calcular total
            total_proximos = df_proximos['Valor Parcela'].sum()
            
            # Mostrar total em destaque ANTES da tabela
            col_total1, col_total2 = st.columns([2, 1])
            with col_total1:
                st.markdown(f"**Total a Receber (próximos 30 dias):**")
            with col_total2:
                st.metric("", f"R$ {formatar_moeda(total_proximos)}", delta_color="normal")
            
            st.divider()
            
            # Mostrar tabela
            df_exibir = df_proximos[['Data Vencimento', 'Categoria', 'Subcategoria', 'Valor Parcela']].copy()
            df_exibir['Data Vencimento'] = pd.to_datetime(df_exibir['Data Vencimento']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum recebimento previsto para os próximos 30 dias.")
    else:
        st.info("Nenhuma parcela em aberto.")