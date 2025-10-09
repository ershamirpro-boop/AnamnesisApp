from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any

import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="Smart Anamnesis Recommender",
    page_icon="🩺",
    layout="wide",
)

# ---------- Unified, mobile-first styles (Light/Dark + Selectbox fix + RTL) ----------
st.markdown("""
<style>
/* ===== RTL בסיסי ===== */
.stApp { direction: rtl; }
.block-container{ padding-top:12px; padding-bottom:20px; }
h1,h2,h3,h4{ letter-spacing:.2px; text-align:right; }
p,li,span,label,.stMarkdown{ text-align:right; }

/* ===== קישורים ===== */
a,a:visited{ color:inherit; text-decoration:none; font-weight:600; }
a:hover{ text-decoration:underline; }

/* ===== כרטיסים (לא נוגעים ברקע העמוד!) ===== */
.card{
  background: rgba(255,255,255,.84);          /* ברירת מחדל נעימה ל-Light */
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 14px; padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
/* Dark mode tweaks */
@media (prefers-color-scheme: dark){
  .card{
    background: rgba(17,24,39,.85);           /* #111827 שקוף מעט */
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 1px 3px rgba(0,0,0,.35);
  }
}

/* ===== כפתורי הפעולות למעלה (רענון/איפוס) – מראה עקבי בשני המצבים ===== */
.topbar-btn button{
  background: #0f6fec !important;
  color:#fff !important; border:0 !important; height:48px !important;
  border-radius:10px !important; font-weight:600 !important; width:100% !important;
  box-shadow:0 1px 2px rgba(0,0,0,.15) !important;
}
.topbar-btn button:hover{ filter:brightness(.95); }

/* ===== Selectbox / dropdown =====
   לא כופים צבעים מוחלטים – נאחזים ב-inherit כדי לקבל את צבעי התֵמה הנוכחית. */
.stSelectbox [data-baseweb="select"]{
  background: transparent !important;
  color: inherit !important;
  border-radius:10px !important;
  border:1px solid rgba(128,128,128,.35) !important;
}
.stSelectbox [data-baseweb="popover"]{
  background: inherit !important;   /* יקבל רקע לפי התֵמה */
  color: inherit !important;
  border:1px solid rgba(128,128,128,.35) !important;
  border-radius:12px !important;
}
.stSelectbox [data-baseweb="option"]{ background: transparent !important; }
@media (prefers-color-scheme: light){
  .stSelectbox [data-baseweb="option"]:hover{ background: rgba(0,0,0,.04) !important; }
}
@media (prefers-color-scheme: dark){
  .stSelectbox [data-baseweb="option"]:hover{ background: rgba(255,255,255,.06) !important; }
}

/* ===== Radio כ"כרטיס" – כל השורה לחיצה, בלי ריבועים בתוך ריבועים ===== */
.stRadio div[role="radiogroup"]{ display:grid; gap:10px; margin-top:6px; }
.stRadio div[role="radiogroup"] input[type="radio"]{ display:none !important; }
.stRadio div[role="radiogroup"] > label{
  width:100%; display:flex; align-items:center; gap:10px; padding:12px 14px;
  background: transparent; color: inherit;
  border:1px solid rgba(128,128,128,.35); border-radius:12px; cursor:pointer; transition:all .12s;
}
@media (prefers-color-scheme: light){
  .stRadio div[role="radiogroup"] > label:hover{ background: rgba(0,0,0,.04); }
  .stRadio div[role="radiogroup"] > label[aria-checked="true"]{
    background: rgba(59,130,246,.14); border-color:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,.25);
  }
}
@media (prefers-color-scheme: dark){
  .stRadio div[role="radiogroup"] > label:hover{ background: rgba(255,255,255,.06); }
  .stRadio div[role="radiogroup"] > label[aria-checked="true"]{
    background: rgba(59,130,246,.18); border-color:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,.25);
  }
}
.stRadio div[role="radiogroup"] > label span{ white-space:normal !important; line-height:1.35; }

/* ===== פריסת RTL בדסקטופ / מובייל ===== */
@media (min-width:821px){
  [data-testid="stHorizontalBlock"]{ flex-direction: row-reverse !important; }
}
@media (max-width:820px){
  [data-testid="stHorizontalBlock"]{ flex-direction: column !important; gap:0 !important; }
  [data-testid="column"]{ width:100% !important; }
  .block-container{ padding-left:8px; padding-right:8px; }
}

/* ===== להסתיר את הסיידבר של סטריםליט אם יופיע ===== */
[data-testid='stSidebar']{ display:none; }
</style>
""", unsafe_allow_html=True)


