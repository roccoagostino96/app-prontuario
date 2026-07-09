import streamlit as dict_streamlit
import urllib.request
import json
from deep_translator import GoogleTranslator

# Configurazione
dict_streamlit.set_page_config(page_title="Prontuario Clinico Rapido", page_icon="⚕️", layout="centered")
PIN_SEGRETO = "1234"

def traduci_in_italiano(testo):
    if not testo: return "Dato non presente."
    testo_sicuro = testo[:4000] # Limite per velocizzare
    try:
        return GoogleTranslator(source='en', target='it').translate(testo_sicuro)
    except:
        return "Errore di traduzione temporaneo."

def riassumi_testo(testo, num_frasi=4):
    """Bisturi automatico: taglia il testo per mostrare solo le informazioni principali"""
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
pin_inserito = dict_streamlit.text_input("Inserisci il PIN per accedere:", type="password")

if pin_inserito == PIN_SEGRETO:
    nome_farmaco_it = dict_streamlit.text_input("🔍 Principio Attivo (es: furosemide, amoxicillina):")
    
    if nome_farmaco_it:
        # Traduciamo la richiesta in inglese per il database USA
        nome_farmaco_en = GoogleTranslator(source='it', target='en').translate(nome_farmaco_it).lower()
        # Chiediamo alla FDA di darci fino a 15 formulazioni diverse di questo farmaco
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{nome_farmaco_en}\"&limit=15"
        
        try:
            with urllib.request.urlopen(url_api) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    # Raccogliamo tutte le vie di somministrazione disponibili
                    formulazioni_trovate = {}
                    for risultato in dati["results"]:
                        dati_fda = risultato.get("openfda", {})
                        forma = dati_fda.get("dosage_form", [""])[0].upper()
                        via = dati_fda.get("route", [""])[0].upper()
                        
                        if forma and via:
                            chiave = f"Via {via} - {forma}"
                            if chiave not in formulazioni_trovate:
                                formulazioni_trovate[chiave] = risultato
                                
                    if not formulazioni_trovate:
                        dict_streamlit.warning("Dati trovati, ma formulazioni specifiche non elencate.")
                        formulazioni_trovate["Generico (Dati non specifici)"] = dati["results"][0]

                    dict_streamlit.success(f"✅ Molecola trovata: **{nome_farmaco_it.upper()}**")
                    
                    # 1. MENU A TENDINA MAGICO
                    scelta = dict_streamlit.selectbox("👇 Seleziona la formulazione esatta che hai in mano:", list(formulazioni_trovate.keys()))
                    
                    if scelta:
                        info_scelta = formulazioni_trovate[scelta]
                        dict_streamlit.markdown(f"### Dati clinici per: {traduci_in_italiano(scelta)}")
                        
                        # 2. ALLARME FRANTUMAZIONE INTELLIGENTE ED ESATTO
                        scelta_en = scelta.lower()
                        if "oral" in scelta_en and ("tablet" in scelta_en or "capsule" in scelta_en):
                            if "extended" in scelta_en or "delayed" in scelta_en or "enteric" in scelta_en or "release" in scelta_en:
                                dict_streamlit.error("🚨 **ASSOLUTAMENTE NON TRITARE O DIVIDERE.** Formulazione a rilascio modificato/gastroresistente. Alterare la pillola causa tossicità o inefficacia.")
                            else:
                                dict_streamlit.success("🟢 **TRITABILE/DIVISIBILE.** È una formulazione orale a rilascio immediato standard. Può essere frantumata (es. per pazienti disfagici o SNG) salvo diversa indicazione medica.")
                        elif "injection" in scelta_en or "intravenous" in scelta_en:
                            dict_streamlit.info("💉 **USO PARENTERALE.** Verificare incompatibilità con i liquidi di infusione (es. SF o SG).")
                            
                        # 3. SCHEDE CON TESTI TAGLIATI E RIASSUNTI
                        tab1, tab2, tab3, tab4 = dict_streamlit.tabs(["⏱️ Posologia", "⚠️ Reazioni Avverse", "🔄 Interazioni", "❌ Controind."])
                        
                        with tab1:
                            if "dosage_and_administration" in info_scelta:
                                # Prendiamo le prime 8 frasi della posologia (le più importanti)
                                testo_posologia = riassumi_testo(info_scelta["dosage_and_administration"][0], num_frasi=8)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_posologia)))
                            else: dict_streamlit.write("Dato non estratto in sintesi.")
                                
                        with tab2:
                            dict_streamlit.caption("Mostro solo i sintomi più comuni/rilevanti (prime indicazioni del documento ufficiale).")
                            if "adverse_reactions" in info_scelta:
                                # Tagliamo le reazioni avverse alle prime 4 frasi!
                                testo_avverse = riassumi_testo(info_scelta["adverse_reactions"][0], num_frasi=4)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_avverse)))
                            else: dict_streamlit.write("Dato non estratto in sintesi.")
                                
                        with tab3:
                            if "drug_interactions" in info_scelta:
                                testo_interazioni = riassumi_testo(info_scelta["drug_interactions"][0], num_frasi=5)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_interazioni)))
                            else: dict_streamlit.write("Nessuna interazione principale evidenziata.")
                            
                        with tab4:
                            if "contraindications" in info_scelta:
                                testo_contro = riassumi_testo(info_scelta["contraindications"][0], num_frasi=3)
                                dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(testo_contro)))
                            else: dict_streamlit.write("Nessuna controindicazione assoluta segnalata in evidenza.")

        except Exception as e:
            dict_streamlit.error("Molecola non trovata. Controlla l'ortografia e assicurati di usare il principio attivo e non il nome commerciale.")

elif pin_inserito != "":
    dict_streamlit.error("PIN non valido. Accesso negato.")
