"""
modules/bac/base.py — Date BAC reale 2021-2025, configurații materii, funcții de prompt.

Exportă:
  MATERII_BAC          — configurația tuturor materiilor simulabile
  MATERII_SIMULARE_DISPONIBILE — lista materiilor cu suport AI
  PROFILE_BAC          — ierarhia filiere → profil → specializare → materii
  BAC_DATE_REALE       — subiecte și tipare reale BAC 2021-2025
  get_bac_prompt_ai()  — construiește promptul pentru generarea unui subiect
  get_bac_correction_prompt() — promptul pentru corectarea unui răspuns
  parse_bac_subject()  — parsează răspunsul AI în subiect + barem
  format_timer()       — formatează secunde ca HH:MM:SS
"""
import random
import re


# ══════════════════════════════════════════════════════════════════
# CONFIGURAȚIE MATERII BAC
# ══════════════════════════════════════════════════════════════════

MATERII_BAC = {
    "📐 Matematică M1": {
        "cod": "matematica_m1",
        "profile": ["M1 - Mate-Info"],
        "subiecte": ["Numere complexe", "Funcții", "Ecuații/inecuații", "Probabilități",
                     "Geometrie analitică", "Matrice și sisteme", "Legi de compoziție",
                     "Derivate și monotonie", "Integrale și limite"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "6 exerciții scurte × 5p = 30p",
            "S2": "2 probleme (matrice+sisteme, lege compoziție) = 30p",
            "S3": "2 probleme (funcții+derivate, integrale/limite) = 30p",
        },
    },
    "📐 Matematică M2": {
        "cod": "matematica_m2",
        "profile": ["M2 - Științe ale naturii"],
        "subiecte": ["Funcții", "Ecuații/inecuații", "Probabilități", "Geometrie",
                     "Derivate", "Integrale"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "6 exerciții scurte × 5p = 30p",
            "S2": "2 probleme (matrice+sisteme sau geometrie, funcții) = 30p",
            "S3": "2 probleme (derivate+monotonie, integrale/arii) = 30p",
        },
    },
    "🔬 Fizică real": {
        "cod": "fizica_real",
        "profile": ["Matematică-Informatică", "Științe ale naturii"],
        "subiecte": ["Mecanică", "Termodinamică", "Electromagnetism", "Optică", "Fizică modernă"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "10 itemi grilă × 3p = 30p",
            "S2": "Probleme structurate (mecanică + termodinamică) = 30p",
            "S3": "Problemă complexă (electromagnetism/optică/fizică modernă) = 30p",
        },
    },
    "⚡ Fizică tehnolog": {
        "cod": "fizica_tehnologic",
        "profile": ["Filiera tehnologică"],
        "subiecte": ["Mecanică", "Termodinamică", "Curent continuu", "Optică"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "arii": "4 arii (A-Mecanică, B-Termodinamică, C-Curent continuu, D-Optică)",
            "alegere": "Candidatul alege 2 arii din 4",
            "per_arie": "S.I (5 grilă × 3p) + S.II (problemă 15p) + S.III (problemă 15p)",
        },
    },
    "🧪 Chimie": {
        "cod": "chimie",
        "profile": ["Chimie anorganică", "Chimie organică"],
        "subiecte": ["Chimie anorganică", "Chimie organică"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "10 itemi grilă (30p) — noțiuni generale",
            "S2": "Probleme calcul anorganic/organic (30p)",
            "S3": "Probleme aplicative complexe (30p)",
        },
    },
    "🧬 Biologie": {
        "cod": "biologie",
        "profile": ["Biologie vegetală și animală", "Anatomie și fiziologie umană"],
        "subiecte": ["Celulă și țesuturi", "Genetică", "Fiziologie umană", "Ecologie", "Evoluție"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "10 itemi grilă (30p)",
            "S2": "Itemi semiobiectivi și eseu scurt (30p)",
            "S3": "Eseu structurat (30p)",
        },
    },
    "🏛️ Istorie": {
        "cod": "istorie",
        "profile": ["Umanist", "Pedagogic"],
        "subiecte": ["Popoare și spații istorice", "Oameni, societate, lume",
                     "Relații internaționale", "Secolul XX în România"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "Sursă primară — 4 cerințe (30p)",
            "S2": "Eseu scurt factori/cauze/consecințe (30p)",
            "S3": "Eseu structurat 2 pagini cu argumente (30p)",
        },
    },
    "🌍 Geografie": {
        "cod": "geografie",
        "profile": ["Profiluri umaniste"],
        "subiecte": ["Relief", "Climă și hidrografie", "Vegetație și faună",
                     "Populație și așezări", "Economie", "Europa și UE"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "Hartă + 5 cerințe (30p)",
            "S2": "Noțiuni geografice — definiții + exemple (30p)",
            "S3": "Eseu despre o regiune/fenomen geografic (30p)",
        },
    },
    "📖 Română real/tehn": {
        "cod": "romana_real_tehn",
        "profile": ["Real/tehnologic"],
        "subiecte": ["Text la prima vedere", "Comentariu literar", "Eseu personaj/curent"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "50p: A (5 itemi 30p) + B (text argumentativ 150+ cuvinte, 20p)",
            "S2": "10p: comentariu 50+ cuvinte pe fragment literar",
            "S3": "30p: eseu 400+ cuvinte (personaj/text narativ/curent literar)",
        },
    },
    "📖 Română uman/ped": {
        "cod": "romana_uman",
        "profile": ["Umanist", "Pedagogic"],
        "subiecte": ["Text la prima vedere", "Comentariu literar", "Eseu personaj/curent"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "50p: A (5 itemi 30p) + B (text argumentativ 150+ cuvinte, 20p)",
            "S2": "10p: comentariu 50+ cuvinte pe fragment literar",
            "S3": "30p: eseu 400+ cuvinte (personaj/text narativ/curent literar)",
        },
    },
    "💻 Informatică": {
        "cod": "informatica",
        "profile": ["C++", "Pascal"],
        "subiecte": ["Algoritmi", "Structuri de date", "Programare completă"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": True,
        "structura": {
            "S1": "Algoritmi și pseudocod (30p)",
            "S2": "Probleme cu tablouri/șiruri (30p)",
            "S3": "Problemă complexă de programare (30p)",
        },
    },
    "⚖️ Economie": {
        "cod": "economie",
        "profile": ["Economic", "Științe sociale"],
        "subiecte": ["Piața și mecanismele ei", "Agenții economici", "Macroeconomie", "Economie mondială"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": False,
    },
    "🧠 Psihologie": {
        "cod": "psihologie",
        "profile": ["Umanist"],
        "subiecte": ["Procese psihice", "Personalitate", "Psihologie socială"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": False,
    },
    "📐 Logică": {
        "cod": "logica",
        "profile": ["Umanist"],
        "subiecte": ["Propoziții logice", "Inferențe", "Argumentare"],
        "timp_minute": 180,
        "punctaj_total": 100,
        "date_reale": False,
    },
}

MATERII_SIMULARE_DISPONIBILE = list(MATERII_BAC.keys())


# ══════════════════════════════════════════════════════════════════
# PROFILE BAC — ierarhie completă filiere/profiluri/specializări
# ══════════════════════════════════════════════════════════════════

PROFILE_BAC = {
    "🏫 Filiera teoretică": {
        "📐 Profilul real": {
            "Matematică-Informatică": {
                "descriere": "Matematică M1 (obligatorie) + Informatică sau Fizică",
                "materii_obligatorii": ["📐 Matematică M1", "📖 Română real/tehn"],
                "materii_optionale": ["🔬 Fizică real", "💻 Informatică"],
            },
            "Științe ale naturii": {
                "descriere": "Matematică M2 (obligatorie) + Fizică/Chimie/Biologie",
                "materii_obligatorii": ["📐 Matematică M2", "📖 Română real/tehn"],
                "materii_optionale": ["🔬 Fizică real", "🧪 Chimie", "🧬 Biologie"],
            },
        },
        "📚 Profilul umanist": {
            "Filologie": {
                "descriere": "Română (obligatorie) + Istorie/Geografie/Psihologie/Logică",
                "materii_obligatorii": ["📖 Română uman/ped"],
                "materii_optionale": ["🏛️ Istorie", "🌍 Geografie", "🧠 Psihologie", "📐 Logică"],
            },
            "Științe sociale": {
                "descriere": "Română + Economie/Sociologie/Psihologie",
                "materii_obligatorii": ["📖 Română uman/ped"],
                "materii_optionale": ["⚖️ Economie", "🧠 Psihologie", "🏛️ Istorie"],
            },
        },
    },
    "🏭 Filiera tehnologică": {
        "⚙️ Profil tehnic": {
            "Tehnician": {
                "descriere": "Română + Matematică M2 + Fizică tehnologică",
                "materii_obligatorii": ["📖 Română real/tehn", "📐 Matematică M2"],
                "materii_optionale": ["⚡ Fizică tehnolog"],
            },
        },
        "🌾 Profil resurse naturale și protecția mediului": {
            "Tehnician în agricultură": {
                "descriere": "Română + Matematică M2 + Chimie/Biologie",
                "materii_obligatorii": ["📖 Română real/tehn"],
                "materii_optionale": ["🧪 Chimie", "🧬 Biologie", "📐 Matematică M2"],
            },
        },
        "💼 Profil servicii": {
            "Tehnician în turism / comerț": {
                "descriere": "Română + Matematică M2 + Economie",
                "materii_obligatorii": ["📖 Română real/tehn"],
                "materii_optionale": ["⚖️ Economie", "📐 Matematică M2"],
            },
        },
    },
    "🎨 Filiera vocațională": {
        "🎭 Profil artistic": {
            "Arte vizuale / Muzică / Coregrafie": {
                "descriere": "Română + Matematică M2 + materie de specialitate",
                "materii_obligatorii": ["📖 Română uman/ped"],
                "materii_optionale": ["📐 Matematică M2", "🏛️ Istorie"],
            },
        },
        "⛪ Profil teologic": {
            "Teologie ortodoxă / catolică": {
                "descriere": "Română + Religie + materie de specialitate",
                "materii_obligatorii": ["📖 Română uman/ped"],
                "materii_optionale": ["🏛️ Istorie", "📐 Logică"],
            },
        },
        "🏅 Profil sportiv": {
            "Educație fizică și sport": {
                "descriere": "Română + Matematică + Biologie",
                "materii_obligatorii": ["📖 Română real/tehn"],
                "materii_optionale": ["🧬 Biologie", "📐 Matematică M2"],
            },
        },
        "🎖️ Profil militar": {
            "Liceu militar": {
                "descriere": "Română + Matematică M1 + Fizică real",
                "materii_obligatorii": ["📖 Română real/tehn", "📐 Matematică M1"],
                "materii_optionale": ["🔬 Fizică real"],
            },
        },
        "🧑‍🏫 Profil pedagogic": {
            "Pedagogic": {
                "descriere": "Română + Matematică M2 + Psihologie",
                "materii_obligatorii": ["📖 Română uman/ped"],
                "materii_optionale": ["🧠 Psihologie", "📐 Matematică M2", "📐 Logică"],
            },
        },
    },
}


# ══════════════════════════════════════════════════════════════════
# DATE REALE BAC 2021-2025
# ══════════════════════════════════════════════════════════════════

BAC_DATE_REALE = {
    "matematica_m1": {
        "tipare": [
            "Numere complexe: forma algebrică, modul, argument, operații",
            "Matrice și determinanți: rangul, inversa, sisteme Cramer",
            "Legi de compoziție: element neutru, simetrizabil, ecuații",
            "Funcții: domeniu, monotonie, valori extreme, grafic",
            "Ecuații/inecuații exponențiale și logaritmice cu parametru",
            "Probabilități: combinatorică, repartizare Bernoulli",
            "Geometrie analitică: drepte, distanțe, cercuri",
            "Derivate: f'(x), monotonie, extreme, tangentă, convexitate",
            "Integrale definite: calcul, arie, volum de rotație",
            "Limite: forme nedeterminate, L'Hôpital, șiruri",
        ],
        "subiecte_reale": [
            {"an": 2021, "s1": "Complex z=2-i, z²+|z|²; Matrice inversabilă A; Progresie geometrică q=2; Ecuație log₂(x+1)+log₂(3-x)=2; Probabilitate C(6,2)/C(8,2); Geometrie: distanță punct-dreaptă", "s2": "Matricea A=[1,1;0,1]: A²,A³,Aⁿ, sistem; Lege x*y=xy-x-y+6: proprietăți, ecuație x*x=3x", "s3": "f(x)=(x²-1)/(x+1): discontinuitate, continuare, monotonie, grafic, arie | Integrală ∫₀¹ xe^x dx, șir Iₙ=∫₀¹ xⁿeˣdx"},
            {"an": 2022, "s1": "Complex z=1+i√3: argument, putere z⁶; Sistem Cramer cu parametru; Funcție f(x)=x³-3x; Ecuație |log₃x|=2; P(X=3) binomială; Dreaptă prin 2 puncte, unghi cu Ox", "s2": "A=[2,1;1,1]: A⁻¹, sistem, B matrice; Lege x*y=3xy-3x-3y+4: asociativitate, element neutru, simetrizabil", "s3": "f(x)=ln(x²+1): f', extreme, convexitate, asimptote, grafic, arie | Integrală ∫₁ᵉ lnx dx, volum rotație"},
            {"an": 2023, "s1": "z=(1+i)/(1-i): forma algebrică; Determinant 3×3; Ec. 9ˣ-4·3ˣ+3=0; Progresie aritmetic cu condiție; P(cel puțin 2 din 5); Tangentă la cerc", "s2": "Matrice cu parametru: rangul, sistem nedeterminat; Lege x*y=2x+2y-xy-2: tabelul, ecuație", "s3": "f(x)=(x-1)eˣ: f', extreme, inflexiune, asimptotă oblică, grafic | Integrală ∫₀¹(x+1)eˣdx, arie"},
            {"an": 2024, "s1": "Complex z: |z-2|=|z+2i| locul geometric; Matrice: trace, det; Funcție fracționară cu asimptote; Ecuație 4ˣ-5·2ˣ+4=0; Combinatorică bilet 3 cifre; Cerc tangent la dreaptă", "s2": "Matrice A³=I: relație; Lege x*y=x+y-xy/2 pe (−∞,2): element neutru, simetrizabil, injecție", "s3": "f(x)=x²·e^(−x): f', extreme, inflexiune, limite, grafic, arie | Volum rotație în jurul Ox"},
            {"an": 2025, "s1": "z=a+bi cu z²=5-12i; Sistem incompatibil cu parametru; Ecuație log₂(x+1)=3-x grafic; ec. exponențiale 25ˣ-6·5ˣ+5=0; Probabilitate hipergeometrică; Punct la distanță d de dreaptă", "s2": "A=[0,1;-1,0]: A^2024; Lege a*b=2ab-a-b+1 pe (½,+∞): proprietăți, ec. iterată x*x*x=81", "s3": "f(x)=x·ln(x+1): f', extreme, inflexiune, asimptotă oblică, grafic, arie | Integrală cu parametru m"},
        ],
    },
    "matematica_m2": {
        "tipare": [
            "Funcții: domeniu, monotonie, grafic, f(x)=a soluție unică",
            "Ecuații/inecuații exponențiale sau logaritmice cu parametru",
            "Probabilități: combinatorică, evenimente independente, Bernoulli",
            "Geometrie analitică: drepte, distanțe, cercuri, tangente",
            "Derivate: calcul f'(x), extreme, monotonie, tangentă la grafic",
            "Integrale definite: calcul, arie, volum de rotație",
            "Șiruri: recurență, convergență, limită",
            "Trigonometrie: ecuații, identități, funcții trigonometrice",
        ],
        "subiecte_reale": [
            {"an": 2022, "s1": "f(x)=2x-1, f(f(3)); 4ˣ-5·2ˣ+4=0; Probabilitate bile; Distanță punct-dreaptă; f(x)=xeˣ extreme; ∫₀¹(2x+1)dx", "s2": "f(x)=x³-3x+2: monotonie, extreme, grafic | Geometrie: cerc, tangente", "s3": "f(x)=ln(x²+1): asimptote, f', arie | Integrală cu parametru"},
            {"an": 2023, "s1": "Progresie geometrică cu parametru; log₂(x+1)+log₂(x+3)=3; Combinatorică; Dreaptă prin 2 puncte; f(x)=(x²+1)/(x-1); ∫₁²(3x²-2x)dx", "s2": "f(x)=x·eˣ: monotonie, extreme, tangentă | Sistem parametru, discuție", "s3": "f(x)=x²-2lnx: f', extreme, asimptote, arie | Integrală improprie"},
            {"an": 2024, "s1": "f(f(x))=2x+3; 9ˣ-4·3ˣ-5=0; P(3 din 5, p=½); Mijlocul segmentului; f(x)=sin²x-2sinx; ∫₀^(π/2)cosxdx", "s2": "f(x)=x³-6x²+9x: monotonie, grafic, inegalitate | Matrice 2×2", "s3": "f(x)=(x+1)·e^(-x): f', extreme, inflexiune, arie | Șir recursiv"},
            {"an": 2025, "s1": "Șir aritmetic r=2, a₁=3; log₃(2x-1)=log₃(x+2); P(≥2 din 4, p=⅓); Distanță A(2,3) la x-y+1=0; f(x)=xlnx: f'(e); ∫₁^e(1/x)dx", "s2": "f(x)=x/(x²+1): asimptote, monotonie, extreme, grafic | Tangentă la y=x²-2x, paralelă cu y=x", "s3": "f(x)=2x-e^(2x): f', monotonie, concavitate | ∫₀¹f(x)dx, arie, volum"},
        ],
    },
    "fizica_real": {
        "tipare": {
            "A_mecanica": [
                "MRU și MRUV: formule, grafice, probleme cu 2-3 mărimi necunoscute",
                "Dinamică: plan înclinat, forță de frecare, legile Newton aplicate vectorial",
                "Lucru mecanic, putere, randament: calculul L, P, η pe mai mulți pași",
                "Conservarea energiei mecanice cu și fără frecare: Ec+Ep=const vs Q disipată",
                "Ciocniri: elastic și perfect plastic — conservare impuls și/sau energie",
                "Echilibru: translație (ΣF=0) și rotație (ΣM=0), centrul de greutate",
                "Mișcare circulară uniformă: MCU — viteză unghiulară, centripetă, frecvență",
                "Gravitație: câmpul gravitațional, G universal, viteze cosmice, sateliți",
                "Mecanica fluidelor: Arhimede, Bernoulli, Pascal, ecuația de continuitate",
            ],
            "B_termodinamica": [
                "Gaze ideale: ecuația de stare pV/T=const, transformările (izoterm, izobar, izocor)",
                "Calorimetrie: căldură specifică, bilanț termic Q_cedat=Q_primit",
                "Schimbări de stare: căldura latentă, curba de răcire/încălzire",
                "Principiul I termodinamică: ΔU=Q+L, sens convenție semne",
                "Motoare termice: ciclul Carnot, randament η=1−Q_rece/Q_cald",
                "Entropie — calitativ (principiul II)",
            ],
            "C_curent_continuu": [
                "Legea Ohm (globală și locală), circuite serie/paralel, rezistivitate",
                "Generatoare reale: t.e.m, rezistență internă, tensiunea la borne",
                "Legile lui Kirchhoff: nodul (I) și ochiul (II) — sisteme cu 2-3 ramuri",
                "Putere și energie electrică: P=UI, P=RI², W=Pt; efectul Joule Q=RI²t",
                "Condensatorul în curent continuu: câmp, energie, conectare serie/paralel",
                "Câmpul electric: forța Coulomb, câmpul E, potențialul V, lucrul mecanic",
                "Câmpul magnetic: forța Lorentz (conductor și sarcină), inducție B",
            ],
            "D_optica": [
                "Reflexia și refracția luminii: legea Snell, indicele de refracție",
                "Reflexia totală internă: unghiul limită, aplicații (fibra optică)",
                "Lentile subțiri: formula lentilei, mărirea laterală, tipuri de imagini",
                "Oglinzi sferice: formula oglinzii, imagini reale și virtuale",
                "Interferența luminii: Young — Δy=λD/d, franje luminoase și întunecate",
                "Difracția: rețea de difracție d·sinθ=kλ, condiții maxim/minim",
                "Dispersia luminii: prisma, spectrul vizibil, indicele de refracție vs λ",
                "Polarizarea: legea Malus I=I₀cos²θ, polarizatoare",
            ],
        },
        "subiecte_reale": [
            {"an": 2021,
             "A_mecanica": {"I_grile": ["MRU viteză medie", "Forță centripetă", "Energie cinetică", "Impuls", "Plan înclinat fără frecare"], "II_problema": "Corp pe plan înclinat cu frecare: forță, accelerație, lucru mecanic pe distanță d", "III_problema": "Ciocnire perfectă plastică + conservare energie; verificare cu Ep înainte/după"},
             "B_termodinamica": {"I_grile": ["Izotermă p1V1=p2V2", "Căldură specifică", "Schimbare stare", "Principiul I", "Randament motor"], "II_problema": "Gaz ideal: transformare izocoră apoi izobară, calcul ΔU, Q, L", "III_problema": "Motor termic Carnot, randament, Q absorbită, L util"},
             "C_curent_continuu": {"I_grile": ["Legea Ohm", "Rezistoare paralel", "Efectul Joule", "Kirchhoff nod", "Condensator energie"], "II_problema": "Circuit cu 2 generatoare și 3 rezistoare: Kirchhoff, curenți, tensiuni", "III_problema": "Câmp electric: forță Coulomb, potențial, lucru mecanic al câmpului"},
             "D_optica": {"I_grile": ["Indicele refracție", "Reflexie totală unghi limită", "Lentilă convergentă", "Interferență franje", "Difracție rețea"], "II_problema": "Lentilă: obiect real, imagine, mărire, natura imaginii (convergentă f=10cm)", "III_problema": "Interferența Young: Δy, λ, separarea fente"},
            },
            {"an": 2022,
             "A_mecanica": {"I_grile": ["MRUV accelerație", "Forță gravitațională", "Lucru mecanic", "Putere medie", "Echilibru rotație"], "II_problema": "Corp aruncat oblic: parametrii traiectoriei, înălțime max, bătaie", "III_problema": "Sistem scripete dublu: accelerație, tensiune fir, lucru mecanic"},
             "B_termodinamica": {"I_grile": ["Transformare izobară", "Căldură latentă", "Bilanț termic", "Principiul I adiabatic", "Motor termic eficiență"], "II_problema": "Gaz ideal ciclu: 1→2 izoterm, 2→3 izobar, 3→1 izocor. Calcul Q, L, ΔU pentru fiecare", "III_problema": "Calorimetrie: amestecare apă+gheață, temperatură finală, masa gheții topite"},
             "C_curent_continuu": {"I_grile": ["R serie+paralel echivalent", "Legea Ohm globală", "Putere maximă transferată", "Câmp magnetic forță", "Inducție electromagnetică"], "II_problema": "Baterie cu r internă: circuit cu R₁,R₂ în paralel; tensiune borne, curent scurtcircuit", "III_problema": "Câmp magnetic: fir conductor L în câmp B, forța, variație cu unghiul"},
             "D_optica": {"I_grile": ["Refracție Snell unghi", "Reflexie totală condiție", "Oglinzi sferice imagine", "Interferență franje distanță", "Polarizare Malus"], "II_problema": "Oglindă concavă f=15cm: obiect la 30cm, 20cm, 10cm — imagini", "III_problema": "Interferența: λ=600nm, D=1m, d=0.5mm → Δy; schimbarea λ pe același dispozitiv"},
            },
            {"an": 2023,
             "A_mecanica": {"I_grile": ["MCU viteză unghiulară", "Centripetă formulă", "Energia potențială elastică", "Teorema impulsului", "Arhimede condiție plutire"], "II_problema": "Resort + masă oscilații: T, f, ω, x(t); energia în puncte diferite", "III_problema": "Legile lui Kepler: satelit orbită circulară, viteză orbitală, perioadă"},
             "B_termodinamica": {"I_grile": ["pV=νRT calcul", "Izocor variație p", "Q=mcΔT", "L gaz expansiune izobară", "Eficiență Carnot Tₕ/Tₖ"], "II_problema": "2 gaze separate de piston mobil: echilibru termic și mecanic, presiune finală", "III_problema": "Ciclu termic pe diagramă pV: calcul L, Q, ΔU pentru fiecare ramură și total"},
             "C_curent_continuu": {"I_grile": ["Kirchhoff curenți nod", "Rezistivitate material", "Condensatoare serie energie", "Forța Lorentz sarcină", "Flux magnetic"], "II_problema": "Circuit Wheatstone: condiție echilibru, galvanometru I=0, calcul Rx", "III_problema": "Inducție electromagnetică: spira în câmp B variabil, f.e.m. indusă, curent Faraday"},
             "D_optica": {"I_grile": ["Snell sin θ₁/sin θ₂=n₂/n₁", "Lentilă divergentă imagine", "Interferență franje întunecate", "Difracție ordinul 2", "Dispersie prisma"], "II_problema": "Sistem optic: lentilă convergentă + oglinzi; construcție imagine, mărire totală", "III_problema": "Difracție rețea: d=2μm, λ=500nm, ordinele maxime posibile; schimbare unghi"},
            },
            {"an": 2024,
             "A_mecanica": {"I_grile": ["MRUV distanță parcursă", "Forță de frecare coeficient", "Conservare impuls ciocnire", "Lucru mecanic forță oblică", "Echilibru static moment"], "II_problema": "Proiectil aruncat orizontal de la înălțime h: viteză la impact, unghi, timp", "III_problema": "Mișcare circulară: șosea curbă, forța normală, viteză maximă fără derapaj"},
             "B_termodinamica": {"I_grile": ["Temperatura în Kelvin", "Transformare izocoră Q=0?", "Căldura latentă de vaporizare", "Principiul II — sens natural", "Randament pompa de căldură"], "II_problema": "Gaz ideal: ciclu triunghiular pe diagrama pV — calcul L, Q, ΔU și verificare", "III_problema": "Calorimetrie + schimbare stare: lichid adăugat în recipient cu gheață+apă"},
             "C_curent_continuu": {"I_grile": ["Grupare mixtă rezistoare", "Generator t.e.m curent max", "Condensator în CC (R bloc. după încărcare)", "Câmp B produs de fir drept", "Inducție f.e.m = BLv"], "II_problema": "Circuit complex 4 rezistoare + sursă: Kirchhoff, curenți, putere disipată", "III_problema": "Câmp electromagnetic: fir în câmp B uniform, forța, oscilație, analogie Lenz"},
             "D_optica": {"I_grile": ["Legea refracției n₁sinθ₁=n₂sinθ₂", "Reflexie totală θ>θₗ", "Lentilă: 1/f=1/do+1/di", "Young λ din Δy", "Polarizare intensitate după analizor"], "II_problema": "Microscop simplu: distanță focală, mărire unghiulară pentru ochi relaxat vs accomodat", "III_problema": "Interferența cu lame: grosimea peliculei, λ în mediu, condiție maxim/minim"},
            },
        ],
    },
    "fizica_tehnologic": {
        "tipare": {
            "mecanica": [
                "MRUV: v=v₀+at, x=v₀t+at²/2, v²=v₀²+2ax — calculul a sau distanței",
                "Dinamică: forța rezultantă, plan înclinat, frecare — ΣF=ma pe axe",
                "Lucru mecanic L=Fd·cosα, putere P=L/t, randament η",
                "Conservarea energiei: Ec+Ep=const; cu frecare: +Q disipată",
                "Ciocnire perfect inelastică: conservare impuls mv=(m+M)V",
            ],
            "termodinamica": [
                "Transformările gazelor: calcul p,V,T final cu legile specifice",
                "Calorimetrie: Q=mcΔT, bilanț termic la amestecare",
                "Căldura latentă: Q=mL la schimbare de stare",
                "Motoare termice: randament η=L/Q₁=1−Q₂/Q₁",
            ],
            "curent": [
                "Legea Ohm: U=RI, circuite serie R₁+R₂ și paralel 1/R=1/R₁+1/R₂",
                "Generator: U=ε−Ir; curent de scurtcircuit Isc=ε/r",
                "Kirchhoff pentru circuit cu 2-3 rezistoare și sursă",
                "Putere electrică P=UI=RI²=U²/R; energia W=Pt; Joule Q=RI²t",
            ],
            "optica": [
                "Reflexia: θ_i=θ_r; oglinzi plane — construcție imagine",
                "Refracția: n₁sinθ₁=n₂sinθ₂; reflexia totală unghiul limită sinθₗ=n₂/n₁",
                "Lentile: 1/f=1/d_o+1/d_i; mărire M=−d_i/d_o; convergență C=1/f (dioptrii)",
            ],
        },
        "subiecte_reale": [
            {"an": 2021, "A_mecanica": "MRUV corp pe plan orizontal: accelerație din v și d; energie cinetică finală | Corp aruncat oblic: înălțime maximă, bătaie | Ciocnire: conservare impuls, viteza după", "B_termodinamica": "Gaz ideal transformare izocoră + izobară: p,V,T final, Q, L | Calorimetrie: apă+fier, t finală", "C_curent_continuu": "Circuit serie-paralel: R_eq, curenți, tensiuni, putere | Generator cu r=1Ω: U_borne la diferite R", "D_optica": "Lentilă convergentă f=20cm: 3 poziții obiect — imagine, natură, mărire | Reflexie totală în fibra optică"},
            {"an": 2022, "A_mecanica": "Plan înclinat cu frecare μ: accelerație, viteză la baza, lucru mecanic frecare | Scripete: ecuații sistem corp1+corp2", "B_termodinamica": "Gaz ideal ciclu: izotermă+izocoră+izobară pe diagramă pV — L_total, Q_total | Motor termic: η, Q_cedată", "C_curent_continuu": "Kirchhoff: 2 surse cu rezistoare — curenți ramuri, putere sursă | Condensator C: energie, sarcina electrică Q=CU", "D_optica": "Oglinzi sferice: concavă f=10cm — imagine la d_o=15cm, 5cm | Snell: unghiul de refracție în apă (n=1.33)"},
            {"an": 2023, "A_mecanica": "MRUV frânare: distanța de oprire în funcție de v₀ și μ | Oscilație resort: T, f, energia totală, viteza în echilibru", "B_termodinamica": "Amestec gaze: presiunea finală dacă T=const | Calorimetrie + topire gheață: temperatura de echilibru", "C_curent_continuu": "Grupare mixtă: R_ech, I_total, U pe fiecare rezistor | Efectul Joule: Q generată în 1h, costul energiei electrice", "D_optica": "Microscop: lentilă obiectiv+ocular, mărire totală | Interferența Young: distanța dintre franje Δy"},
        ],
    },
    "biologie": {
        "tipare": {
            "vegetala_animala": [
                "Celula — organite, funcții, tipuri (procariote/eucariote, vegetale/animale)",
                "Diviziunea celulară — mitoza și meioza: faze, importanță, comparație",
                "Genetică mendeliană — mono/dihybridare, dominanță, codominanță, genotip/fenotip",
                "Genetica umană — grupe sanguine AB0, Rh, boli genetice, ereditate X-linked",
                "Evoluție — teorii Darwin/Lamarck, speciație, adaptare, selecție naturală",
                "Ecologie — biocenoza, biotop, lanțuri trofice, ecosisteme, ciclu carbon/azot",
            ],
            "anatomie_fiziologie": [
                "Sistemul nervos — neuronul, sinapsa, SNC+SNP, reflexul, analizatori",
                "Sistemul endocrin — glande, hormoni, mecanisme feedback, afecțiuni",
                "Sistemul circulator — inima (structură, ciclu cardiac), vase sanguine, sânge",
                "Sistemul respirator — plămâni, ventilație pulmonară, schimburi gazoase",
                "Sistemul digestiv — enzime, absorbție, organe, reglare neuroumorală",
                "Sistemul excretor — nefronul, filtrare glomerulară, reabsorbție",
                "Sistemul locomotor — oase, articulații, mușchi, contracție musculară",
                "Reproducerea — aparatul reproductor, gametogeneză, ciclul menstrual",
            ],
        },
        "subiecte_reale": [
            {"an": 2021, "profil": "Anatomie", "s1": "10 itemi grilă: neuron, sinapsa, reflex | S2: Sistemul nervos — structura neuronului, tipuri de neuroni, arcul reflex, calea motorie | S3: Eseu sistemul endocrin — hipofiza, tiroidă, suprarenale, feedback negativ, diabet"},
            {"an": 2022, "profil": "Anatomie", "s1": "10 itemi: circulație, sânge, grupe sanguine | S2: Inima — structura, ciclul cardiac, EKG, debitul cardiac | S3: Eseu sistemul respirator — ventilație, surfactant, capacitate vitală, insuficiență respiratorie"},
            {"an": 2023, "profil": "Anatomie", "s1": "10 itemi: digestie, absorbție, enzime | S2: Nefronul — filtrare, reabsorbție tubulară, compoziție urină, insuficiență renală | S3: Eseu reproducere — gametogeneză, ciclu menstrual, fertilizare, FIV"},
            {"an": 2024, "profil": "Anatomie", "s1": "10 itemi: muschi, os, articulatie | S2: Contracția musculară — teoria glisării filamentelor, ATP, Ca²⁺, oboseala musculară | S3: Eseu sistemul imunitar — imunitate nespecifică/specifică, anticorpi, limfocite T și B"},
            {"an": 2025, "profil": "Anatomie", "s1": "10 itemi: hormoni, glande endocrine | S2: Reglarea glicemiei — insulina vs glucagon, diabet tip 1 vs 2 | S3: Eseu sistem nervos vegetativ — simpatic vs parasimpatic, mediatori chimici"},
            {"an": 2023, "profil": "Vegetala", "s1": "10 itemi: celula vegetala, fotosinteza | S2: Meioza — faze, crossing-over, importanță genetică | S3: Eseu genetică — legile lui Mendel, dihybridare, grupe sanguine"},
            {"an": 2024, "profil": "Vegetala", "s1": "10 itemi: ecosisteme, populatii | S2: Lanțuri trofice — producători/consumatori, flux energetic, ciclul carbonului | S3: Eseu evoluție — teoria sintetică, speciație, dovezi paleontologice"},
        ],
    },
    "chimie": {
        "tipare": {
            "anorganica": [
                "Structura atomului — configurații electronice, periodicitate",
                "Legătura chimică — ionică, covalentă, metalică",
                "Reacții redox — oxidant/reducător, bilanț electronic",
                "Acizi și baze — pH, soluții tampon, grade de disociere",
                "Electroliză — legi Faraday, celulă electrolitică",
                "Echilibru chimic — Kc, Kp, principiul Le Chatelier",
            ],
            "organica": [
                "Hidrocarburi — alcani, alchene, alchine, arene",
                "Derivați halogenați — SN1/SN2, eliminare",
                "Alcooli, aldehide, cetone — reacții de identificare (Tollens, Fehling)",
                "Acizi carboxilici — esterificare, saponificare",
                "Amine și aminoacizi — bazicitate, proteine",
                "Glucide — mono/di/polizaharide, structură, proprietăți",
                "Polimeri — polimerizare, policondensare",
            ],
        },
        "subiecte_reale": [
            {"an": 2021, "profil": "Chimie anorganică", "s1": "10 grilă: config. electronică, periodicitate, legătură ionică | S2: Echilibru chimic Kc pentru N₂+3H₂⇌2NH₃, Le Chatelier, conversia | S3: Electroliză CuSO₄ — masa la catod, volumul O₂ la anod"},
            {"an": 2022, "profil": "Chimie anorganică", "s1": "10 grilă: redox, nr oxidare, balansare | S2: Acizi și baze — pH HCl 0.1M, tampon CH₃COOH/CH₃COONa | S3: Coroziunea metalelor — pile galvanice, protecție catodică"},
            {"an": 2023, "profil": "Chimie anorganică", "s1": "10 grilă: cinetica, viteza, cataliza | S2: Kps AgCl, efect ion comun, precipitare selectivă | S3: Sinteza amoniacului Haber — echilibru, randament, moli"},
            {"an": 2021, "profil": "Chimie organică", "s1": "10 grilă: hidrocarburi, izomeri, IUPAC | S2: Alcooli — reacție Na, oxidare etanol, deshidratare | S3: Esteri — esterificare, Ke, saponificarea grăsimilor"},
            {"an": 2022, "profil": "Chimie organică", "s1": "10 grilă: aldehide, cetone | S2: Aminoacizi — reacții, legătura peptidică, structura glicilalaninei | S3: Polimeri — polietilenă (addiție), Nylon (condensare)"},
            {"an": 2023, "profil": "Chimie organică", "s1": "10 grilă: acizi carboxilici | S2: Glucide — glucoza (Haworth, Tollens, fermentatie), zaharoza | S3: Benzena și derivați — nitrare, sulfonare, SEAr"},
        ],
    },
    "istorie": {
        "tipare": {
            "cerinte_sursa": [
                "1. Numiți o informație din sursa X (răspuns direct din text)",
                "2. Precizați secolul/perioada la care se referă sursa",
                "3. Menționați două acțiuni/măsuri/caracteristici prezentate în surse",
                "4. Prezentați un punct de vedere din sursă și argumentați cu o informație exterioară",
            ],
            "teme_frecvente": [
                "Autonomiile locale și instituțiile centrale medievale",
                "Cruciada a IV-a și consecințele pentru spațiul românesc (1204)",
                "Întemeierea Țării Românești și Moldovei (sec. XIV)",
                "Mircea cel Bătrân, Iancu de Hunedoara, Ștefan cel Mare — relații cu Imperiul Otoman",
                "Revoluția de la 1848 în Principatele Române",
                "Unirea Principatelor (1859) — context, rolul lui Cuza, reformele",
                "Primul Război Mondial — România (1916-1918), Marea Unire (1918)",
                "Al Doilea Război Mondial — România: 1939-1944, 23 august 1944",
                "Regimul comunist în România — instaurare, Dej, Ceaușescu, rezistență",
                "Revoluția din 1989 și tranziția democratică",
            ],
            "structura_eseu": [
                "Introducere: context temporal și spațial (2-3 rânduri)",
                "Argument 1: cauze/premise + exemplu concret din surse sau cunoștințe",
                "Argument 2: desfășurare/actori principali + consecințe imediate",
                "Concluzie: importanța evenimentului în context mai larg (2-3 rânduri)",
            ],
        },
        "subiecte_reale": [
            {"an": 2021, "s1": "Surse despre autonomii locale sec. XIV | S2: Rolul lui Mircea cel Bătrân față de expansiunea otomană | S3: Eseu: Revoluția de la 1848 — cauze, desfășurare, actori, consecințe"},
            {"an": 2022, "s1": "Surse despre Unirea Principatelor (1859) | S2: România în Primul Război Mondial — intrarea, campania, Marea Unire | S3: Eseu: Regimul comunist — instaurarea, represiunea, Securitatea"},
            {"an": 2023, "s1": "Surse despre Alexandru cel Bun și Iancu de Hunedoara | S2: Revoluția din 1989 — cauze, desfășurare, tranziția | S3: Eseu: România în al Doilea Război Mondial — cedările teritoriale, 23 august 1944"},
            {"an": 2024, "s1": "Surse despre formarea statelor medievale românești | S2: Reformele lui Al. I. Cuza (1859-1866) | S3: Eseu: Participarea României la Primul Război Mondial și Marea Unire"},
            {"an": 2025, "s1": "Surse despre democrația ateniană vs republica romană | S2: Nicolae Ceaușescu — cultul personalității, politica externă, criza economică | S3: Eseu: Constituirea României moderne în sec. XIX"},
        ],
    },
    "geografie": {
        "tipare": {
            "harta": [
                "Identificarea pe hartă a formelor de relief (munți, câmpii, dealuri, podișuri)",
                "Recunoașterea râurilor, lacurilor, regiunilor geografice",
                "Localizarea orașelor, județelor, regiunilor de dezvoltare",
            ],
            "teme_frecvente": [
                "Relieful României — Carpații, Subcarpații, Podișuri, Câmpii, Delta Dunării",
                "Clima României — factori genetici, tipuri climatice, temperatura/precipitații",
                "Hidrografia — bazinele hidrografice, Dunărea, fluvii, lacuri",
                "Vegetația și fauna — etajarea vegetației, zone protejate",
                "Populația — evoluție, structură, mișcarea naturală și migratorie",
                "Agricultura, industria, transporturile, turismul",
                "Uniunea Europeană — instituții, extindere, politici, fonduri structurale",
                "Europa — regiuni geografice, mari fluvii, caracteristici climatice",
            ],
            "structura_eseu": [
                "Definiție/caracterizare generală a fenomenului/regiunii",
                "Localizare și răspândire spațială (cu exemple concrete)",
                "Cauze/factori determinanți (naturali și/sau umani)",
                "Consecințe și importanță economico-socială",
            ],
        },
        "subiecte_reale": [
            {"an": 2021, "s1": "Hartă România fizică — Munții Apuseni, Câmpia Bărăganului, Mureș, Lacul Bicaz | S2: Clima României — factori genetici, temperatura, precipitații, inversii de temperatură | S3: Eseu: Dunărea — izvor, afluenți, sectoare, Delta, importanța economică"},
            {"an": 2022, "s1": "Hartă — județe din Muntenia și Moldova, orașe, drumuri europene | S2: Populația României — evoluție, bilanț natural negativ, emigrație, structura pe etnii | S3: Eseu: Agricultura românească — resurse, culturi, regiuni, probleme, politica agricolă"},
            {"an": 2023, "s1": "Hartă Europa — state, capitale, mări, Alpi, Pirinei | S2: Relieful României — Carpații, Subcarpații | S3: Eseu: Industria românească după 1990 — ramuri competitive, centre industriale"},
            {"an": 2024, "s1": "Hartă Romania — hidrografie, bazine hidrografice | S2: Transporturile în România — rețele rutiere, feroviare, Dunăre, aeroporturi | S3: Eseu: Turismul în România — resurse, stațiuni, probleme"},
            {"an": 2025, "s1": "Hartă UE — state membre, candidate, instituții | S2: Vegetația și solurile României — etajarea vegetației, zone protejate | S3: Eseu: Uniunea Europeană — etapele extinderii, instituțiile, politici, aderarea României"},
        ],
    },
    "romana_real_tehn": {
        "tipare_s1_itemi": [
            "1. Indică sensul din text al cuvântului X și al secvenței Y",
            "2. Menționează o caracteristică/profesie/calitate a personajului X, valorificând textul",
            "3. Precizează momentul/reacția/trăsătura morală + justifică cu o secvență din text",
            "4. Explică motivul pentru care... / reprezintă un eveniment / are loc situația X",
            "5. Prezintă în 30-50 cuvinte atmosfera/atitudinea/o situație conform textului",
        ],
        "teme_argumentativ": [
            "importanța lecturii / culturii generale",
            "rolul școlii / al educației în societatea contemporană",
            "influența tehnologiei / rețelelor sociale asupra tinerilor",
            "necesitatea voluntariatului și a implicării civice",
            "valoarea prieteniei și a relațiilor autentice",
        ],
        "tipare_s2": [
            "Precizează rolul notațiilor autorului în textul dramatic dat",
            "Prezintă perspectiva narativă din fragmentul dat (min. 50 cuvinte)",
            "Comentează relația dintre o idee poetică și mijloacele artistice utilizate",
        ],
        "repere_s3": [
            "1. Prezentarea statutului social, psihologic, moral al personajului ales",
            "2. Evidențierea unei trăsături prin două episoade sau secvențe comentate",
            "3. Analiza a două elemente de structură/compoziție/limbaj",
            "4. Exprimarea unui punct de vedere argumentat despre semnificația personajului",
        ],
        "autori_opere": [
            "Mihai Eminescu — Luceafărul, Floare albastră, Scrisoarea I",
            "Tudor Arghezi — Testament, Flori de mucigai",
            "Lucian Blaga — Eu nu strivesc corola de minuni a lumii",
            "Liviu Rebreanu — Ion, Pădurea spânzuraților",
            "George Călinescu — Enigma Otiliei",
            "Camil Petrescu — Ultima noapte de dragoste...",
            "Marin Preda — Moromeții",
            "I.L. Caragiale — O scrisoare pierdută",
            "Ioan Slavici — Moara cu noroc",
            "Ion Creangă — Amintiri din copilărie",
        ],
        "subiecte_reale": [
            {"an": 2021, "s1_text": "Text la prima vedere", "s2": "Comentariu relație idee poetică — mijloace artistice", "s3": "Eseu personaj dintr-un text narativ studiat"},
            {"an": 2022, "s1_text": "Fragment publicistic", "s2": "Rolul notațiilor autorului în fragment dramatic", "s3": "Eseu personaj dintr-o nuvelă/roman din literatura română"},
            {"an": 2023, "s1_text": "Text la prima vedere — 5 întrebări standard", "s2": "Perspectiva narativă din fragmentul dat", "s3": "Eseu 400+ cuvinte personaj dintr-o nuvelă/roman"},
            {"an": 2024, "s1_text": "Fragment memorialistic", "s2": "Perspectiva narativă în min. 50 cuvinte", "s3": "Eseu 400+ cuvinte personaj dintr-un text dramatic/narativ"},
            {"an": 2025, "s1_text": "Fragment despre profesor", "s2": "Rolul notațiilor autorului în fragment dramatic", "s3": "Eseu min. 400 cuvinte: particularitățile de construcție ale unui personaj"},
        ],
    },
    "romana_uman": {
        "tipare_s1_itemi": [
            "1. Indică sensul din text al cuvântului X și al secvenței Y",
            "2. Menționează o caracteristică/profesie/calitate a personajului X",
            "3. Precizează momentul/reacția/trăsătura morală + justifică cu secvență din text",
            "4. Explică motivul pentru care...",
            "5. Prezintă în 30-50 cuvinte atmosfera/atitudinea/o situație conform textului",
        ],
        "teme_argumentativ": [
            "importanța lecturii / culturii generale",
            "rolul școlii / al educației",
            "influența tehnologiei asupra tinerilor",
            "valoarea prieteniei",
            "importanța cunoașterii istoriei și identității naționale",
        ],
        "tipare_s2": [
            "Prezentarea rolului notațiilor autorului în fragment dramatic",
            "Comentariu relație idee poetică — mijloace artistice",
            "Perspectiva narativă în fragmentul dat",
        ],
        "repere_s3": [
            "1. Prezentarea statutului social, psihologic, moral al personajului ales",
            "2. Evidențierea unei trăsături prin două episoade sau secvențe comentate",
            "3. Analiza a două elemente de structură/compoziție/limbaj",
            "4. Exprimarea unui punct de vedere argumentat",
        ],
        "autori_opere": [
            "Mihai Eminescu — Luceafărul, Floare albastră, Scrisoarea I, Odă (în metru antic)",
            "Tudor Arghezi — Testament, Flori de mucigai, Psalm",
            "Lucian Blaga — Eu nu strivesc corola de minuni a lumii, Izvorul nopții",
            "Ion Barbu — Riga Crypto și Lapona Enigel, Joc secund",
            "Nichita Stănescu — Leoaică tânără, iubirea",
            "Ioan Slavici — Moara cu noroc",
            "Liviu Rebreanu — Ion, Pădurea spânzuraților",
            "Mihail Sadoveanu — Baltagul",
            "George Călinescu — Enigma Otiliei",
            "Camil Petrescu — Ultima noapte de dragoste...",
            "Marin Preda — Moromeții",
            "I.L. Caragiale — O scrisoare pierdută",
        ],
        "subiecte_reale": [
            {"an": 2022, "s1_text": "Text despre critici literari", "s2": "Rolul notațiilor autorului în fragment dramatic", "s3": "Eseu personaj dintr-un basm cult"},
            {"an": 2023, "s1_text": "Text la prima vedere", "s2": "Comentariu relație idee poetică", "s3": "Eseu 400+ cuvinte personaj dintr-o nuvelă/roman"},
            {"an": 2024, "s1_text": "Fragment memorialistic despre Sadoveanu", "s2": "Perspectiva narativă din fragmentul dat", "s3": "Eseu 400+ cuvinte personaj dintr-un text dramatic/narativ"},
            {"an": 2025, "s1_text": "Fragment despre profesorul Vasile Pârvan", "s2": "Rolul notațiilor autorului în fragment din G.M. Zamfirescu", "s3": "Eseu min. 400 cuvinte: particularitățile de construcție ale unui personaj din Creangă sau Slavici"},
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def format_timer(seconds_remaining: int) -> str:
    """Formatează secunde ca HH:MM:SS."""
    h = seconds_remaining // 3600
    m = (seconds_remaining % 3600) // 60
    s = seconds_remaining % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_bac_subject(response: str) -> tuple[str, str]:
    """Parsează răspunsul AI în (subiect, barem).
    Caută delimitatorii [[BAREM_BAC]]...[[/BAREM_BAC]] sau fallback la secțiune 'Barem'.
    """
    barem = ""
    subject_text = response

    match = re.search(r"\[\[BAREM_BAC\]\](.*?)\[\[/BAREM_BAC\]\]", response, re.DOTALL)
    if match:
        barem = match.group(1).strip()
        subject_text = response[:match.start()].strip()
    else:
        barem_match = re.search(
            r'\n(?:##\s*)?(?:BAREM|Barem|barem)[:\s]+(.*)',
            response, re.DOTALL | re.IGNORECASE
        )
        if barem_match:
            barem = barem_match.group(1).strip()
            subject_text = response[:barem_match.start()].strip()

    return subject_text, barem


# ══════════════════════════════════════════════════════════════════
# PROMPT GENERATION
# ══════════════════════════════════════════════════════════════════

def get_bac_prompt_ai(materie_label: str, materie_info: dict, profil: str) -> str:
    """Construiește promptul AI pentru generarea unui subiect BAC complet."""
    cod = materie_info.get("cod", "")

    # ── Matematică M1 ──
    if cod == "matematica_m1":
        data    = BAC_DATE_REALE["matematica_m1"]
        ref     = random.choice(data["subiecte_reale"])
        tipare_str = "\n".join(f"  - {t}" for t in data["tipare"])
        return (
            f"Generează un subiect COMPLET de BAC la Matematică M1 (Matematică-Informatică), "
            f"IDENTIC ca structură și dificultate cu subiectele oficiale române din 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ (obligatorie):\n"
            f"SUBIECTUL I (30 puncte) — 6 exerciții × 5p:\n"
            f"  Tipare reale:\n{tipare_str}\n\n"
            f"SUBIECTUL al II-lea (30 puncte) — 2 probleme structurate:\n"
            f"  Problema 1: matrice și determinanți (A inversabilă, sistem Cramer, proprietăți)\n"
            f"  Problema 2: lege de compoziție (element neutru, simetrizabil, ecuații)\n\n"
            f"SUBIECTUL al III-lea (30 puncte) — 2 probleme structurate:\n"
            f"  Problema 1: funcții — f', extreme, monotonie, tangentă, tabel de variație\n"
            f"  Problema 2: integrale — calcul, arie delimitată de axe/curbe, volum de rotație\n\n"
            f"REFERINȚĂ (subiect real {ref['an']}):\n"
            f"  S.I: {ref['s1']}\n  S.II: {ref['s2']}\n  S.III: {ref['s3']}\n\n"
            f"Folosește valori numerice DIFERITE față de referință.\n"
            f"Dificultatea trebuie să fie realistă pentru BAC național.\n"
            f"10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\n"
            f"SUBIECTUL I: [răspunsurile corecte pentru fiecare item]\n"
            f"SUBIECTUL al II-lea: [soluțiile complete pas cu pas]\n"
            f"SUBIECTUL al III-lea: [soluțiile complete pas cu pas]\n"
            f"[[/BAREM_BAC]]"
        )

    # ── Matematică M2 ──
    elif cod == "matematica_m2":
        data = BAC_DATE_REALE["matematica_m2"]
        ref  = random.choice(data["subiecte_reale"])
        tipare_str = "\n".join(f"  - {t}" for t in data["tipare"])
        return (
            f"Generează un subiect COMPLET de BAC la Matematică M2 (Științe ale naturii), "
            f"IDENTIC ca structură și dificultate cu subiectele oficiale române din 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ (obligatorie):\n"
            f"SUBIECTUL I (30 puncte) — 6 exerciții × 5p:\n"
            f"  Tipare reale:\n{tipare_str}\n\n"
            f"SUBIECTUL al II-lea (30 puncte) — 2 probleme structurate:\n"
            f"  Problema 1: funcții, monotonie, extreme, valori\n"
            f"  Problema 2: geometrie analitică sau matrice 2×2\n\n"
            f"SUBIECTUL al III-lea (30 puncte) — 2 probleme structurate:\n"
            f"  Problema 1: derivate — f'(x), extreme, tangentă, convexitate\n"
            f"  Problema 2: integrale definite — calcul, arie, volum\n\n"
            f"REFERINȚĂ (subiect real {ref['an']}):\n"
            f"  S.I: {ref['s1']}\n  S.II: {ref['s2']}\n  S.III: {ref['s3']}\n\n"
            f"Folosește valori numerice DIFERITE față de referință. 10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri]\nSUBIECTUL al II-lea: [soluții pas cu pas]\nSUBIECTUL al III-lea: [soluții pas cu pas]\n[[/BAREM_BAC]]"
        )

    # ── Fizică real ──
    elif cod == "fizica_real":
        data = BAC_DATE_REALE["fizica_real"]
        arie1 = random.choice(["A_mecanica", "B_termodinamica"])
        arie2 = random.choice(["C_curent_continuu", "D_optica"])
        tipare1 = "\n".join(f"  - {t}" for t in data["tipare"][arie1])
        tipare2 = "\n".join(f"  - {t}" for t in data["tipare"][arie2])
        ref = random.choice(data["subiecte_reale"])
        arie1_label = {"A_mecanica": "A. Mecanică", "B_termodinamica": "B. Termodinamică"}[arie1]
        arie2_label = {"C_curent_continuu": "C. Curent continuu", "D_optica": "D. Optică"}[arie2]
        return (
            f"Generează un subiect COMPLET de BAC la Fizică — profil real, "
            f"IDENTIC ca structură cu subiectele oficiale BAC România 2021-2025.\n\n"
            f"STRUCTURĂ OBLIGATORIE (2 arii tematice):\n"
            f"Generează: {arie1_label} + {arie2_label}\n\n"
            f"PENTRU FIECARE ARIE:\n"
            f"  I. 5 grile × 3p (a,b,c,d) = 15 puncte\n"
            f"  II. Problemă cu 4 cerințe (a,b,c,d) = 15 puncte\n"
            f"  III. Problemă mai complexă cu 4 cerințe = 15 puncte\n\n"
            f"TIPARE {arie1_label}:\n{tipare1}\n\n"
            f"TIPARE {arie2_label}:\n{tipare2}\n\n"
            f"REGULI: g=10m/s², NA=6.02×10²³, R=8.31 J/(mol·K), c=3×10⁸m/s\n"
            f"10 puncte din oficiu. Timp: 3 ore.\n\n"
            f"[[BAREM_BAC]]\n"
            f"{arie1_label}: I: [1-x,...,5-x] II: [soluție] III: [soluție]\n"
            f"{arie2_label}: I: [1-x,...,5-x] II: [soluție] III: [soluție]\n"
            f"[[/BAREM_BAC]]"
        )

    # ── Fizică tehnologic ──
    elif cod == "fizica_tehnologic":
        data = BAC_DATE_REALE["fizica_tehnologic"]
        arii_alese = random.sample(["A. MECANICĂ", "B. TERMODINAMICĂ", "C. CURENT CONTINUU", "D. OPTICĂ"], 2)
        tipare_mec  = "\n".join(f"    - {t}" for t in data["tipare"]["mecanica"])
        tipare_term = "\n".join(f"    - {t}" for t in data["tipare"]["termodinamica"])
        tipare_cur  = "\n".join(f"    - {t}" for t in data["tipare"]["curent"])
        tipare_opt  = "\n".join(f"    - {t}" for t in data["tipare"]["optica"])
        return (
            f"Generează un subiect COMPLET de BAC la Fizică — filiera tehnologică, "
            f"IDENTIC ca structură cu subiectele oficiale române din 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ:\n"
            f"Subiectul are 4 ARII tematice (A–D). Candidatul rezolvă DOAR 2 la alegere.\n"
            f"Generează TOATE cele 4 arii. Pentru fiecare arie:\n"
            f"  - Subiectul I (15 puncte): 5 itemi tip GRILĂ (a, b, c, d) × 3p\n"
            f"  - Subiectul II (15 puncte): problemă structurată cu 4 cerințe (a, b, c, d)\n"
            f"  - Subiectul III (15 puncte): problemă mai complexă cu 4 cerințe\n\n"
            f"TIPARE REALE:\n"
            f"A. MECANICĂ:\n{tipare_mec}\n\n"
            f"B. TERMODINAMICĂ:\n{tipare_term}\n\n"
            f"C. CURENT CONTINUU:\n{tipare_cur}\n\n"
            f"D. OPTICĂ:\n{tipare_opt}\n\n"
            f"IMPORTANT: Date numerice realiste, calcule curate. 10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\n"
            f"ARIA A: [grile + soluții]\nARIA B: [grile + soluții]\n"
            f"ARIA C: [grile + soluții]\nARIA D: [grile + soluții]\n"
            f"[[/BAREM_BAC]]"
        )

    # ── Chimie ──
    elif cod == "chimie":
        data = BAC_DATE_REALE["chimie"]
        profil_key = "anorganica" if "anorgan" in profil.lower() else "organica"
        tipare = data["tipare"][profil_key]
        ref_list = [s for s in data["subiecte_reale"] if profil.lower()[:5] in s.get("profil", "").lower()]
        ref = random.choice(ref_list) if ref_list else random.choice(data["subiecte_reale"])
        tipare_str = "\n".join(f"  - {t}" for t in tipare)
        return (
            f"Generează un subiect COMPLET de BAC la Chimie — {profil}, "
            f"IDENTIC ca structură cu subiectele oficiale BAC România 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ:\n"
            f"SUBIECTUL I (30p) — 10 itemi GRILĂ × 3p (exact 1 variantă corectă din 4)\n\n"
            f"SUBIECTUL al II-lea (30p) — probleme de calcul chimic:\n"
            f"  - Minimum 2 probleme structurate cu (a, b, c, d)\n"
            f"  - Include ecuații chimice balansate, calcule cu moli, mase, volume, concentrații\n\n"
            f"SUBIECTUL al III-lea (30p) — problemă complexă cu 4-5 cerințe legate logic\n\n"
            f"TIPARE REALE ({profil}):\n{tipare_str}\n\n"
            f"REFERINȚĂ (subiect real {ref['an']}):\n  {ref['s1']}\n\n"
            f"Date numerice realiste. 10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [1-x,...]\nSUBIECTUL al II-lea: [soluții pas cu pas cu ecuații]\nSUBIECTUL al III-lea: [soluție completă]\n[[/BAREM_BAC]]"
        )

    # ── Biologie ──
    elif cod == "biologie":
        data = BAC_DATE_REALE["biologie"]
        profil_key = "anatomie_fiziologie" if "Anatomie" in profil else "vegetala_animala"
        tipare = data["tipare"][profil_key]
        ref_list = [s for s in data["subiecte_reale"] if profil.split()[0].lower() in s.get("profil", "").lower()]
        ref = random.choice(ref_list) if ref_list else random.choice(data["subiecte_reale"])
        tipare_str = "\n".join(f"  - {t}" for t in tipare)
        return (
            f"Generează un subiect COMPLET de BAC la Biologie — {profil}, "
            f"IDENTIC ca structură cu subiectele oficiale BAC România 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ:\n"
            f"SUBIECTUL I (30p) — 10 itemi GRILĂ × 3p (a, b, c, d — exact 1 corect)\n\n"
            f"SUBIECTUL al II-lea (30p) — itemi semiobiectivi:\n"
            f"  - 2-3 cerințe tip completare/definire/comparație (10-15p)\n"
            f"  - 1 problemă de genetică sau fiziologie cu calcul (15-20p)\n\n"
            f"SUBIECTUL al III-lea (30p) — eseu structurat:\n"
            f"  - Prezintă complet un sistem/proces biologic cu: definiție, structură, funcționare, reglare, afecțiuni\n\n"
            f"TIPARE REALE ({profil}):\n{tipare_str}\n\n"
            f"REFERINȚĂ (subiect real {ref['an']}, {ref.get('profil','')}):\n  {ref['s1']}\n\n"
            f"10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [grila: 1-x, 2-x, ...]\nSUBIECTUL al II-lea: [răspunsuri + punctaj]\nSUBIECTUL al III-lea: [repere eseu + punctaj]\n[[/BAREM_BAC]]"
        )

    # ── Istorie ──
    elif cod == "istorie":
        data = BAC_DATE_REALE["istorie"]
        ref = random.choice(data["subiecte_reale"])
        teme_str    = "\n".join(f"  - {t}" for t in data["tipare"]["teme_frecvente"])
        cerinte_str = "\n".join(f"  {c}" for c in data["tipare"]["cerinte_sursa"])
        eseu_str    = "\n".join(f"  {e}" for e in data["tipare"]["structura_eseu"])
        return (
            f"Generează un subiect COMPLET de BAC la Istorie — {profil}, "
            f"IDENTIC ca structură cu subiectele oficiale BAC România 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ:\n\n"
            f"SUBIECTUL I (30p) — Analiză surse istorice:\n"
            f"  Generează 2 surse scurte (80-120 cuvinte fiecare) despre un eveniment/perioadă.\n"
            f"  Formulează EXACT 4 cerințe standard:\n{cerinte_str}\n\n"
            f"SUBIECTUL al II-lea (30p) — Eseu scurt (1 pagină):\n"
            f"  'Prezentați două cauze/consecințe/caracteristici ale [eveniment]'\n\n"
            f"SUBIECTUL al III-lea (30p) — Eseu structurat (2 pagini):\n"
            f"  Structură:\n{eseu_str}\n\n"
            f"TEME FRECVENTE (alege una din fiecare subiect):\n{teme_str}\n\n"
            f"REFERINȚĂ (structura {ref['an']}):\n"
            f"  S.I: {ref['s1']}\n  S.II: {ref['s2']}\n  S.III: {ref['s3']}\n\n"
            f"10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri per cerință]\nSUBIECTUL al II-lea: [repere + punctaj]\nSUBIECTUL al III-lea: [repere eseu + conținut (18p) + redactare (12p)]\n[[/BAREM_BAC]]"
        )

    # ── Geografie ──
    elif cod == "geografie":
        data = BAC_DATE_REALE["geografie"]
        ref = random.choice(data["subiecte_reale"])
        teme_str = "\n".join(f"  - {t}" for t in data["tipare"]["teme_frecvente"])
        eseu_str = "\n".join(f"  {e}" for e in data["tipare"]["structura_eseu"])
        return (
            f"Generează un subiect COMPLET de BAC la Geografie — {profil}, "
            f"IDENTIC ca structură cu subiectele oficiale BAC România 2021-2025.\n\n"
            f"STRUCTURĂ EXACTĂ:\n\n"
            f"SUBIECTUL I (30p) — Hartă:\n"
            f"  Descrie o hartă (România fizică/politică sau Europa) și formulează 5 cerințe\n\n"
            f"SUBIECTUL al II-lea (30p) — Noțiuni geografice:\n"
            f"  3-4 cerințe de definire, exemplificare și caracterizare\n\n"
            f"SUBIECTUL al III-lea (30p) — Eseu geografic (300-400 cuvinte):\n"
            f"  Structură:\n{eseu_str}\n\n"
            f"TEME FRECVENTE:\n{teme_str}\n\n"
            f"REFERINȚĂ (structura {ref['an']}):\n  S.I: {ref['s1']}\n  S.II: {ref['s2']}\n  S.III: {ref['s3']}\n\n"
            f"10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri]\nSUBIECTUL al II-lea: [răspunsuri]\nSUBIECTUL al III-lea: [repere eseu]\n[[/BAREM_BAC]]"
        )

    # ── Română real/tehn ──
    elif cod in ("romana_real_tehn", "romana_uman"):
        data = BAC_DATE_REALE[cod]
        ref = random.choice(data["subiecte_reale"])
        itemi_str   = "\n".join(f"  {it}" for it in data["tipare_s1_itemi"])
        teme_str    = "\n".join(f"  - {t}" for t in data["teme_argumentativ"])
        s2_str      = "\n".join(f"  - {t}" for t in data["tipare_s2"])
        repere_str  = "\n".join(f"  {r}" for r in data["repere_s3"])
        autori_str  = "\n".join(f"  - {a}" for a in data["autori_opere"])
        return (
            f"Generează un subiect COMPLET de BAC la Limba și literatura română — {profil}, "
            f"IDENTIC ca structură cu subiectele oficiale din 2021-2025.\n\n"
            f"SUBIECTUL I (50p):\n"
            f"Partea A (30p) — Text la prima vedere (200-300 cuvinte).\n"
            f"Formulează EXACT 5 cerințe:\n{itemi_str}\n\n"
            f"Partea B (20p) — Text argumentativ ≥150 cuvinte:\n"
            f"  Alege o temă:\n{teme_str}\n\n"
            f"SUBIECTUL al II-lea (10p):\n"
            f"  Fragment literar scurt + una din cerințele:\n{s2_str}\n\n"
            f"SUBIECTUL al III-lea (30p) — Eseu ≥400 cuvinte:\n"
            f"  Alege un autor și operă din:\n{autori_str}\n"
            f"  Repere obligatorii:\n{repere_str}\n\n"
            f"REFERINȚĂ (structura {ref['an']}):\n  S.II: {ref.get('s2','')}\n  S.III: {ref.get('s3','')}\n\n"
            f"10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\n"
            f"SUBIECTUL I — Partea A: [răspunsuri așteptate + punctaj]\n"
            f"SUBIECTUL I — Partea B: [criterii text argumentativ + punctaj]\n"
            f"SUBIECTUL al II-lea: [răspuns așteptat + criterii]\n"
            f"SUBIECTUL al III-lea: [repere eseu + criterii conținut (18p) + redactare (12p)]\n"
            f"[[/BAREM_BAC]]"
        )

    # ── Informatică ──
    elif cod == "informatica":
        return (
            f"Generează un subiect COMPLET de BAC la Informatică — limbaj {profil}, "
            f"identic ca structură cu subiectele oficiale BAC România.\n\n"
            f"STRUCTURĂ EXACTĂ:\n"
            f"SUBIECTUL I (30p) — Algoritmi și pseudocod:\n"
            f"  - Analiza unui algoritm dat (urmărire pe date de test)\n"
            f"  - Scrierea pseudocodului pentru o cerință simplă\n"
            f"  - Corectarea unui algoritm cu erori\n\n"
            f"SUBIECTUL al II-lea (30p) — Tablouri și șiruri de caractere:\n"
            f"  - Problemă cu vectori/matrice și operații elementare\n"
            f"  - Prelucrare șiruri de caractere\n\n"
            f"SUBIECTUL al III-lea (30p) — Problemă complexă de programare:\n"
            f"  - Algoritm cu subprograme (funcții/proceduri)\n"
            f"  - Poate implica recursivitate sau structuri mai complexe\n\n"
            f"Scrie cerințele în {profil}. 10 puncte din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri + algoritmi corecți]\nSUBIECTUL al II-lea: [cod + explicații]\nSUBIECTUL al III-lea: [cod complet + complexitate]\n[[/BAREM_BAC]]"
        )

    # ── Economie ──
    elif cod == "economie":
        return (
            f"Generează un subiect COMPLET de BAC la Economie — {profil}.\n\n"
            f"SUBIECTUL I (30p) — itemi grilă și semiobiectivi: piață, cerere/ofertă, prețuri, agenți economici\n"
            f"SUBIECTUL al II-lea (30p) — studiu de caz economic + întrebări structurate\n"
            f"SUBIECTUL al III-lea (30p) — eseu economic: macroeconomie, șomaj, inflație, PIB\n"
            f"10p din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri]\nSUBIECTUL al II-lea: [soluții]\nSUBIECTUL al III-lea: [repere eseu]\n[[/BAREM_BAC]]"
        )

    # ── Psihologie ──
    elif cod == "psihologie":
        return (
            f"Generează un subiect COMPLET de BAC la Psihologie — {profil}.\n\n"
            f"SUBIECTUL I (30p) — definiții, caracterizare procese psihice\n"
            f"SUBIECTUL al II-lea (30p) — analiză personalitate: temperament, caracter, aptitudini\n"
            f"SUBIECTUL al III-lea (30p) — eseu: psihologie socială sau sănătate mentală\n"
            f"10p din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri]\nSUBIECTUL al II-lea: [soluții]\nSUBIECTUL al III-lea: [repere eseu]\n[[/BAREM_BAC]]"
        )

    # ── Logică ──
    elif cod == "logica":
        return (
            f"Generează un subiect COMPLET de BAC la Logică și argumentare — {profil}.\n\n"
            f"SUBIECTUL I (30p) — propoziții logice, tabele de adevăr, inferențe, simbolizare\n"
            f"SUBIECTUL al II-lea (30p) — analiză argumente: premize, concluzie, evaluare validitate, sofisme\n"
            f"SUBIECTUL al III-lea (30p) — construcție argument deductiv/inductiv + contra-argumente\n"
            f"10p din oficiu.\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri]\nSUBIECTUL al II-lea: [analiză]\nSUBIECTUL al III-lea: [repere argument]\n[[/BAREM_BAC]]"
        )

    # ── Fallback generic ──
    else:
        subiecte = materie_info.get("subiecte", [])
        subiecte_str = ", ".join(subiecte) if subiecte else materie_label
        structura = materie_info.get("structura", {})
        structura_str = "\n".join(f"  {k}: {v}" for k, v in structura.items()) if structura else ""
        timp = materie_info.get("timp_minute", 180)
        return (
            f"Generează un subiect complet de BAC la {materie_label} ({profil}), "
            f"identic ca structură și dificultate cu subiectele oficiale din România.\n\n"
            f"STRUCTURĂ OBLIGATORIE:\n"
            f"- SUBIECTUL I (30 puncte): itemi obiectivi/semiobiectivi\n"
            f"- SUBIECTUL al II-lea (30 puncte): probleme/analiză structurată\n"
            f"- SUBIECTUL al III-lea (30 puncte): problemă complexă / eseu / sinteză\n"
            f"- 10 puncte din oficiu\n\n"
            f"TEME: {subiecte_str}\nTIMP: {timp} minute\n\n"
            f"[[BAREM_BAC]]\nSUBIECTUL I: [răspunsuri și punctaj]\nSUBIECTUL al II-lea: [soluții și punctaj]\nSUBIECTUL al III-lea: [criterii și punctaj]\n[[/BAREM_BAC]]"
        )


def get_bac_correction_prompt(materie_label: str, subiect: str, raspuns_elev: str, from_photo: bool = False) -> str:
    """Construiește promptul pentru corectarea unui răspuns BAC."""
    source_note = (
        "NOTĂ: Răspunsul a fost extras automat dintr-o fotografie a lucrării. "
        "Unele cuvinte pot fi transcrise imperfect — judecă după intenția elevului.\n\n"
        if from_photo else ""
    )

    if "Română" in materie_label:
        lang_rules = (
            "CORECTARE LIMBĂ ROMÂNĂ (OBLIGATORIU — punctaj separat):\n"
            "- Ortografie și punctuație\n"
            "- Acordul gramatical\n"
            "- Exprimare clară, fără pleonasme sau cacofonii\n"
            "- Registru stilistic adecvat eseului de BAC\n"
            "- Acordă până la 10 puncte bonus/penalizare\n\n"
        )
    else:
        lang_rules = (
            f"CORECTARE LIMBAJ ȘTIINȚIFIC ({materie_label}):\n"
            "- Terminologie specifică folosită corect\n"
            "- Notații, simboluri și unități de măsură corecte\n"
            "- Raționament logic și coerent\n"
            "- Acordă până la 5 puncte bonus/penalizare\n\n"
        )

    return (
        f"Ești examinator BAC România pentru {materie_label}.\n\n"
        f"{source_note}"
        f"SUBIECTUL:\n{subiect}\n\n"
        f"RĂSPUNSUL ELEVULUI:\n{raspuns_elev}\n\n"
        f"Corectează COMPLET în această ordine:\n\n"
        f"## 📊 Punctaj per subiect\n"
        f"- Subiectul I: X/30 puncte\n"
        f"- Subiectul II: X/30 puncte\n"
        f"- Subiectul III: X/30 puncte\n"
        f"- Din oficiu: 10 puncte\n\n"
        f"## ✅ Ce a făcut bine\n[aspecte corecte]\n\n"
        f"## ❌ Greșeli și explicații\n[fiecare greșeală explicată]\n\n"
        f"## 🖊️ Calitatea limbii și exprimării\n{lang_rules}"
        f"## 🎓 Nota finală\n**Nota: X/10** — [verdict scurt]\n\n"
        f"## 💡 Recomandări pentru BAC\n[2-3 sfaturi concrete]\n\n"
        f"Fii constructiv, cald, dar riguros ca un examinator real."
    )
