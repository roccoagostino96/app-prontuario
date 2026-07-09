import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Prontuario 2.0", page_icon="💊")

# --- 1. CARICAMENTO DATI ---
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
            df_temp = pd.read_csv(f, sep=None, engine='python', on_bad_lines='skip')
            df_temp.columns = df_temp.columns.str.strip()
            df_list.append(df_temp)
    
    db_master = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    return db_gold, db_master

# --- 2. LOGICA AUTENTICAZIONE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💊 Prontuario 2.0")
    st.caption("created by Rocco Agostino")
    password = st.text_input("Inserisci la password per accedere:", type="password")
    if password == "1234":
        st.session_state.logged_in = True
        st.rerun()
    elif password != "":
        st.error("Password errata!")
    st.stop()

# --- 3. INTERFACCIA PRINCIPALE ---
db_gold, db_master = load_data()

st.title("💊 Prontuario 2.0")
st.caption("Accesso autorizzato - Benvenuto, Rocco")

query = st.text_input("🔍 Cerca farmaco:").strip().lower()

# Mappatura icone per le sezioni
icons = {
    "nome_commerciale": "🏷️",
    "forma": "📦",
    "triturabile": "✂️",
    "posologia": "📋",
    "controindicazioni": "🚫",
    "interazioni": "⚠️",
    "effetti_collaterali": "🩺"
}

if query:
    db_gold_lower = {k.lower(): v for k, v in db_gold.items()}
    
    # A. CERCA NEL GOLD
    if query in db_gold_lower:
        st.success("✅ Trovato nel tuo Prontuario Personale")
        dati = db_gold_lower[query]
        
        # Visualizzazione formattata
        for key, value in dati.items():
            icona = icons.get(key, "ℹ️")
            st.markdown(f"### {icona} {key.replace('_', ' ').upper()}")
            st.write(value)
    
   # B. CERCA NEL MASTER (Se non trovato nel Gold)
    else:
        col_nome = next((c for c in db_master.columns if 'DENOMINAZIONE' in c.upper()), None)
        if col_nome:
            risultati = db_master[db_master[col_nome].str.lower().str.contains(query, na=False)]
            
            if not risultati.empty:
                # Modifica qui: st.warning rende il box giallo, avvisandoti del cambio di database
                st.warning("⚠️ Farmaco non nel Prontuario Personale. Dati estratti dall'Anagrafica Ufficiale:")
                st.dataframe(risultati, use_container_width=True)
            else:
                st.error("❌ Nessun risultato trovato in nessun database.")
