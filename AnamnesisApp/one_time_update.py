from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

BASE = Path(__file__).parent
EXCEL_PATH = BASE / "AAA.xlsx"     # ← ודא שהשם תואם לקובץ שהעלית
KNOWLEDGE_OUT = BASE / "knowledge.json"
VIDEO_OUT = BASE / "video_links.json"

# ---------------- Utils ----------------
def split_clean(s: Any) -> List[str]:
    """פיצול טקסט לרשימה לפי שורות/תבליטים/פסיקים/מקפים והסרת רעשים."""
    if not isinstance(s, str) or not s.strip():
        return []
    parts = re.split(r"[\n\r;•·\u2022,]+|\s*[-–—]+\s*", s)
    out: List[str] = []
    for p in parts:
        p = p.strip(" \t:.;-–—")
        if p and p not in out:
            out.append(p)
    return out

def norm_label(t: str) -> str:
    """נירמול קל של labels כדי לצמצם וריאנטים קטנים."""
    t = (t or "").strip()
    t = re.sub(r"\s+", " ", t)
    # התאמות נפוצות
    t = t.replace("פלואורסצאין / הפיכת עפעף", "פלואורסצאין/הפיכת עפעף")
    t = t.replace("האזנה לריאות - צפצופים/קראקלס", "האזנה לריאות (קראקלס)")
    t = t.replace("JVP ובצקות", "JVP ובצקות היקפיות")
    if t == "JVP":
        t = "JVP ובצקות היקפיות"
    if t == "האזנה לריאות":
        t = "האזנה לריאות (קראקלס)"
    if t == "מישוש בטן":
        t = "מישוש בטן והערכת רגישות"
    if t == "סימני גירוי צפקי":
        t = "סימני גירוי צפקי וריבאונד"
    return t

# ---------------- סרטונים (label → urls) ----------------
EXAM_LABEL_TO_URLS: Dict[str, List[str]] = {
    # לב וכלי דם / נשימה
    "האזנה ללב (קצב/אוושות)": ["https://www.youtube.com/results?search_query=cardiac+auscultation+osce"],
    "JVP ובצקות היקפיות": ["https://www.youtube.com/watch?v=Ez7KsKRi8e8"],
    "JVP": ["https://www.youtube.com/watch?v=Ez7KsKRi8e8"],  # כינוי נוסף כדי להתאים ל-labelים קצרים
    "האזנה לריאות (קראקלס)": ["https://www.youtube.com/results?search_query=lung+auscultation+osce"],
    "האזנה לריאות": ["https://www.youtube.com/results?search_query=lung+auscultation+osce"],  # כיסוי גם בלי "(קראקלס)"
    "סטורציה ו-RR": ["https://www.youtube.com/results?search_query=pulse+oximetry+respiratory+rate"],
    "POCUS לב/ריאות": ["https://www.youtube.com/results?search_query=lung+ultrasound+B+lines+pleural+effusion"],
    "מישוש דופן חזה": ["https://www.youtube.com/results?search_query=chest+wall+palpation+examination"],

    # נוירו
    "בדיקה נוירולוגית ממוקדת/עצבי גולגולת": ["https://www.youtube.com/results?search_query=cranial+nerve+examination+osce"],
    "בדיקה נוירולוגית ממוקדת": ["https://www.youtube.com/results?search_query=neurological+examination+osce"],
    "עצבי גולגולת": ["https://www.youtube.com/results?search_query=cranial+nerve+examination+osce"],
    "Dix-Hallpike": ["https://www.youtube.com/watch?v=D6qEdlFVxig", "https://www.youtube.com/watch?v=Ey7TlLJUErY"],
    "בדיקת ניסטגמוס": ["https://www.youtube.com/results?search_query=nystagmus+examination+osce"],

    # בטן
    "מישוש בטן והערכת רגישות": ["https://www.youtube.com/results?search_query=abdominal+examination+palpation+osce"],
    "מישוש בטן": ["https://www.youtube.com/results?search_query=abdominal+examination+palpation+osce"],  # למקרה שמופיע בלי "והערכת רגישות"
    "סימני גירוי צפקי וריבאונד": ["https://www.youtube.com/results?search_query=peritoneal+signs+rebound+guarding+exam"],
    "סימן מרפי": ["https://www.youtube.com/results?search_query=Murphy+sign+examination"],
    "US בטן": ["https://www.youtube.com/results?search_query=abdominal+ultrasound+basics"],

    # שתן/גניטואורינרי
    "רגישות CVA": ["https://www.youtube.com/results?search_query=CVA+tenderness+exam"],
    "בדיקת אזור השופכה והפניס/פרינאום": ["https://www.youtube.com/results?search_query=male+genitourinary+exam+osce"],

    # א.א.ג
    "טמפונדה קדמית אם צריך": ["https://www.youtube.com/results?search_query=anterior+nasal+packing+epistaxis"],
    "טמפונדה קדמית": ["https://www.youtube.com/results?search_query=anterior+nasal+packing+epistaxis"],  # כיסוי בלי "אם צריך"
    "בדיקה קדמית של אף/אוזן/לוע": ["https://www.youtube.com/results?search_query=ENT+anterior+rhinoscopy+otoscopy+oropharynx+exam"],

    # עור
    "הערכת עור - מורפולוגיה והתפשטות": ["https://www.youtube.com/results?search_query=skin+examination+osce"],
    "הערכת עור": ["https://www.youtube.com/results?search_query=skin+examination+osce"],  # קיצור נפוץ
    "בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)": ["https://www.youtube.com/results?search_query=soft+tissue+infection+abscess+exam"],
    "בדיקה ל-DVT ברגליים": ["https://www.youtube.com/results?search_query=POCUS+DVT+compression+ultrasound"],

    # עיניים
    "בדיקת חדות ראייה": ["https://www.youtube.com/results?search_query=visual+acuity+snellen+osce"],
    "שדות ראייה ותנועות עיניים": ["https://www.youtube.com/results?search_query=eye+movements+visual+fields+examination"],
    "פלואורסצאין/הפיכת עפעף": ["https://www.youtube.com/results?search_query=eyelid+eversion+fluorescein"],

    # עזר כללי
    "צילום חזה": ["https://www.youtube.com/results?search_query=chest+xray+interpretation+basics"],
}

