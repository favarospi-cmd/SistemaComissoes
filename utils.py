import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import streamlit as st

# --- CONFIGURAÇÃO DO SUPABASE (Lê do arquivo secrets.toml) ---
SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    if pd.isna(valor) or valor is None: return "0,00"
    formatted = f"{valor:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data_str):
    if not data_str: return ""
    try: return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return data_str

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_regras():
    # Estas são regras globais do sistema (compartilhadas)
    cats_raw = supabase.table('categorias').select('id, nome').execute().data
    subs_raw = supabase.table('subcategorias').select('id, nome, tipo, total_parcelas, percentual_total, categoria_id').execute().data
    regras_raw = supabase.table('regras_parcelas').select('subcategoria_id, numero_parcela, percentual').order('numero_parcela').execute().data

    subcategorias, regras_parcelas, subs_por_cat = {}, {}, {}
    
    for sub in subs_raw:
        subs_por_cat.setdefault(sub['categoria_id'], []).append(sub)
    
    for cat in cats_raw:
        subcategorias[cat['nome']] = [s['nome'] for s in subs_por_cat.get(cat['id'], [])]
        for s in subs_por_cat.get(cat['id'], []):
            percentuais = [r['percentual'] for r in regras_raw if r['subcategoria_id'] == s['id']]
            regras_parcelas[s['nome']] = {
                "total_parcelas": s['total_parcelas'], "percentuais": percentuais,
                "total_comissao": s['percentual_total'], "subcategoria_id": s['id']
            }
            
    fps = supabase.table('formas_pagamento').select('id, nome').execute().data
    formas_pagamento = {fp['nome']: fp['id'] for fp in fps}
        
    return formas_pagamento, subcategorias, regras_parcelas

def buscar_todas_parcelas(user_id):
    response = supabase.table('parcelas').select('''
        id, numero_parcela, valor_parcela, data_vencimento, data_pagamento, status,
        lancamentos (subcategorias (nome, tipo, categorias(nome)))
    ''').eq('user_id', user_id).order('data_vencimento', desc=False).execute()
    
    dados = []
    for p in response.data:
        lanc = p['lancamentos']; subcat = lanc['subcategorias']; cat = subcat['categorias']
        dados.append({
            "ID": p['id'], "Categoria": cat['nome'], "Subcategoria": subcat['nome'], "Tipo": subcat['tipo'],
            "Valor Parcela": p['valor_parcela'], "Data Vencimento": p['data_vencimento'],
            "Data Pagamento": p['data_pagamento'], "Status": p['status']
        })
    return pd.DataFrame(dados)

def buscar_parcelas_abertas(user_id):
    response = supabase.table('parcelas').select('''
        id, numero_parcela, percentual_parcela, valor_parcela, data_vencimento, status,
        lancamentos (data_venda, valor_negociado, subcategorias (nome, tipo, total_parcelas, categorias(nome)), formas_pagamento (nome))
    ''').eq('user_id', user_id).eq('status', 'EM ABERTO').order('data_vencimento', desc=False).execute()
    
    dados = []
    for p in response.data:
        lanc = p['lancamentos']; subcat = lanc['subcategorias']; cat = subcat['categorias']
        dados.append({
            "ID": p['id'], "Data Venda": formatar_data(lanc['data_venda']), "Categoria": cat['nome'],
            "Subcategoria": subcat['nome'], "Tipo": subcat['tipo'], "Valor Negociado": formatar_moeda(lanc['valor_negociado']),
            "Parcela": f"{p['numero_parcela']}/{subcat['total_parcelas']}", "% Parcela": formatar_moeda(p['percentual_parcela']),
            "Valor Parcela": formatar_moeda(p['valor_parcela']), "Vencimento": formatar_data(p['data_vencimento']),
            "DataVencRaw": p['data_vencimento'], "Forma Pgto": lanc['formas_pagamento']['nome'], "Status": p['status']
        })
    return pd.DataFrame(dados)

def buscar_historico_vendas(user_id):
    response = supabase.table('lancamentos').select('''
        id, data_venda, valor_negociado, descricao,
        subcategorias (nome, tipo, categorias(nome)), formas_pagamento (nome)
    ''').eq('user_id', user_id).order('data_venda', desc=True).execute()
    
    dados = []
    for l in response.data:
        subcat = l['subcategorias']; cat = subcat['categorias']
        dados.append({
            "Data Venda": formatar_data(l['data_venda']), "Categoria": cat['nome'],
            "Subcategoria": subcat['nome'], "Tipo": subcat['tipo'],
            "Valor Negociado": f"R$ {formatar_moeda(l['valor_negociado'])}",
            "Forma Pgto": l['formas_pagamento']['nome'], "Descrição": l['descricao']
        })
    return pd.DataFrame(dados)

def salvar_venda(data_venda, subcat_nome, valor_negociado, forma_pagto_nome, descricao, user_id):
    formas_pagamento, subcategorias, regras_parcelas = carregar_regras()
    subcat_info = regras_parcelas[subcat_nome]
    
    lancamento_data = {
        "data_venda": data_venda.strftime("%Y-%m-%d"),
        "subcategoria_id": subcat_info["subcategoria_id"],
        "valor_negociado": valor_negociado,
        "forma_pagamento_id": formas_pagamento[forma_pagto_nome],
        "descricao": descricao,
        "user_id": user_id
    }
    lanc_response = supabase.table('lancamentos').insert(lancamento_data).execute()
    lancamento_id = lanc_response.data[0]['id']
    
    parcelas_to_insert = []
    for i in range(subcat_info["total_parcelas"]):
        num_parcela = i + 1
        perc_parcela = subcat_info["percentuais"][i]
        data_venc = data_venda + timedelta(days=30 * num_parcela)
        parcelas_to_insert.append({
            "lancamento_id": lancamento_id,
            "numero_parcela": num_parcela,
            "percentual_parcela": perc_parcela,
            "valor_parcela": valor_negociado * (perc_parcela / 100),
            "data_vencimento": data_venc.strftime("%Y-%m-%d"),
            "status": "EM ABERTO",
            "forma_pagamento_id": formas_pagamento[forma_pagto_nome],
            "user_id": user_id
        })
    supabase.table('parcelas').insert(parcelas_to_insert).execute()

def atualizar_status_parcela(parcela_id, novo_status, user_id):
    update_data = {"status": novo_status}
    if novo_status == "PAGO": update_data["data_pagamento"] = datetime.now().strftime("%Y-%m-%d")
    else: update_data["data_pagamento"] = None
    
    # Segurança: só atualiza se o user_id bater
    supabase.table('parcelas').update(update_data).eq('id', parcela_id).eq('user_id', user_id).execute()

def carregar_config_empresa(user_id):
    try:
        response = supabase.table('config_empresa').select('*').eq('user_id', user_id).execute()
        if response.data: return response.data[0]
    except: pass
    return {'nome_empresa': 'Sua Empresa', 'cnpj': '', 'telefone': '', 'email': '', 'slogan': 'Controle Inteligente'}

def salvar_config_empresa(dados, user_id):
    dados['user_id'] = user_id
    # Usamos user_id como conflito para upsert
    supabase.table('config_empresa').upsert(dados, on_conflict='user_id').execute()

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def fazer_login(email, senha):
    try:
        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return resposta.user
    except Exception:
        return None

def fazer_logout():
    supabase.auth.sign_out()

def get_usuario_atual():
    try:
        resposta = supabase.auth.get_user()
        return resposta.user
    except:
        return None

# Inicialização global (regras são compartilhadas)
formas_pagamento, subcategorias, regras_parcelas = carregar_regras()