"""
modules/bac/admitere_ui.py — UI complet pentru simularea admiterii la facultate.
"""
import re
import time
import streamlit as st

from modules.ai.gemini_client import run_chat_with_rotation
from modules.materii.base import get_system_prompt
from modules.ui.svg_renderer import render_message_with_svg
from modules.auth.supabase_auth import _log
from modules.bac.base import format_timer
from modules.bac.admitere_base import ADMITERE_CONFIG, ADMITERE_NIVELE, get_admitere_prompt


def parse_grila_questions(text: str) -> list[dict]:
    """Parsează întrebările grilă din textul AI.
    Suportă formate cu 6 variante (a-f) pentru UPB ETTI și 4 variante (a-d).
    Baremul din [[BAREM]]...[[/BAREM]] are prioritate față de RĂSPUNS inline.
    """
    # Protejăm SVG-urile în timpul parsării
    svg_store = {}
    counter   = [0]

    def _replace_svg(m):
        key = f"__SVG_{counter[0]}__"
        svg_store[key] = m.group(0)
        counter[0] += 1
        return key

    t = re.sub(r'\[\[DESEN_SVG\]\].*?\[\[/DESEN_SVG\]\]', _replace_svg, text, flags=re.DOTALL)
    t = re.sub(r'<svg\b[^>]*>.*?</svg\s*>', _replace_svg, t, flags=re.DOTALL | re.IGNORECASE)

    def _restore(s):
        for k, v in svg_store.items():
            s = s.replace(k, v)
        return s

    # Extragem baremul
    barem_map   = {}
    barem_match = re.search(r'\[\[BAREM\]\](.*?)\[\[/BAREM\]\]', t, re.DOTALL)
    if barem_match:
        for item in re.split(r'[,;\n]+', barem_match.group(1).strip()):
            m = re.match(r'(\d+)\s*[-–:]\s*([a-f])', item.strip(), re.IGNORECASE)
            if m:
                barem_map[int(m.group(1))] = m.group(2).lower()

    text_clean = re.sub(r'\[\[BAREM\]\].*?\[\[/BAREM\]\]', '', t, flags=re.DOTALL).strip()

    def _get_var(block, lit):
        m = re.search(
            rf'(?:^|;|\n)\s*{lit}\)\s*(.*?)(?=\s*(?:[a-f]\)|;|\n\s*[a-f]\)|\Z))',
            block, re.IGNORECASE | re.DOTALL
        )
        if m:
            val = m.group(1).strip().rstrip(';').strip()
            return re.sub(r'\s*\n\s*', ' ', val).strip()
        return ""

    questions = []

    # FORMAT 6 variante (a-f) — UPB ETTI
    has_6var = bool(re.search(r'\be\)\s*\S|\bf\)\s*\S', text_clean, re.IGNORECASE))
    if has_6var:
        blocks = re.split(r'(?=^\s*\d+[\.\.)]\s)', text_clean, flags=re.MULTILINE)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            nr_m = re.match(r'^(\d+)[\.\.)]\s*', block)
            if not nr_m:
                continue
            nr = int(nr_m.group(1))
            enunt_m = re.match(r'^\d+[\.\.)]\s*(.*?)(?=\s*(?:^|\n)\s*a\))', block, re.DOTALL | re.MULTILINE)
            if not enunt_m:
                continue
            enunt_raw = re.sub(r'\s*\n\s*', ' ', enunt_m.group(1)).strip()
            enunt_raw = re.sub(r'\s*\(\s*\d+\s*p(?:ct\.?)?\s*\)', '', enunt_raw).strip()
            enunt     = _restore(enunt_raw)
            variante  = {l: _restore(_get_var(block, l)) for l in "abcdef"}
            if not (variante.get("a") and variante.get("b") and variante.get("c")):
                continue
            questions.append({
                "nr": nr, "enunt": enunt, "variante": variante, "nr_variante": 6,
                "raspuns_corect": barem_map.get(nr, ""),
                "has_svg": bool(svg_store and any(k in enunt for k in svg_store)),
            })
        if len(questions) >= 3:
            return sorted(questions, key=lambda q: q["nr"])

    # FORMAT Q prefix + RĂSPUNS inline
    questions = []
    pattern_q = re.compile(
        r'Q(\d+)\.\s*(.*?)\na\)\s*(.*?)\nb\)\s*(.*?)\nc\)\s*(.*?)\nd\)\s*(.*?)\nRĂ?SPUNS\s*:?\s*([a-d])',
        re.DOTALL | re.IGNORECASE
    )
    for m in pattern_q.finditer(text_clean):
        nr    = int(m.group(1))
        enunt = _restore(m.group(2).strip())
        questions.append({
            "nr": nr, "enunt": enunt,
            "variante": {
                "a": _restore(m.group(3).strip()), "b": _restore(m.group(4).strip()),
                "c": _restore(m.group(5).strip()), "d": _restore(m.group(6).strip()),
            },
            "nr_variante": 4,
            "raspuns_corect": barem_map.get(nr, m.group(7).strip().lower()),
            "has_svg": bool(svg_store and any(k in enunt for k in svg_store)),
        })
    if len(questions) >= 3:
        return sorted(questions, key=lambda q: q["nr"])

    # FORMAT simplu: număr + 4 variante
    questions = []
    blocks    = re.split(r'(?=^\s*\d+[\.\.)]\s)', text_clean, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        nr_m = re.match(r'^(\d+)[\.\.)]\s*', block)
        if not nr_m:
            continue
        nr      = int(nr_m.group(1))
        enunt_m = re.match(r'^\d+[\.\.)]\s*(.*?)(?=\s*(?:^|\n)\s*a\))', block, re.DOTALL | re.MULTILINE)
        if not enunt_m:
            continue
        enunt_raw = re.sub(r'\s*\n\s*', ' ', enunt_m.group(1)).strip()
        enunt     = _restore(enunt_raw)
        variante  = {l: _restore(_get_var(block, l)) for l in "abcd"}
        if not (variante.get("a") and variante.get("b") and variante.get("c")):
            continue
        raspuns_m = re.search(r'RĂ?SPUNS\s*:?\s*([a-d])', block, re.IGNORECASE)
        raspuns   = barem_map.get(nr, raspuns_m.group(1).lower() if raspuns_m else "")
        questions.append({
            "nr": nr, "enunt": enunt, "variante": variante, "nr_variante": 4,
            "raspuns_corect": raspuns,
            "has_svg": bool(svg_store and any(k in enunt for k in svg_store)),
        })

    return sorted(questions, key=lambda q: q["nr"]) if len(questions) >= 3 else []


def run_admitere_ui():
    st.subheader("🏛️ Admitere Facultate")

    if not st.session_state.get("admitere_active"):
        col1, col2 = st.columns(2)
        with col1:
            univ = st.selectbox("🏫 Universitate:", options=list(ADMITERE_CONFIG.keys()), key="adm_univ_sel")
            spec_options = list(ADMITERE_CONFIG[univ]["specializari"].keys())
            spec = st.selectbox("🎯 Specializare:", options=spec_options, key="adm_spec_sel")
        with col2:
            probe     = ADMITERE_CONFIG[univ]["specializari"][spec]["probe"]
            proba_idx = st.selectbox("📋 Proba:", options=range(len(probe)),
                                     format_func=lambda i: probe[i]["label"], key="adm_proba_sel")
            proba     = probe[proba_idx]
            if proba["tip"] == "grila":
                mod_grila = st.radio("📝 Mod rezolvare:",
                                     options=["🖱️ Grilă interactivă", "✍️ Răspuns liber"],
                                     key="adm_mod_grila", horizontal=True)
            else:
                mod_grila = "✍️ Răspuns liber"
                st.info("✍️ Probă cu rezolvare scrisă")

        st.markdown(
            f"<div style='background:linear-gradient(135deg,#f093fb22,#f5576c22);"
            f"border:1px solid #f093fb55;padding:14px 18px;border-radius:10px;margin:10px 0'>"
            f"<b>{univ}</b> · {spec}<br>"
            f"<span style='font-size:13px'>{proba['descriere']}</span><br>"
            f"<span style='font-size:12px;opacity:0.8'>⏱️ {proba['timp_minute']} min · {proba['structura']}</span>"
            f"</div>", unsafe_allow_html=True)

        nivel_dificultate = st.radio(
            "🎯 Nivel de dificultate:",
            options=list(ADMITERE_NIVELE.keys()),
            format_func=lambda k: f"{k}  —  {ADMITERE_NIVELE[k]['descriere']}",
            key="adm_nivel_dificultate",
            horizontal=False,
        )

        use_timer = st.checkbox(f"⏱️ Cronometru ({proba['timp_minute']} min)", value=True, key="adm_timer")
        st.divider()

        if st.button("🚀 Generează subiect", type="primary", use_container_width=True):
            with st.spinner("📝 Se generează subiectul de admitere..."):
                prompt = get_admitere_prompt(proba["cod"], proba, spec, univ, nivel_dificultate)
                full   = "".join(run_chat_with_rotation([], [prompt],
                    system_prompt=get_system_prompt(
                        materie=None, pas_cu_pas=False, mod_avansat=True,
                        mod_strategie=False, mod_bac_intensiv=False
                    )
                ))
                barem_m      = re.search(r'\[\[BAREM\]\](.*?)\[\[/BAREM\]\]', full, re.DOTALL)
                barem        = barem_m.group(1).strip() if barem_m else ""
                subject_text = full[:barem_m.start()].strip() if barem_m else full

                st.session_state.update({
                    "admitere_active": True, "admitere_univ": univ,
                    "admitere_spec": spec, "admitere_proba": proba,
                    "admitere_subject": subject_text, "admitere_barem": barem,
                    "admitere_mod_grila": mod_grila, "admitere_nivel": nivel_dificultate,
                    "admitere_corectat": False, "admitere_raspuns": "",
                })

                if proba["tip"] == "grila" and "🖱️" in mod_grila:
                    parsed = parse_grila_questions(full)
                    if not parsed:
                        _log(f"parse_grila_questions a returnat [] pentru:\n{full[:500]}", "silent")
                    st.session_state.admitere_grila_questions  = parsed
                    st.session_state.admitere_grila_answers    = {}
                    st.session_state.admitere_grila_submitted  = False

                if use_timer:
                    st.session_state.admitere_start_time = time.time()
                    st.session_state.admitere_timp_min   = proba["timp_minute"]
                st.rerun()

        if st.button("← Înapoi", key="adm_back_start"):
            st.session_state.admitere_mode = False
            st.rerun()
        return

    # ── ECRAN REZOLVARE ──
    univ      = st.session_state.admitere_univ
    spec      = st.session_state.admitere_spec
    proba     = st.session_state.admitere_proba
    subject   = st.session_state.admitere_subject
    barem     = st.session_state.admitere_barem
    mod_grila = st.session_state.get("admitere_mod_grila", "✍️ Răspuns liber")

    st.markdown(f"### {univ} · {spec}")
    _nivel_activ = st.session_state.get("admitere_nivel", "🟢 Normal")
    st.caption(f"📋 {proba['label']}  ·  {_nivel_activ}")

    # Cronometru
    start_time = st.session_state.get("admitere_start_time")
    if start_time:
        elapsed   = int(time.time() - start_time)
        total     = st.session_state.get("admitere_timp_min", 180) * 60
        remaining = max(0, total - elapsed)
        col_t1, col_t2 = st.columns([3, 1])
        with col_t2:
            color = "#e53e3e" if remaining < 600 else "#38a169"
            st.markdown(
                f"<div style='text-align:center;background:{color}22;border:1px solid {color}55;"
                f"border-radius:8px;padding:8px;font-size:20px;font-weight:bold;color:{color}'>"
                f"⏱️ {format_timer(remaining)}</div>", unsafe_allow_html=True)

    # ── MOD GRILĂ INTERACTIVĂ ──
    if proba["tip"] == "grila" and "🖱️" in mod_grila:
        questions = st.session_state.get("admitere_grila_questions", [])
        answers   = st.session_state.get("admitere_grila_answers", {})
        submitted = st.session_state.get("admitere_grila_submitted", False)

        if not questions:
            with st.expander("📄 Subiectul", expanded=True):
                st.markdown(subject)
            st.divider()
            st.warning("Nu s-au putut parsa întrebările. Încearcă modul 'Răspuns liber'.")
        else:
            nr_variante          = questions[0].get("nr_variante", 4) if questions else 4
            puncte_per_intrebare = 9 if nr_variante == 6 else 3
            st.markdown(f"**{len(questions)} întrebări · {puncte_per_intrebare}p/întrebare · 10p oficiu**")

            for q in questions:
                nr           = q["nr"]
                variante_keys = list(q["variante"].keys())
                st.markdown(f"**{nr}.**")
                render_message_with_svg(q["enunt"])

                if submitted:
                    corect = q["raspuns_corect"]
                    ales   = answers.get(nr, "")
                    for lit in variante_keys:
                        text = f"{lit}) {q['variante'][lit]}"
                        if lit == corect:
                            st.markdown(f"✅ **{text}**")
                        elif lit == ales and ales != corect:
                            st.markdown(f"❌ ~~{text}~~")
                        else:
                            st.markdown(f"&nbsp;&nbsp;{text}")
                else:
                    ales = st.radio(
                        f"Q{nr}", options=variante_keys,
                        format_func=lambda l, q=q: f"{l}) {q['variante'][l]}",
                        key=f"adm_q_{nr}", label_visibility="collapsed", horizontal=True
                    )
                    answers[nr] = ales
                st.markdown("---")

            st.session_state.admitere_grila_answers = answers

            if not submitted:
                st.caption(f"Răspuns la {sum(1 for q in questions if q['nr'] in answers)}/{len(questions)} întrebări")
                if st.button("✅ Trimite grila", type="primary", use_container_width=True):
                    st.session_state.admitere_grila_submitted = True
                    st.rerun()
            else:
                corecte      = sum(1 for q in questions if answers.get(q["nr"], "") == q["raspuns_corect"])
                scor_intreb  = corecte * puncte_per_intrebare
                scor_total   = scor_intreb + 10
                nota         = round(scor_total / 10, 2)
                culoare      = "#38a169" if scor_total >= 50 else "#e53e3e"
                st.markdown(
                    f"<div style='background:linear-gradient(135deg,{culoare}33,{culoare}11);"
                    f"border:2px solid {culoare}88;padding:20px;border-radius:12px;text-align:center'>"
                    f"<h2 style='margin:0'>🎯 {corecte}/{len(questions)} corecte</h2>"
                    f"<h3 style='margin:8px 0 4px 0'>{scor_intreb}p + 10p oficiu = "
                    f"<b>{scor_total}/100p</b></h3>"
                    f"<div style='font-size:22px;font-weight:bold'>Nota: {nota}/10</div>"
                    f"</div>", unsafe_allow_html=True)

    # ── MOD RĂSPUNS LIBER ──
    else:
        with st.expander("📄 Subiectul", expanded=True):
            render_message_with_svg(subject)
        st.divider()

        if not st.session_state.admitere_corectat:
            raspuns = st.text_area(
                "✍️ Scrie rezolvarea ta:",
                value=st.session_state.admitere_raspuns,
                height=300, key="adm_raspuns_input",
                placeholder="Scrie rezolvarea completă aici..."
            )
            st.session_state.admitere_raspuns = raspuns

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Corectează", type="primary",
                             use_container_width=True, disabled=not raspuns.strip()):
                    with st.spinner("🤖 Se corectează..."):
                        prompt_cor = (
                            f"Corectează admitere {univ.replace('🎓 ','').replace('🏛️ ','')} — {proba['label']}.\n"
                            f"SUBIECT:\n{subject}\n\n"
                            f"BAREM:\n{barem}\n\n"
                            f"RĂSPUNS CANDIDAT:\n{raspuns}\n\n"
                            f"Dă: punctaj per cerință, greșeli, nota/100, top 3 lacune de remediat."
                        )
                        corectare = "".join(run_chat_with_rotation(
                            [], [prompt_cor],
                            system_prompt=get_system_prompt(
                                materie=None, pas_cu_pas=True, mod_avansat=True,
                                mod_strategie=False, mod_bac_intensiv=False
                            )
                        ))
                    st.session_state.admitere_corectare = corectare
                    st.session_state.admitere_corectat  = True
                    st.rerun()
            with col2:
                if barem:
                    with st.expander("📋 Barem"):
                        st.markdown(barem)
        else:
            st.success("✅ Corectare finalizată")
            st.markdown(st.session_state.admitere_corectare)
            if barem:
                with st.expander("📋 Barem oficial"):
                    st.markdown(barem)

    st.divider()
    col_r, col_n = st.columns(2)
    with col_r:
        if st.button("🔄 Subiect nou", use_container_width=True):
            _saved = {k: st.session_state.get(k) for k in
                      ["admitere_univ", "admitere_spec", "admitere_proba", "admitere_nivel"]}
            for k in ["admitere_active", "admitere_subject", "admitere_barem", "admitere_raspuns",
                      "admitere_corectat", "admitere_corectare", "admitere_grila_questions",
                      "admitere_grila_answers", "admitere_grila_submitted", "admitere_start_time"]:
                st.session_state.pop(k, None)
            if _saved.get("admitere_univ"):
                st.session_state["adm_univ_sel"] = _saved["admitere_univ"]
            if _saved.get("admitere_spec"):
                st.session_state["adm_spec_sel"] = _saved["admitere_spec"]
            if _saved.get("admitere_nivel"):
                st.session_state["adm_nivel_dificultate"] = _saved["admitere_nivel"]
            st.rerun()
    with col_n:
        if st.button("← Înapoi la selecție", use_container_width=True):
            _saved = {k: st.session_state.get(k) for k in
                      ["admitere_univ", "admitere_spec", "admitere_proba", "admitere_nivel"]}
            for k in ["admitere_active", "admitere_subject", "admitere_barem", "admitere_raspuns",
                      "admitere_corectat", "admitere_corectare", "admitere_grila_questions",
                      "admitere_grila_answers", "admitere_grila_submitted", "admitere_start_time"]:
                st.session_state.pop(k, None)
            if _saved.get("admitere_univ"):
                st.session_state["adm_univ_sel"] = _saved["admitere_univ"]
            if _saved.get("admitere_spec"):
                st.session_state["adm_spec_sel"] = _saved["admitere_spec"]
            if _saved.get("admitere_nivel"):
                st.session_state["adm_nivel_dificultate"] = _saved["admitere_nivel"]
            st.rerun()