# התאמות טקסט חופשי → label
KEYWORD_TO_LABEL = [
    (r"Dix[- ]?Hallpike|דיקס", "Dix-Hallpike"),
    (r"ניסטגמוס", "בדיקת ניסטגמוס"),
    (r"חדות.*ראי|snellen", "בדיקת חדות ראייה"),
    (r"שדות.*עיניי|eye movements|visual fields", "שדות ראייה ותנועות עיניים"),
    (r"פלואורסצאין|עפעף", "פלואורסצאין/הפיכת עפעף"),
    (r"murphy|מרפי", "סימן מרפי"),
    (r"צפק|rebound|guarding", "סימני גירוי צפקי וריבאונד"),
    (r"\bCVA\b|קוסטו", "רגישות CVA"),
    (r"lung.*auscult|האזנה.*ריאות|צפצופים|קראקלס", "האזנה לריאות (קראקלס)"),
    (r"JVP", "JVP ובצקות היקפיות"),
    (r"auscult.*heart|האזנה.*לב|אוושות", "האזנה ללב (קצב/אוושות)"),
    (r"POCUS.*(לב|ריאות)|US.*ריאות", "POCUS לב/ריאות"),
    (r"US.*בטן|אולטרה.*בטן", "US בטן"),
    (r"עור|skin", "הערכת עור - מורפולוגיה והתפשטות"),
    (r"soft tissue|אבצס|צלוליט", "בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)"),
    (r"nasal.*pack|טמפונד", "טמפונדה קדמית אם צריך"),
    (r"otoscopy|רינוסקופ|לוע", "בדיקה קדמית של אף/אוזן/לוע"),
    (r"chest wall|דופן חזה", "מישוש דופן חזה"),
    (r"\bCXR\b|צילום חזה", "צילום חזה"),
    (r"cranial nerve|עצבי גולגולת", "בדיקה נוירולוגית ממוקדת/עצבי גולגולת"),
    (r"neurological exam|בדיקה נוירולוגית", "בדיקה נוירולוגית ממוקדת"),
    (r"\bDVT\b|Compression", "בדיקה ל-DVT ברגליים"),
]

HEADER_ALIASES = {
    "מערכת": ["מערכת", "System"],
    "תלונה": ["תלונה", "Complaint", "Chief complaint"],
    "שאלות לשאול": ["שאלות לשאול", "Questions", "מה לשאול"],
    "מה צריך לבדוק": ["מה צריך לבדוק", "בדיקה גופנית", "Physical exam", "מה לבדוק"],
    "מעבדה": ["מעבדה", "Laboratory", "Labs"],
    "דימות": ["דימות", "הדמיה", "Imaging", "צילום/CT/MRI"],
    "SCORES": ["SCORES", "Scores", "סקורים"],
    "המלצות": ["המלצות", "Notes", "הערות"],
    "סרטונים": ["סרטונים", "Videos"],
    "אבחנה מבדלת": ["אבחנה מבדלת", "Differential", "Dx diff"],
}

