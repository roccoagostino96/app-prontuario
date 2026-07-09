import streamlit as dict_streamlit
import urllib.request
import json

dict_streamlit.set_page_config(page_title="Prontuario Farmaci Smart", page_icon="💊", layout="centered")

# --- SISTEMA DI SICUREZZA PRIVATO ---
PIN_SEGRETO = "1234"  # <-- PUOI CAMBIARE QUESTO NUMERO COME PREFERISCI

dict_streamlit.title("💊 Prontuario Farmaceutico Personale")

# Richiesta del PIN prima di mostrare l'app
pin_inserito = dict_streamlit.text_input("Inserisci il PIN per accedere:", type="password")

if pin_inserito == PIN_SEGRETO:
    dict_streamlit.success("Accesso consentito!")
    
    # --- DA QUI INIZIA LA VERA APP ---
    dict_streamlit.write("Digita il nome di un principio attivo (in inglese, es: *ibuprofen*, *aspirin*) per vedere somministrazione e interazioni.")
    
    nome_farmaco = dict_streamlit.text_input("Inserisci il principio attivo:", placeholder="Es. ibuprofen")
    
    if nome_farmaco:
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{nome_farmaco.lower()}&limit=1"
        
        try:
            with urllib.request.urlopen(url_api) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    info_farmaco = dati["results"][0]
                    dict_streamlit.success(f"Risultati trovati per: **{nome_farmaco.upper()}**")
                    
                    # SEZIONE 1
                    dict_streamlit.subheader("📂 Modo di Somministrazione")
                    if "dosage_and_administration" in info_farmaco:
                        dict_streamlit.write(info_farmaco["dosage_and_administration"][0])
                    elif "indications_and_usage" in info_farmaco:
                        dict_streamlit.write(info_farmaco["indications_and_usage"][0])
                    else:
                        dict_streamlit.write("Dettagli non presenti nel riassunto principale.")
                    
                    # SEZIONE 2
                    dict_streamlit.subheader("⚠️ Interazioni e Avvertenze")
                    if "drug_interactions" in info_farmaco:
                        dict_streamlit.write("**Interazioni con altri farmaci:**\n" + info_farmaco["drug_interactions"][0])
                    if "food_interactions" in info_farmaco:
                        dict_streamlit.write("**Interazioni con il cibo:**\n" + info_farmaco["food_interactions"][0])
                    if "warnings" in info_farmaco:
                        dict_streamlit.write("**Avvertenze generali:**\n" + info_farmaco["warnings"][0])
                        
                else:
                    dict_streamlit.error("Nessun farmaco trovato. Usa termini in inglese (es: paracetamol).")
                    
        except Exception as errore:
            dict_streamlit.error("Farmaco non trovato nel database.")
            
elif pin_inserito != "":
    dict_streamlit.error("PIN errato. Riprova.")
