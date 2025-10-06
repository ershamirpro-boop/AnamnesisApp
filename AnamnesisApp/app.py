import json
import streamlit as st
from pathlib import Path
from typing import Dict, List

st.set_page_config(page_title="Smart Anamnesis Recommender", page_icon="🩺", layout="wide")
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "knowledge.json"
VIDEO_PATHS = [BASE_DIR / "video_links.json", BASE_DIR / "anamnesis_video_links.json"]

@st.cache_data(ttl=0)
def load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def try_load_video_links() -> Dict[str, List[Dict[str, List[str]]]]:
    for p in VIDEO_PATHS:
        if p.exists():
            return load_json(p)
    return {}

def merge_video_links(rec_block: Dict, system_name: str):
    if not rec_block or "physical_exam" not in rec_block:
        return
    video_map = try_load_video_links()
    sys_list = video_map.get(system_name, [])
    if not sys_list:
        return
    label_to_urls = {}
    for item in sys_list:
        label = item.get("label", "").strip()
        urls = item.get("urls", [])
        if label and urls:
            label_to_urls[label] = urls
    for it in rec_block.get("physical_exam", []):
        if isinstance(it, dict):
            label = it.get("label", "").strip()
            if label in label_to_urls and not it.get("url"):
                it["url"] = label_to_urls[label][0]

def role_gate():
    st.sidebar.header("זיהוי")
    role = st.sidebar.selectbox("תפקיד", ["סטודנט", "מתמחה", "רופא", "אחות", "אורח"], index=2)
    dept = st.sidebar.text_input("מחלקה", "מלר\"ד")
    age = st.sidebar.number_input("גיל", min_value=0, max_value=120, value=40, step=1)

    st.sidebar.button("רענון תוכן - טען JSON מחדש", on_click=load_json.clear)
    if st.sidebar.button("סיום והתחל חדש"):
        st.experimental_set_query_params()
        load_json.clear()
        st.experimental_rerun()

    st.sidebar.caption("אין שמירת היסטוריה - כל אינטראקציה עומדת בפני עצמה.")
    return {"role": role, "department": dept, "age": age}

def render_questions(qs: List[str]):
    st.markdown("### אנמנזה - שאלות לשאול")
    if not qs:
        st.write("- אין שאלות מוגדרות")
    for q in qs:
        st.write(f"- {q}")

def render_list_with_links(items, title: str):
    st.markdown(f"### {title}")
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

def render_scores(scores):
    st.markdown("### 📊 scorים רלוונטיים")
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

def compose_entry(data: Dict, system: str, complaint: str) -> Dict:
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
            "notes": base.get("notes", [])
        }
    return systems.get(system, {}).get(complaint, {})

def main():
    st.title("🩺 Smart Anamnesis Recommender - v0.6.0")
    if not DATA_PATH.exists():
        st.error("לא נמצא knowledge.json. ודא שהקובץ נמצא באותה תיקיה כמו app.py")
        st.stop()

    data = load_json(DATA_PATH)
    identity = role_gate()
    st.caption(f"תפקיד: {identity['role']} | מחלקה: {identity['department']} | גיל: {identity['age']}")

    systems = sorted(set(list(data.get("systems", {}).keys()) + list(data.get("generic_by_system", {}).keys())))
    if not systems:
        st.error("קובץ נתונים ריק. אנא מלא את knowledge.json")
        st.stop()

    system = st.selectbox("בחר מערכת", systems, index=0)

    sys_complaints = sorted(list(data.get("systems", {}).get(system, {}).keys()))
    if "אחר" not in sys_complaints:
        sys_complaints = ["אחר"] + sys_complaints
    complaint = st.selectbox("בחר תלונה", sys_complaints, index=0)

    rec = compose_entry(data, system, complaint)
    merge_video_links(rec, system)

    st.subheader(f"🧭 מערכת: {system} | תלונה: {complaint}")
    render_questions(rec.get("questions", []))

    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_list_with_links(rec.get("physical_exam", []), "🧍‍♂️ מה צריך לבדוק (בדיקה גופנית)")
    with col2:
        render_list_with_links(rec.get("labs", []), "🧪 בדיקות מעבדה מומלצות")
    with col3:
        render_list_with_links(rec.get("imaging", []), "🖥️ בדיקות עזר/הדמיה")

    if rec.get("notes"):
        st.markdown("---")
        st.markdown("### 🧴 המלצות/הערות")
        for n in rec["notes"]:
            st.write(f"- {n}")

    st.markdown("---")
    render_scores(rec.get("scores", []))

if __name__ == "__main__":
    main()