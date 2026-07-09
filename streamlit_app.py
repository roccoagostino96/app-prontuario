import streamlit as dict_streamlit
import json

# Configurazione App
dict_streamlit.set_page_config(page_title="Prontuario Clinico AIFA", page_icon="⚕️", layout="centered")

PIN_SEGRETO = "1234"

# Iniezione CSS per stile
dict_streamlit.markdown("""
<style>
.stTabs button p { font-size: 1.15rem !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

if "autenticato" not in dict_streamlit.session_state:
    dict_streamlit.session_state["autenticato"] = False

# Funzione per caricare il database locale
def carica_database():
    try:
        with open("dati_aifa.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

dict_streamlit.title("⚕️ Prontuario Clinico AIFA")

# --- SCHERMATA BLOCCO ---
if not dict_streamlit.session_state["autenticato"]:
    dict_streamlit.write("Inserisci il PIN di sicurezza.")
    pin_inserito = dict_streamlit.text_input("🔑 PIN:", type="password")
    
    if pin_inserito == PIN_SEGRETO:
        dict_streamlit.session_state["autenticato"] = True
        dict_streamlit.rerun() 
    elif pin_inserito != "":
        dict_streamlit.error("PIN errato. Riprova.")

# --- SCHERMATA APP ---
if dict_streamlit.session_state["autenticato"]:
    
    col1, col2 = dict_streamlit.columns([8, 2])
    with col2:
        if dict_streamlit.button("🔒 Esci"):
            dict_streamlit.session_state["autenticato"] = False
            dict_streamlit.rerun()
            
    dict_streamlit.markdown("### 🔍 Cerca Farmaco (Database Locale)")
    
    database = carica_database()
    
    if database is None:
        dict_streamlit.error("❌ Errore: File 'dati_aifa.json' non trovato. Crealo su GitHub!")
    else:
        # Crea una lista di tutte le molecole disponibili nel database
        molecole_disponibili = list(database.keys())
        
        nome_farmaco = dict_streamlit.text_input("Digita Principio Attivo (es: paracetamolo, furosemide):").lower().strip()
        
        if nome_farmaco:
            if nome_farmaco in database:
                dati = database[nome_farmaco]
                
                dict_streamlit.success(f"✅ Molecola trovata: **{nome_farmaco.upper()}**")
                
                dict_streamlit.markdown(f"**Nomi Commerciali Comuni:** {dati.get('nome_commerciale', 'N/D')}")
                dict_streamlit.markdown(f"**Formulazioni:** {dati.get('forma', 'N/D')}")
                
                triturabile = dati.get('triturabile', 'N/D').lower()
                if "no" in triturabile or "non" in triturabile:
                    dict_streamlit.error(f"🚨 **TRITURABILITÀ:** {dati.get('triturabile')}")
                else:
                    dict_streamlit.success(f"🟢 **TRITURABILITÀ:** {dati.get('triturabile')}")
                    
                tab1, tab2, tab3, tab4 = dict_streamlit.tabs(["⏱️ Posologia", "❌ Controindicazioni", "🔄 Interazioni", "⚠️ Effetti Collaterali"])
                
                with tab1:
                    dict_streamlit.write(dati.get("posologia", "Nessun dato"))
                with tab2:
                    dict_streamlit.write(dati.get("controindicazioni", "Nessun dato"))
                with tab3:
                    dict_streamlit.write(dati.get("interazioni", "Nessun dato"))
                with tab4:
                    dict_streamlit.write(dati.get("effetti_collaterali", "Nessun dato"))
            else:
                dict_streamlit.warning(f"Molecola '{nome_farmaco}' non ancora presente nel database locale. Controlla l'ortografia o aggiorna il file JSON.")
