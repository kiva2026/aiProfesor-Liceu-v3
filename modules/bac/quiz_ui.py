"""
modules/bac/quiz_ui.py — UI complet pentru modul Quiz rapid.
"""
import re
import streamlit as st

from config import MATERII
from modules.ai.gemini_client import run_chat_with_rotation
from modules.materii.base import get_system_prompt


NIVELE_QUIZ  = ["🟢 Ușor (gimnaziu)", "🟡 Mediu (liceu)", "🔴 Greu (BAC)"]
MATERII_QUIZ = [m for m in list(MATERII.keys()) if m != "🤖 Automat"]


def get_quiz_prompt(materie_label: str, nivel: str, materie_val: str) -> str:
    nivel_text = nivel.split(" ", 1)[1].strip("()")
    return f"""Generează un quiz de 5 întrebări la {materie_label} pentru nivel {nivel_text}.

REGULI STRICTE:
1. Generează EXACT 5 întrebări numerotate (1. 2. 3. 4. 5.)
2. Fiecare întrebare are 4 variante de răspuns: A) B) C) D)
3. La finalul TUTUROR întrebărilor adaugă un bloc special cu răspunsurile corecte:

[[RASPUNSURI_CORECTE]]
1: X
2: X
3: X
4: X
5: X
[[/RASPUNSURI_CORECTE]]

unde X este A, B, C sau D.
4. Întrebările trebuie să fie clare și potrivite pentru nivel {nivel_text}.
5. Folosește LaTeX ($...$) pentru formule matematice.
6. NU da explicații acum — doar întrebările și răspunsurile corecte la final."""


def parse_quiz_response(response: str) -> tuple[str, dict]:
    correct = {}
    clean_response = response

    match = re.search(r'\[\[RASPUNSURI_CORECTE\]\](.*?)\[\[/RASPUNSURI_CORECTE\]\]',
                      response, re.DOTALL)
    if not match:
        match = re.search(
            r'(?:raspunsuri\s*corecte|answers?)[:\s]*\n'
            r'((?:\s*\d+\s*[:.)-]\s*[A-D].*\n?){3,})',
            response, re.IGNORECASE | re.DOTALL
        )

    if match:
        clean_response = response[:match.start()].strip()
        raw_block = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
        for line in raw_block.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r'\*{0,2}(\d{1,2})\*{0,2}\s*[:.)-]\s*\*{0,2}([A-D])\b', line, re.IGNORECASE)
            if m:
                try:
                    correct[int(m.group(1))] = m.group(2).upper()
                except ValueError:
                    pass

    if not correct:
        for m in re.finditer(
            r'(?:intrebarea|question)?\s*(\d+).*?r[a]spuns(?:ul)?\s*(?:corect)?\s*[:\s]+([A-D])\b',
            response, re.IGNORECASE
        ):
            try:
                q_num = int(m.group(1))
                if 1 <= q_num <= 10:
                    correct[q_num] = m.group(2).upper()
            except ValueError:
                pass

    return clean_response, correct


def evaluate_quiz(user_answers: dict, correct_answers: dict) -> tuple[int, str]:
    score = sum(1 for q, a in user_answers.items() if correct_answers.get(q) == a)
    total = len(correct_answers)

    lines = []
    for q in sorted(correct_answers.keys()):
        user_ans    = user_answers.get(q, "—")
        correct_ans = correct_answers[q]
        if user_ans == correct_ans:
            lines.append(f"✅ **Întrebarea {q}**: {user_ans} — Corect!")
        else:
            lines.append(f"❌ **Întrebarea {q}**: ai răspuns **{user_ans}**, corect era **{correct_ans}**")

    if score == total:
        verdict = "🏆 Excelent! Nota 10!"
    elif score >= total * 0.8:
        verdict = "🌟 Foarte bine!"
    elif score >= total * 0.6:
        verdict = "👍 Bine, mai exersează puțin!"
    elif score >= total * 0.4:
        verdict = "📚 Trebuie să mai studiezi."
    else:
        verdict = "💪 Nu-ți face griji, încearcă din nou!"

    return score, f"### Rezultat: {score}/{total} — {verdict}\n\n" + "\n\n".join(lines)


