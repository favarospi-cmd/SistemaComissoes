import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
from datetime import datetime
from utils import (supabase, carregar_regras, carregar_config_empresa, 
                   buscar_todas_parcelas, formatar_moeda, 
                   fazer_login, fazer_logout, get_usuario_atual)

# --- URL DA LOGO (hospedada no próprio GitHub) ---
LOGO_URL = "https://raw.githubusercontent.com/favarospi-cmd/SistemaComissoes/main/logo_cq.png"

# --- CONFIGURAÇÃO DE IDIOMA ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    except locale.Error:
        pass

st.set_page_config(page_title="C&Q Sistemas Inteligentes", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<script>document.documentElement.lang = "pt-BR";</script>', unsafe_allow_html=True)

# ============================================================
# CSS GLOBAL MODERNO
# ============================================================
st.markdown("""
<style>
    /* Base */
    body { background-color: #f8fafc !important; }
    section[data-testid="stSidebar"] { width: 280px !important; }
    
    /* Header */
    .header-cq {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        padding: 30px 20px 20px 20px;
    }
    .header-cq img { width: 50px; height: auto; }
    .header-cq h2 {
        color: #1e3a8a;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 6px;
        margin: 0;
        text-transform: uppercase;
    }
    
    /* Tarja Azul Hero */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        border-radius: 20px;
        padding: 50px 40px;
        margin: 20px 0 40px 0;
        display: flex;
        align-items: center;
        gap: 40px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
    }
    .hero-logo-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        flex-shrink: 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hero-logo-box img { width: 140px; height: auto; display: block; }
    .hero-text h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin: 0 0 15px 0;
    }
    .hero-text p {
        color: rgba(255,255,255,0.95);
        font-size: 17px;
        line-height: 1.6;
        margin: 0;
    }
    .hero-text strong { color: white; font-size: 18px; }
    
    /* Seções */
    .section-title {
        color: #1e3a8a;
        font-size: 24px;
        font-weight: 700;
        margin: 40px 0 25px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Cards */
    .card-ideal {
        background: white;
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s;
        height: 100%;
    }
    .card-ideal:hover { transform: translateY(-5px); }
    .card-ideal .icon { font-size: 45px; margin-bottom: 15px; }
    .card-ideal p { color: #1e3a8a; font-weight: 600; margin: 0; font-size: 15px; }
    
    .card-benefit {
        background: white;
        border-radius: 12px;
        padding: 30px 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        height: 100%;
    }
    .card-benefit .icon { font-size: 40px; margin-bottom: 15px; }
    .card-benefit h4 { color: #1e3a8a; margin: 0 0 10px 0; font-size: 18px; font-weight: 700; }
    .card-benefit p { color: #64748b; line-height: 1.6; margin: 0; font-size: 14px; }
    
    /* CTA Box */
    .cta-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 20px;
        padding: 40px 30px;
        text-align: center;
        margin: 50px 0 30px 0;
        border: 1px solid #bae6fd;
    }
    .cta-box h3 { color: #1e3a8a; font-size: 26px; margin: 0 0 10px 0; font-weight: 700; }
    .cta-box p { color: #64748b; font-size: 16px; margin: 0 0 25px 0; }
    
    /* Botões iguais */
    .btn-action {
        display: block;
        width: 100%;
        padding: 18px 30px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 700;
        text-align: center;
        text-decoration: none;
        cursor: pointer;
        border: none;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        transition: all 0.2s;
    }
    .btn-action:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
    .btn-whatsapp { background-color: #25D366; color: white; }
    .btn-login { background-color: #1e3a8a; color: white; }
    
    /* Banner empresa (interno) */
    .banner-empresa {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 20px 30px; border-radius: 10px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .banner-empresa h1 { margin: 0; font-size: 26px; font-weight: bold; }
    .banner-empresa p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
    
    /* Login compacto */
    .login-container {
        max-width: 320px !important;
        margin: 20px auto !important;
        padding: 15px !important;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .login-container h1 { font-size: 18px !important; margin-bottom: 5px !important; }
    .login-container p { font-size: 11px !important; margin-bottom: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LÓGICA DE SESSÃO
# ============================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = get_usuario_atual()

if "mostrar_login" not in st.session_state:
    st.session_state.mostrar_login = False

# ============================================================
# TELA DE VITRINE OU LOGIN
# ============================================================
if not st.session_state.usuario_logado:
    
    if not st.session_state.mostrar_login:
        # --- HEADER COM LOGO PEQUENA + NOME ---
        st.markdown(f"""
        <div class="header-cq">
            <img src="{LOGO_URL}" alt="C&Q">
            <h2>Sistemas Inteligentes</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # --- TARJA AZUL HERO COM LOGO ---
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-logo-box">
                <img src="{LOGO_URL}" alt="C&Q Logo">
            </div>
            <div class="hero-text">
                <h1>💰 Sistema de Controle de Comissões</h1>
                <p>Trabalha com comissão e quer saber exatamente o que vai cair no seu bolso este mês e nos próximos?<br><strong>Este é o sistema feito para você.</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- IDEAL PARA ---
        st.markdown('<h3 class="section-title">🎯 Ideal para:</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.markdown("""
            <div class="card-ideal">
                <div class="icon">🏠</div>
                <p>Corretores de Imóveis</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="card-ideal">
                <div class="icon">🚗</div>
                <p>Vendedores de Veículos</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="card-ideal">
                <div class="icon">🤝</div>
                <p>Correspondentes e Autônomos</p>
            </div>
            """, unsafe_allow_html=True)
        
        # --- POR QUE ESCOLHER ---
        st.markdown('<h3 class="section-title">🚀 Por que escolher a C&Q?</h3>', unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns(3, gap="large")
        with b1:
            st.markdown("""
            <div class="card-benefit">
                <div class="icon">📅</div>
                <h4>Previsibilidade Total</h4>
                <p>Saiba exatamente quanto vai receber no mês corrente e nos próximos meses. Chega de surpresas.</p>
            </div>
            """, unsafe_allow_html=True)
        with b2:
            st.markdown("""
            <div class="card-benefit">
                <div class="icon">🎯</div>
                <h4>Metas vs Realizado</h4>
                <p>Acompanhe seu desempenho em tempo real. Bata suas metas com precisão cirúrgica.</p>
            </div>
            """, unsafe_allow_html=True)
        with b3:
            st.markdown("""
            <div class="card-benefit">
                <div class="icon">🔒</div>
                <h4>100% Seguro e Privado</h4>
                <p>Seus dados de vendas e comissões são isolados e protegidos. Ninguém mais tem acesso.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # --- CTA FINAL ---
        st.markdown("""
        <div class="cta-box">
            <h3>Quer levar o controle total das suas vendas?</h3>
            <p>Fale diretamente com <strong>Cesar</strong> e agende uma demonstração gratuita.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- BOTÕES IGUAIS (ambos em HTML puro) ---
        col_btn1, col_btn2 = st.columns([1, 1], gap="large")
        with col_btn1:
            st.markdown("""
            <a href="https://wa.me/5541999753534" target="_blank" style="text-decoration: none;">
                <div class="btn-action btn-whatsapp"> Chamar no WhatsApp</div>
            </a>
            """, unsafe_allow_html=True)
        with col_btn2:
            # Botão login como link que recarrega a página com parâmetro
            st.markdown("""
            <a href="?login=1" style="text-decoration: none;">
                <div class="btn-action btn-login">🔓 Já sou cliente? Fazer Login</div>
            </a>
            """, unsafe_allow_html=True)
        
        # Detectar clique no botão de login via URL params
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(st.query_params.to_dict() if hasattr(st, 'query_params') else {})
        # Método alternativo usando st.experimental_get_query_params (compatível)
        try:
            params = st.query_params
            if hasattr(params, 'get') and params.get('login'):
                st.session_state.mostrar_login = True
                st.rerun()
        except:
            pass

    else:
        # --- TELA DE LOGIN ---
        st.markdown("""
        <div class="login-container">
            <h1>Controle de Comissões</h1>
            <p>Acesse sua conta para gerenciar suas vendas</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            col1, col2 = st.columns(2)
            with col1:
                botao_entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            with col2:
                botao_cadastro = st.form_submit_button("Criar Conta", use_container_width=True)

        if botao_entrar:
            if email and senha:
                usuario = fazer_login(email, senha)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
            else:
                st.warning("Preencha todos os campos.")

        if botao_cadastro:
            if email and senha:
                try:
                    supabase.auth.sign_up({"email": email, "password": senha})
                    st.success("Conta criada com sucesso! Agora faça o login.")
                except Exception as e:
                    st.error(f"Erro ao criar conta: {str(e)}")
            else:
                st.warning("Preencha e-mail e senha.")
        
        if st.button("Voltar para a página inicial"):
            st.session_state.mostrar_login = False
            st.rerun()

    st.stop()

# ============================================================
# APLICATIVO PRINCIPAL (logado)
# ============================================================
st.set_page_config(initial_sidebar_state="expanded")

formas_pagamento, subcategorias, regras_parcelas = carregar_regras()
user_id = st.session_state.usuario_logado.id
config_empresa = carregar_config_empresa(user_id)

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

st.sidebar.title(f"👤 {st.session_state.usuario_logado.email}")
if st.sidebar.button("Sair do Sistema", use_container_width=True):
    fazer_logout()
    st.session_state.usuario_logado = None
    st.session_state.mostrar_login = False
    st.rerun()
st.sidebar.divider()
st.sidebar.info("Sistema v1.0 - Multi-tenant ativo!")

# Dashboard
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
    st.warning("⚠️ Nenhum dado encontrado. Comece lançando vendas em **Lançamentos**.")
else:
    st.subheader(" Visão Geral Financeira")
    
    total_geral = df_tudo['Valor Parcela'].sum()
    total_aberto = df_tudo[df_tudo['Status'] == 'EM ABERTO']['Valor Parcela'].sum()
    total_atrasado = df_tudo[df_tudo['Status'] == 'ATRASADO']['Valor Parcela'].sum()
    
    df_pago = df_tudo[df_tudo['Status'] == 'PAGO'].copy()
    if not df_pago.empty:
        df_pago['DataPagDT'] = pd.to_datetime(df_pago['Data Pagamento'])
        recebido_mes = df_pago[(df_pago['DataPagDT'].dt.month == mes_atual) & (df_pago['DataPagDT'].dt.year == ano_atual)]['Valor Parcela'].sum()
        recebido_ano = df_pago[df_pago['DataPagDT'].dt.year == ano_atual]['Valor Parcela'].sum()
    else:
        recebido_mes = 0.0
        recebido_ano = 0.0
    
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("💰 Total Geral", f"R$ {formatar_moeda(total_geral)}")
    kpi2.metric("✅ Recebido (Mês)", f"R$ {formatar_moeda(recebido_mes)}")
    kpi3.metric("📂 Em Aberto", f"R$ {formatar_moeda(total_aberto)}")
    kpi4.metric("⚠️ Atrasado", f"R$ {formatar_moeda(total_atrasado)}")
    kpi5.metric(" Recebido (Ano)", f"R$ {formatar_moeda(recebido_ano)}")
    
    st.divider()
    
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("🥧 Distribuição por Status")
        df_status = df_tudo.groupby('Status')['Valor Parcela'].sum().reset_index()
        if not df_status.empty:
            fig_pizza = px.pie(df_status, values='Valor Parcela', names='Status', 
                               color_discrete_map={'PAGO': '#2ecc71', 'EM ABERTO': '#f1c40f', 'ATRASADO': '#e74c3c'}, hole=0.4)
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_graf2:
        st.subheader("📊 Faturamento por Categoria")
        df_cat = df_tudo.groupby('Categoria')['Valor Parcela'].sum().reset_index()
        if not df_cat.empty:
            fig_barra = px.bar(df_cat, x='Categoria', y='Valor Parcela', color='Categoria', text_auto='.2s')
            fig_barra.update_layout(showlegend=False)
            st.plotly_chart(fig_barra, use_container_width=True)
    
    st.divider()
    st.subheader("📅 Próximos Recebimentos (30 dias)")
    df_aberto = df_tudo[df_tudo['Status'] == 'EM ABERTO'].copy()
    if not df_aberto.empty:
        df_aberto['DataVencDT'] = pd.to_datetime(df_aberto['Data Vencimento'])
        limite = hoje + pd.Timedelta(days=30)
        df_proximos = df_aberto[(df_aberto['DataVencDT'] >= hoje) & (df_aberto['DataVencDT'] <= limite)]
        if not df_proximos.empty:
            df_proximos = df_proximos.sort_values('DataVencDT')
            st.metric("Total a Receber", f"R$ {formatar_moeda(df_proximos['Valor Parcela'].sum())}")
            df_exibir = df_proximos[['Data Vencimento', 'Categoria', 'Subcategoria', 'Valor Parcela']].copy()
            df_exibir['Data Vencimento'] = pd.to_datetime(df_exibir['Data Vencimento']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum recebimento previsto para os próximos 30 dias.")
    else:
        st.info("Nenhuma parcela em aberto.")
