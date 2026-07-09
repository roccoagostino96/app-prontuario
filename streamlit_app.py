import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIGURAZIONE E CARICAMENTO ---
st.set_page_config(page_title="Prontuario 2.0", page_icon="💊")

@st.cache_data
def load_data():
    db_gold = {}
    if os.path.exists('dati_aifa.json'):
        try:
            with open('dati_aifa.json', 'r', encoding='utf-8') as f:
                db_gold = json.load(f)
        except:
            pass
    
    files = ['anagrafica_AD.csv', 'anagrafica_EH.csv', 'anagrafica_IM.csv', 'anagrafica_NR.csv', 'anagrafica_SZ.csv']
    df_list = []
    for f in files:
        if os.path.exists(f):
            # Forza separatore ; e salta riga 0 (intestazioni alla riga 1)
            df_temp = pd.read_csv(f, sep=';', header=1, engine='python', on_bad_lines='skip')
            df_temp.columns = df_temp.columns.str.strip()
            df_list.append(df_temp)
    
    db_master = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    return db_gold, db_master

db_gold, db_master = load_data()

# Dizionario icone per una visualizzazione uniforme
ICON_MAP = {
    "DENOMINAZIONE": "🏷️",
    "FORMA": "📦",
    "PA_ASSOCIATI": "🧪",
    "RAGIONE_SOCIALE": "🏭",
    "FORNITURA": "📝",
    "LINK_FI": "🔗",
    "LINK_RCP": "📄",
    "POSOLOGIA": "📋",
    "TRITURABILE": "✂️",
    "NOTE": "💡"
}

# --- 2. LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💊 Prontuario 2.0")
    st.caption("created by Rocco Agostino")
    password = st.text_input("Inserisci password:", type="password")
    if password == "1234":
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# --- 3. INTERFACCIA PRINCIPALE ---
st.title("💊 Prontuario 2.0")
st.caption("Accesso autorizzato - Benvenuto, Rocco")

query = st.text_input("🔍 Cerca farmaco:").strip().lower()

if query:
    db_gold_lower = {k.lower(): v for k, v in db_gold.items()}
    
    # --- LOGICA DI VISUALIZZAZIONE UNIFICATA ---
    
    # A. SE TROVATO NEL GOLD
    if query in db_gold_lower:
        st.success("✅ Trovato nel tuo Prontuario Personale")
        dati = db_gold_lower[query]
        for key, value in dati.items():
            icona = ICON_MAP.get(key.upper(), "ℹ️")
            st.markdown(f"### {icona} {key.replace('_', ' ').upper()}")
            st.write(value)
            
    # B. SE TROVATO NEL MASTER (CSV)
    else:
        col_nome = next((c for c in db_master.columns if 'DENOMINAZIONE' in c.upper()), None)
        if col_nome:
            risultati = db_master[db_master[col_nome].astype(str).str.lower().str.contains(query, na=False)]
            
            if not risultati.empty:
                st.warning("⚠️ Farmaco trovato nell'Anagrafica Ufficiale")
                # Mostriamo il primo risultato come scheda
                row = risultati.iloc[0]
                for col in db_master.columns:
                    valore = row[col]
                    # Mostriamo solo se il campo non è vuoto
                    if pd.notna(valore) and str(valore).strip() != "":
                        icona = ICON_MAP.get(col.upper(), "ℹ️")
                        st.markdown(f"**{icona} {col.replace('_', ' ')}**")
                        st.write(valore)
            else:
                st.error("❌ Nessun risultato trovato.")
        else:
            st.error("Errore nel caricamento file.")
