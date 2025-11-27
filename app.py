import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Keto Tracker Pro", page_icon="🥑", layout="wide")

# --- ARQUIVOS ---
ARQUIVO_COMIDA = 'historico_keto.csv'
ARQUIVO_PESO = 'historico_peso.csv'
META_CARBO = 30 

# --- FUNÇÕES DE CARREGAMENTO ---
def carregar_comida():
    if not os.path.exists(ARQUIVO_COMIDA):
        df = pd.DataFrame(columns=['Data', 'Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal'])
        df.to_csv(ARQUIVO_COMIDA, index=False)
        return df
    return pd.read_csv(ARQUIVO_COMIDA)

def carregar_peso():
    if not os.path.exists(ARQUIVO_PESO):
        df = pd.DataFrame(columns=['Data', 'Peso'])
        df.to_csv(ARQUIVO_PESO, index=False)
        return df
    return pd.read_csv(ARQUIVO_PESO)

# --- FUNÇÕES DE SALVAMENTO ---
def salvar_refeicao(cardapio, c, p, g, k):
    df = carregar_comida()
    nova_linha = {
        'Data': datetime.now().strftime("%d/%m/%Y"),
        'Cardápio': cardapio,
        'Carbo': c, 'Prot': p, 'Gord': g, 'Kcal': k
    }
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(ARQUIVO_COMIDA, index=False)

def salvar_peso(peso_atual):
    df = carregar_peso()
    nova_linha = {
        'Data': datetime.now().strftime("%d/%m/%Y"),
        'Peso': peso_atual
    }
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(ARQUIVO_PESO, index=False)

def deletar_refeicao(index):
    df = carregar_comida()
    df = df.drop(index)
    df.to_csv(ARQUIVO_COMIDA, index=False)

# --- INTERFACE ---
st.title("🥑 Painel de Controle Keto")

# Criamos as 4 abas principais
aba_food, aba_weight, aba_reports, aba_settings = st.tabs([
    "🍽️ Alimentação", "⚖️ Peso", "📊 Relatórios", "⚙️ Gerenciar"
])

# --- ABA 1: ALIMENTAÇÃO ---
with aba_food:
    st.header("Lançar Refeição")
    with st.container(border=True):
        nome = st.text_input("O que você comeu?", placeholder="Ex: Frango com brócolis")
        c1, c2, c3, c4 = st.columns(4)
        with c1: carbo = st.number_input("Carbo (g)", 0.0, step=0.1)
        with c2: prot = st.number_input("Prot (g)", 0.0, step=0.1)
        with c3: gord = st.number_input("Gord (g)", 0.0, step=0.1)
        with c4: kcal = st.number_input("Kcal", 0.0, step=1.0)
        
        if st.button("💾 Salvar Refeição", type="primary"):
            if nome:
                salvar_refeicao(nome, carbo, prot, gord, kcal)
                st.toast(f"✅ {nome} salvo!")
                st.rerun() # Atualiza a tela
            else:
                st.error("Digite o nome do alimento!")

# --- ABA 2: PESO ---
with aba_weight:
    st.header("Controle de Peso")
    
    col_input, col_graph = st.columns([1, 2])
    
    with col_input:
        with st.container(border=True):
            st.subheader("Registrar Peso Hoje")
            peso_hoje = st.number_input("Seu peso (kg)", 0.0, step=0.1, format="%.1f")
            if st.button("⚖️ Salvar Peso"):
                if peso_hoje > 0:
                    salvar_peso(peso_hoje)
                    st.toast("Peso registrado!")
                    st.rerun()
    
    with col_graph:
        st.subheader("Sua Evolução")
        df_peso = carregar_peso()
        if not df_peso.empty:
            # Tratamento de data para o gráfico ficar bonito
            df_peso['Data_Obj'] = pd.to_datetime(df_peso['Data'], dayfirst=True)
            df_peso = df_peso.sort_values('Data_Obj')
            
            # Gráfico de Linha
            st.line_chart(df_peso, x='Data', y='Peso')
            
            # Mostra o último peso
            ultimo_peso = df_peso.iloc[-1]['Peso']
            st.metric("Peso Atual", f"{ultimo_peso} kg")
        else:
            st.info("Nenhum peso registrado ainda.")

# --- ABA 3: RELATÓRIOS ---
with aba_reports:
    st.header("Relatórios de Performance")
    
    df_food = carregar_comida()
    if not df_food.empty:
        # Prepara dados
        df_food['Data_Obj'] = pd.to_datetime(df_food['Data'], dayfirst=True)
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        
        # --- RESUMO DE HOJE ---
        st.subheader(f"📅 Resumo de Hoje ({hoje_str})")
        df_hoje = df_food[df_food['Data'] == hoje_str]
        
        if not df_hoje.empty:
            total_c = df_hoje['Carbo'].sum()
            total_p = df_hoje['Prot'].sum()
            total_g = df_hoje['Gord'].sum()
            total_k = df_hoje['Kcal'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Carbo", f"{total_c:.1f}g", f"{META_CARBO - total_c:.1f}g restante", delta_color="inverse")
            col2.metric("Prot", f"{total_p:.1f}g")
            col3.metric("Gord", f"{total_g:.1f}g")
            col4.metric("Kcal", f"{total_k:.0f}")
            
            # Barra de Progresso
            prog = min(total_c / META_CARBO, 1.0)
            st.progress(prog)
            if total_c > 35: st.error("🚨 Cuidado! Carbos altos.")
            elif total_c > 25: st.warning("⚠️ Atenção.")
            else: st.success("✅ Na zona Keto!")
        else:
            st.info("Nada registrado hoje.")

        st.divider()

        # --- RESUMO SEMANAL (GRÁFICOS) ---
        st.subheader("📈 Histórico dos Últimos Dias")
        
        # Agrupa por dia
        df_agrupado = df_food.groupby('Data')['Carbo'].sum().reset_index()
        # Ordena por data (gambiarra pra ordenar string de data corretamente)
        df_agrupado['Data_Sort'] = pd.to_datetime(df_agrupado['Data'], dayfirst=True)
        df_agrupado = df_agrupado.sort_values('Data_Sort').tail(7) # Pega os últimos 7 dias
        
        st.write("Consumo de Carboidratos (g) por dia:")
        st.bar_chart(df_agrupado, x='Data', y='Carbo')
        
    else:
        st.write("Comece a registrar para ver os gráficos!")

# --- ABA 4: GERENCIAR ---
with aba_settings:
    st.header("Correções")
    df = carregar_comida()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        lista = [f"{i} - {row['Data']} - {row['Cardápio']}" for i, row in df.iterrows()]
        escolha = st.selectbox("Apagar item:", lista)
        if st.button("🗑️ Excluir Item"):
            idx = int(escolha.split(' - ')[0])
            deletar_refeicao(idx)
            st.success("Apagado!")
            st.rerun()
    
    st.divider()
    # Backup
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha Completa", csv, "backup_keto.csv", "text/csv")
