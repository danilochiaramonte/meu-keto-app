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

# Agora a função aceita a DATA como argumento
def salvar_refeicao(data_str, cardapio, c, p, g, k):
    df = carregar_comida()
    nova_linha = {
        'Data': data_str,
        'Cardápio': cardapio,
        'Carbo': c, 'Prot': p, 'Gord': g, 'Kcal': k
    }
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(ARQUIVO_COMIDA, index=False)

def salvar_peso(data_str, peso_atual):
    df = carregar_peso()
    nova_linha = {
        'Data': data_str,
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

# --- ABA 1: ALIMENTAÇÃO (COM DATA RETROATIVA) ---
with aba_food:
    st.header("Lançar Refeição")
    with st.container(border=True):
        # Seletor de Data
        col_data, col_nome = st.columns([1, 3])
        with col_data:
            data_registro = st.date_input("📅 Data da refeição:", datetime.now())
        with col_nome:
            nome = st.text_input("O que você comeu?", placeholder="Ex: Frango com brócolis")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: carbo = st.number_input("Carbo (g)", 0.0, step=0.1)
        with c2: prot = st.number_input("Prot (g)", 0.0, step=0.1)
        with c3: gord = st.number_input("Gord (g)", 0.0, step=0.1)
        with c4: kcal = st.number_input("Kcal", 0.0, step=1.0)
        
        if st.button("💾 Salvar Refeição", type="primary"):
            if nome:
                # Converte a data escolhida para texto
                data_str = data_registro.strftime("%d/%m/%Y")
                salvar_refeicao(data_str, nome, carbo, prot, gord, kcal)
                st.toast(f"✅ Salvo em {data_str}!")
                st.rerun()
            else:
                st.error("Digite o nome do alimento!")

    st.divider()
    st.subheader("👇 Registros do Dia Selecionado:")
    df = carregar_comida()
    if not df.empty:
        data_atual_str = data_registro.strftime("%d/%m/%Y")
        df_hoje = df[df['Data'] == data_atual_str]
        if not df_hoje.empty:
            st.dataframe(df_hoje[['Cardápio', 'Carbo', 'Prot', 'Gord', 'Kcal']], use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum registro para {data_atual_str}")

# --- ABA 2: PESO (COM DATA RETROATIVA) ---
with aba_weight:
    st.header("Controle de Peso")
    col_input, col_graph = st.columns([1, 2])
    
    with col_input:
        with st.container(border=True):
            st.subheader("Registrar Peso")
            data_peso = st.date_input("📅 Data da pesagem:", datetime.now())
            peso_hoje = st.number_input("Peso (kg)", 0.0, step=0.1, format="%.1f")
            
            if st.button("⚖️ Salvar Peso"):
                if peso_hoje > 0:
                    data_str = data_peso.strftime("%d/%m/%Y")
                    salvar_peso(data_str, peso_hoje)
                    st.toast(f"Peso de {data_str} registrado!")
                    st.rerun()
    
    with col_graph:
        st.subheader("Evolução")
        df_peso = carregar_peso()
        if not df_peso.empty:
            df_peso['Data_Obj'] = pd.to_datetime(df_peso['Data'], dayfirst=True)
            df_peso = df_peso.sort_values('Data_Obj')
            st.line_chart(df_peso, x='Data', y='Peso')
            st.dataframe(df_peso, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum peso registrado ainda.")

# --- ABA 3: RELATÓRIOS (COM CALENDÁRIO FIXO) ---
with aba_reports:
    st.header("Diário Alimentar")
    
    # Seletor de data SEMPRE visível
    col_date, col_vazia = st.columns([1, 3])
    with col_date:
        data_selecionada = st.date_input("📅 Visualizar dia:", datetime.now())
    
    df_food = carregar_comida()
    
    if not df_food.empty:
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
        if 'Data' in df_food.columns:
             df_food['Data_Obj'] = pd.to_datetime(df_food['Data'], dayfirst=True)
             df_agrupado = df_food.groupby('Data')['Carbo'].sum().reset_index()
             df_agrupado['Data_Sort'] = pd.to_datetime(df_agrupado['Data'], dayfirst=True)
             df_agrupado = df_agrupado.sort_values('Data_Sort').tail(7)
             st.bar_chart(df_agrupado, x='Data', y='Carbo')
        
    else:
        st.info("Comece a registrar na aba 'Alimentação' para ver os dados.")

# --- ABA 4: GERENCIAR ---
with aba_settings:
    st.header("Backup e Restauração")
    st.info("Salve seus dados regularmente!")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("⬇️ Baixar")
        df = carregar_comida()
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Histórico Comida", csv, "historico_keto.csv", "text/csv")
            
        df_p = carregar_peso()
        if not df_p.empty:
            csv_p = df_p.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Histórico Peso", csv_p, "historico_peso.csv", "text/csv")

    with c2:
        st.subheader("⬆️ Restaurar")
        uploaded_file = st.file_uploader("Enviar 'historico_keto.csv'", type="csv")
        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                df_up.to_csv(ARQUIVO_COMIDA, index=False)
                st.success("✅ Histórico Comida Restaurado!")
            except:
                st.error("Erro no arquivo.")

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
