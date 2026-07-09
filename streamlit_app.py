import streamlit as dict_streamlit
import urllib.request
import json
from deep_translator import GoogleTranslator

# Configurazione iniziale dell'interfaccia clinica
dict_streamlit.set_page_config(page_title="Prontuario Clinico Rapido", page_icon="⚕️", layout="centered")

PIN_SEGRETO = "1234"  # Il tuo PIN di accesso

# Funzioni di traduzione e formattazione
def traduci_in_italiano(testo):
    if not testo: return "Dato non presente nel registro ufficiale."
    testo_sicuro = testo[:4500] 
    try:
        return GoogleTranslator(source='en', target='it').translate(testo_sicuro)
    except:
        return "Errore di traduzione. Dato originale disponibile in lingua inglese."

def traduci_in_inglese(testo):
    try:
        return GoogleTranslator(source='it', target='en').translate(testo)
    except:
        return testo

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

# Interfaccia Grafica
dict_streamlit.title("⚕️ Prontuario Clinico Rapido")
dict_streamlit.caption("Strumento di consultazione immediata per professionisti sanitari - Dati istituzionali OpenFDA")

pin_inserito = dict_streamlit.text_input("Inserisci il PIN per accedere:", type="password")

if pin_inserito == PIN_SEGRETO:
    nome_farmaco_it = dict_streamlit.text_input("🔍 Inserisci il Principio Attivo (es: ketoprofene, furosemide, amoxicillina):", placeholder="Es. furosemide")
    
    if nome_farmaco_it:
        dict_streamlit.info("Estrazione e traduzione dei dati ministeriali in corso... ⏳")
        
        nome_farmaco_en = traduci_in_inglese(nome_farmaco_it).lower()
        url_api = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{nome_farmaco_en}&limit=1"
        
        try:
            with urllib.request.urlopen(url_api) as risposta:
                dati = json.loads(risposta.read().decode())
                
                if "results" in dati:
                    info = dati["results"][0]
                    dati_extra = info.get("openfda", {})
                    
                    forma_farmaceutica = dati_extra.get("dosage_form", ["Non specificata"])[0]
                    via_somministrazione = dati_extra.get("route", ["Non specificata"])[0]
                    
                    dict_streamlit.success(f"✅ Principio Attivo Riscontrato: **{nome_farmaco_it.upper()}**")
                    
                    # --- ALERT SICUREZZA FRANTUMAZIONE ---
                    forma_attesa = forma_farmaceutica.lower()
                    if "extended release" in forma_attesa or "sustained release" in forma_attesa or "delayed release" in forma_attesa or "enteric" in forma_attesa:
                        dict_streamlit.error("🚨 **ALERT FORMULAZIONE RILASCIO MODIFICATO / GASTRORESISTENTE:** NON frantumare, non tritare e non masticare la forma solida per non alterare il profilo farmacocinetico.")
                    else:
                        dict_streamlit.warning("⚠️ **VERIFICA INTEGRITÀ:** Prima di frantumare o dividere forme solide orali, verificare sempre l'assenza di rivestimenti gastroresistenti o film protettivi non divisibili.")

                    # --- CREAZIONE DELLE SCHEDE CLINICHE (TABS) ---
                    tab1, tab2, tab3, tab4, tab5 = dict_streamlit.tabs([
                        "📋 Indicazioni", 
                        "⏱️ Posologia", 
                        "🔄 Interazioni", 
                        "❌ Controindicazioni", 
                        "⚠️ Reazioni Avverse"
                    ])
                    
                    with tab1:
                        dict_streamlit.markdown("### 📋 Indicazioni Terapeutiche")
                        dict_streamlit.markdown(f"**Forma Farmaceutica d'origine:** {traduci_in_italiano(forma_farmaceutica)}")
                        dict_streamlit.markdown(f"**Via di Somministrazione prevalente:** {traduci_in_italiano(via_somministrazione)}")
                        dict_streamlit.markdown("---")
                        if "indications_and_usage" in info:
                            dict_streamlit.markdown(formatta_a_punts(traduci_in_italiano(info["indications_and_usage"][0])))
                        else:
                            dict_streamlit.write("Dato non disponibile nel riassunto principale.")
                            
                    with tab2:
                        dict_streamlit.markdown("### ⏱️ Posologia e Modo di Somministrazione")
                        dict_streamlit.caption("Include dosaggi raccomandati, schemi orari, somministrazioni estemporanee e indicazioni sulla somministrazione.")
                        if "dosage_and_administration" in info:
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["dosage_and_administration"][0])))
                        else:
                            dict_streamlit.write("Dato non estratto automaticamente. Verificare le avvertenze generali.")
                            
                    with tab3:
                        dict_streamlit.markdown("### 🔄 Interazioni Medicamentose e Alimentari")
                        if "drug_interactions" in info:
                            dict_streamlit.markdown("**Interazioni con altri Farmaci:**")
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["drug_interactions"][0])))
                        if "food_interactions" in info:
                            dict_streamlit.markdown("**Interazioni con Alimenti (es. Succo di Pompelmo, Alcolici, Latticini):**")
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["food_interactions"][0])))
                        if "drug_interactions" not in info and "food_interactions" not in info:
                            dict_streamlit.write("Nessuna interazione clinica di rilievo registrata in questa sezione.")
                            
                    with tab4:
                        dict_streamlit.markdown("### ❌ Controindicazioni Assolute")
                        dict_streamlit.caption("Condizioni cliniche o concomitanti terapeutiche in cui il farmaco NON deve essere somministrato.")
                        if "contraindications" in info:
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["contraindications"][0])))
                        else:
                            dict_streamlit.write("Nessuna controindicazione assoluta evidenziata nei dati di sintesi.")
                            
                    with tab5:
                        dict_streamlit.markdown("### ⚠️ Reazioni Avverse ed Effetti Indesiderati")
                        dict_streamlit.caption("Segni, sintomi ed effetti collaterali più comuni o clinicamente rilevanti.")
                        if "adverse_reactions" in info:
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["adverse_reactions"][0])))
                        elif "warnings" in info:
                            dict_streamlit.markdown(formatta_a_punti(traduci_in_italiano(info["warnings"][0])))
                        else:
                            dict_streamlit.write("Dati sul profilo di tollerabilità non presenti in questa scheda.")
                            
                else:
                    dict_streamlit.error("Nessun principio attivo riscontrato. Verificare la corretta grafia del termine in italiano.")
                    
        except Exception as errore:
            dict_streamlit.error("Nessun riscontro nel database istituzionale. Verificare che si tratti di un principio attivo e non di un nome commerciale italiano.")

elif pin_inserito != "":
    dict_streamlit.error("PIN non valido. Accesso negato.")
