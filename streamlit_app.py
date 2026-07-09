import streamlit as dict_streamlit
import urllib.request
import json
from deep_translator import GoogleTranslator

# Configurazione iniziale
dict_streamlit.set_page_config(page_title="Prontuario Farmaci Smart", page_icon="💊", layout="centered")

PIN_SEGRETO = "1234"  # Il tuo PIN

# Funzione per tradurre testi lunghi in italiano (con limite di sicurezza per non bloccare l'app)
def traduci_in_italiano(testo):
    if not testo: return ""
    # Tagliamo a 4500 caratteri nel caso il testo sia enorme, per non far bloccare il traduttore
    testo_sicuro = testo[:4500] 
    try:
        return GoogleTranslator(source='en', target='it').translate(testo_sicuro)
    except:
        return "Errore nella traduzione del testo, riprova."

def traduci_in_inglese(testo):
    try:
        return GoogleTranslator(source='it', target='en').translate(testo)
    except:
        return testo

# Grafica dell'app
dict_streamlit.title("💊 Il Mio Prontuario Smart")

pin_inserito = dict_streamlit.text_input("Inserisci il PIN per accedere:", type="password")

if pin_inserito == PIN_SEGRETO:
    
    dict_streamlit.write("Digita il principio attivo in italiano (es: *ibuprofene*, *amoxicillina*). L'app cercherà i dati e li tradurrà in italiano.")
    
    nome_farmaco_it = dict_streamlit.text_input("🔍 Principio attivo:", placeholder="Es. ibuprofene")
    
    if nome_farmaco_it:
        dict_streamlit.info("Sto cercando i dati e traducendo in italiano... attendi qualche secondo ⏳")
        
        nome_farmaco_en = traduci_in_inglese(nome_farmaco_it).lower()
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{nome_farmaco_en}&limit=1"
        
        try:
            with urllib.request.urlopen(url_api) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    info = dati["results"][0]
                    dict_streamlit.success(f"✅ Risultati per: **{nome_farmaco_it.upper()}**")
                    
                    # 1. MODO D'USO E SOMMINISTRAZIONE
                    dict_streamlit.subheader("📝 Modo d'uso e Somministrazione")
                    if "dosage_and_administration" in info:
                        dict_streamlit.write(traduci_in_italiano(info["dosage_and_administration"][0]))
                    elif "indications_and_usage" in info:
                        dict_streamlit.write(traduci_in_italiano(info["indications_and_usage"][0]))
                    else:
                        dict_streamlit.write("Dati sulla somministrazione non presenti.")
                    
                    # 2. COSA NON SOMMINISTRARE INSIEME (CONTROINDICAZIONI) - NUOVA SEZIONE
                    dict_streamlit.subheader("🚫 COSA NON SOMMINISTRARE (Controindicazioni)")
                    if "contraindications" in info:
                        dict_streamlit.error(traduci_in_italiano(info["contraindications"][0]))
                    else:
                        dict_streamlit.write("Nessuna controindicazione assoluta segnalata in evidenza.")

                    # 3. INTERAZIONI CON FARMACI E CIBO
                    dict_streamlit.subheader("🔄 Interazioni con altri farmaci o cibi")
                    if "drug_interactions" in info:
                        dict_streamlit.write("**Interazioni Farmacologiche:**")
                        dict_streamlit.warning(traduci_in_italiano(info["drug_interactions"][0]))
                    else:
                        dict_streamlit.write("**Interazioni Farmacologiche:** Non specificate in evidenza.")
                        
                    if "food_interactions" in info:
                        dict_streamlit.write("**Interazioni con il Cibo:**")
                        dict_streamlit.warning(traduci_in_italiano(info["food_interactions"][0]))

                    # 4. AVVERTENZE GENERALI
                    dict_streamlit.subheader("⚠️ Avvertenze")
                    if "warnings" in info:
                        dict_streamlit.write(traduci_in_italiano(info["warnings"][0]))
                    else:
                        dict_streamlit.write("Nessuna avvertenza generale di rilievo segnalata.")
                        
                else:
                    dict_streamlit.error("Nessun farmaco trovato. Prova a controllare l'ortografia.")
                    
        except Exception as errore:
            dict_streamlit.error("Farmaco non trovato. Assicurati di usare il nome del principio attivo.")
            
elif pin_inserito != "":
    dict_streamlit.error("PIN errato.")
