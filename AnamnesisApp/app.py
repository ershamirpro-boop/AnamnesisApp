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

# ---------- Unified, mobile-first styles (incl. Selectbox fix) ----------
st.markdown("""
<style>
:root{
  --pri:#0f6fec; --bg:#f8fafc; --card:#ffffff; --text:#0f172a;
  --dark:#0f172a; --dark-2:#111827; --dark-3:#1f2937; --dark-4:#334155; --light:#ffffff;
}

/* רקע כללי */
html,body,.stApp{background:var(--bg)!important;color:var(--text)!important}
.block-container{padding-top:12px;padding-bottom:20px}

/* כותרות וטיפוגרפיה */
h1,h2,h3,h4{color:#0b1220!important;letter-spacing:.2px}
p,li,span,label,.stMarkdown{color:var(--text)!important;font-size:1rem}

/* כפתורים */
div.stButton>button:first-child{
  background:var(--pri);color:#fff;border:0;height:48px;border-radius:10px;
  font-weight:600;width:100%;box-shadow:0 1px 2px rgba(15,23,42,.15)
}
div.stButton>button:first-child:hover{filter:brightness(.95)}

/* ===== סיידבר כהה עם טקסט לבן ===== */
[data-testid="stSidebar"]{
  background:var(--dark-2)!important;border-right:1px solid var(--dark-4)
}
[data-testid="stSidebar"] *{color:#e5e7eb!important}

/* קלטים בסיידבר */
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea{
  background:var(--dark-3)!important;color:#fff!important;border:1px solid var(--dark-4)!important;border-radius:10px!important;min-height:44px
}
[data-testid="stSidebar"] .stNumberInput input{background:var(--dark-3)!important;color:#fff!important}
[data-testid="stSidebar"] .stNumberInput button{background:var(--dark-4)!important;color:#fff!important;border:0}

/* ===== Selectbox כהה עם טקסט לבן (גם במיין וגם בסיידבר) ===== */
/* התיבה עצמה */
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] *{
  background:var(--dark-2)!important;color:#fff!important;border:1px solid var(--dark-4)!important;border-radius:10px!important;min-height:44px
}
/* value/placeholder */
.stSelectbox [data-baseweb="single-value"], .stSelectbox [data-baseweb="placeholder"]{color:#fff!important;opacity:1!important}
/* חץ */
.stSelectbox svg{fill:#fff!important;color:#fff!important}

/* ===== התפריט הנפתח – ה-portal מחוץ לעץ ===== */
body [data-baseweb="popover"], body [data-baseweb="menu"], body [data-baseweb="menu"] *{
  background:var(--dark-2)!important;color:#fff!important;border-color:var(--dark-4)!important
}
body [data-baseweb="menu"] [role="option"]{background:var(--dark-2)!important;color:#fff!important}
body [data-baseweb="menu"] [role="option"]:hover,
body [data-baseweb="menu"] [role="option"][aria-selected="true"]{
  background:var(--dark-3)!important;color:#fff!important
}

/* קישורים וכרטיסים */
a,a:visited{color:var(--pri)!important;text-decoration:none;font-weight:600}
a:hover{text-decoration:underline}
.card{background:var(--card);border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.hr{height:1px;background:#e5e7eb;border:0;margin:14px 0}

/* רספונסיבי – מובייל: לערום עמודות */
@media (max-width:820px){
  [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:0!important}
  [data-testid="column"]{width:100%!important}
  .block-container{padding-left:8px;padding-right:8px}
  h1{font-size:1.5rem} h2{font-size:1.2rem} h3{font-size:1.05rem}
  .card{padding:12px;border-radius:12px}
  div.stButton>button:first-child{height:50px;font-size:1rem}
}
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

# ---------- Sidebar - identity + actions ----------
with st.sidebar:
    st.header("זיהוי")
    role = st.selectbox("תפקיד", ["סטודנט", "מתמחה", "רופא", "אחות", "אורח"], index=2)
    dept = st.text_input("מחלקה", "מלר\"ד")
    age = st.number_input(" גיל מטופל", min_value=0, max_value=120, value=40, step=1)

    st.caption("ניהול")
    colR1, colR2 = st.columns(2)
    with colR1:
        if st.button("רענון תוכן"):
            load_json_safe.clear()
            st.experimental_rerun()
    with colR2:
        if st.button("איפוס מסך"):
            st.experimental_set_query_params()
            load_json_safe.clear()
            st.experimental_rerun()

# ---------- Header ----------
st.title("🩺 Smart Anamnesis Recommender")
st.caption(f"תפקיד: {role} | מחלקה: {dept} |  גיל מטופל: {age}")
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
    st.markdown(f"<span class='pill'>מערכת: {system}</span> <span class='pill'>תלונה: {complaint}</span>", unsafe_allow_html=True)

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
    st.markdown("### 📊 scorים רלוונטיים")
    box = st.container()
    with box:
        if not scores:
            st.write("- אין scorים מוגדרים")
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
st.caption("נכתב עי לירן שחר Smart Anamnesis Recommender - גרסה קלינית ראשונה. אין שמירת היסטוריה בין סשנים.")