def _col(df: pd.DataFrame, key: str) -> str:
    for cand in HEADER_ALIASES[key]:
        if cand in df.columns:
            return cand
    return ""

def guess_labels(text: str) -> List[str]:
    labs: List[str] = []
    if not isinstance(text, str):
        return labs
    for pat, lab in KEYWORD_TO_LABEL:
        if re.search(pat, text, flags=re.I):
            lab = norm_label(lab)
            if lab not in labs:
                labs.append(lab)
    return labs

def enrich_special(complaint: str, block: Dict[str, Any]) -> None:
    """העשרות ייעודיות לפי תלונה (יתר ל״ד, המופטיזיס)."""
    comp = complaint or ""
    # יתר לחץ דם
    if ("לחץ דם" in comp) or ("יתר לחץ" in comp):
        notes = block.setdefault("notes", [])
        extra = [
            "סיווג: **Hypertensive Urgency** – ל״ד גבוה ללא פגיעה באיבר מטרה.",
            "סיווג: **Hypertensive Emergency** – ל״ד גבוה עם פגיעה באיבר מטרה (לב/מוח/כליה/עיניים/ריאות).",
            "סיווג: **Hypertensive Crisis** – מונח מטרייה; לאתר Target-organ damage."
        ]
        for n in extra:
            if n not in notes:
                notes.append(n)

        q = block.setdefault("questions", [])
        for s in [
            "תסמיני איבר מטרה: כאב חזה/קוצר נשימה/הפרעה נוירולוגית/פגיעה בראייה/אוליגוריה?",
            "תרופות/החמצות/NSAIDs/קוקאין/סטימולנטים?"
        ]:
            if s not in q:
                q.append(s)

        labs = block.setdefault("labs", [])
        def addlab(test, why="", when=""):
            item = {"test": test}
            if why: item["why"] = why
            if when: item["when"] = when
            if item not in labs: labs.append(item)
        addlab("טרופונין", "לב", "אם כאב חזה/תסמיני לב")
        addlab("BMP (Na⁺, K⁺, Cr)", "כליה/אלקטרוליטים")
        addlab("שתן כללית (UA)", "חלבון/דם – פגיעה כלייתית")
        imaging = block.setdefault("imaging", [])
        cxr = {"modality": "צילום חזה", "trigger": "חשד לבצקת ריאות/קרדיומגליה"}
        if cxr not in imaging:
            imaging.append(cxr)

    # המופטיזיס – העשרות
    if comp.strip() in ("המופטיזיס", "Hemoptysis"):
        q = block.setdefault("questions", [])
        for s in [
            "חזרה מחו\"ל/immobilization/ממאירות/גלולות/קרישיות יתר?",
            "דפיקות לב/כאבי חזה?"
        ]:
            if s not in q:
                q.append(s)
        labs = block.setdefault("labs", [])
        dd = {"test": "D-dimer", "why": "PE", "when": "סיכון נמוך/בינוני"}
        if dd not in labs:
            labs.append(dd)
        phys = block.setdefault("physical_exam", [])
        if {"label": "בדיקה ל-DVT ברגליים"} not in phys:
            phys.append({"label": "בדיקה ל-DVT ברגליים"})

