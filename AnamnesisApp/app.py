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
/* ====== Radio כ"כרטיס" – כל השורה לחיצה, בלי ריבועים בתוך ריבועים ====== */
.stRadio div[role="radiogroup"]{
  display:grid; gap:10px; margin-top:6px;
}

/* מסתיר את עיגול הרדיו עצמו */
.stRadio div[role="radiogroup"] input[type="radio"]{
  display:none !important;
}

/* הכרטיס (label) – כל השורה לחיצה */
.stRadio div[role="radiogroup"] > label{
  width:100%;
  display:flex; align-items:center; gap:10px;
  padding:12px 14px;
  background:#ffffff;
  color:#0f172a;
  border:1px solid #e5e7eb;
  border-radius:12px;
  cursor:pointer;
  transition:all .12s ease-in-out;
}

/* ריחוף */
.stRadio div[role="radiogroup"] > label:hover{
  background:#f8fafc;
  border-color:#cbd5e1;
}

/* מצב נבחר – משתמשים ב-aria-checked שמציב סטריםליט על ה-label */
.stRadio div[role="radiogroup"] > label[aria-checked="true"]{
  background:#eef4ff;
  border-color:#0f6fec;
  box-shadow:0 0 0 3px rgba(15,111,236,.12);
  color:#0b1220;
}

/* טקסט ארוך – שבירה נקייה */
.stRadio div[role="radiogroup"] > label span{
  white-space:normal !important;
  line-height:1.35;
}

/* מובייל – יותר מרווח לחיצה */
@media (max-width:820px){
  .stRadio div[role="radiogroup"] > label{ padding:14px 16px; }
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





