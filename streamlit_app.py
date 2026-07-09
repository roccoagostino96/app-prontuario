import streamlit as st
import pandas as pd
import json
import os

# --- 1. Caricamento Dati ---
@st.cache_data
def load_data():
    # Carica database personale (Gold)
    db_gold = {}
    if os.path.exists('dati_aifa.json'):
        try:
            with open('dati_aifa.json', 'r', encoding='utf-8') as f:
                db_gold = json.load(f)
        except:
            pass
    
    # Carica file CSV (Master)
    files = ['anagrafica_AD.csv', 'anagrafica_EH.csv', 'anagrafica_IM.csv', 'anagrafica_NR.csv', 'anagrafica_SZ.csv']
    df_list = []
    
    # Lista delle colonne che hai confermato
    cols_to_use = [
        'CODICE_AIC', 'COD_FARMACO', 'COD_CONFEZIONE', 'DENOMINAZIONE', 
        'DESCRIZIONE', 'CODICE_DITTA', 'RAGIONE_SALES', 'STATO_AMMINISTRATIVO', 
        'TIPO_PROCEDURA', 'FORMA', 'CODICE_ATC', 'PA_ASSOCIATI', 
        'FORNITURA', 'LINK_FI', 'LINK_RCP'
    ]

    for f in files:
        if os.path.exists(f):
            # header=1 è il comando magico che salta la prima riga "sporca"
            df_temp = pd.read_csv(f, sep=None, engine='python', on_bad_lines='skip', header=1)
            
            # Pulisce gli spazi nei nomi delle colonne
            df_temp.columns = df_temp.columns.str.strip()
            df_list.append(df_temp)
    
    db_master = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    return db_gold, db_master

db_gold, db_master = load_data()

# --- 2. Interfaccia ---
st.set_page_config(page_title="Prontuario 2.0", page_icon="💊")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💊 Prontuario 2.0")
    password = st.text_input("Password:", type="password")
    if password == "1234":
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

st.title("💊 Prontuario 2.0")
query = st.text_input("🔍 Cerca farmaco:").strip().lower()

# Debug switch
mostra_debug = st.checkbox("Mostra info tecniche (DEBUG)")

if query:
    db_gold_lower = {k.lower(): v for k, v in db_gold.items()}
    
    if query in db_gold_lower:
        st.success("✅ Trovato nel tuo Prontuario Personale")
        st.write(db_gold_lower[query])
    else:
        # Cerca la colonna col nome (cerchiamo 'DENOMINAZIONE')
        col_nome = next((c for c in db_master.columns if 'DENOMINAZIONE' in c.upper()), None)
        
        if mostra_debug:
            st.write(f"Colonna trovata per i nomi: {col_nome}")
            st.write("Prime 5 colonne:", db_master.columns.tolist()[:5])

        if col_nome:
            risultati = db_master[db_master[col_nome].astype(str).str.lower().str.contains(query, na=False)]
            if not risultati.empty:
                st.warning("⚠️ Farmaco trovato nell'Anagrafica Ufficiale:")
                st.dataframe(risultati, use_container_width=True)
            else:
                st.error("❌ Nessun risultato trovato.")
        else:
            st.error("Errore: Non trovo la colonna DENOMINAZIONE. Controlla il Debug.")
