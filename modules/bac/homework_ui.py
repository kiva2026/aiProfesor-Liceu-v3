"""
modules/bac/homework_ui.py — UI complet pentru corectura temei.
"""
import streamlit as st

from config import MATERII
from modules.ai.gemini_client import run_chat_with_rotation
from modules.materii.base import get_system_prompt


def extract_text_from_photo(photo_bytes: bytes, materie_label: str) -> str:
    """Extrage textul dintr-o fotografie a temei folosind Gemini Vision."""
    import tempfile, os, time
    from google import genai
    from google.genai import types as genai_types

    keys = st.session_state.get("_api_keys_list", [])
    if not keys:
        return "[Eroare: nicio cheie API disponibilă]"

    try:
        gemini_client = genai.Client(api_key=keys[st.session_state.key_index])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(photo_bytes)
            tmp_path = tmp.name

        gfile = gemini_client.files.upload(
            file=tmp_path,
            config=genai_types.UploadFileConfig(mime_type="image/jpeg")
        )
        poll = 0
        while str(gfile.state) in ("FileState.PROCESSING", "PROCESSING") and poll < 30:
            time.sleep(1)
            gfile = gemini_client.files.get(gfile.name)
            poll += 1
        os.unlink(tmp_path)

        prompt = (
            f"Transcrie EXACT și COMPLET textul din această fotografie. "
            f"E o temă de {materie_label} scrisă de mână. "
            f"Transcrie tot ce este scris, inclusiv formulele matematice, fără să explici sau rezolvi. "
            f"Păstrează structura: exercițiu 1, exercițiu 2 etc."
        )
        parts = [
            genai_types.Part(file_data=genai_types.FileData(
                file_uri=gfile.uri, mime_type=gfile.mime_type
            )),
            genai_types.Part(text=prompt),
        ]
        from config import GEMINI_MODEL, SAFETY_SETTINGS
        from google.genai import types as gt
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[gt.Content(role="user", parts=parts)],
            config=gt.GenerateContentConfig(
                safety_settings=[
                    gt.SafetySetting(category=s["category"], threshold=s["threshold"])
                    for s in SAFETY_SETTINGS
                ]
            )
        )
        try:
            gemini_client.files.delete(gfile.name)
        except Exception:
            pass

        return response.text or "[Nu s-a putut extrage textul]"

    except Exception as e:
        return f"[Eroare la extragerea textului: {e}]"


def get_homework_correction_prompt(materie_label: str, text_tema: str, from_photo: bool = False) -> str:
    source_note = (
        "NOTĂ: Tema a fost extrasă dintr-o fotografie. "
        "Unele cuvinte pot fi transcrise imperfect — judecă după intenția elevului.\n\n"
        if from_photo else ""
    )

    if "Română" in materie_label:
        corectare_limba = (
            "## 🖊️ Corectare limbă și stil\n"
            "Acordă atenție specială:\n"
            "- **Ortografie**: diacritice (ă,â,î,ș,ț), cratimă, apostrof\n"
            "- **Punctuație**: virgulă, punct, linie de dialog, ghilimele «»\n"
            "- **Acord gramatical**: subiect-predicat, adjectiv-substantiv\n"
            "- **Exprimare**: cacofonii, pleonasme, tautologii\n"
            "- **Coerență**: logica textului, legătura dintre idei\n"
            "Subliniază greșelile găsite și explică regula corectă.\n\n"
        )
    else:
        corectare_limba = (
            f"## 🖊️ Limbaj și exprimare ({materie_label})\n"
            "- Terminologie specifică folosită corect\n"
            "- Notații, simboluri și unități de măsură corecte\n"
            "- Raționament exprimat clar și logic\n\n"
        )

    return (
        f"Ești profesor de {materie_label} și corectezi tema unui elev de liceu.\n\n"
        f"{source_note}"
        f"TEMA ELEVULUI:\n{text_tema}\n\n"
        f"Corectează complet și constructiv:\n\n"
        f"## ✅ Ce a făcut bine\n[aspecte corecte — fii specific]\n\n"
        f"## ❌ Greșeli de conținut\n[fiecare greșeală explicată cu varianta corectă]\n\n"
        f"{corectare_limba}"
        f"## 📊 Notă orientativă\n**Nota: X/10** — [justificare scurtă]\n\n"
        f"## 💡 Sfaturi pentru data viitoare\n[2-3 recomandări concrete]\n\n"
        f"Ton: cald, constructiv, ca un profesor care vrea să ajute."
    )


