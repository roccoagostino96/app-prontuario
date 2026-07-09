import streamlit as dict_streamlit
import urllib.request
import json
from deep_translator import GoogleTranslator

# Configurazione iniziale
dict_streamlit.set_page_config(page_title="Prontuario Farmaci Smart", page_icon="💊", layout="centered")

PIN_SEGRETO = "1234"  # Il tuo PIN

# Funzione per tradurre testi
def traduci_in_italiano(testo):
    if not testo: return ""
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

# --- NUOVA FUNZIONE: Trasforma i muri di testo in elenchi puntati ---
def formatta_a_punti(testo):
    if not testo: return ""
    # Divide il blocco di testo ogni volta che trova un punto e spazio
    frasi = testo.split(". ")
    testo_bello = ""
    for frase in frasi:
        frase = frase.strip()
        if len(frase) > 5: # Salta spazi vuoti
            if not frase.endswith("."):
                frase += "."
            testo_bello += f"* {frase}\n\n"
    return testo_bello

# Grafica dell'app
dict_streamlit.title("💊 Il Mio Prontuario Smart")

pin_inserito = dict_streamlit.text_input("Inserisci il PIN per accedere:", type="password")

if pin_inserito == PIN_SEGRETO:
    
    dict_streamlit.write("Digita il principio attivo in italiano (es: *ketoprofene*, *ibuprofene*). L'app cercherà i dati, li tradurrà e li formatterà per te.")
    
    nome_farmaco_it = dict_streamlit.text_input("🔍 Principio attivo:", placeholder="Es. ketoprofene")
    
    if nome_farmaco_it:
        dict_streamlit.info("Sto analizzando e formattando i dati... attendi ⏳")
        
        nome_farmaco_en = traduci_in_inglese(nome_farmaco_it).lower()
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{nome_farmaco_en}&limit=1"
        
        try:
            with urllib.request.urlopen(url_api) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    info = dati["results"][0]
                    dict_streamlit.success(f"✅ Risultati per: **{nome_farmaco_it.upper()}**")
                    
                    # --- NUOVA SEZIONE 1: FORMA E VIA DI SOMMINISTRAZIONE ---
                    dict_streamlit.subheader("💊 Specifiche del Farmaco")
                    dati_extra = info.get("openfda", {})
                    
                    forma = dati_extra.get("dosage_form", ["Dato non disponibile"])[0]
                    via = dati_extra.get("route", ["Dato non disponibile"])[0]
                    
                    # Creiamo due colonne affiancate
                    col1, col2 = dict_streamlit.columns(2)
                    with col1:
                        dict_streamlit.markdown("**Forma Farmaceutica:**")
                        dict_streamlit.info(traduci_in_italiano(forma).capitalize())
                    with col2:
                        dict_streamlit.markdown("**Via di somministrazione:**")
                        dict_streamlit.info(traduci_in_italiano(via).capitalize())
                    
                    dict_streamlit.markdown("---") # Linea di separazione
                    
                    # 2. MODO D'USO E SOMMINISTRAZIONE (ORA A PUNTI)
                    dict_streamlit.subheader("📝 Modo d'uso e Somministrazione")
                    testo_uso = ""
                    if "dosage_and_administration" in info:
                        testo_uso = info["dosage_and_administration"][0]
                    elif "indications_and_usage" in info:
                        testo_uso = info["indications_and_usage"][0]
                    
                    if testo_uso:
                        testo_tradotto = traduci_in_italiano(testo_uso)
                        # Usiamo la nuova funzione per fare l'elenco puntato
                        dict_streamlit.markdown(formatta_a_punti(testo_tradotto))
                    else:
                        dict_streamlit.write("Dati sulla somministrazione non presenti.")
                    
                    # 3. CONTROINDICAZIONI
                    dict_streamlit.subheader("🚫 COSA NON SOMMINISTRARE (Controindicazioni)")
                    if "contraindications" in info:
                        testo_contro = traduci_in_italiano(info["contraindications"][0])
                        dict_streamlit.error(formatta_a_punti(testo_contro))
                    else:
                        dict_streamlit.write("Nessuna controindicazione assoluta segnalata in evidenza.")

                    # 4. INTERAZIONI CON FARMACI E CIBO
                    dict_streamlit.subheader("🔄 Interazioni con altri farmaci o cibi")
                    if "drug_interactions" in info:
                        dict_streamlit.write("**Interazioni Farmacologiche:**")
                        testo_inter = traduci_in_italiano(info["drug_interactions"][0])
                        dict_streamlit.warning(formatta_a_punti(testo_inter))
                    else:
                        dict_streamlit.write("**Interazioni Farmacologiche:** Non specificate in evidenza.")
                        
                    if "food_interactions" in info:
                        dict_streamlit.write("**Interazioni con il Cibo:**")
                        testo_cibo = traduci_in_italiano(info["food_interactions"][0])
                        dict_streamlit.warning(formatta_a_punti(testo_cibo))

                    # 5. AVVERTENZE GENERALI
                    dict_streamlit.subheader("⚠️ Avvertenze")
                    if "warnings" in info:
                        testo_avv = traduci_in_italiano(info["warnings"][0])
                        dict_streamlit.markdown(formatta_a_punti(testo_avv))
                    else:
                        dict_streamlit.write("Nessuna avvertenza generale di rilievo segnalata.")
                        
                else:
                    dict_streamlit.error("Nessun farmaco trovato. Prova a controllare l'ortografia.")
                    
        except Exception as errore:
            dict_streamlit.error("Farmaco non trovato. Assicurati di usare il nome del principio attivo.")
            
elif pin_inserito != "":
    dict_streamlit.error("PIN errato.")    
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
