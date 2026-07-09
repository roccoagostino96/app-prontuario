import streamlit as st
import pandas as pd
import json
import os

# 1. Caricamento Dati (usiamo cache per non rallentare l'app)
@st.cache_data
def load_data():
    # Carica database personale (Gold)
    db_gold = {}
    if os.path.exists('dati_aifa.json'):
        try:
            with open('dati_aifa.json', 'r', encoding='utf-8') as f:
                db_gold = json.load(f)
        except json.JSONDecodeError:
            st.error("Errore nel file JSON: controlla che le parentesi siano chiuse correttamente!")
    
    # Carica file CSV (Master)
    files = ['anagrafica_AD.csv', 'anagrafica_EH.csv', 'anagrafica_IM.csv', 'anagrafica_NR.csv', 'anagrafica_SZ.csv']
    df_list = []
    for f in files:
        if os.path.exists(f):
            # Carichiamo solo le colonne necessarie per velocità
            df_temp = pd.read_csv(f, usecols=['DENOMINAZIONE', 'PRINCIPIO_ATTIVO', 'DITTA', 'LINK FI', 'LINK RCP'])
            df_list.append(df_temp)
    
    db_master = pd.concat(df_list, ignore_index=True)
    return db_gold, db_master

# Carichiamo i dati
db_gold, db_master = load_data()

# 2. Interfaccia
st.title("Prontuario Clinico AIFA")
query = st.text_input("Inserisci il nome del farmaco:").strip().lower()

if query:
    # A. CERCA NEL GOLD (Priorità)
    if query in db_gold:
        st.success("Trovato nel tuo Prontuario Personale")
        st.write(db_gold[query])
    
    # B. CERCA NEL MASTER (Se non trovato nel Gold)
    else:
        risultati = db_master[db_master['DENOMINAZIONE'].str.lower().str.contains(query, na=False)]
        
        if not risultati.empty:
            st.info(f"Trovati {len(risultati)} risultati nell'anagrafica ufficiale:")
            st.dataframe(risultati)
        else:
            st.error("Farmaco non trovato né nel tuo prontuario, né negli archivi ufficiali.")
