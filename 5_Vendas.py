   import streamlit as st

   st.set_page_config(page_title="Planos e Preços", layout="wide")
   
   st.title("🚀 Leve o Controle Total das suas Comissões")
   st.markdown("Chega de planilhas confusas e comissões perdidas. Nosso sistema foi feito para **Corretores, Correspondentes e Vendedores** que querem previsibilidade financeira.")
   
   st.divider()
   
   col1, col2, col3 = st.columns(3)
   with col1:
       st.markdown("### 📊 Dashboard Inteligente")
       st.write("Veja exatamente quanto vai receber este mês, o que está atrasado e o desempenho vs metas em tempo real.")
   with col2:
       st.markdown("### 🔒 100% Seguro")
       st.write("Seus dados são criptografados e isolados. Nenhum outro usuário tem acesso às suas vendas.")
   with col3:
       st.markdown("### 📱 Acesso de Qualquer Lugar")
       st.write("Acesse pelo computador, tablet ou celular, de onde estiver.")
       
   st.divider()
   
   st.subheader("💰 Investimento")
   st.info("**Plano Mensal:** R$ 97,00 / mês (Sem taxa de configuração, cancele quando quiser).")
   
   st.markdown("### 📞 Quer fazer um teste ou tirar dúvidas?")
   st.markdown("Fale diretamente comigo pelo WhatsApp: **[Seu Número Aqui]** ou E-mail: **[Seu E-mail Aqui]**")