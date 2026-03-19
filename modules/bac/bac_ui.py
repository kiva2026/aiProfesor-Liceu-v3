"""
modules/bac/bac_ui.py — UI complet pentru simularea BAC.
"""
import time
import streamlit as st
import streamlit.components.v1 as components

from config import MATERII
from modules.ai.gemini_client import run_chat_with_rotation
from modules.materii.base import get_system_prompt
from modules.ui.svg_renderer import render_message_with_svg
from modules.bac.base import (
    MATERII_BAC, MATERII_SIMULARE_DISPONIBILE, PROFILE_BAC,
    get_bac_prompt_ai, get_bac_correction_prompt,
    parse_bac_subject, format_timer,
)


def extract_text_from_photo_bac(img_bytes: bytes, materie_label: str) -> str:
    """Extrage textul din fotografia lucrării BAC."""
    from modules.bac.homework_ui import extract_text_from_photo
    return extract_text_from_photo(img_bytes, materie_label)


def run_bac_sim_ui():
    st.subheader("🎓 Simulare BAC")

    # ── ECRAN DE START ──
    if not st.session_state.get("bac_active"):
        st.markdown("#### 🎓 Alege profilul tău")
        col1, col2 = st.columns(2)
        with col1:
            filiere = list(PROFILE_BAC.keys())
            bac_filiera = st.selectbox("🏫 Filiera:", options=filiere, key="bac_filiera_sel")
            profile_in_filiera = list(PROFILE_BAC[bac_filiera].keys())
            bac_profil_grup = st.selectbox("📂 Profil:", options=profile_in_filiera, key="bac_profil_grup_sel")

        with col2:
            specializari = list(PROFILE_BAC[bac_filiera][bac_profil_grup].keys())
            bac_specializare = st.selectbox("🎯 Specializare:", options=specializari, key="bac_spec_sel")
            spec_info    = PROFILE_BAC[bac_filiera][bac_profil_grup][bac_specializare]
            obligatorii  = spec_info["materii_obligatorii"]
            optionale    = spec_info["materii_optionale"]
            toate        = obligatorii + optionale
            disponibile  = [m for m in toate if m in MATERII_SIMULARE_DISPONIBILE]
            indisponibile = [m for m in toate if m not in MATERII_SIMULARE_DISPONIBILE]

            if disponibile:
                def _label(m):
                    return f"{m}  ✦ obligatorie" if m in obligatorii else m
                bac_materie = st.selectbox(
                    "📚 Materia de simulat:",
                    options=disponibile, format_func=_label, key="bac_mat_sel"
                )
            else:
                st.warning("⚠️ Nicio materie cu suport AI pentru această specializare.")
                bac_materie = None

        if indisponibile:
            st.caption(f"ℹ️ Fără simulare AI (în curând): {', '.join(indisponibile)}")

        st.markdown(
            f"<div style='background:linear-gradient(135deg,#667eea22,#764ba222);"
            f"border:1px solid #667eea44;padding:12px 18px;border-radius:10px;margin:8px 0 4px 0'>"
            f"<b>{bac_specializare}</b> — {spec_info['descriere']}</div>",
            unsafe_allow_html=True
        )

        if bac_materie is None:
            return

        info = MATERII_BAC.get(bac_materie, {})
        if not info:
            st.error(f"Materia '{bac_materie}' nu are configurație în sistem.")
            return

        bac_profil = bac_specializare

        # Selector tip fizică
        if info.get("cod") in ("fizica_real", "fizica_tehnologic"):
            tip_fizica = st.radio(
                "🔬 Tip Fizică:",
                options=["🔬 Fizică profil real", "⚡ Fizică profil tehnologic"],
                key="bac_fizica_tip", horizontal=True,
            )
            if "real" in tip_fizica:
                bac_materie = "🔬 Fizică real"
                info = MATERII_BAC.get("🔬 Fizică real", info)
            else:
                bac_materie = "⚡ Fizică tehnolog"
                info = MATERII_BAC.get("⚡ Fizică tehnolog", info)
        elif len(info.get("profile", [])) > 1:
            bac_profil = st.selectbox(
                f"📋 Varianta {bac_materie}:",
                options=info["profile"], key="bac_prof_var_sel"
            )

        use_timer = st.checkbox(f"⏱️ Cronometru ({info.get('timp_minute', 180)} min)", value=True, key="bac_timer")

        if info.get("date_reale"):
            structura    = info.get("structura", {})
            structura_html = "".join(f"<li><b>{k}:</b> {v}</li>" for k, v in structura.items())
            st.markdown(
                "<div style='background:linear-gradient(135deg,#11998e,#38ef7d);"
                "color:white;padding:18px 22px;border-radius:12px;margin:12px 0'>"
                "<h4 style='margin:0 0 8px 0'>✅ Subiecte bazate pe tipare reale BAC 2021–2025</h4>"
                f"<ul style='margin:0;padding-left:18px;line-height:1.9'>{structura_html}</ul>"
                "<p style='margin:10px 0 0 0;font-size:13px;opacity:0.9'>"
                "⏱️ 3 ore · 100 puncte (90p scrise + 10p oficiu)</p></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='background:linear-gradient(135deg,#667eea,#764ba2);"
                "color:white;padding:18px 22px;border-radius:12px;margin:12px 0'>"
                "<h4 style='margin:0 0 8px 0'>📋 Subiect generat de AI</h4>"
                "<ul style='margin:0;padding-left:18px;line-height:1.8'>"
                "<li>Structură inspirată din modelele BAC oficiale</li>"
                "<li>Rezolvi în timp real cu cronometru opțional</li>"
                "<li>Primești corectare AI detaliată + barem</li>"
                "</ul></div>",
                unsafe_allow_html=True
            )

        st.divider()
        col_s, col_b = st.columns(2)
        with col_s:
            if st.button("🚀 Generează subiect AI", type="primary", use_container_width=True):
                with st.spinner("📝 Se generează subiectul BAC..."):
                    prompt = get_bac_prompt_ai(bac_materie, info, bac_profil)
                    full   = "".join(run_chat_with_rotation(
                        [], [prompt],
                        system_prompt=get_system_prompt(
                            materie=None,
                            pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                            mod_avansat=st.session_state.get("mod_avansat", False),
                            mod_strategie=st.session_state.get("mod_strategie", False),
                            mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                        )
                    ))
                subject_text, barem = parse_bac_subject(full)
                st.session_state.update({
                    "bac_active": True, "bac_materie": bac_materie, "bac_profil": bac_profil,
                    "bac_subject": subject_text, "bac_barem": barem,
                    "bac_raspuns": "", "bac_corectat": False, "bac_corectare": "",
                    "bac_start_time": time.time() if use_timer else None,
                    "bac_timp_min": info["timp_minute"], "bac_use_timer": use_timer,
                })
                st.rerun()
        with col_b:
            if st.button("↩️ Înapoi la chat", use_container_width=True):
                st.session_state.pop("bac_mode", None)
                st.rerun()
        return

    # ── SIMULARE ACTIVĂ ──
    col_title, col_timer = st.columns([3, 1])
    with col_title:
        st.markdown(f"### {st.session_state.bac_materie} · {st.session_state.bac_profil}")
    with col_timer:
        if st.session_state.get("bac_use_timer") and st.session_state.get("bac_start_time"):
            elapsed = int(time.time() - st.session_state.bac_start_time)
            total   = st.session_state.bac_timp_min * 60
            left    = max(0, total - elapsed)
            pct     = left / total
            color   = "#2ecc71" if pct > 0.5 else ("#e67e22" if pct > 0.2 else "#e74c3c")
            st.markdown(
                f'<div style="background:{color};color:white;padding:8px 12px;'
                f'border-radius:8px;text-align:center;font-size:20px;font-weight:700">'
                f'⏱️ {format_timer(left)}</div>',
                unsafe_allow_html=True
            )
            if left == 0:
                st.warning("⏰ Timpul a expirat!")
                if (
                    not st.session_state.get("bac_corectat")
                    and not st.session_state.get("bac_timer_submitted")
                    and st.session_state.get("bac_raspuns", "").strip()
                ):
                    st.session_state["bac_timer_submitted"] = True
                    with st.spinner("⏰ Timp expirat — se corectează automat..."):
                        prompt_timeout = get_bac_correction_prompt(
                            st.session_state.bac_materie,
                            st.session_state.bac_subject,
                            st.session_state.bac_raspuns,
                            from_photo=st.session_state.get("bac_from_photo", False),
                        )
                        corectare_timeout = "".join(run_chat_with_rotation(
                            [], [prompt_timeout],
                            system_prompt=get_system_prompt(
                                materie=MATERII.get(st.session_state.bac_materie),
                                pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                                mod_avansat=st.session_state.get("mod_avansat", False),
                                mod_strategie=st.session_state.get("mod_strategie", False),
                                mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                            )
                        ))
                    st.session_state.bac_corectare = corectare_timeout
                    st.session_state.bac_corectat  = True
                    st.rerun()
            elif left > 0 and not st.session_state.get("bac_corectat"):
                components.html(
                    "<script>setTimeout(() => window.parent.location.reload(), 1000);</script>",
                    height=0
                )
                st.stop()

    st.divider()

    with st.expander("📋 Subiectul", expanded=not st.session_state.bac_corectat):
        st.markdown(st.session_state.bac_subject)

    if not st.session_state.bac_corectat:
        st.markdown("### ✏️ Răspunsurile tale")
        tab_foto, tab_text = st.tabs(["📷 Fotografiază lucrarea", "⌨️ Scrie manual"])

        with tab_foto:
            st.info(
                "📱 **Pe telefon:** fotografiază lucrarea.\n\n"
                "💻 **Pe calculator:** încarcă o poză din galerie.\n\n"
                "AI-ul va citi textul și va porni corectarea automat."
            )
            uploaded_photo = st.file_uploader(
                "Încarcă fotografia lucrării:",
                type=["jpg", "jpeg", "png", "webp", "heic"],
                key="bac_photo_upload",
            )

            if uploaded_photo and not st.session_state.get("bac_ocr_done"):
                st.image(uploaded_photo, caption="Fotografia încărcată", use_container_width=True)
                with st.spinner("🔍 Profesorul citește lucrarea..."):
                    text_extras = extract_text_from_photo_bac(
                        uploaded_photo.read(), st.session_state.bac_materie
                    )
                st.session_state.bac_raspuns    = text_extras
                st.session_state.bac_ocr_done   = True
                st.session_state.bac_from_photo = True
                with st.spinner("📊 Se corectează lucrarea..."):
                    prompt = get_bac_correction_prompt(
                        st.session_state.bac_materie, st.session_state.bac_subject,
                        text_extras, from_photo=True
                    )
                    corectare = "".join(run_chat_with_rotation(
                        [], [prompt],
                        system_prompt=get_system_prompt(
                            materie=MATERII.get(st.session_state.bac_materie),
                            pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                            mod_avansat=st.session_state.get("mod_avansat", False),
                            mod_strategie=st.session_state.get("mod_strategie", False),
                            mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                        )
                    ))
                st.session_state.bac_corectare = corectare
                st.session_state.bac_corectat  = True
                st.rerun()

            if st.session_state.get("bac_ocr_done"):
                with st.expander("📄 Text extras din poză", expanded=False):
                    st.text(st.session_state.get("bac_raspuns", ""))

        with tab_text:
            raspuns = st.text_area(
                "Scrie rezolvarea completă:",
                value=st.session_state.get("bac_raspuns", ""),
                height=350,
                placeholder="Subiectul I:\n1. ...\n\nSubiectul II:\n...\n\nSubiectul III:\n...",
                key="bac_ans_input"
            )
            st.session_state.bac_raspuns    = raspuns
            st.session_state.bac_from_photo = False

            if st.button("🤖 Corectare AI", type="primary", use_container_width=True,
                         disabled=not raspuns.strip()):
                with st.spinner("📊 Se corectează lucrarea..."):
                    prompt = get_bac_correction_prompt(
                        st.session_state.bac_materie, st.session_state.bac_subject,
                        raspuns, from_photo=False
                    )
                    corectare = "".join(run_chat_with_rotation(
                        [], [prompt],
                        system_prompt=get_system_prompt(
                            materie=MATERII.get(st.session_state.bac_materie),
                            pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                            mod_avansat=st.session_state.get("mod_avansat", False),
                            mod_strategie=st.session_state.get("mod_strategie", False),
                            mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                        )
                    ))
                st.session_state.bac_corectare = corectare
                st.session_state.bac_corectat  = True
                st.rerun()

        st.divider()
        col_barem, col_nou = st.columns(2)
        with col_barem:
            if st.session_state.get("bac_barem"):
                if st.button("📋 Arată Baremul", use_container_width=True):
                    st.session_state.bac_show_barem = not st.session_state.get("bac_show_barem", False)
                    st.rerun()
        with col_nou:
            if st.button("🔄 Subiect nou", use_container_width=True):
                _save = {k: st.session_state.get(k) for k in
                         ["bac_filiera_sel", "bac_profil_grup_sel", "bac_spec_sel", "bac_mat_sel"]}
                for k in [k for k in list(st.session_state.keys()) if k.startswith("bac_")]:
                    st.session_state.pop(k, None)
                for k, v in _save.items():
                    if v: st.session_state[k] = v
                st.rerun()

        if st.session_state.get("bac_show_barem") and st.session_state.get("bac_barem"):
            with st.expander("📋 Barem de corectare", expanded=True):
                st.markdown(st.session_state.bac_barem)

    else:
        st.markdown("### 📊 Corectare AI")
        st.markdown(st.session_state.bac_corectare)
        if st.session_state.get("bac_barem"):
            with st.expander("📋 Barem"):
                st.markdown(st.session_state.bac_barem)
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Subiect nou", type="primary", use_container_width=True):
                _save = {k: st.session_state.get(k) for k in
                         ["bac_filiera_sel", "bac_profil_grup_sel", "bac_spec_sel", "bac_mat_sel"]}
                for k in [k for k in list(st.session_state.keys()) if k.startswith("bac_")]:
                    st.session_state.pop(k, None)
                for k, v in _save.items():
                    if v: st.session_state[k] = v
                st.rerun()
        with col2:
            if st.button("✏️ Reîncerc același subiect", use_container_width=True):
                st.session_state.bac_corectat  = False
                st.session_state.bac_corectare = ""
                st.session_state.bac_raspuns   = ""
                if st.session_state.get("bac_use_timer"):
                    st.session_state.bac_start_time = time.time()
                st.rerun()
        with col3:
            if st.button("💬 Înapoi la chat", use_container_width=True):
                for k in [k for k in list(st.session_state.keys()) if k.startswith("bac_")]:
                    st.session_state.pop(k, None)
                st.session_state.pop("bac_mode", None)
                st.rerun()
