import streamlit as st
import pandas as pd
from utils import salvar_config_empresa, subcategorias, formas_pagamento, SUPABASE_URL, supabase, carregar_regras, carregar_config_empresa

st.title("⚙️ Configurações / Parâmetros")

user_id = st.session_state.usuario_logado.id
config_empresa = carregar_config_empresa(user_id)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏢 Dados da Empresa", 
    "📊 Metas de Venda", 
    "📁 Categorias", 
    "📂 Subcategorias",
    " Regras de Parcelas",
    " Importar/Exportar"
])

# ============================================================
# ABA 1: DADOS DA EMPRESA
# ============================================================
with tab1:
    st.subheader("🏢 Dados da Empresa")
    st.info("Preencha os dados abaixo. Eles aparecerão no banner do topo do sistema.")

    with st.form("form_empresa"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome da Empresa", value=config_empresa.get('nome_empresa', ''))
            cnpj = st.text_input("CNPJ", value=config_empresa.get('cnpj', ''))
            telefone = st.text_input("Telefone", value=config_empresa.get('telefone', ''))
        with col2:
            email = st.text_input("E-mail", value=config_empresa.get('email', ''))
            endereco = st.text_input("Endereço", value=config_empresa.get('endereco', ''))
            slogan = st.text_input("Slogan / Frase", value=config_empresa.get('slogan', ''))
        
        submitted = st.form_submit_button("💾 Salvar Dados da Empresa", type="primary", use_container_width=True)
        
        if submitted:
            dados_empresa = {
                "id": 1, "nome_empresa": nome_empresa, "cnpj": cnpj, "endereco": endereco, 
                "telefone": telefone, "email": email, "slogan": slogan
            }
            salvar_config_empresa(dados_empresa, user_id)
            st.success("✅ Dados da empresa salvos com sucesso!")
            st.rerun()

# ============================================================
# ABA 2: METAS DE VENDA
# ============================================================
with tab2:
    st.subheader(" Metas de Venda por Mês/Categoria")
    
    with st.form("form_meta"):
        st.write("**➕ Cadastrar Nova Meta**")
        col1, col2, col3 = st.columns(3)
        with col1:
            ano_meta = st.number_input("Ano", min_value=2024, max_value=2030, value=2026)
        with col2:
            mes_meta = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        with col3:
            cat_meta = st.selectbox("Categoria", list(subcategorias.keys()))
        
        valor_meta = st.number_input("Valor da Meta (R$)", min_value=0.0, format="%.2f")
        
        submitted_meta = st.form_submit_button("💾 Cadastrar Meta", use_container_width=True)
        
        if submitted_meta and valor_meta > 0:
            meses_num = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
                        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
            
            cats_raw = supabase.table('categorias').select('id, nome').execute().data
            cat_id = next((c['id'] for c in cats_raw if c['nome'] == cat_meta), None)
            
            if cat_id:
                meta_data = {
                    "ano": ano_meta,
                    "mes": meses_num[mes_meta],
                    "categoria_id": cat_id,
                    "valor_meta": valor_meta,
                    "user_id": user_id
                }
                supabase.table('metas').insert(meta_data).execute()
                st.success(f"✅ Meta cadastrada para {mes_meta}/{ano_meta} - {cat_meta}")
                st.rerun()
    
    st.divider()
    
    st.write("**📋 Metas Cadastradas**")
    metas_raw = supabase.table('metas').select('id, ano, mes, categoria_id, valor_meta, categorias(nome)').eq('user_id', user_id).order('ano').order('mes').execute().data
    
    if metas_raw:
        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        df_metas = pd.DataFrame([{
            "ID": m['id'],
            "Ano": m['ano'],
            "Mês": meses_pt[m['mes']],
            "Categoria": m['categorias']['nome'],
            "Meta (R$)": f"R$ {m['valor_meta']:,.2f}"
        } for m in metas_raw])
        
        st.dataframe(df_metas, use_container_width=True, hide_index=True)
        
        st.write("**️ Excluir Meta**")
        meta_excluir = st.selectbox("Selecione a meta para excluir:", 
                                    [f"{m['ano']} - {meses_pt[m['mes']]} - {m['categorias']['nome']} - R$ {m['valor_meta']:,.2f}" for m in metas_raw])
        
        if st.button("🗑️ Excluir Meta Selecionada", type="secondary"):
            meta_id = metas_raw[[f"{m['ano']} - {meses_pt[m['mes']]} - {m['categorias']['nome']} - R$ {m['valor_meta']:,.2f}" for m in metas_raw].index(meta_excluir)]['id']
            supabase.table('metas').delete().eq('id', meta_id).eq('user_id', user_id).execute()
            st.success("✅ Meta excluída com sucesso!")
            st.rerun()
    else:
        st.info("Nenhuma meta cadastrada ainda.")

# ============================================================
# ABA 3: CATEGORIAS
# ============================================================
with tab3:
    st.subheader("📁 Gerenciamento de Categorias")
    cats_raw = supabase.table('categorias').select('id, nome').order('nome').execute().data
    
    st.write("** Adicionar Nova Categoria**")
    with st.form("form_nova_cat"):
        nova_cat = st.text_input("Nome da Nova Categoria", placeholder="Ex: CRÉDITOS SEGUROS")
        submitted_cat = st.form_submit_button("➕ Adicionar Categoria", use_container_width=True)
        
        if submitted_cat and nova_cat.strip():
            if any(c['nome'].upper() == nova_cat.upper() for c in cats_raw):
                st.error("❌ Já existe uma categoria com esse nome!")
            else:
                supabase.table('categorias').insert({"nome": nova_cat.upper()}).execute()
                st.success(f"✅ Categoria '{nova_cat.upper()}' adicionada!")
                st.rerun()
    
    st.divider()
    st.write("**📋 Categorias Cadastradas**")
    if cats_raw:
        for cat in cats_raw:
            col_del, col_nome = st.columns([1, 5])
            with col_nome:
                st.markdown(f"**{cat['nome']}**")
            with col_del:
                if st.button("🗑️", key=f"del_cat_{cat['id']}"):
                    subs_vinculadas = supabase.table('subcategorias').select('id').eq('categoria_id', cat['id']).execute().data
                    if subs_vinculadas:
                        st.error(f"⚠️ Não é possível excluir! Existem {len(subs_vinculadas)} subcategoria(s) vinculada(s).")
                    else:
                        supabase.table('categorias').delete().eq('id', cat['id']).execute()
                        st.success(f"✅ Categoria '{cat['nome']}' excluída!")
                        st.rerun()
    else:
        st.info("Nenhuma categoria cadastrada.")

# ============================================================
# ABA 4: SUBCATEGORIAS
# ============================================================
with tab4:
    st.subheader("📂 Gerenciamento de Subcategorias")
    cats_raw = supabase.table('categorias').select('id, nome').order('nome').execute().data
    
    if not cats_raw:
        st.warning("️ Cadastre pelo menos uma categoria primeiro na aba 'Categorias'.")
    else:
        st.write("**➕ Adicionar Nova Subcategoria**")
        with st.form("form_nova_sub"):
            col1, col2 = st.columns(2)
            with col1:
                cat_pai = st.selectbox("Categoria Pai:", [c['nome'] for c in cats_raw])
                nome_sub = st.text_input("Nome da Subcategoria", placeholder="Ex: IMÓVEIS PORTO SEGURO")
            with col2:
                tipo_sub = st.selectbox("Tipo:", ["IMÓVEIS", "VEÍCULOS", "PARCERIAS"])
                total_parc = st.number_input("Total de Parcelas:", min_value=1, max_value=24, value=8)
            
            perc_total = st.number_input("Percentual Total da Comissão (%):", min_value=0.0, max_value=100.0, step=0.01, format="%.2f", value=4.50)
            submitted_sub = st.form_submit_button("💾 Adicionar Subcategoria", use_container_width=True)
            
            if submitted_sub and nome_sub.strip():
                if any(s['nome'].upper() == nome_sub.upper() for s in supabase.table('subcategorias').select('nome').execute().data):
                    st.error("❌ Já existe uma subcategoria com esse nome!")
                else:
                    cat_id = next(c['id'] for c in cats_raw if c['nome'] == cat_pai)
                    sub_data = {
                        "categoria_id": cat_id,
                        "nome": nome_sub.upper(),
                        "tipo": tipo_sub,
                        "total_parcelas": total_parc,
                        "percentual_total": perc_total
                    }
                    supabase.table('subcategorias').insert(sub_data).execute()
                    st.success(f"✅ Subcategoria '{nome_sub.upper()}' adicionada!")
                    st.rerun()
        
        st.divider()
        st.write("**✏️ Editar Subcategoria Existente**")
        subs_raw = supabase.table('subcategorias').select('id, nome, tipo, total_parcelas, percentual_total, categoria_id').order('nome').execute().data
        
        if subs_raw:
            sub_para_editar = st.selectbox(
                "Selecione a subcategoria para editar:",
                [""] + [f"{s['nome']} (Tipo: {s['tipo']} | {s['total_parcelas']} parcelas | {s['percentual_total']}%)" for s in subs_raw]
            )
            
            if sub_para_editar:
                sub_selecionada = next(s for s in subs_raw if f"{s['nome']} (Tipo: {s['tipo']} | {s['total_parcelas']} parcelas | {s['percentual_total']}%)" == sub_para_editar)
                st.info(f"Editando: **{sub_selecionada['nome']}**")
                
                with st.form("form_editar_sub"):
                    col1, col2 = st.columns(2)
                    with col1:
                        cat_atual = next((c['nome'] for c in cats_raw if c['id'] == sub_selecionada['categoria_id']), "")
                        cat_pai_edit = st.selectbox("Categoria Pai:", [c['nome'] for c in cats_raw], index=[c['nome'] for c in cats_raw].index(cat_atual))
                        nome_sub_edit = st.text_input("Nome da Subcategoria:", value=sub_selecionada['nome'])
                    with col2:
                        tipo_sub_edit = st.selectbox("Tipo:", ["IMÓVEIS", "VEÍCULOS", "PARCERIAS"], index=["IMÓVEIS", "VEÍCULOS", "PARCERIAS"].index(sub_selecionada['tipo']))
                        total_parc_edit = st.number_input("Total de Parcelas:", min_value=1, max_value=24, value=sub_selecionada['total_parcelas'])
                    
                    perc_total_edit = st.number_input("Percentual Total da Comissão (%):", min_value=0.0, max_value=100.0, step=0.01, format="%.2f", value=float(sub_selecionada['percentual_total']))
                    submitted_edit = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                    
                    if submitted_edit and nome_sub_edit.strip():
                        nome_existe = any(s['nome'].upper() == nome_sub_edit.upper() and s['id'] != sub_selecionada['id'] for s in subs_raw)
                        if nome_existe:
                            st.error("❌ Já existe outra subcategoria com esse nome!")
                        else:
                            cat_id_edit = next(c['id'] for c in cats_raw if c['nome'] == cat_pai_edit)
                            sub_data_edit = {
                                "categoria_id": cat_id_edit,
                                "nome": nome_sub_edit.upper(),
                                "tipo": tipo_sub_edit,
                                "total_parcelas": total_parc_edit,
                                "percentual_total": perc_total_edit
                            }
                            try:
                                supabase.table('subcategorias').update(sub_data_edit).eq('id', sub_selecionada['id']).execute()
                                st.success(f"✅ Subcategoria '{nome_sub_edit.upper()}' atualizada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao atualizar: {str(e)}")
        else:
            st.info("Nenhuma subcategoria cadastrada para editar.")
        
        st.divider()
        st.write("**📋 Subcategorias Cadastradas**")
        subs_completo = supabase.table('subcategorias').select('id, nome, tipo, total_parcelas, percentual_total, categoria_id, categorias(nome)').order('categoria_id').execute().data
        
        if subs_completo:
            for cat in cats_raw:
                subs_da_cat = [s for s in subs_completo if s['categoria_id'] == cat['id']]
                if subs_da_cat:
                    st.markdown(f"### 📁 {cat['nome']}")
                    for sub in subs_da_cat:
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                        with col1: st.markdown(f"**{sub['nome']}**")
                        with col2: st.markdown(f"Tipo: {sub['tipo']}")
                        with col3: st.markdown(f"Parc: {sub['total_parcelas']}")
                        with col4: st.markdown(f"Total: {sub['percentual_total']}%")
                        with col5:
                            if st.button("🗑️", key=f"del_sub_{sub['id']}"):
                                lancamentos_vinc = supabase.table('lancamentos').select('id').eq('subcategoria_id', sub['id']).execute().data
                                if lancamentos_vinc:
                                    st.error(f"️ **Não é possível excluir '{sub['nome']}'!**")
                                    st.warning(f" Existem **{len(lancamentos_vinc)} venda(s)** registrada(s) com esta subcategoria.")
                                else:
                                    supabase.table('regras_parcelas').delete().eq('subcategoria_id', sub['id']).execute()
                                    supabase.table('subcategorias').delete().eq('id', sub['id']).execute()
                                    st.success(f"✅ Subcategoria '{sub['nome']}' excluída!")
                                    st.rerun()
                    st.divider()
        else:
            st.info("Nenhuma subcategoria cadastrada.")

# ============================================================
# ABA 5: REGRAS DE PARCELAS
# ============================================================
with tab5:
    st.subheader("📈 Regras de Percentuais por Parcela")
    st.info("✏️ Edite o percentual de cada parcela individualmente. A soma deve bater com o percentual total da subcategoria.")
    
    subs_raw = supabase.table('subcategorias').select('id, nome, tipo, total_parcelas, percentual_total').order('nome').execute().data
    
    if not subs_raw:
        st.warning("️ Cadastre subcategorias primeiro na aba 'Subcategorias'.")
    else:
        sub_escolhida = st.selectbox("Selecione a Subcategoria para Editar as Parcelas:", 
                                     [f"{s['nome']} ({s['total_parcelas']} parcelas | Total: {s['percentual_total']}%)" for s in subs_raw])
        
        sub_id = subs_raw[[f"{s['nome']} ({s['total_parcelas']} parcelas | Total: {s['percentual_total']}%)" for s in subs_raw].index(sub_escolhida)]['id']
        sub_info = next(s for s in subs_raw if s['id'] == sub_id)
        
        st.divider()
        regras_atuais = supabase.table('regras_parcelas').select('id, numero_parcela, percentual').eq('subcategoria_id', sub_id).order('numero_parcela').execute().data
        
        if not regras_atuais:
            st.info(f"📌 Nenhuma regra cadastrada para '{sub_info['nome']}'. Criando regras padrão...")
            perc_padrao = sub_info['percentual_total'] / sub_info['total_parcelas']
            for i in range(1, sub_info['total_parcelas'] + 1):
                supabase.table('regras_parcelas').insert({
                    "subcategoria_id": sub_id,
                    "numero_parcela": i,
                    "percentual": perc_padrao
                }).execute()
            regras_atuais = supabase.table('regras_parcelas').select('id, numero_parcela, percentual').eq('subcategoria_id', sub_id).order('numero_parcela').execute().data
        
        st.write(f"**✏️ Editando: {sub_info['nome']}**")
        st.write(f"Total de Parcelas: **{sub_info['total_parcelas']}** | Percentual Total: **{sub_info['percentual_total']}%**")
        
        with st.form("form_regras"):
            colunas = st.columns(min(4, sub_info['total_parcelas']))
            novos_perc = {}
            
            for regra in regras_atuais:
                col_idx = (regra['numero_parcela'] - 1) % len(colunas)
                with colunas[col_idx]:
                    perc_atual = st.number_input(
                        f"Parcela {regra['numero_parcela']} (%)",
                        min_value=0.0, max_value=100.0, step=0.01, format="%.2f",
                        value=float(regra['percentual']),
                        key=f"perc_{regra['id']}"
                    )
                    novos_perc[regra['id']] = perc_atual
            
            soma_perc = sum(novos_perc.values())
            diff = sub_info['percentual_total'] - soma_perc
            
            if abs(diff) > 0.001:
                st.warning(f"️ A soma dos percentuais ({soma_perc:.2f}%) não bate com o total ({sub_info['percentual_total']}%). Diferença: {diff:.2f}%")
            else:
                st.success(f"✅ Soma dos percentuais ({soma_perc:.2f}%) está correta!")
            
            submitted_regras = st.form_submit_button(" Salvar Regras de Parcelas", type="primary", use_container_width=True)
            
            if submitted_regras:
                for regra_id, novo_perc in novos_perc.items():
                    supabase.table('regras_parcelas').update({"percentual": novo_perc}).eq('id', regra_id).execute()
                st.success("✅ Regras de parcelas atualizadas com sucesso!")
                st.rerun()

# ============================================================
# ABA 6: IMPORTAR/EXPORTAR
# ============================================================
with tab6:
    st.subheader("📥 Importar e Exportar Dados")
    st.info("Exporte seus dados para Excel, edite/popule com novos registros e importe de volta.")
    
    col_exp, col_imp = st.columns(2)
    
    with col_exp:
        st.markdown("###  Exportar Dados")
        st.write("Gera um arquivo Excel com todas as tabelas do sistema.")
        
        if st.button(" Gerar Excel de Exportação", type="primary", use_container_width=True):
            with st.spinner("Gerando arquivo Excel..."):
                from datetime import datetime
                arquivo_excel = "backup_sistema_comissoes.xlsx"
                
                with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
                    categorias_df = pd.DataFrame(supabase.table('categorias').select('id, nome').execute().data)
                    categorias_df.to_excel(writer, sheet_name='Categorias', index=False)
                    
                    subs_df = pd.DataFrame(supabase.table('subcategorias').select('id, categoria_id, nome, tipo, total_parcelas, percentual_total').execute().data)
                    subs_df.to_excel(writer, sheet_name='Subcategorias', index=False)
                    
                    fps_df = pd.DataFrame(supabase.table('formas_pagamento').select('id, nome').execute().data)
                    fps_df.to_excel(writer, sheet_name='Formas_Pagamento', index=False)
                    
                    metas_df = pd.DataFrame(supabase.table('metas').select('id, ano, mes, categoria_id, valor_meta').eq('user_id', user_id).execute().data)
                    metas_df.to_excel(writer, sheet_name='Metas', index=False)
                    
                    lancs_df = pd.DataFrame(supabase.table('lancamentos').select('id, data_venda, subcategoria_id, valor_negociado, forma_pagamento_id, descricao').eq('user_id', user_id).execute().data)
                    lancs_df.to_excel(writer, sheet_name='Lancamentos', index=False)
                    
                    parcelas_df = pd.DataFrame(supabase.table('parcelas').select('id, lancamento_id, numero_parcela, percentual_parcela, valor_parcela, data_vencimento, status, data_pagamento, forma_pagamento_id').eq('user_id', user_id).execute().data)
                    parcelas_df.to_excel(writer, sheet_name='Parcelas', index=False)
                
                with open(arquivo_excel, "rb") as file:
                    st.download_button(
                        label="⬇️ Baixar Excel",
                        data=file,
                        file_name=f"backup_comissoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.success("✅ Arquivo Excel gerado com sucesso!")
    
    with col_imp:
        st.markdown("###  Importar Dados")
        st.write("Importe um arquivo Excel previamente exportado e editado.")
        st.warning("⚠️ **Atenção:** Os dados importados serão ADICIONADOS aos existentes.")
        
        uploaded_file = st.file_uploader("Selecione o arquivo Excel:", type=['xlsx', 'xls'])
        
        if uploaded_file:
            st.info(f"📄 Arquivo selecionado: **{uploaded_file.name}**")
            
            if st.button("📥 Importar Dados do Excel", type="primary", use_container_width=True):
                with st.spinner("Importando dados..."):
                    xls = pd.ExcelFile(uploaded_file)
                    total_importados = 0
                    
                    try:
                        if 'Lancamentos' in xls.sheet_names:
                            df_lancs = pd.read_excel(xls, sheet_name='Lancamentos')
                            for _, row in df_lancs.iterrows():
                                data_venda = row['data_venda']
                                if isinstance(data_venda, str):
                                    data_venda = pd.to_datetime(data_venda).strftime('%Y-%m-%d')
                                else:
                                    data_venda = data_venda.strftime('%Y-%m-%d')
                                
                                lanc_data = {
                                    "data_venda": data_venda,
                                    "subcategoria_id": int(row['subcategoria_id']),
                                    "valor_negociado": float(row['valor_negociado']),
                                    "forma_pagamento_id": int(row['forma_pagamento_id']),
                                    "descricao": row.get('descricao', ''),
                                    "user_id": user_id
                                }
                                supabase.table('lancamentos').insert(lanc_data).execute()
                                total_importados += 1
                        
                        if 'Parcelas' in xls.sheet_names:
                            df_parcelas = pd.read_excel(xls, sheet_name='Parcelas')
                            for _, row in df_parcelas.iterrows():
                                data_venc = row['data_vencimento']
                                if isinstance(data_venc, str):
                                    data_venc = pd.to_datetime(data_venc).strftime('%Y-%m-%d')
                                else:
                                    data_venc = data_venc.strftime('%Y-%m-%d')
                                
                                data_pag = row.get('data_pagamento')
                                if pd.notna(data_pag):
                                    if isinstance(data_pag, str):
                                        data_pag = pd.to_datetime(data_pag).strftime('%Y-%m-%d')
                                    else:
                                        data_pag = data_pag.strftime('%Y-%m-%d')
                                else:
                                    data_pag = None
                                
                                parcela_data = {
                                    "lancamento_id": int(row['lancamento_id']),
                                    "numero_parcela": int(row['numero_parcela']),
                                    "percentual_parcela": float(row['percentual_parcela']),
                                    "valor_parcela": float(row['valor_parcela']),
                                    "data_vencimento": data_venc,
                                    "status": row['status'],
                                    "data_pagamento": data_pag,
                                    "forma_pagamento_id": int(row['forma_pagamento_id']),
                                    "user_id": user_id
                                }
                                supabase.table('parcelas').insert(parcela_data).execute()
                                total_importados += 1
                        
                        st.success(f"✅ Importação concluída! {total_importados} registros adicionados.")
                        st.info("🔄 Recarregue a página para ver os novos dados.")
                    except Exception as e:
                        st.error(f"❌ Erro durante a importação: {str(e)}")

# ============================================================
# INFORMAÇÕES DO SISTEMA
# ============================================================
st.divider()
st.subheader("📊 Informações do Sistema")
col_info1, col_info2, col_info3 = st.columns(3)
col_info1.info(f"🔗 Supabase: Conectado")
col_info2.info(f"📁 Categorias: {len(subcategorias)}")
col_info3.info(f"💳 Formas Pgto: {len(formas_pagamento)}")