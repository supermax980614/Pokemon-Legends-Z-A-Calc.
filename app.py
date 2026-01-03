import streamlit as st
import math

# --- 1. 傷害計算核心 ---
def calculate_damage(power, atk_stat, def_stat, criticle, wall_on, stab_bonus, typem, typdef, plus, move_name):
    if def_stat <= 0: def_stat = 1

    inner = math.floor(22 * power * atk_stat / def_stat)
    base = math.floor(inner / 72) + 2
    damagemin = math.floor(base * 0.85)
    damagemax = math.floor(base * 1)
    
    if criticle:
        damagemin = math.floor(damagemin * 1.5)
        damagemax = math.floor(damagemax * 1.5)
    elif wall_on:
        damagemin = math.floor(damagemin * 2/3)
        damagemax = math.floor(damagemax * 2/3)
        
    dmin, dmax = damagemin, damagemax
    if stab_bonus:   
        damagemin = math.floor(damagemin * 1.5)
        damagemax = math.floor(damagemax * 1.5)
         
    # --- 屬性表 (龍對妖精修正為 0) ---
    multi = 1.0
    chart = {
        "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
        "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
        "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
        "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2},
        "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
        "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
        "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "
