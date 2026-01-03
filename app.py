import streamlit as st
import math

# --- 1. 傷害計算核心 ---
def calculate_damage(power, atk_stat, def_stat, criticle, wall_on, stab_bonus, typem, typdef, plus):
    # 基礎傷害公式
    inner = math.floor(22 * power * atk_stat / def_stat)
    base = math.floor(inner / 72) + 2
    damagemin = math.floor(base * 0.85)
    damagemax = math.floor(base * 1)
    
    # 要害與牆判定 (反射壁/光牆在要害時無效)
    if criticle:
        damagemin = math.floor(damagemin * 1.5)
        damagemax = math.floor(damagemax * 1.5)
    elif wall_on:
        damagemin = math.floor(damagemin * 2/3)
        damagemax = math.floor(damagemax * 2/3)
        
    dmin, dmax = damagemin, damagemax
    
    # 屬性一致加成 (STAB)
    if stab_bonus:   
        damagemin = math.floor(damagemin * 1.5)
        damagemax = math.floor(damagemax * 1.5)
         
    # --- 完整屬性相剋表 ---
    multi = 1.0
    chart = {
        "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
        "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
        "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
        "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2},
        "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
        "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
        "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
        "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
        "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
        "flying": {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
        "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
        "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "fairy": 0.5, "steel": 0.5},
        "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
        "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
        "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
        "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
        "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
        "fairy": {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5},
    }
    for t_def in typdef:
        if t_def != "none" and typem in chart and t_def in chart[typem]:
            multi *= chart[typem][t_def]

    damagemin = math.floor(damagemin * multi)
    damagemax = math.floor(damagemax * multi)

    # Plus (C+) 模式邏輯
    if plus:
        if damagemin > (dmin * 1.7) and damagemax > (dmax * 1.7):
            damagemin *= 1.3; damagemax *= 1.3
        else:
            damagemin *= 1.2; damagemax *= 1.2
            
    return [math.floor(damagemin), math.floor(damagemax)]

# --- 2. 性格與數據庫 ---
NATURES = {
    "勤奮 (中性)": [1,1,1,1,1], "怕死 (加攻減防)": [1.1,0.9,1,1,1], "固執 (加攻減特攻)": [1.1,1,0.9,1,1],
    "調皮 (加攻減特防)": [1.1,1,1,0.9,1], "勇敢 (加攻減速)": [1.1,1,1,1,0.9], "大膽 (加防減攻)": [0.9,1.1,1,1,1],
    "淘氣 (加防減特攻)": [1,1.1,0.9,1,1], "無慮 (加防減特防)": [1,1.1,1,0.9,1], "悠閒 (加防減速)": [1,1.1,1,1,0.9],
    "內斂 (加特攻減攻)": [0.9,1,1.1,1,1], "慢吞吞 (加特攻減防)": [1,0.9,1.1,1,1], "馬虎 (加特攻減特防)": [1,1,1.1,0.9,1],
    "冷靜 (加特攻減速)": [1,1,1.1,1,0.9], "溫和 (加特防減攻)": [0.9,1,1,1.1,1], "溫順 (加特防減防)": [1,0.9,1,1.1,1],
    "慎重 (加特防減特攻)": [1,1,0.9,1.1,1], "狂妄 (加特防減速)": [1,1,1,1.1,0.9], "膽小 (加速減攻)": [0.9,1,1,1,1.1],
    "急躁 (加速減防)": [1,0.9,1,1,1.1], "爽朗 (加速減特攻)": [1,1,0.9,1,1.1], "天真 (加速減特防)": [1,1,1,0.9,1.1]
}

pokemon_db = {
    "基格爾德 (50%形態)": [108, 100, 121, 81, 95, 95, ["dragon", "ground"]],
    "基格爾德 (10%形態)": [54, 100, 71, 61, 85, 115, ["dragon", "ground"]],
    "基格爾德 (完全體)": [216, 100, 121, 91, 95, 85, ["dragon", "ground"]],
    "噴火龍": [78, 84, 78, 109, 85, 100, ["fire", "flying"]],
    "巨沼怪": [100, 110, 90, 85, 90, 65, ["water", "ground"]]
}

move_db = {
    "千箭齊發 (物)": ["p", "ground", 90], "核心懲罰者 (特)": ["s", "dragon", 100],
    "熱風 (特)": ["s", "fire", 95], "地震 (物)": ["p", "ground", 100], "日光束 (特)": ["s", "grass", 120]
}

# --- 3. 網頁介面 ---
st.set_page_config(page_title="ZA 傷害計算機", layout="wide")
st.title("🛡寶可夢 ZA 傷害計算機")

def calc_stat(base, ev, iv, nature_mod, is_hp=False):
    if is_hp:
        return math.floor((base * 2 + iv + ev / 4) * 50 / 100 + 10 + 50)
    return math.floor(math.floor((base * 2 + iv + ev / 4) * 50 / 100 + 5) * nature_mod)

col1, col2 = st.columns(2)

with col1:
    st.header("👤 攻擊方設定")
    pa = st.selectbox("選擇寶可夢", list(pokemon_db.keys()))
    nature_a = st.selectbox("選擇性格", list(NATURES.keys()), index=2) # 預設固執
    
    with st.expander("調整努力值 (EVs)"):
        a_evs = [st.slider(f"攻方 {n} 努力值", 0, 252, 0, step=4) for n in ["HP", "物攻", "物防", "特攻", "特防", "速度"]]
    
    move_name = st.selectbox("選擇招式", list(move_db.keys()))
    plus_on = st.toggle("開啟 Plus (C+) 模式")

with col2:
    st.header("🛡️ 防守方設定")
    pd = st.selectbox("選擇防守寶可夢", list(pokemon_db.keys()), index=3)
    nature_d = st.selectbox("選擇性格 ", list(NATURES.keys()), index=0)
    
    with st.expander("調整努力值 (EVs) "):
        d_evs = [st.slider(f"防方 {n} 努力值", 0, 252, 0, step=4) for n in ["HP", "物攻", "物防", "特攻", "特防", "速度"]]
        
    crit_on = st.toggle("擊中要害 (Crit)")
    wall_on = st.toggle("對手有牆 (反射壁/光牆)")

# --- 4. 計算邏輯 ---
if st.button("🔥 執行傷害計算", use_container_width=True):
    atk_base = pokemon_db[pa]
    def_base = pokemon_db[pd]
    m_info = move_db[move_name]
    
    # 取得性格修正 [物攻, 物防, 特攻, 特防, 速度]
    mod_a = NATURES[nature_a]
    mod_d = NATURES[nature_d]
    
    # 判定攻擊類型
    if m_info[0] == "s":
        final_atk = calc_stat(atk_base[3], a_evs[3], 31, mod_a[2])
        final_def = calc_stat(def_base[4], d_evs[4], 31, mod_d[3])
    else:
        final_atk = calc_stat(atk_base[1], a_evs[1], 31, mod_a[0])
        final_def = calc_stat(def_base[2], d_evs[2], 31, mod_d[1])
        
    final_hp = calc_stat(def_base[0], d_evs[0], 31, 1.0, is_hp=True)
    stab = m_info[1] in atk_base[6]
    
    res = calculate_damage(m_info[2], final_atk, final_def, crit_on, wall_on, stab, m_info[1], def_base[6], plus_on)
    
    # 顯示結果
    st.divider()
    p_min, p_max = res[0]/final_hp, res[1]/final_hp
    st.subheader(f"造成傷害: {res[0]} ~ {res[1]} (對手總 HP: {final_hp})")
    st.write(f"傷害佔比: **{p_min:.1%} ~ {p_max:.1%}**")
    
    if p_min >= 1: st.success("🎯 確定一擊擊倒！")
    elif p_max >= 1: st.warning("🎲 亂數一擊擊倒")
    else: st.info(f"⚔️ 擊倒需要攻擊次數: {math.ceil(1/p_max)} 次")
