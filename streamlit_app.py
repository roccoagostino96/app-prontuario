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
            st.warning("Il file JSON ha un errore di sintassi.")
    
    # Carica file CSV (Master)
    files = ['anagrafica_AD.csv', 'anagrafica_EH.csv', 'anagrafica_IM.csv', 'anagrafica_NR.csv', 'anagrafica_SZ.csv']
    df_list = []
    
    for f in files:
        if os.path.exists(f):
            # Leggiamo il file senza forzare le colonne, per evitare errori
            # sep=None capisce da solo se il separatore è virgola o punto e virgola
            df_temp = pd.read_csv(f, sep=None, engine='python', on_bad_lines='skip')
            
            # Pulisce i nomi delle colonne da spazi bianchi inutili
            df_temp.columns = df_temp.columns.str.strip()
            df_list.append(df_temp)
    
    if df_list:
        db_master = pd.concat(df_list, ignore_index=True)
    else:
        db_master = pd.DataFrame()
        
    return db_gold, db_master

# Carichiamo i dati
db_gold, db_master = load_data()

# --- 2. Interfaccia ---
st.title("Prontuario Clinico AIFA")
query = st.text_input("Inserisci il nome del farmaco:").strip().lower()

if query:
    # A. CERCA NEL GOLD (Priorità)
    # Convertiamo le chiavi del JSON in minuscolo per confronto facile
    db_gold_lower = {k.lower(): v for k, v in db_gold.items()}
    
    if query in db_gold_lower:
        st.success("Trovato nel tuo Prontuario Personale")
        st.write(db_gold_lower[query])
    
    # B. CERCA NEL MASTER (Se non trovato nel Gold)
    else:
        # Controlliamo se esiste una colonna chiamata 'DENOMINAZIONE' o simile
        col_nome = None
        for col in db_master.columns:
            if 'DENOMINAZIONE' in col.upper():
                col_nome = col
                break
        
        if col_nome:
            risultati = db_master[db_master[col_nome].str.lower().str.contains(query, na=False)]
            
            if not risultati.empty:
                st.info(f"Trovati {len(risultati)} risultati nell'anagrafica ufficiale:")
                st.dataframe(risultati)
            else:
                st.error("Farmaco non trovato né nel tuo prontuario, né negli archivi ufficiali.")
        else:
            st.error("Errore: Non riesco a trovare la colonna dei nomi nei file CSV. Colonne trovate: " + str(list(db_master.columns)))
