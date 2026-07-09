import streamlit as st
import pandas as pd
import json
import os

# --- 1. Caricamento Dati ---
@st.cache_data
def load_data():
    db_gold = {}
    if os.path.exists('dati_aifa.json'):
        with open('dati_aifa.json', 'r', encoding='utf-8') as f:
            try: db_gold = json.load(f)
            except: pass
    
    files = ['anagrafica_AD.csv', 'anagrafica_EH.csv', 'anagrafica_IM.csv', 'anagrafica_NR.csv', 'anagrafica_SZ.csv']
    df_list = []
    for f in files:
        if os.path.exists(f):
            df_temp = pd.read_csv(f, sep=None, engine='python', on_bad_lines='skip')
            df_temp.columns = df_temp.columns.str.strip() # Pulisce spazi
            df_list.append(df_temp)
    
    db_master = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    return db_gold, db_master

db_gold, db_master = load_data()

# --- 2. Interfaccia ---
st.title("Prontuario Clinico AIFA")
query = st.text_input("Inserisci il nome del farmaco:").strip().lower()

# --- DEBUG: Vediamo cosa vede l'app ---
if st.checkbox("Mostra info tecniche (DEBUG)"):
    st.write(f"Righe totali nel master: {len(db_master)}")
    st.write("Colonne trovate:", db_master.columns.tolist())

if query:
    db_gold_lower = {k.lower(): v for k, v in db_gold.items()}
    
    if query in db_gold_lower:
        st.success("Trovato nel tuo Prontuario Personale")
        st.write(db_gold_lower[query])
    else:
        # CERCA COLONNA
        col_nome = None
        for col in db_master.columns:
            if 'DENOMINAZIONE' in col.upper():
                col_nome = col
                break
        
        if col_nome:
            risultati = db_master[db_master[col_nome].astype(str).str.lower().str.contains(query, na=False)]
            if not risultati.empty:
                st.warning("⚠️ Farmaco trovato nell'Anagrafica Ufficiale:")
                st.dataframe(risultati, use_container_width=True)
            else:
                st.error("Nessun risultato trovato.")
        else:
            st.error("Errore: Non trovo la colonna con i nomi dei farmaci!")
