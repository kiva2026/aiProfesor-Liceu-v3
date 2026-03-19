"""modules/bac — Simulare examene, corecturi și admitere facultate."""
from .base import (
    MATERII_BAC, MATERII_SIMULARE_DISPONIBILE, PROFILE_BAC, BAC_DATE_REALE,
    get_bac_prompt_ai, get_bac_correction_prompt, parse_bac_subject, format_timer,
)
from .admitere_base import ADMITERE_CONFIG, ADMITERE_NIVELE, get_admitere_prompt
from .quiz_ui import run_quiz_ui
from .homework_ui import run_homework_ui
from .bac_ui import run_bac_sim_ui
from .admitere_ui import run_admitere_ui

__all__ = [
    "MATERII_BAC", "MATERII_SIMULARE_DISPONIBILE", "PROFILE_BAC", "BAC_DATE_REALE",
    "get_bac_prompt_ai", "get_bac_correction_prompt", "parse_bac_subject", "format_timer",
    "ADMITERE_CONFIG", "ADMITERE_NIVELE", "get_admitere_prompt",
    "run_quiz_ui", "run_homework_ui", "run_bac_sim_ui", "run_admitere_ui",
]