def run_homework_ui():
    st.subheader("📚 Corectare Temă")

    if not st.session_state.get("hw_done"):
        col1, col2 = st.columns([2, 1])
        with col1:
            hw_materie = st.selectbox(
                "📚 Materia temei:",
                options=[m for m in MATERII.keys() if m != "🤖 Automat"],
                key="hw_materie_sel"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Profesorul se adaptează materiei.")

        st.divider()
        tab_foto, tab_text = st.tabs(["📷 Fotografiază tema", "⌨️ Scrie / lipește textul"])

        with tab_foto:
            st.info(
                "📱 **Pe telefon:** fotografiază caietul sau foaia de temă.\n\n"
                "💻 **Pe calculator:** încarcă o poză din galerie.\n\n"
                "Profesorul va citi și corecta automat."
            )
            hw_photo = st.file_uploader(
                "Încarcă fotografia temei:",
                type=["jpg", "jpeg", "png", "webp", "heic"],
                key="hw_photo_upload",
                help="Asigură-te că poza e clară și bine luminată."
            )

            if hw_photo and not st.session_state.get("hw_ocr_done"):
                st.image(hw_photo, caption="Fotografia încărcată", use_container_width=True)
                with st.spinner("🔍 Profesorul citește tema..."):
                    text_extras = extract_text_from_photo(hw_photo.read(), hw_materie)
                st.session_state.hw_text       = text_extras
                st.session_state.hw_ocr_done   = True
                st.session_state.hw_from_photo = True
                st.session_state.hw_materie    = hw_materie
                with st.spinner("📝 Se corectează tema..."):
                    prompt = get_homework_correction_prompt(hw_materie, text_extras, from_photo=True)
                    corectare = "".join(run_chat_with_rotation(
                        [], [prompt],
                        system_prompt=get_system_prompt(
                            materie=MATERII.get(hw_materie),
                            pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                            mod_avansat=st.session_state.get("mod_avansat", False),
                            mod_strategie=st.session_state.get("mod_strategie", False),
                            mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                        )
                    ))
                st.session_state.hw_corectare = corectare
                st.session_state.hw_done      = True
                st.rerun()
            elif hw_photo and st.session_state.get("hw_ocr_done"):
                with st.expander("📄 Text extras din poză", expanded=False):
                    st.text(st.session_state.get("hw_text", ""))

        with tab_text:
            hw_text = st.text_area(
                "Lipește sau scrie textul temei:",
                value=st.session_state.get("hw_text", ""),
                height=300,
                placeholder="Scrie sau lipește tema aici...",
                key="hw_text_input"
            )
            st.session_state.hw_text = hw_text
            if st.button("📝 Corectează tema", type="primary",
                         use_container_width=True, disabled=not hw_text.strip()):
                st.session_state.hw_materie    = hw_materie
                st.session_state.hw_from_photo = False
                with st.spinner("📝 Se corectează tema..."):
                    prompt = get_homework_correction_prompt(hw_materie, hw_text, from_photo=False)
                    corectare = "".join(run_chat_with_rotation(
                        [], [prompt],
                        system_prompt=get_system_prompt(
                            materie=MATERII.get(hw_materie),
                            pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                            mod_avansat=st.session_state.get("mod_avansat", False),
                            mod_strategie=st.session_state.get("mod_strategie", False),
                            mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                        )
                    ))
                st.session_state.hw_corectare = corectare
                st.session_state.hw_done      = True
                st.rerun()

    else:
        mat = st.session_state.get("hw_materie", "")
        src = "📷 din fotografie" if st.session_state.get("hw_from_photo") else "✏️ scrisă manual"
        st.caption(f"{mat} · temă {src}")
        if st.session_state.get("hw_from_photo") and st.session_state.get("hw_text"):
            with st.expander("📄 Text extras din poză", expanded=False):
                st.text(st.session_state.hw_text)
        st.markdown(st.session_state.hw_corectare)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 Corectează altă temă", type="primary", use_container_width=True):
                _hw_mat = st.session_state.get("hw_materie_sel")
                for k in [k for k in list(st.session_state.keys()) if k.startswith("hw_")]:
                    st.session_state.pop(k, None)
                if _hw_mat:
                    st.session_state["hw_materie_sel"] = _hw_mat
                st.rerun()
        with col2:
            if st.button("💬 Înapoi la chat", use_container_width=True):
                for k in [k for k in list(st.session_state.keys()) if k.startswith("hw_")]:
                    st.session_state.pop(k, None)
                st.session_state.pop("homework_mode", None)
                st.rerun()