def run_quiz_ui():
    st.subheader("📝 Mod Examinare")

    if not st.session_state.get("quiz_active"):
        col1, col2 = st.columns(2)
        with col1:
            quiz_materie_label = st.selectbox("Materie:", options=MATERII_QUIZ, key="quiz_materie_select")
        with col2:
            quiz_nivel = st.selectbox("Nivel:", options=NIVELE_QUIZ, key="quiz_nivel_select")

        if st.button("🚀 Generează Quiz", type="primary", use_container_width=True):
            quiz_materie_val = MATERII[quiz_materie_label]
            with st.spinner("📝 Profesorul pregătește întrebările..."):
                prompt   = get_quiz_prompt(quiz_materie_label, quiz_nivel, quiz_materie_val)
                full_resp = "".join(run_chat_with_rotation(
                    [], [prompt],
                    system_prompt=get_system_prompt(
                        materie=quiz_materie_val,
                        pas_cu_pas=st.session_state.get("pas_cu_pas", False),
                        mod_avansat=st.session_state.get("mod_avansat", False),
                        mod_strategie=st.session_state.get("mod_strategie", False),
                        mod_bac_intensiv=st.session_state.get("mod_bac_intensiv", False),
                    )
                ))
            questions_text, correct = parse_quiz_response(full_resp)
            if len(correct) >= 3:
                st.session_state.update({
                    "quiz_active": True,
                    "quiz_questions": questions_text,
                    "quiz_correct": correct,
                    "quiz_answers": {},
                    "quiz_submitted": False,
                    "quiz_materie": quiz_materie_label,
                    "quiz_nivel": quiz_nivel,
                })
                st.rerun()
            else:
                st.error("❌ Nu am putut genera quiz-ul. Încearcă din nou.")
        return

    st.caption(f"📚 {st.session_state.quiz_materie} · {st.session_state.quiz_nivel}")
    st.markdown(st.session_state.quiz_questions)
    st.divider()

    if not st.session_state.quiz_submitted:
        st.markdown("**Alege răspunsurile tale:**")
        answers = {}
        for q_num in sorted(st.session_state.quiz_correct.keys()):
            answers[q_num] = st.radio(
                f"Întrebarea {q_num}:",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key=f"quiz_ans_{q_num}",
                index=None
            )
        all_answered = all(v is not None for v in answers.values())
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Trimite răspunsurile", type="primary",
                         disabled=not all_answered, use_container_width=True):
                st.session_state.quiz_answers  = {k: v for k, v in answers.items() if v}
                st.session_state.quiz_submitted = True
                st.rerun()
        with col2:
            if st.button("🔄 Quiz nou", use_container_width=True):
                _mat = st.session_state.get("quiz_materie_select")
                _niv = st.session_state.get("quiz_nivel_select")
                for k in ["quiz_active", "quiz_questions", "quiz_correct", "quiz_answers", "quiz_submitted"]:
                    st.session_state.pop(k, None)
                if _mat: st.session_state["quiz_materie_select"] = _mat
                if _niv: st.session_state["quiz_nivel_select"]   = _niv
                st.rerun()
    else:
        score, feedback = evaluate_quiz(st.session_state.quiz_answers, st.session_state.quiz_correct)
        st.markdown(feedback)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Quiz nou", type="primary", use_container_width=True):
                _mat = st.session_state.get("quiz_materie_select")
                _niv = st.session_state.get("quiz_nivel_select")
                for k in ["quiz_active", "quiz_questions", "quiz_correct", "quiz_answers", "quiz_submitted"]:
                    st.session_state.pop(k, None)
                if _mat: st.session_state["quiz_materie_select"] = _mat
                if _niv: st.session_state["quiz_nivel_select"]   = _niv
                st.rerun()
        with col2:
            if st.button("💬 Înapoi la chat", use_container_width=True):
                for k in ["quiz_active", "quiz_questions", "quiz_correct",
                          "quiz_answers", "quiz_submitted", "quiz_mode"]:
                    st.session_state.pop(k, None)
                st.rerun()
