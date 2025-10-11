from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import quote_plus

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
/* ===== RTL ===== */
.stApp { direction: rtl; }
.block-container{ padding-top:12px; padding-bottom:20px; }
h1,h2,h3,h4{ letter-spacing:.2px; text-align:right; }
p,li,span,label,.stMarkdown{ text-align:right; }

/* ===== Links ===== */
a,a:visited{ color:inherit; text-decoration:none; font-weight:600; }
a:hover{ text-decoration:underline; }

/* ===== Cards ===== */
.card{
  background: rgba(255,255,255,.84);
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 14px; padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark){
  .card{
    background: rgba(17,24,39,.85);
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 1px 3px rgba(0,0,0,.35);
  }
}

/* ===== Top buttons ===== */
.topbar-btn button{
  background: #0f6fec !important;
  color:#fff !important; border:0 !important; height:48px !important;
  border-radius:10px !important; font-weight:600 !important; width:100% !important;
  box-shadow:0 1px 2px rgba(0,0,0,.15) !important;
}
.topbar-btn button:hover{ filter:brightness(.95); }

/* ===== Selectbox / dropdown ===== */
.stSelectbox [data-baseweb="select"]{
  background: transparent !important;
  color: inherit !important;
  border-radius:10px !important;
  border:1px solid rgba(128,128,128,.35) !important;
}
.stSelectbox [data-baseweb="popover"]{
  background: inherit !important;
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

/* ===== Radio as cards ===== */
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

/* ===== Responsive layout ===== */
@media (min-width:821px){
  [data-testid="stHorizontalBlock"]{ flex-direction: row-reverse !important; }
}
@media (max-width:820px){
  [data-testid="stHorizontalBlock"]{ flex-direction: column !important; gap:0 !important; }
  [data-testid="column"]{ width:100% !important; }
  .block-container{ padding-left:8px; padding-right:8px; }
}

/* ===== Hide sidebar ===== */
[data-testid='stSidebar']{ display:none; }

/* ===== simple hr ===== */
.hr{ height:1px; width:100%; background:linear-gradient(90deg, transparent, rgba(128,128,128,.35), transparent); margin:12px 0 18px; }
</style>
""", unsafe_allow_html=True)
st.markdown("<style>[data-testid='stSidebar']{display:none}</style>", unsafe_allow_html=True)

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
    """
    ממלא url לכל פריט 'physical_exam' אם יש התאמה ב-video_links.json.
    אם אין התאמה – נוסיף חיפוש יוטיוב תקני (quote_plus) לפי התווית.
    """
    if not rec_block or "physical_exam" not in rec_block:
        return
    video_map = try_load_video_links()
    sys_list = video_map.get(system_name, [])
    label_to_urls: Dict[str, List[str]] = {}
    for item in sys_list:
        label = (item.get("label") or "").strip()
        urls = item.get("urls") or []
        if label and urls:
            label_to_urls[label] = urls
    for it in rec_block.get("physical_exam", []):
        if isinstance(it, dict):
            label = (it.get("label") or "").strip()
            if not label:
                continue
            if label in label_to_urls:
                it.setdefault("url", label_to_urls[label][0])
            else:
                # חיפוש כללי ביוטיוב עם קידוד תקני
                it.setdefault("url", "https://www.youtube.com/results?search_query=" + quote_plus(label))

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

def _check_block(issues: list[str], path: str, block: Any) -> None:
    if not isinstance(block, dict):
        issues.append(f"'{path}' חייב להיות אובייקט (dict) של רשימות.")
        return
    for fld in ("questions", "physical_exam", "labs", "imaging", "scores", "notes"):
        if fld in block and not isinstance(block[fld], list):
            issues.append(f"'{path}.{fld}' חייב להיות רשימה (list).")
    if isinstance(block.get("physical_exam"), list):
        for i, it in enumerate(block["physical_exam"]):
            if not (isinstance(it, dict) and "label" in it):
                issues.append(f"'{path}.physical_exam[{i}]' חייב להיות dict עם 'label' (ו-'url' אופציונלי).")
    if isinstance(block.get("labs"), list):
        for i, it in enumerate(block["labs"]):
            if not (isinstance(it, dict) and "test" in it):
                issues.append(f"'{path}.labs[{i}]' חייב להיות dict עם 'test' (+ 'why'/'when' אופציונליים).")
    if isinstance(block.get("imaging"), list):
        for i, it in enumerate(block["imaging"]):
            if not (isinstance(it, dict) and "modality" in it):
                issues.append(f"'{path}.imaging[{i}]' חייב להיות dict עם 'modality' (+ 'trigger' אופציונלי).")
    if isinstance(block.get("scores"), list):
        for i, it in enumerate(block["scores"]):
            if not isinstance(it, dict) or "name" not in it:
                issues.append(f"'{path}.scores[{i}]' מומלץ להיות dict עם 'name' (+ 'about'/'rule_in'/'rule_out'/'ref' אופציונליים).")

def validate_knowledge(data: Dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["הקובץ העליון חייב להיות אובייקט JSON (dict)."]
    if "metadata" in data and not isinstance(data["metadata"], dict):
        issues.append("'metadata' צריך להיות אובייקט (dict).")
    for key in ("systems", "generic_by_system"):
        if key not in data:
            issues.append(f"חסר מפתח עליון '{key}'. מומלץ להוסיף: \"{key}\": {{}}")
        elif not isinstance(data[key], dict):
            issues.append(f"'{key}' חייב להיות אובייקט (dict).")
    sys_map = data.get("systems", {})
    if isinstance(sys_map, dict):
        for sys_name, comp_map in sys_map.items():
            if not isinstance(comp_map, dict):
                issues.append(f"'systems.{sys_name}' חייב להיות אובייקט של תלונות (dict).")
                continue
            for complaint, block in comp_map.items():
                _check_block(issues, f"systems.{sys_name}.{complaint}", block)
    gen_map = data.get("generic_by_system", {})
    if isinstance(gen_map, dict):
        for sys_name, block in gen_map.items():
            _check_block(issues, f"generic_by_system.{sys_name}", block)
    return issues

# ---------- Top bar controls ----------
top_left, top_right = st.columns(2)
with top_left:
    if st.container().button("רענון תוכן", key="refresh_btn", help="טען מחדש את קבצי ה־JSON", use_container_width=True):
        load_json_safe.clear()
        st.toast("התוכן עודכן", icon="✅")
        st.rerun()

with top_right:
    if st.container().button("איפוס מסך", key="reset_btn", help="ניקוי בחירות ואיפוס המסך", use_container_width=True):
        try:
            st.query_params.clear()
        except Exception:
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

issues = validate_knowledge(data)
if issues:
    with st.expander("⚠️ נמצאו הערות/בעיות במבנה הקובץ (לחץ להצגה)"):
        for i, msg in enumerate(issues, start=1):
            st.markdown(f"{i}. {msg}")

# ---------- Quick view ----------
with st.expander("📚 מבט מהיר על הידע (מערכות ותלונות)"):
    sys_map = data.get("systems", {})
    gen_map = data.get("generic_by_system", {})
    total_systems = len(set(sys_map.keys()) | set(gen_map.keys()))
    st.caption(f"נמצאו {total_systems} מערכות | {sum(len(v) for v in sys_map.values())} תלונות ספציפיות | {len(gen_map)} מערכות עם 'אחר' כללי")
    for sys_name in sorted(set(sys_map.keys()) | set(gen_map.keys())):
        complaints = sorted(list(sys_map.get(sys_name, {}).keys()))
        st.markdown(f"#### • {sys_name}")
        if complaints:
            st.markdown("תלונות ספציפיות:")
            st.write(", ".join(complaints))
        else:
            st.write("אין תלונות ספציפיות בקובץ למערכת זו.")
        if sys_name in gen_map:
            st.caption("כולל בלוק כללי ('אחר') למערכת זו.")
    st.divider()

# ---------- Selection ----------
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
    st.markdown(
        f"<span class='card' style='display:inline-block;padding:6px 10px;border-radius:999px;'>מערכת: {system}</span> "
        f"<span class='card' style='display:inline-block;padding:6px 10px;border-radius:999px;margin-right:8px;'>תלונה: {complaint}</span>",
        unsafe_allow_html=True
    )

rec = compose_entry(data, system, complaint)
merge_video_links(rec, system)

# ---------- Render helpers ----------
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
                st.markdown(f"- **{modality}**" + (f" - מתי: {trigger}" if trigger else ""))
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
            name = (s.get("name") if isinstance(s, dict) else str(s)) or ""
            about = s.get("about", "") if isinstance(s, dict) else ""
            rule_in = s.get("rule_in", "") if isinstance(s, dict) else ""
            rule_out = s.get("rule_out", "") if isinstance(s, dict) else ""
            ref = s.get("ref", "") if isinstance(s, dict) else ""
            st.markdown(f"**{name}**")
            if about: st.caption(f"מה בודק: {about}")
            if rule_in: st.write(f"- Rule-in: {rule_in}")
            if rule_out: st.write(f"- Rule-out: {rule_out}")
            if ref: st.caption(f"ⓘ רפרנס: {ref}")
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
st.caption("נכתב ע\"י לירן שחר • Smart Anamnesis Recommender • גרסה קלינית ראשונה. אין שמירת היסטוריה בין סשנים.")
