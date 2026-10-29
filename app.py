import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
from datetime import datetime
from utils import (supabase, carregar_regras, carregar_config_empresa, 
                   buscar_todas_parcelas, formatar_moeda, 
                   fazer_login, fazer_logout, get_usuario_atual)

# --- CONFIGURAÇÃO DE IDIOMA E PÁGINA (CORRIGIDA PARA LINUX) ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    except locale.Error:
        pass

st.set_page_config(page_title="C&Q Sistemas Inteligentes", page_icon="&#x1F4B0", layout="wide", initial_sidebar_state="collapsed")

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
    
    /* LOGIN COMPACTO */
    .login-container {
        max-width: 320px !important;
        margin: 20px auto !important;
        padding: 15px !important;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .login-container h1 {
        font-size: 18px !important;
        margin-bottom: 5px !important;
    }
    .login-container p {
        font-size: 11px !important;
        margin-bottom: 10px !important;
    }
    
    /* Forçar redução dos inputs e botões do formulário */
    .stForm {
        max-width: 320px !important;
        margin: 0 auto !important;
    }
    .stTextInput > div > div > input {
        font-size: 13px !important;
        padding: 8px 12px !important;
        height: 35px !important;
    }
    .stButton > button {
        font-size: 13px !important;
        padding: 6px 12px !important;
        height: 35px !important;
    }
    .stForm > div[data-testid="stHorizontalBlock"] {
        gap: 10px !important;
    }
</style>""", unsafe_allow_html=True)

# ============================================================
# LÓGICA DE SESSÃO E VITRINE DE VENDAS
# ============================================================
# TELA DE VITRINE OU LOGIN (Se não estiver logado)
if not st.session_state.usuario_logado:
    
    if not st.session_state.mostrar_login:
        # --- NOVA PÁGINA DE VENDAS (LAYOUT MODERNO) ---
        
        # Logo pequena no canto superior esquerdo
        col_logo_top1, col_logo_top2 = st.columns([1, 10])
        with col_logo_top1:
            try:
                st.image("logo_cq.png", width=80, use_container_width=False)
            except Exception:
                pass
        
        # Texto "SISTEMAS INTELIGENTES" centralizado no topo
        st.markdown("""
        <div style="text-align: center; margin: -70px 0 30px 0;">
            <h3 style="color: #1e3a8a; font-size: 18px; font-weight: bold; margin: 0; letter-spacing: 4px;">SISTEMAS INTELIGENTES</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Tarja azul com logo à esquerda e texto à direita
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 40px; border-radius: 15px; margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 30px;">
            <div style="flex-shrink: 0; background: white; border-radius: 10px; padding: 15px;">
                <img src="logo_cq.png" style="width: 120px; height: auto; display: block;">
            </div>
            <div style="flex-grow: 1; color: white;">
                <h2 style="font-size: 28px; margin: 0 0 15px 0; font-weight: bold; color: white;">💰 Sistema de Controle de Comissões</h2>
                <p style="font-size: 16px; line-height: 1.6; margin: 0; color: white; opacity: 0.95;">Trabalha com comissão e quer saber exatamente o que vai cair no seu bolso este mês e nos próximos?<br><strong style="font-size: 17px;">Este é o sistema feito para você.</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Seção "Ideal para:"
        st.markdown("""
        <div style="margin-bottom: 40px;">
            <h3 style="color: #1e3a8a; font-size: 22px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 28px;"></span> Ideal para:
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; height: 100%;">
                <div style="font-size: 40px; margin-bottom: 10px;">🏠</div>
                <p style="color: #1e3a8a; font-weight: 600; margin: 0;">Corretores de Imóveis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; height: 100%;">
                <div style="font-size: 40px; margin-bottom: 10px;">🚗</div>
                <p style="color: #1e3a8a; font-weight: 600; margin: 0;">Vendedores de Veículos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; height: 100%;">
                <div style="font-size: 40px; margin-bottom: 10px;">🤝</div>
                <p style="color: #1e3a8a; font-weight: 600; margin: 0;">Correspondentes e Autônomos</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
        
        # Seção "Por que escolher a C&Q?"
        st.markdown("""
        <div style="margin-bottom: 40px;">
            <h3 style="color: #1e3a8a; font-size: 22px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 28px;">🚀</span> Por que escolher a C&Q?
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("""
            <div style="padding: 25px; border-radius: 10px; height: 100%;">
                <div style="font-size: 35px; margin-bottom: 15px;">📅</div>
                <h4 style="color: #1e3a8a; margin-bottom: 10px; font-size: 18px;">Previsibilidade Total</h4>
                <p style="color: #64748b; line-height: 1.6; margin: 0; font-size: 14px;">Saiba exatamente quanto vai receber no mês corrente e nos próximos meses. Chega de surpresas.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with b2:
            st.markdown("""
            <div style="padding: 25px; border-radius: 10px; height: 100%;">
                <div style="font-size: 35px; margin-bottom: 15px;">🎯</div>
                <h4 style="color: #1e3a8a; margin-bottom: 10px; font-size: 18px;">Metas vs Realizado</h4>
                <p style="color: #64748b; line-height: 1.6; margin: 0; font-size: 14px;">Acompanhe seu desempenho em tempo real. Bata suas metas com precisão cirúrgica.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with b3:
            st.markdown("""
            <div style="padding: 25px; border-radius: 10px; height: 100%;">
                <div style="font-size: 35px; margin-bottom: 15px;">🔒</div>
                <h4 style="color: #1e3a8a; margin-bottom: 10px; font-size: 18px;">100% Seguro e Privado</h4>
                <p style="color: #64748b; line-height: 1.6; margin: 0; font-size: 14px;">Seus dados de vendas e comissões são isolados e protegidos. Ninguém mais tem acesso.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 50px 0; border-top: 2px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        
        # Contato e CTA
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 15px; margin-bottom: 30px;">
            <h3 style="color: #1e3a8a; margin-bottom: 10px; font-size: 24px;">Quer levar o controle total das suas vendas?</h3>
            <p style="color: #64748b; font-size: 16px; margin-bottom: 25px;">Fale diretamente com <strong>Cesar</strong> e agende uma demonstração.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            st.markdown(f'<a href="https://wa.me/5541999753534" target="_blank" style="text-decoration: none;"><button style="background-color: #25D366; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; box-shadow: 0 4px 6px rgba(37, 211, 102, 0.3);"> Chamar no WhatsApp</button></a>', unsafe_allow_html=True)
        with col_btn2:
            if st.button(" Já sou cliente? Fazer Login", use_container_width=True, type="primary"):
                st.session_state.mostrar_login = True
                st.rerun()

    else:
        # --- TELA DE LOGIN ---
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
                botao_entrar = st.form_submit_button("🔓 Entrar", type="primary", use_container_width=True)
            with col2:
                botao_cadastro = st.form_submit_button(" Criar Conta", use_container_width=True)

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
        
        if st.button("️ Voltar para a página inicial"):
            st.session_state.mostrar_login = False
            st.rerun()

    st.stop()        """, unsafe_allow_html=True)

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
            st.markdown("### 📅 Previsibilidade Total")
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
            st.markdown(f'<a href="https://wa.me/5541999753534" target="_blank" style="text-decoration: none;"><button style="background-color: #25D366; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; width: 100%; cursor: pointer;"> Chamar no WhatsApp</button></a>', unsafe_allow_html=True)
        with col_btn2:
            if st.button("🔓 Já sou cliente? Fazer Login", use_container_width=True, type="primary"):
                st.session_state.mostrar_login = True
                st.rerun()

    else:
        # --- TELA DE LOGIN ---
        st.markdown("""
        <div class="login-container">
            <h1>&#x1F4B0; Controle de Comissões</h1>
            <p>Acesse sua conta para gerenciar suas vendas</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            col1, col2 = st.columns(2)
            with col1:
                botao_entrar = st.form_submit_button("🔓 Entrar", type="primary", use_container_width=True)
            with col2:
                botao_cadastro = st.form_submit_button(" Criar Conta", use_container_width=True)

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
        
        if st.button("️ Voltar para a página inicial"):
            st.session_state.mostrar_login = False
            st.rerun()

    st.stop()

# ============================================================
# APLICATIVO PRINCIPAL (Só carrega se estiver logado)
# ============================================================
st.set_page_config(initial_sidebar_state="expanded")

formas_pagamento, subcategorias, regras_parcelas = carregar_regras()
user_id = st.session_state.usuario_logado.id
config_empresa = carregar_config_empresa(user_id)

# Banner da Empresa
info_extra = []
if config_empresa.get('cnpj'): info_extra.append(f"CNPJ: {config_empresa['cnpj']}")
if config_empresa.get('telefone'): info_extra.append(f"Tel: {config_empresa['telefone']}")
info_texto = " | ".join(info_extra)

st.markdown(f"""
<div class="banner-empresa">
    <h1>&#x1F4B0; {config_empresa.get('nome_empresa', 'Sua Empresa')}</h1>
    <p>{config_empresa.get('slogan', '')} {('• ' + info_texto) if info_texto else ''}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar com Logout
st.sidebar.title(f"👤 {st.session_state.usuario_logado.email}")
if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
    fazer_logout()
    st.session_state.usuario_logado = None
    st.session_state.mostrar_login = False
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
    with col_ac1: st.info(" **Lançamentos**\n\nRegistre novas vendas e comissões")
    with col_ac2: st.info("⚙️ **Parâmetros**\n\nConfigure metas, categorias e regras")
    with col_ac3: st.info("📈 **Dashboards**\n\nVisualize gráficos e análises")
else:
    st.subheader(" Visão Geral Financeira")
    
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
                    <strong>Legenda:</strong> <span style="color: #2ecc71;">■ Verde</span> = Meta Atingida (&ge;100%) | 
                    <span style="color: #f39c12;">Laranja</span> = Quase Lá (70-99%) | <span style="color: #e74c3c;">Vermelho</span> = Abaixo da Meta (<70%)
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
            total_proximos = df_proximos['Valor Parcela'].sum()
            
            col_total1, col_total2 = st.columns([2, 1])
            with col_total1:
                st.markdown(f"**Total a Receber (próximos 30 dias):**")
            with col_total2:
                st.metric("", f"R$ {formatar_moeda(total_proximos)}", delta_color="normal")
            
            st.divider()
            df_exibir = df_proximos[['Data Vencimento', 'Categoria', 'Subcategoria', 'Valor Parcela']].copy()
            df_exibir['Data Vencimento'] = pd.to_datetime(df_exibir['Data Vencimento']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum recebimento previsto para os próximos 30 dias.")
    else:
        st.info("Nenhuma parcela em aberto.")
