import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da Página
st.set_page_config(page_title="Keto Tracker", page_icon="🥑")

# --- CONFIGURAÇÕES ---
ARQUIVO_COMIDA = 'historico_keto.csv'
META_CARBO = 30  # Meta diária

# --- FUNÇÕES ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_COMIDA):
        df = pd.DataFrame(columns=['Data', 'Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal'])
        df.to_csv(ARQUIVO_COMIDA, index=False)
    return pd.read_csv(ARQUIVO_COMIDA)

def salvar_refeicao(cardapio, c, p, g, k):
    df = carregar_dados()
    nova_linha = {
        'Data': datetime.now().strftime("%d/%m/%Y"),
        'Cardápio': cardapio,
        'Carbo': c, 'Prot': p, 'Gord': g, 'Kcal': k
    }
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(ARQUIVO_COMIDA, index=False)

# --- INTERFACE DO APP (O que aparece na tela) ---
st.title("🥑 Meu Keto Tracker")

# Abas do App
aba1, aba2 = st.tabs(["🍽️ Registrar", "📊 Relatórios"])

with aba1:
    st.header("Nova Refeição")
    
    # Formulário de entrada
    nome = st.text_input("O que você comeu?", placeholder="Ex: 3 ovos com bacon")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: carbo = st.number_input("Carbo (g)", min_value=0.0, step=0.1)
    with col2: prot = st.number_input("Prot (g)", min_value=0.0, step=0.1)
    with col3: gord = st.number_input("Gord (g)", min_value=0.0, step=0.1)
    with col4: kcal = st.number_input("Kcal", min_value=0.0, step=1.0)
    
    if st.button("Salvar Refeição", type="primary"):
        if nome:
            salvar_refeicao(nome, carbo, prot, gord, kcal)
            st.success(f"✅ {nome} registrado!")
        else:
            st.warning("Escreva o nome do alimento!")

with aba2:
    st.header("Resumo do Dia")
    
    df = carregar_dados()
    
    if not df.empty:
        # Filtra só hoje
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        
        if not df_hoje.empty:
            total_carbo = df_hoje['Carbo'].sum()
            total_prot = df_hoje['Prot'].sum()
            total_gord = df_hoje['Gord'].sum()
            total_kcal = df_hoje['Kcal'].sum()
            
            # Métricas grandes
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Carbo", f"{total_carbo:.1f}g", delta=f"{META_CARBO - total_carbo:.1f}g restantes", delta_color="inverse")
            c2.metric("Proteína", f"{total_prot:.1f}g")
            c3.metric("Gordura", f"{total_gord:.1f}g")
            c4.metric("Calorias", f"{total_kcal:.0f}")
            
            # Barra de Progresso do Carbo
            progresso = min(total_carbo / META_CARBO, 1.0)
            st.write(f"Meta de Carbo: {int(progresso*100)}%")
            
            if total_carbo < 25:
                cor_barra = "green" # Streamlit usa cor do tema, mas podemos avisar
                st.success("🟢 Você está na zona de Queima de Gordura!")
            elif total_carbo < 35:
                st.warning("🟡 Atenção com os carbos!")
            else:
                st.error("🔴 Cuidado! Risco de sair da cetose.")
            
            st.progress(progresso)
            
            st.divider()
            st.subheader("Histórico de Hoje")
            st.dataframe(df_hoje[['Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal']], hide_index=True)
            
        else:
            st.info("Nenhuma refeição registrada hoje.")
    else:
        st.write("Seu histórico está vazio.")
