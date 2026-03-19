"""
modules/bac/admitere_base.py — Configurație admitere facultate și generare prompturi.

Exportă:
  ADMITERE_CONFIG   — universități, specializări, probe
  ADMITERE_NIVELE   — niveluri de dificultate cu instrucțiuni detaliate
  UPB_ETTI_DATE_REALE — subiecte reale UPB ETTI 2021-2025
  get_admitere_prompt() — construiește promptul AI pentru generarea unui test de admitere
"""

# ══════════════════════════════════════════════════════════════════
# CONFIGURAȚIE UNIVERSITĂȚI
# ══════════════════════════════════════════════════════════════════

ADMITERE_CONFIG = {
    "🎓 FMI București": {
        "descriere": "Facultatea de Matematică și Informatică — Universitatea din București",
        "specializari": {
            "💻 Informatică": {
                "probe": [
                    {"cod": "fmi_info_matematica", "label": "Matematică (obligatorie)", "tip": "clasic",
                     "timp_minute": 180, "nr_intrebari": 0,
                     "descriere": "Algebră + Analiză matematică — nivel universitar an 1",
                     "structura": "3 probleme × 30p"},
                    {"cod": "fmi_info_informatica", "label": "Informatică (obligatorie)", "tip": "grila",
                     "timp_minute": 180, "nr_intrebari": 30,
                     "descriere": "30 întrebări grilă — algoritmi, structuri date, C/C++",
                     "structura": "30 grile × 3p"},
                ],
            },
            "📐 Matematică": {
                "probe": [
                    {"cod": "fmi_mate_matematica", "label": "Matematică (obligatorie)", "tip": "clasic",
                     "timp_minute": 180, "nr_intrebari": 0,
                     "descriere": "Algebră + Analiză matematică — nivel avansat",
                     "structura": "3 probleme × 30p"},
                    {"cod": "fmi_mate_informatica", "label": "Informatică (opțională)", "tip": "grila",
                     "timp_minute": 180, "nr_intrebari": 30,
                     "descriere": "Grilă informatică sau subiect suplimentar de matematică",
                     "structura": "30 grile × 3p"},
                ],
            },
        },
    },
    "🏛️ UPB — ACS (Automatică și Calculatoare)": {
        "descriere": "Facultatea de Automatică și Calculatoare — Universitatea Politehnica București",
        "specializari": {
            "⚙️ Calculatoare și Tehnologia Informației": {
                "probe": [
                    {"cod": "upb_acs_matematica", "label": "Matematică (obligatorie)", "tip": "clasic",
                     "timp_minute": 180, "nr_intrebari": 0,
                     "descriere": "Algebră și analiză matematică — nivel BAC avansat + intro universitar",
                     "structura": "Probleme structurate: matrice, funcții, derivate, integrale"},
                    {"cod": "upb_acs_informatica", "label": "Informatică (grilă)", "tip": "grila",
                     "timp_minute": 120, "nr_intrebari": 30,
                     "descriere": "Grilă — algoritmi, C/C++, structuri de date",
                     "structura": "30 grile × 3p"},
                    {"cod": "upb_acs_fizica", "label": "Fizică (grilă) — alternativă", "tip": "grila",
                     "timp_minute": 120, "nr_intrebari": 30,
                     "descriere": "Grilă fizică — mecanică, termodinamică, curent continuu",
                     "structura": "30 grile × 3p"},
                ],
            },
        },
    },
    "🏛️ UPB — ETTI (Electronică și Telecomunicații)": {
        "descriere": "Facultatea de Electronică, Telecomunicații și Tehnologia Informației — UPB",
        "specializari": {
            "📡 Electronică / Telecomunicații / Tehnologia informației": {
                "probe": [
                    {"cod": "upb_etti_matematica",
                     "label": "Algebră și Analiză Matematică AAM (P1 — obligatorie)", "tip": "grila",
                     "timp_minute": 120, "nr_intrebari": 10,
                     "descriere": "10 grile × 9p — Algebră + Analiză (limite, derivate, integrale, funcții)",
                     "structura": "10 grile × 9p + 10p oficiu = 100p. P1 obligatorie — 40% din nota finală.",
                     "date_reale": True},
                    {"cod": "upb_etti_fizica",
                     "label": "Fizică F (P2 — la alegere)", "tip": "grila",
                     "timp_minute": 120, "nr_intrebari": 10,
                     "descriere": "10 grile × 9p — Termodinamică, Electricitate DC/AC, Mecanică, Optică",
                     "structura": "10 grile × 9p + 10p oficiu = 100p. P2 la alegere — 40% din nota finală.",
                     "date_reale": True},
                    {"cod": "upb_etti_informatica",
                     "label": "Informatică I (P2 — alternativă la Fizică)", "tip": "grila",
                     "timp_minute": 120, "nr_intrebari": 10,
                     "descriere": "10 grile × 9p — Algoritmi, structuri de date, C/C++, complexitate",
                     "structura": "10 grile × 9p + 10p oficiu = 100p. P2 alternativă — 40% din nota finală."},
                ],
            },
        },
    },
}


