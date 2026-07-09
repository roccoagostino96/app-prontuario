import streamlit as dict_streamlit
import urllib.request
import urllib.parse
import json
from deep_translator import GoogleTranslator

# Configurazione
dict_streamlit.set_page_config(page_title="Prontuario Clinico Rapido", page_icon="⚕️", layout="centered")
PIN_SEGRETO = "1234"

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

# --- SCHERMATA APP (Senza PIN visibile) ---
if dict_streamlit.session_state["autenticato"]:
    
    col1, col2 = dict_streamlit.columns([8, 2])
    with col2:
        if dict_streamlit.button("🔒 Esci"):
            dict_streamlit.session_state["autenticato"] = False
            dict_streamlit.rerun()
            
    nome_farmaco_it = dict_streamlit.text_input("🔍 Principio Attivo (es: furosemide, amoxicillina):")
    
    if nome_farmaco_it:
        dict_streamlit.info("Ricerca di tutte le formulazioni in corso... ⏳")
        nome_farmaco_en = GoogleTranslator(source='it', target='en').translate(nome_farmaco_it).lower().strip()
        
        nome_farmaco_url = urllib.parse.quote(nome_farmaco_en)
        
        # IL NUOVO MOTORE DI RICERCA: Forza la FDA a dare solo dati con forma farmaceutica (dosage_form) e cerca su 100 risultati.
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{nome_farmaco_url}+AND+_exists_:openfda.dosage_form&limit=100"
        
        try:
            req = urllib.request.Request(url_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    formulazioni_trovate = {}
                    for risultato in dati["results"]:
                        dati_fda = risultato.get("openfda", {})
                        forme = dati_fda.get("dosage_form", [])
                        vie = dati_fda.get("route", [])
                        
                        if forme and vie:
                            forma = forme[0].upper()
                            via = vie[0].upper()
                            
                            if "BULK" not in forma and "UNSPECIFIED" not in forma: 
                                chiave = f"{via} - {forma}"
                                if chiave not in formulazioni_trovate:
                                    formulazioni_trovate[chiave] = risultato
                                
                    if not formulazioni_trovate:
                        dict_streamlit.warning("Documenti trovati, ma senza specificazioni di forma. Mostro i dati generali.")
                        formulazioni_trovate["Generico (Dati non specifici)"] = dati["results"][0]

                    dict_streamlit.success(f"✅ Molecola trovata: **{nome_farmaco_it.upper()}**")
                    
                    scelta = dict_streamlit.selectbox("👇 Seleziona la formulazione esatta che hai in mano:", list(formulazioni_trovate.keys()))
                    
                    if scelta:
                        info_scelta = formulazioni_trovate[scelta]
                        dict_streamlit.markdown(f"### Dati per: {traduci_in_italiano(scelta)}")
                        
                        scelta_en = scelta.lower()
                        if "oral" in scelta_en and ("tablet" in scelta_en or "capsule" in scelta_en or "pill" in scelta_en):
                            if "extended" in scelta_en or "delayed" in scelta_en or "enteric" in scelta_en or "release" in scelta_en:
                                dict_streamlit.error("🚨 **ASSOLUTAMENTE NON TRITARE O DIVIDERE.** Formulazione a rilascio modificato/gastroresistente. Alterare la pillola causa tossicità o inefficacia.")
                            else:
                                dict_streamlit.success("🟢 **TRITABILE/DIVISIBILE.** Formulazione a rilascio immediato standard. Può essere frantumata salvo diversa indicazione medica (es. sondino).")
                        elif "suspension" in scelta_en or "syrup" in scelta_en or "solution" in scelta_en or "powder" in scelta_en:
                            dict_streamlit.success("💧 **FORMA LIQUIDA/SOSPENSIONE ORALE.** Agitare bene prima della somministrazione (se sospensione) o ricostituire correttamente.")
                        elif "injection" in scelta_en or "intravenous" in scelta_en:
                            dict_streamlit.info("💉 **USO PARENTERALE.** Verificare incompatibilità con i liquidi di infusione (es. SF o SG).")
                            
                        tab1, tab2, tab3, tab4 = dict_streamlit.tabs(["⏱️ Posologia", "⚠️ Reazioni Avverse", "🔄 Interazioni", "❌ Controind."])
                        
                        with tab1:
                            if "dosage_and_administration" in info_scelta:
                                testo_posologia = riassumi_testo(info_scelta["dosage_and_administration"][0], num_frasi=6)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_posologia)))
                            else: dict_streamlit.write("Dato non estratto in sintesi.")
                                
                        with tab2:
                            dict_streamlit.caption("Sintomi più comuni (prime indicazioni del documento ufficiale).")
                            if "adverse_reactions" in info_scelta:
                                testo_avverse = riassumi_testo(info_scelta["adverse_reactions"][0], num_frasi=4)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_avverse)))
                            else: dict_streamlit.write("Dato non estratto in sintesi.")
                                
                        with tab3:
                            if "drug_interactions" in info_scelta:
                                testo_interazioni = riassumi_testo(info_scelta["drug_interactions"][0], num_frasi=4)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_interazioni)))
                            else: dict_streamlit.write("Nessuna interazione principale evidenziata.")
                            
                        with tab4:
                            if "contraindications" in info_scelta:
                                testo_contro = riassumi_testo(info_scelta["contraindications"][0], num_frasi=3)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_contro)))
                            else: dict_streamlit.write("Nessuna controindicazione assoluta segnalata in evidenza.")

        except Exception as e:
            dict_streamlit.error("Molecola non trovata nel database ufficiale o errore di connessione. Controlla l'ortografia.")