# ---------- Paths ----------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "knowledge.json"
VIDEO_PATHS = [BASE_DIR / "video_links.json", BASE_DIR / "anamnesis_video_links.json"]

# ---------- Helpers ----------
@st.cache_data(ttl=0)
def load_json_safe(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"⚠️ לא נמצא הקובץ: {path.name}")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON לא תקין בקובץ {path.name} - {e}")
        return {}

def try_load_video_links() -> Dict[str, List[Dict[str, List[str]]]]:
    for p in VIDEO_PATHS:
        if p.exists():
            return load_json_safe(p) or {}
    return {}

def merge_video_links(rec_block: Dict[str, Any], system_name: str) -> None:
    if not rec_block or "physical_exam" not in rec_block:
        return
    video_map = try_load_video_links()
    sys_list = video_map.get(system_name, [])
    if not sys_list:
        return
    label_to_urls: Dict[str, List[str]] = {}
    for item in sys_list:
        label = (item.get("label") or "").strip()
        urls = item.get("urls") or []
        if label and urls:
            label_to_urls[label] = urls
    for it in rec_block.get("physical_exam", []):
        if isinstance(it, dict):
            label = (it.get("label") or "").strip()
            if label in label_to_urls and not it.get("url"):
                it["url"] = label_to_urls[label][0]

def compose_entry(data: Dict[str, Any], system: str, complaint: str) -> Dict[str, Any]:
    systems = data.get("systems", {})
    generic = data.get("generic_by_system", {})
    if complaint == "אחר":
        base = generic.get(system, {})
        return {
            "questions": base.get("questions", []),
            "physical_exam": base.get("physical_exam", []),
            "labs": base.get("labs", []),
            "imaging": base.get("imaging", []),
            "scores": base.get("scores", []),
            "notes": base.get("notes", []),
        }
    return systems.get(system, {}).get(complaint, {})

# ---------- Top bar controls (instead of sidebar) ----------
top_left, top_right = st.columns(2)
with top_left:
    if st.container().button("רענון תוכן", key="refresh_btn", help="טען מחדש את קבצי ה־JSON"):
        load_json_safe.clear()
        st.toast("התוכן עודכן", icon="✅")
        st.rerun()

with top_right:
    if st.container().button("איפוס מסך", key="reset_btn", help="ניקוי בחירות ואיפוס המסך"):
        # איפוס בטוח – בלי לקרוס
        try:
            # Streamlit >= 1.30
            st.query_params.clear()
        except Exception:
            # בגרסאות ישנות יותר
            try:
                st.experimental_set_query_params()
            except Exception:
                pass
        try:
            st.session_state.clear()
        except Exception:
            pass
        load_json_safe.clear()
        st.rerun()

# ---------- Header ----------
st.title("🩺 Smart Anamnesis Recommender")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# ---------- Load data ----------
if not DATA_PATH.exists():
    st.error("לא נמצא knowledge.json בתיקייה של האפליקציה. העלה את הקובץ לאותה תיקייה שבה app.py נמצא.")
    st.stop()

data = load_json_safe(DATA_PATH)
if not data:
    st.stop()

# ---------- System and complaint selection ----------
systems = sorted(set(list(data.get("systems", {}).keys()) + list(data.get("generic_by_system", {}).keys())))
if not systems:
    st.error("קובץ הנתונים ריק - מלא את knowledge.json לפי המבנה שהוגדר.")
    st.stop()