# ---------------- Main ----------------
def main():
    if not EXCEL_PATH.exists():
        raise SystemExit(f"לא נמצא הקובץ: {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH)
    df.columns = [str(c).strip() for c in df.columns]

    # ניסיון לשמר generic_by_system מקובץ קיים (אם יש)
    existing_generic: Dict[str, Any] = {}
    existing_systems: Dict[str, Dict[str, Any]] = {}
    if KNOWLEDGE_OUT.exists():
        try:
            existing = json.loads(KNOWLEDGE_OUT.read_text(encoding="utf-8"))
            if isinstance(existing.get("generic_by_system"), dict):
                existing_generic = existing["generic_by_system"]
            if isinstance(existing.get("systems"), dict):
                existing_systems = existing["systems"]
        except Exception:
            pass

    # עמודות חובה
    system_col = _col(df, "מערכת")
    comp_col   = _col(df, "תלונה")
    if not system_col or not comp_col:
        raise SystemExit("❌ חסרות עמודות חובה: 'מערכת' ו/או 'תלונה'")

    # עמודות רשות
    q_col     = _col(df, "שאלות לשאול")
    pe_col    = _col(df, "מה צריך לבדוק")
    lab_col   = _col(df, "מעבדה")
    img_col   = _col(df, "דימות")
    score_col = _col(df, "SCORES")
    notes_col = _col(df, "המלצות")
    vids_col  = _col(df, "סרטונים")
    diff_col  = _col(df, "אבחנה מבדלת")

    systems_map: Dict[str, Dict[str, Any]] = dict(existing_systems)  # מתחילים מהקיים
    videos_map: Dict[str, Dict[str, List[str]]] = {}

    for _, row in df.iterrows():
        system = str(row.get(system_col, "")).strip()
        complaint = str(row.get(comp_col, "")).strip()
        if not system or not complaint:
            continue

        questions = split_clean(row.get(q_col, "")) if q_col else []
        physical_raw = str(row.get(pe_col, "")) if pe_col else ""
        labs_raw = str(row.get(lab_col, "")) if lab_col else ""
        imaging_raw = str(row.get(img_col, "")) if img_col else ""
        scores_raw = str(row.get(score_col, "")) if score_col else ""
        notes_raw = str(row.get(notes_col, "")) if notes_col else ""
        videos_raw = str(row.get(vids_col, "")) if vids_col else ""
        diff_raw = str(row.get(diff_col, "")) if diff_col else ""

        # Physical exam
        phys_labels = [norm_label(x) for x in split_clean(physical_raw)]
        for g in guess_labels(physical_raw):
            if g not in phys_labels:
                phys_labels.append(g)
        physical_exam = [{"label": lab} for lab in phys_labels] if phys_labels else []

        # Labs
        labs: List[Dict[str, str]] = []
        for t in split_clean(labs_raw):
            test_name = t.strip()
            item: Dict[str, str] = {"test": test_name}
            if re.search(r"D-?dimer|די[- ]?דימר", test_name, flags=re.I):
                item.setdefault("why", "PE")
                item.setdefault("when", "סיכון נמוך/בינוני")
            labs.append(item)

        # Imaging
        imaging: List[Dict[str, str]] = []
        for m in split_clean(imaging_raw):
            trig = ""
            if re.search(r"קו ראשון", m): trig = "קו ראשון"
            elif re.search(r"חשד|לפי קליניקה|when|trigger", m): trig = "לפי קליניקה/חשד"
            modality = re.sub(r"\s*-\s*.*$", "", m).strip()
            imaging.append({"modality": modality, "trigger": trig})

        # Scores
        scores = [{"name": s} for s in split_clean(scores_raw)]

        # Notes + Differential
        notes = split_clean(notes_raw)
        diffs = split_clean(diff_raw)
        if diffs:
            notes.append("אבחנה מבדלת: " + "; ".join(diffs))
            # גם כשאלה לשים לב לדיפרנציאל
            questions.append("שקול באבחנה מבדלת: " + ", ".join(diffs))

        block = {
            "questions": questions,
            "physical_exam": physical_exam,
            "labs": labs,
            "imaging": imaging,
            "scores": scores,
            "notes": notes,
        }

        # העשרות
        enrich_special(complaint, block)

        # עדכון/החלפה של התלונה תחת המערכת
        systems_map.setdefault(system, {})
        systems_map[system][complaint] = block

        # סרטונים: לפי labels שנתפסו
        videos_map.setdefault(system, {})
        labels_for_videos = set(phys_labels) | set(guess_labels(videos_raw))
        for lab in labels_for_videos:
            if not lab:
                continue
            lab_n = norm_label(lab)
            urls = EXAM_LABEL_TO_URLS.get(lab_n) or [
                f"https://www.youtube.com/results?search_query={re.sub(r'\\s+','+',lab_n)}"
            ]
            videos_map[system].setdefault(lab_n, [])
            for u in urls:
                if u not in videos_map[system][lab_n]:
                    videos_map[system][lab_n].append(u)

    # בונים knowledge.json
    knowledge = {
        "metadata": {"version": "1.0.0", "language": "he", "notes": "נבנה אוטומטית מ'מעודכן.xlsx' (כולל מיזוג עם קיים)"},
        "generic_by_system": existing_generic or {},   # שימור הגנרי הקיים
        "systems": systems_map,
    }

    # בונים video_links.json
    videos_clean: Dict[str, List[Dict[str, List[str]]]] = {}
    for sys_name, label2urls in videos_map.items():
        videos_clean[sys_name] = [{"label": k, "urls": v} for k, v in label2urls.items()]

    KNOWLEDGE_OUT.write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")
    VIDEO_OUT.write_text(
        json.dumps({"metadata": {"version": "1.0.0", "notes": "נוצר אוטומטית מהאקסל"}, **videos_clean},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("✅ נוצרו/עודכנו:")
    print(f" - {KNOWLEDGE_OUT}")
    print(f" - {VIDEO_OUT}")
    total_systems = len(systems_map)
    total_complaints = sum(len(v) for v in systems_map.values())
    print(f"📦 סה\"כ מערכות: {total_systems} | סה\"כ תלונות: {total_complaints}")

if __name__ == "__main__":
    main()



