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

# --- FUNÇÕES ---
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
                st.rerun()
            else:
                st.error("Digite o nome do alimento!")

    st.divider()
    st.subheader("👇 Já registrado hoje:")
    df = carregar_comida()
    if not df.empty:
        hoje = datetime.now().strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == hoje]
        if not df_hoje.empty:
            st.dataframe(df_hoje[['Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal']], use_container_width=True, hide_index=True)

# --- ABA 2: PESO ---
with aba_weight:
    st.header("Controle de Peso")
    col_input, col_graph = st.columns([1, 2])
    
    with col_input:
        with st.container(border=True):
            st.subheader("Registrar Peso")
            peso_hoje = st.number_input("Peso (kg)", 0.0, step=0.1, format="%.1f")
            if st.button("⚖️ Salvar Peso"):
                if peso_hoje > 0:
                    salvar_peso(peso_hoje)
                    st.toast("Peso registrado!")
                    st.rerun()
    
    with col_graph:
        st.subheader("Evolução")
        df_peso = carregar_peso()
        if not df_peso.empty:
            df_peso['Data_Obj'] = pd.to_datetime(df_peso['Data'], dayfirst=True)
            df_peso = df_peso.sort_values('Data_Obj')
            st.line_chart(df_peso, x='Data', y='Peso')
            st.metric("Peso Atual", f"{df_peso.iloc[-1]['Peso']} kg")
        else:
            st.info("Nenhum peso registrado ainda.")

# --- ABA 3: RELATÓRIOS ---
with aba_reports:
    st.header("Diário Alimentar")
    
    df_food = carregar_comida()
    if not df_food.empty:
        col_date, col_vazia = st.columns([1, 3])
        with col_date:
            data_selecionada = st.date_input("📅 Escolha o dia:", datetime.now())
        
        data_str = data_selecionada.strftime("%d/%m/%Y")
        df_filtrada = df_food[df_food['Data'] == data_str]
        
        st.divider()
        st.subheader(f"Resumo de: {data_str}")
        
        if not df_filtrada.empty:
            total_c = df_filtrada['Carbo'].sum()
            total_p = df_filtrada['Prot'].sum()
            total_g = df_filtrada['Gord'].sum()
            total_k = df_filtrada['Kcal'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Carbo", f"{total_c:.1f}g", f"{META_CARBO - total_c:.1f}g resta", delta_color="inverse")
            c2.metric("Prot", f"{total_p:.1f}g")
            c3.metric("Gord", f"{total_g:.1f}g")
            c4.metric("Kcal", f"{total_k:.0f}")
            
            prog = min(total_c / META_CARBO, 1.0)
            st.progress(prog)
            
            st.dataframe(df_filtrada, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Nenhum registro encontrado para o dia {data_str}.")

        st.divider()
        st.subheader("📈 Visão Geral da Semana")
        # Correção para evitar erro se a coluna não existir
        if 'Data' in df_food.columns:
             df_food['Data_Obj'] = pd.to_datetime(df_food['Data'], dayfirst=True)
             df_agrupado = df_food.groupby('Data')['Carbo'].sum().reset_index()
             df_agrupado['Data_Sort'] = pd.to_datetime(df_agrupado['Data'], dayfirst=True)
             df_agrupado = df_agrupado.sort_values('Data_Sort').tail(7)
             st.bar_chart(df_agrupado, x='Data', y='Carbo')
        
    else:
        st.write("Sem dados.")

# --- ABA 4: GERENCIAR (O SEGREDO ESTÁ AQUI) ---
with aba_settings:
    st.header("Backup e Restauração")
    st.info("Salve seus dados antes de sair!")
    
    c1, c2 = st.columns(2)
    
    # BOTÕES DE DOWNLOAD
    with c1:
        st.subheader("⬇️ 1. Baixar (Salvar)")
        df = carregar_comida()
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Baixar Histórico Comida", csv, "historico_keto.csv", "text/csv")
        else:
            st.write("Sem histórico de comida para baixar.")
            
        df_p = carregar_peso()
        if not df_p.empty:
            csv_p = df_p.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Baixar Histórico Peso", csv_p, "historico_peso.csv", "text/csv")

    # BOTÃO DE UPLOAD
    with c2:
        st.subheader("⬆️ 2. Restaurar")
        uploaded_file = st.file_uploader("Enviar 'historico_keto.csv'", type="csv")
        
        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                df_up.to_csv(ARQUIVO_COMIDA, index=False)
                st.success("✅ Histórico Restaurado! Pode atualizar a página.")
            except:
                st.error("Arquivo inválido.")

    st.divider()
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
