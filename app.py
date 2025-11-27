import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA (AQUI ESTÁ O TRUQUE) ---
# Adicionei layout="wide" para usar a tela inteira
st.set_page_config(page_title="Keto Tracker", page_icon="🥑", layout="wide")

# --- CONFIGURAÇÕES ---
ARQUIVO_COMIDA = 'historico_keto.csv'
META_CARBO = 30  # Meta diária

# --- FUNÇÕES ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_COMIDA):
        df = pd.DataFrame(columns=['Data', 'Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal'])
        df.to_csv(ARQUIVO_COMIDA, index=False)
        return df
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

def deletar_refeicao(index):
    df = carregar_dados()
    df = df.drop(index)
    df.to_csv(ARQUIVO_COMIDA, index=False)

# --- INTERFACE DO APP ---
st.title("🥑 Meu Keto Tracker")

# Criamos 3 abas
aba1, aba2, aba3 = st.tabs(["🍽️ Registrar", "📊 Relatórios", "✏️ Gerenciar"])

# --- ABA 1: REGISTRAR ---
with aba1:
    st.header("Nova Refeição")
    nome = st.text_input("O que você comeu?", placeholder="Ex: 3 ovos com bacon")
    
    # Colunas para os números ficarem lado a lado
    c1, c2, c3, c4 = st.columns(4)
    with c1: carbo = st.number_input("Carbo (g)", min_value=0.0, step=0.1)
    with c2: prot = st.number_input("Prot (g)", min_value=0.0, step=0.1)
    with c3: gord = st.number_input("Gord (g)", min_value=0.0, step=0.1)
    with c4: kcal = st.number_input("Kcal", min_value=0.0, step=1.0)
    
    if st.button("Salvar Refeição", type="primary"):
        if nome:
            salvar_refeicao(nome, carbo, prot, gord, kcal)
            st.success(f"✅ {nome} registrado!")
            st.rerun() 
        else:
            st.warning("Escreva o nome do alimento!")

# --- ABA 2: RELATÓRIOS ---
with aba2:
    st.header("Resumo do Dia")
    df = carregar_dados()
    
    if not df.empty:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        
        if not df_hoje.empty:
            total_carbo = df_hoje['Carbo'].sum()
            total_prot = df_hoje['Prot'].sum()
            total_gord = df_hoje['Gord'].sum()
            total_kcal = df_hoje['Kcal'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Carbo", f"{total_carbo:.1f}g", delta=f"{META_CARBO - total_carbo:.1f}g resta", delta_color="inverse")
            c2.metric("Prot", f"{total_prot:.1f}g")
            c3.metric("Gord", f"{total_gord:.1f}g")
            c4.metric("Kcal", f"{total_kcal:.0f}")
            
            progresso = min(total_carbo / META_CARBO, 1.0)
            if total_carbo < 25: st.success(f"🟢 Zona de Queima! ({int(progresso*100)}% da meta)")
            elif total_carbo < 35: st.warning(f"🟡 Atenção! ({int(progresso*100)}% da meta)")
            else: st.error(f"🔴 Cuidado! ({int(progresso*100)}% da meta)")
            st.progress(progresso)
            
            st.divider()
            st.write("Histórico de Hoje:")
            # use_container_width=True estica a tabela
            st.dataframe(df_hoje, hide_index=True, use_container_width=True)
        else:
            st.info("Nada registrado hoje.")
            
        st.divider()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Baixar Backup Completo", csv, "backup_keto.csv", "text/csv")
    else:
        st.write("Sem dados.")

# --- ABA 3: GERENCIAR ---
with aba3:
    st.header("Editar Histórico Completo")
    st.info("Se a tabela estiver cortada, tente girar o celular ou maximizar a janela.")
    
    df = carregar_dados()
    if not df.empty:
        # AQUI ESTÁ A MUDANÇA VISUAL DA TABELA
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Área de Exclusão")
        
        lista_opcoes = [f"{i} - {row['Data']} - {row['Cardápio']}" for i, row in df.iterrows()]
        escolha = st.selectbox("Selecione o item para apagar:", options=lista_opcoes)
        
        if st.button("Excluir Selecionado", type="primary"):
            index_to_drop = int(escolha.split(' - ')[0])
            deletar_refeicao(index_to_drop)
            st.success("Item apagado!")
            st.rerun()
    else:
        st.info("O histórico está vazio.")
