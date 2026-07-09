import streamlit as dict_streamlit
import urllib.request
import urllib.parse
import urllib.error
import json
from deep_translator import GoogleTranslator

# Configurazione
dict_streamlit.set_page_config(page_title="Prontuario Clinico Rapido", page_icon="⚕️", layout="centered")
PIN_SEGRETO = "1234"

# --- INIEZIONE CSS PER INGRANDIRE L'INDICE (TABS) E I FONT ---
dict_streamlit.markdown("""
<style>
/* Ingrandisce il font delle schede cliccabili (Tabs) */
.stTabs button p {
    font-size: 1.25rem !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DI MEMORIA PER NASCONDERE IL PIN ---
if "autenticato" not in dict_streamlit.session_state:
    dict_streamlit.session_state["autenticato"] = False

def traduci_in_italiano(testo):
    if not testo: return "Dato non presente."
    testo_sicuro = testo[:4000]
    try:
        return GoogleTranslator(source='en', target='it').translate(testo_sicuro)
    except:
        return "Errore di traduzione temporaneo."

def riassumi_testo(testo, num_frasi=4):
    if not testo: return ""
    frasi = testo.split(". ")
    frasi_brevi = frasi[:num_frasi]
    testo_breve = ". ".join(frasi_brevi)
    if len(frasi) > num_frasi:
        testo_breve += "."
    return testo_breve

def formatta_a_punti(testo):
    if not testo: return ""
    frasi = testo.split(". ")
    testo_bello = ""
    for frase in frasi:
        frase = frase.strip()
        if len(frase) > 5:
            if not frase.endswith("."):
                frase += "."
            testo_bello += f"* {frase}\n\n"
    return testo_bello

dict_streamlit.title("⚕️ Prontuario Clinico Rapido")

# --- SCHERMATA BLOCCO ---
if not dict_streamlit.session_state["autenticato"]:
    dict_streamlit.write("Inserisci il PIN di sicurezza per sbloccare il prontuario.")
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
            
    # TITOLO DI RICERCA PIÙ GRANDE
    dict_streamlit.markdown("### 🔍 Cerca Principio Attivo")
    nome_farmaco_it = dict_streamlit.text_input("es: furosemide, amoxicillina, fentanil", label_visibility="collapsed")
    
    if nome_farmaco_it:
        dati_pronti = False
        formulazioni_trovate = {}
        
        # LO SPINNER BLU: Scompare automaticamente appena finisce di caricare!
        with dict_streamlit.spinner("Ricerca e traduzione in corso... ⏳"):
            try:
                nome_farmaco_en = GoogleTranslator(source='it', target='en').translate(nome_farmaco_it).lower().strip()
                nome_farmaco_url = urllib.parse.quote(nome_farmaco_en)
                
                url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:%22{nome_farmaco_url}%22&limit=200"
                
                req = urllib.request.Request(