sel_cols = st.columns([1, 1, 2])
with sel_cols[0]:
    system = st.selectbox("בחר מערכת", systems, index=0)
with sel_cols[1]:
    sys_complaints = sorted(list(data.get("systems", {}).get(system, {}).keys()))
    if "אחר" not in sys_complaints:
        sys_complaints = ["אחר"] + sys_complaints
    complaint = st.selectbox("בחר תלונה", sys_complaints, index=0)
with sel_cols[2]:
    st.markdown(f"<span class='card' style='display:inline-block;padding:6px 10px;border-radius:999px;'>מערכת: {system}</span> "
                f"<span class='card' style='display:inline-block;padding:6px 10px;border-radius:999px;margin-right:8px;'>תלונה: {complaint}</span>",
                unsafe_allow_html=True)

rec = compose_entry(data, system, complaint)
merge_video_links(rec, system)

# ---------- Sections ----------
def render_questions(qs: List[str]) -> None:
    st.markdown("### אנמנזה - שאלות לשאול")
    box = st.container()
    with box:
        if not qs:
            st.write("- אין שאלות מוגדרות")
        else:
            for q in qs:
                st.write(f"- {q}")

def render_list_with_links(items: Any, title: str) -> None:
    st.markdown(f"### {title}")
    wrap = st.container()
    with wrap:
        if not items:
            st.write("- אין פריטים")
            return
        for item in items:
            if isinstance(item, dict) and "label" in item:
                label = item.get("label", "")
                url = item.get("url", "")
                if url:
                    st.markdown(f"- ▶️ [{label}]({url})")
                else:
                    st.markdown(f"- {label}")
            elif isinstance(item, dict) and "test" in item:
                test = item.get("test", "")
                why = item.get("why", "")
                when = item.get("when", "")
                line = f"- **{test}**"
                if why:
                    line += f" - למה: {why}"
                if when:
                    line += f" - מתי: {when}"
                st.markdown(line)
            elif isinstance(item, dict) and "modality" in item:
                modality = item.get("modality", "")
                trigger = item.get("trigger", "")
                st.markdown(f"- **{modality}** - מתי: {trigger}")
            else:
                st.markdown(f"- {str(item)}")

def render_scores(scores: Any) -> None:
    st.markdown("### 📊 scores רלוונטיים")
    box = st.container()
    with box:
        if not scores:
            st.write("- אין scores מוגדרים")
            return
        for s in scores:
            name = s.get("name", str(s))
            about = s.get("about", "")
            rule_in = s.get("rule_in", "")
            rule_out = s.get("rule_out", "")
            ref = s.get("ref", "")
            st.markdown(f"**{name}**")
            if about:
                st.caption(f"מה בודק: {about}")
            if rule_in:
                st.write(f"- Rule-in: {rule_in}")
            if rule_out:
                st.write(f"- Rule-out: {rule_out}")
            if ref:
                st.caption(f"ⓘ רפרנס: {ref}")
            st.markdown("")

# ---------- Render ----------
st.markdown("<div class='card'>", unsafe_allow_html=True)
render_questions(rec.get("questions", []))
st.markdown("</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    render_list_with_links(rec.get("physical_exam", []), "🧍‍♂️ מה צריך לבדוק - בדיקה גופנית")
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    render_list_with_links(rec.get("labs", []), "🧪 בדיקות מעבדה מומלצות")
    st.markdown("</div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    render_list_with_links(rec.get("imaging", []), "🖥️ בדיקות עזר/הדמיה")
    st.markdown("</div>", unsafe_allow_html=True)

if rec.get("notes"):
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("### 🧴 המלצות והערות")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    for n in rec["notes"]:
        st.write(f"- {n}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
render_scores(rec.get("scores", []))
st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------
st.caption("נכתב עי לירן שחר • Smart Anamnesis Recommender • גרסה קלינית ראשונה. אין שמירת היסטוריה בין סשנים.")