# ══════════════════════════════════════════════════════════════════
# DATE REALE UPB ETTI
# ══════════════════════════════════════════════════════════════════

UPB_ETTI_DATE_REALE = {
    "matematica": {
        2025: {
            "data": "14 iulie 2025",
            "intrebari": [
                {"nr": 1, "capitol": "ecuații", "enunt": "Soluția ecuației |2x+1| = 2|x-1| + 2"},
                {"nr": 2, "capitol": "combinatorică", "enunt": "C(n,2) = 6 → n=?"},
                {"nr": 3, "capitol": "progresii", "enunt": "Progresie aritmetică r=3, a₃=7 → a₅=?"},
                {"nr": 4, "capitol": "ecuații", "enunt": "Ecuație fracționară: 6/(1-2x)=0"},
                {"nr": 5, "capitol": "funcții/derivate", "enunt": "f(x)=eˣ+x-2 → f'(1)=?"},
                {"nr": 6, "capitol": "limite", "enunt": "lim(x→2)(x²-3x+2)/(x-2)"},
                {"nr": 7, "capitol": "integrale/arie", "enunt": "Aria între f(x)=x+1/x, asimptota oblică, x=2, x=3"},
                {"nr": 8, "capitol": "polinoame", "enunt": "f(X)=mX³-6: x₁⁴+x₂⁴+x₃⁴=98 → x₁·x₂·x₃=?"},
                {"nr": 9, "capitol": "ecuații/parte întreagă", "enunt": "Numărul soluțiilor reale ale ecuației cu ⌊·⌋"},
                {"nr": 10, "capitol": "ecuații cu parametru", "enunt": "m ∈ ℝ pentru care ecuația are infinitate de soluții"},
            ],
        },
    },
}


# ══════════════════════════════════════════════════════════════════
# NIVELURI DE DIFICULTATE
# ══════════════════════════════════════════════════════════════════

