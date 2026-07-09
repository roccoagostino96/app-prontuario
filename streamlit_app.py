import streamlit as dict_streamlit
import urllib.request
import urllib.parse
import urllib.error
import json
from deep_translator import GoogleTranslator

# Configurazione
dict_streamlit.set_page_config(page_title="Prontuario Clinico Rapido", page_icon="⚕️", layout="centered")
PIN_SEGRETO = "1234"

dict_streamlit.markdown("""
<style>
.stTabs button p {
    font-size: 1.25rem !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

if "autenticato" not in dict_streamlit.session_state:
    dict_streamlit.session_state["autenticato"] = False

def traduci_in_italiano(testo):
    if not testo: return "Dato non presente."
    testo_sicuro = testo[:4000]
    try:
        return GoogleTranslator(source='en', target='it').translate(testo_sicuro)
    except:
        # Se il traduttore salta, restituisce l'originale in inglese o un avviso pulito (non va in errore rosso!)
        return f"[Testo in lingua originale per mancata connessione al server di traduzione]:\n\n{testo_sicuro}"

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

if not dict_streamlit.session_state["autenticato"]:
    dict_streamlit.write("Inserisci il PIN di sicurezza per sbloccare il prontuario.")
    pin_inserito = dict_streamlit.text_input("🔑 PIN:", type="password")
    
    if pin_inserito == PIN_SEGRETO:
        dict_streamlit.session_state["autenticato"] = True
        dict_streamlit.rerun() 
    elif pin_inserito != "":
        dict_streamlit.error("PIN errato. Riprova.")

if dict_streamlit.session_state["autenticato"]:
    
    col1, col2 = dict_streamlit.columns([8, 2])
    with col2:
        if dict_streamlit.button("🔒 Esci"):
            dict_streamlit.session_state["autenticato"] = False
            dict_streamlit.rerun()
            
    dict_streamlit.markdown("### 🔍 Cerca Principio Attivo o Nome Commerciale")
    nome_farmaco_it = dict_streamlit.text_input("es: furosemide, augmentin, tachipirina, fentanil", label_visibility="collapsed")
    
    if nome_farmaco_it:
        dati_pronti = False
        formulazioni_trovate = {}
        
        with dict_streamlit.spinner("Ricerca e traduzione in corso... ⏳"):
            try:
                testo_da_tradurre = nome_farmaco_it.lower().strip()
                
                # --- BLOCCO ANTI-PANICO DELLA TRADUZIONE ---
                try:
                    if "paracetamolo" in testo_da_tradurre or "paracetamol" in testo_da_tradurre:
                        nome_farmaco_en = "acetaminophen"
                    else:
                        nome_farmaco_en = GoogleTranslator(source='it', target='en').translate(testo_da_tradurre).lower().strip()
                except:
                    # Se il traduttore cade, bypassalo e usa la parola digitata dall'utente
                    nome_farmaco_en = testo_da_tradurre
                # ---------------------------------------------
                
                nome_farmaco_url = urllib.parse.quote(nome_farmaco_en)
                
                url_api = f"https://api.fda.gov/drug/label.json?search=(openfda.generic_name:%22{nome_farmaco_url}%22+OR+openfda.brand_name:%22{nome_farmaco_url}%22)&limit=100"
                
                req = urllib.request.Request(url_api, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as risposta:
                    dati = json.loads(risposta.read().decode())
                    
                    if "results" in dati:
                        for risultato in dati["results"]:
                            if "dosage_and_administration" not in risultato and "indications_and_usage" not in risultato:
                                continue
                                
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
                            nome_chiave = f"Formulazione Standard - {nome_farmaco_it.upper()}"
                            for risultato in dati["results"]:
                                if "dosage_and_administration" in risultato:
                                    formulazioni_trovate[nome_chiave] = risultato
                                    break
                            if not formulazioni_trovate:
                                formulazioni_trovate[nome_chiave] = dati["results"][0]

                        dati_pronti = True

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    dict_streamlit.error("❌ Farmaco o molecola non trovata nel database. Assicurati che sia scritta correttamente.")
                else:
                    dict_streamlit.error(f"❌ Errore del server medico ({e.code}). Riprova tra qualche istante.")
            except Exception as e:
                # Se c'è un errore davvero insolito, non blocca l'app ma avvisa pulito
                dict_streamlit.error(f"❌ Impossibile elaborare la richiesta in questo momento. Errore di rete.")

        if dati_pronti:
            dict_streamlit.success(f"✅ Risultati trovati per: **{nome_farmaco_it.upper()}**")
            
            scelta = dict_streamlit.selectbox("👇 Seleziona la formulazione esatta:", list(formulazioni_trovate.keys()))
            
            if scelta:
                info_scelta = formulazioni_trovate[scelta]
                
                if "Formulazione Standard" in scelta:
                    dict_streamlit.markdown(f"### Dati per: {nome_farmaco_it.upper()}")
                else:
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