ADMITERE_NIVELE = {
    "🟢 Normal": {
        "label": "Normal",
        "descriere": "Subiecte identice cu admiterea reală — exemple din 2021-2025",
        "instructiuni_grila": (
            "NIVEL NORMAL — identic cu subiectele reale UPB AAM din 2021-2025.\n"
            "Fiecare întrebare testează UN singur concept, calcule în 1-2 pași.\n\n"
            "Capitole și exemple EXACTE din subiecte reale:\n\n"
            "ECUAȚII și INECUAȚII:\n"
            "- Ecuație cu modul: |2x+1|=2|x-1|+2 (2025 Q1)\n"
            "- Ecuație exponențială: 2^(3x)=4 (2024 Q3), 9^x=81 (2023 Q5)\n"
            "- Sistem liniar 2×2: x+y=5, x-y=1 (2023 Q4)\n\n"
            "PROGRESII:\n"
            "- Progresie aritmetică: r=3, a₃=7 → a₅=? (2025 Q3)\n\n"
            "COMBINATORICĂ:\n"
            "- C(n,2)=6 → n=? (2025 Q2)\n\n"
            "DERIVATE:\n"
            "- f'(1) pentru f(x)=eˣ+x-2 (2025 Q5)\n\n"
            "LIMITE:\n"
            "- lim(x→2)(x²-3x+2)/(x-2) prin factorizare (2025 Q6)\n\n"
            "INTEGRALE:\n"
            "- Arie între grafic și asimptotă oblică pe interval (2025 Q7)\n\n"
            "NU include: legi de compoziție complexe, matrice la puteri mari.\n"
            "Variantele greșite: erori de calcul frecvente."
        ),
        "instructiuni_clasic": (
            "NIVEL NORMAL — identic cu subiectele reale de admitere 2021-2025.\n"
            "Cerințe directe, pași de calcul clari, fără combinații neașteptate de concepte."
        ),
    },
    "🟡 Mediu": {
        "label": "Mediu",
        "descriere": "Cele mai grele întrebări din 2021-2025 combinate",
        "instructiuni_grila": (
            "NIVEL MEDIU — stilul întrebărilor dificile din subiecte reale UPB AAM 2021-2025.\n"
            "Fiecare întrebare combină 2 concepte sau necesită un pas intermediar neevident.\n\n"
            "Exemple EXACTE din subiecte reale verificate:\n\n"
            "MATRICE:\n"
            "- A dată → suma modulelor elementelor de pe diagonala lui A^459 (2024 Q2)\n\n"
            "ECUAȚII CU PARAMETRU:\n"
            "- 1-2x-2x²=meˣ admite exact 3 soluții reale distincte → valorile lui m (2024 Q5)\n\n"
            "POLINOAME:\n"
            "- P(X)=aX^2024+bX^2023+X²+cX+3 div. prin (X²-1) (2023 Q7)\n"
            "- f(X)=mX³-6, x₁⁴+x₂⁴+x₃⁴=98 → x₁·x₂·x₃ (2025 Q8 — Vieta + Newton)\n\n"
            "LEGI DE COMPOZIȚIE:\n"
            "- x*y = xy-2x-2y+10, suma soluțiilor ecuației x*x=x (2023 Q9)\n\n"
            "FUNCȚII CU PARAMETRU:\n"
            "- f(x)=(x²+ax+b)/(x²+1) cu 3 extreme locale + asimptotă oblică y=x-2 (2023 Q10)\n\n"
            "INTEGRALE:\n"
            "- lim(x→0) [∫₀ˣ dt/(1+4t²+t⁴)] / (2x) (2023 Q8)\n\n"
            "Variantele greșite: rezultate prin metode parțial corecte sau erori conceptuale subtile."
        ),
        "instructiuni_clasic": (
            "NIVEL MEDIU — stilul întrebărilor dificile din subiecte reale 2021-2025.\n"
            "Cerințele combină 2-3 concepte. Cel puțin o cerință necesită un artificiu neevident.\n"
            "Include legi de compoziție, polinoame cu condiții, funcții cu parametru multiplu."
        ),
    },
    "🔴 Avansat": {
        "label": "Avansat",
        "descriere": "Dincolo de 2021-2025 — nivel olimpiadă județeană",
        "instructiuni_grila": (
            "NIVEL AVANSAT — dincolo de subiectele reale UPB, aproape de olimpiadă județeană.\n"
            "Niciun exercițiu să nu fie rezolvabil în sub 3 pași de raționament.\n\n"
            "Exemple EXACTE din cele mai grele întrebări verificate:\n\n"
            "INTEGRALE CU PARAMETRU:\n"
            "- f(x)=∫₁ˣ t(1-lnt)dt → abscisa punctului de maxim local (2021 Q1)\n\n"
            "LEGI DE COMPOZIȚIE COMPLEXE:\n"
            "- x*y=xy-x-y+25 pe ℤ → suma elementelor simetrizabile (2021 Q7)\n\n"
            "COMBINATORICĂ AVANSATĂ:\n"
            "- Câte numere din {1,...,999} conțin cifra 9 cel puțin o dată (2021 Q9 — răspuns: 271)\n\n"
            "POLINOAME + VIETA:\n"
            "- f(X)=mX³-6, x₁⁴+x₂⁴+x₃⁴=98 → x₁·x₂·x₃ (2025 Q8)\n\n"
            "FUNCȚII CU PARAMETRU MULTIPLU:\n"
            "- f(x)=(x²+ax+b)/(x²+1): 3 extreme + asimptotă oblică (2023 Q10)\n\n"
            "MATRICE LA PUTERI MARI:\n"
            "- A^459, A^2024 — ciclicitate la valori neevidente\n\n"
            "Variantele greșite: rezultate plauzibile prin aplicarea greșită a unor formule corecte."
        ),
        "instructiuni_clasic": (
            "NIVEL AVANSAT — dincolo de subiectele reale, aproape de olimpiadă județeană.\n"
            "Include: integrale cu parametru, legi de compoziție complexe, combinatorică,\n"
            "studiu complet de funcție cu mai mulți parametri, identități de putere Vieta."
        ),
    },
    "🔵 Preadmitere": {
        "label": "Preadmitere",
        "descriere": "Stil admitere anticipată (apr.) — materie cls IX-XI, mix ușor+greu",
        "instructiuni_grila": (
            "NIVEL PREADMITERE — stil admitere anticipată UPB (sesiunea aprilie, elevi cls XI).\n"
            "MATERIE: algebră și analiză cls IX-XI. Include derivate și integrale definite.\n\n"
            "INTERZIS EXPLICIT:\n"
            "- Polinoame avansate (Vieta, grad >2)\n"
            "- Legi de compoziție\n"
            "- Matrice la puteri mari (ciclicitate)\n"
            "- Combinatorică avansată (includere-excludere, partiții)\n\n"
            "STRUCTURĂ OBLIGATORIE — 10 întrebări mix:\n"
            "Întrebările 1-6 (UȘOARE): ecuație modul, progresie, derivată directă, exponențială, sistem, integrală\n"
            "Întrebările 7-10 (GRELE): integrală cu parametru, funcție cu parametru și condiție, ecuație exp. cu substituție, module duble\n\n"
            "Variantele greșite: erori tipice de calcul."
        ),
        "instructiuni_clasic": (
            "NIVEL PREADMITERE — materie cls IX-XI.\n"
            "INTERZIS: polinoame avansate, legi de compoziție, matrice la puteri mari.\n"
            "Include derivate, integrale definite cu parametru, funcții cu parametru.\n"
            "Mix: 6 cerințe ușoare + 4 cerințe grele."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════
# PROMPT GENERATION
# ══════════════════════════════════════════════════════════════════

def get_admitere_prompt(proba_cod: str, proba_info: dict, specializare: str,
                        universitate: str, nivel_dificultate: str = "🟢 Normal") -> str:
    """Construiește promptul AI pentru generarea unui test de admitere."""
    univ_scurt = universitate.replace("🎓 ", "").replace("🏛️ ", "")
    spec_scurt = specializare.replace("💻 ", "").replace("📐 ", "").replace("⚙️ ", "").replace("📡 ", "")

    _niv      = ADMITERE_NIVELE.get(nivel_dificultate, ADMITERE_NIVELE["🟢 Normal"])
    _dif_g    = _niv["instructiuni_grila"]
    _dif_c    = _niv["instructiuni_clasic"]
    _niv_lbl  = _niv["label"]

    # ── UPB ETTI — Matematică AAM (10 grile × 6 variante) ──
    if "matematica" in proba_cod and "etti" in proba_cod:
        return (
            f"Generează un CHESTIONAR DE CONCURS pentru admitere UPB — ETTI, "
            f"disciplina Algebră și Elemente de Analiză Matematică AAM.\n\n"
            f"STRUCTURĂ OBLIGATORIE:\n"
            f"- 10 întrebări numerotate 1-10\n"
            f"- Fiecare întrebare: enunț matematic precis + 6 variante (a, b, c, d, e, f)\n"
            f"- O singură variantă corectă per întrebare\n"
            f"- Fiecare întrebare valorează 9 puncte; 10 puncte din oficiu → total 100p\n"
            f"- Timp: 2 ore\n\n"
            f"FORMAT STRICT per întrebare:\n"
            f"[nr]. [Enunț matematic complet]. ([9 pct.])\n"
            f"a) [val]; b) [val]; c) [val]; d) [val]; e) [val]; f) [val].\n\n"
            f"DISTRIBUȚIE CAPITOLE:\n"
            f"- Q1-2: Algebră — ecuații/inecuații (modul, exponențiale, logaritmice, sisteme)\n"
            f"- Q3-4: Algebră — progresii, combinatorică, permutări, aranjamente\n"
            f"- Q5-6: Algebră — matrice/determinanți, polinoame, legi de compoziție\n"
            f"- Q7-8: Analiză — limite (0/0, ∞/∞), derivate, extreme, monotonie\n"
            f"- Q9-10: Analiză — integrale definite, arie, funcții cu parametru\n\n"
            f"REGULI DE STIL:\n"
            f"- Variantele greșite: erori tipice de calcul — plauzibile\n"
            f"- Notații standard românești: tg(x), ctg(x), lg(x), ln(x), f'(x), C(n,k)\n"
            f"- Valori numerice curate (întregi, fracții simple, radicali simpli)\n\n"
            f"NIVEL DE DIFICULTATE — {_niv_lbl.upper()}:\n{_dif_g}\n\n"
            f"La final:\n"
            f"[[BAREM]]1-[lit], 2-[lit], 3-[lit], 4-[lit], 5-[lit], "
            f"6-[lit], 7-[lit], 8-[lit], 9-[lit], 10-[lit][[/BAREM]]"
        )

    # ── UPB ETTI — Fizică (10 grile × 6 variante) ──
    elif "fizica" in proba_cod and "etti" in proba_cod:
        return (
            f"Generează un CHESTIONAR DE CONCURS pentru admitere UPB — ETTI, disciplina Fizică F.\n\n"
            f"STRUCTURĂ OBLIGATORIE:\n"
            f"- 10 întrebări numerotate 1-10\n"
            f"- Fiecare întrebare: enunț cu date numerice concrete + 6 variante (a-f)\n"
            f"- O singură variantă corectă; fiecare valorează 9 puncte; 10p oficiu → 100p\n"
            f"- Timp: 2 ore\n\n"
            f"DISTRIBUȚIE CAPITOLE:\n"
            f"- Q1-2: Termodinamică (gaze ideale, transformări, ciclu Carnot, randament)\n"
            f"- Q3-4: Circuite electrice DC (Legea Ohm, rezistoare serie/paralel, Kirchhoff)\n"
            f"- Q5-6: Mecanică (cinematică, cădere liberă, lucru mecanic, energie, impuls)\n"
            f"- Q7-8: Circuite mixte / aplicații electrice (surse multiple, putere maximă)\n"
            f"- Q9-10: Termodinamică avansată sau Mecanică avansată\n\n"
            f"REGULI: g=10 m/s², R=8.32 J/(mol·K), valori rotunde\n\n"
            f"NIVEL DE DIFICULTATE — {_niv_lbl.upper()}:\n{_dif_g}\n\n"
            f"La final:\n"
            f"[[BAREM]]1-[lit], 2-[lit], 3-[lit], 4-[lit], 5-[lit], "
            f"6-[lit], 7-[lit], 8-[lit], 9-[lit], 10-[lit][[/BAREM]]"
        )

    # ── FMI / UPB ACS — Matematică clasic ──
    elif "matematica" in proba_cod and proba_info.get("tip") == "clasic":
        is_fmi = "fmi" in proba_cod
        nr_probleme = 3 if is_fmi else 4
        puncte_pp   = 30 if is_fmi else 25
        return (
            f"Generează un subiect COMPLET de ADMITERE la {univ_scurt} — {spec_scurt}, "
            f"proba Matematică.\n\n"
            f"STRUCTURĂ OBLIGATORIE:\n"
            f"- {nr_probleme} probleme, fiecare {puncte_pp} puncte\n"
            f"- Fiecare problemă are 3-4 subpuncte (a, b, c, d)\n"
            f"- 10 puncte din oficiu → total 100 puncte\n"
            f"- Timp: 3 ore\n\n"
            f"TEME OBLIGATORII (distribuite între probleme):\n"
            f"  Problemă 1: Algebră — matrice, determinanți, sisteme liniare sau legi de compoziție\n"
            f"  Problemă 2: Algebră — polinoame, numere complexe, combinatorică sau progresii\n"
            f"  Problemă {nr_probleme-1}: Analiză — limite, continuitate, derivabilitate, extreme, monotonie\n"
            f"  Problemă {nr_probleme}: Analiză — integrale, arii, volume de rotație, șiruri convergente\n\n"
            f"NIVEL DE DIFICULTATE — {_niv_lbl.upper()}:\n{_dif_c}\n\n"
            f"[[BAREM]]\n"
            + "\n".join(f"Problema {i+1}: [soluție completă pas cu pas + punctaj per subpunct]" for i in range(nr_probleme))
            + "\n[[/BAREM]]"
        )

    # ── FMI / UPB ACS — Informatică grilă (30 întrebări × 4 variante) ──
    elif "informatica" in proba_cod and proba_info.get("tip") == "grila" and "etti" not in proba_cod:
        nr_q = proba_info.get("nr_intrebari", 30)
        return (
            f"Generează un CHESTIONAR DE CONCURS pentru admitere {univ_scurt} — {spec_scurt}, "
            f"proba Informatică.\n\n"
            f"STRUCTURĂ OBLIGATORIE:\n"
            f"- {nr_q} întrebări numerotate 1-{nr_q}\n"
            f"- Fiecare întrebare: enunț + 4 variante (a, b, c, d); o singură variantă corectă\n"
            f"- Fiecare întrebare valorează {90//nr_q if nr_q else 3} puncte; 10p din oficiu → 100p\n"
            f"- Timp: 3 ore\n\n"
            f"DISTRIBUȚIE TEME:\n"
            f"- Q1-8: Algoritmi și complexitate — căutare, sortare, O(n), recursivitate\n"
            f"- Q9-15: Structuri de date — stivă, coadă, liste înlănțuite, arbori, grafuri\n"
            f"- Q16-22: Programare în C/C++ — pointeri, alocare dinamică, OOP, STL\n"
            f"- Q23-{nr_q}: Probleme aplicative — parsing, simulare, algoritmi pe grafuri\n\n"
            f"NIVEL DE DIFICULTATE — {_niv_lbl.upper()}:\n{_dif_g}\n\n"
            f"La final, pe o linie separată:\n"
            f"[[BAREM]]"
            + ", ".join(f"{i+1}-[lit]" for i in range(nr_q))
            + "[[/BAREM]]"
        )

    # ── Fallback generic ──
    else:
        tip  = proba_info.get("tip", "clasic")
        timp = proba_info.get("timp_minute", 120)
        desc = proba_info.get("descriere", "")
        struct = proba_info.get("structura", "")
        return (
            f"Generează un test de admitere pentru {univ_scurt} — {spec_scurt}, "
            f"proba {proba_info.get('label', proba_cod)}.\n\n"
            f"Descriere: {desc}\n"
            f"Structură: {struct}\n"
            f"Timp: {timp} minute\n\n"
            f"NIVEL: {_niv_lbl}\n"
            + (_dif_g if tip == "grila" else _dif_c)
            + "\n\n[[BAREM]]\n[Răspunsurile corecte]\n[[/BAREM]]"
        )
