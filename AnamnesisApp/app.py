from __future__ import annotations
from typing import Dict, List, Any
from urllib.parse import quote_plus
from pathlib import Path
from datetime import datetime
import streamlit as st

# ========================= Page config + RTL =========================
st.set_page_config(page_title="Smart Anamnesis • תלונות", page_icon="🩺", layout="wide")
st.markdown("""
<style>
.stApp{direction:rtl}
.block-container{padding-top:12px;padding-bottom:20px}
h1,h2,h3,h4{letter-spacing:.2px;text-align:right}
p,li,span,label,.stMarkdown{text-align:right}
.card{background:rgba(255,255,255,.84);border:1px solid rgba(0,0,0,.08);border-radius:14px;padding:14px 16px}
@media (prefers-color-scheme:dark){.card{background:rgba(17,24,39,.85);border:1px solid rgba(255,255,255,.12)}}
.hr{height:1px;background:linear-gradient(90deg,transparent,rgba(128,128,128,.35),transparent);margin:12px 0 18px}
[data-testid='stSidebar']{display:none}
</style>
""", unsafe_allow_html=True)

# רענון עדין כל 5 דק' אם מותקן streamlit-autorefresh (לא חובה)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5 * 60 * 1000, limit=None, key="keepalive_5m")
    st.caption(f"⏱ רענון אחרון: {datetime.now().strftime('%H:%M:%S')}")
except Exception:
    pass

# ========================= עזרי יצירה מקוצרים =========================
def L(test: str, why: str = "", when: str = "") -> Dict[str, str]:
    o = {"test": test}
    if why:  o["why"] = why
    if when: o["when"] = when
    return o

def IMG(modality: str, trigger: str = "") -> Dict[str, str]:
    o = {"modality": modality}
    if trigger: o["trigger"] = trigger
    return o

def S(name: str, about: str = "", rule_in: str = "", rule_out: str = "", ref: str = "") -> Dict[str, str]:
    o = {"name": name}
    if about:    o["about"] = about
    if rule_in:  o["rule_in"] = rule_in
    if rule_out: o["rule_out"] = rule_out
    if ref:      o["ref"] = ref
    return o

# ========================= קישורי וידאו ברירת־מחדל לפי label =========================
DEFAULT_VIDEO_MAP: Dict[str, List[str]] = {
    # לב/נשימה
    "האזנה ללב (קצב/אוושות)": ["https://www.youtube.com/results?search_query="+quote_plus("cardiac auscultation osce")],
    "JVP ובצקות היקפיות": ["https://www.youtube.com/watch?v=Ez7KsKRi8e8"],
    "האזנה לריאות (קראקלס)": ["https://www.youtube.com/results?search_query="+quote_plus("lung auscultation osce")],
    "האזנה - צפצופים/קראקלס": ["https://www.youtube.com/results?search_query="+quote_plus("lung auscultation osce")],
    "סטורציה ו-RR": ["https://www.youtube.com/results?search_query="+quote_plus("pulse oximetry respiratory rate")],
    "POCUS לב/ריאות": ["https://www.youtube.com/results?search_query="+quote_plus("lung ultrasound B lines pleural effusion")],
    "מישוש דופן חזה": ["https://www.youtube.com/results?search_query="+quote_plus("chest wall palpation examination")],
    # נוירו
    "בדיקה נוירולוגית ממוקדת": ["https://www.youtube.com/results?search_query="+quote_plus("neurological examination osce")],
    "בדיקת ניסטגמוס": ["https://www.youtube.com/results?search_query="+quote_plus("nystagmus examination osce")],
    "Dix-Hallpike": ["https://www.youtube.com/watch?v=D6qEdlFVxig","https://www.youtube.com/watch?v=Ey7TlLJUErY"],
    # בטן
    "מישוש בטן והערכת רגישות": ["https://www.youtube.com/results?search_query="+quote_plus("abdominal examination palpation osce")],
    "סימני גירוי צפקי וריבאונד": ["https://www.youtube.com/results?search_query="+quote_plus("peritoneal signs rebound guarding exam")],
    "סימן מרפי": ["https://www.youtube.com/results?search_query="+quote_plus("Murphy sign examination")],
    "US בטן": ["https://www.youtube.com/results?search_query="+quote_plus("abdominal ultrasound basics")],
    # גניטואורינרי
    "רגישות CVA": ["https://www.youtube.com/results?search_query="+quote_plus("CVA tenderness exam")],
    "בדיקת אזור השופכה והפניס/פרינאום": ["https://www.youtube.com/results?search_query="+quote_plus("male genitourinary exam osce")],
    # א.א.ג/עיניים
    "טמפונדה קדמית אם צריך": ["https://www.youtube.com/results?search_query="+quote_plus("anterior nasal packing epistaxis")],
    "בדיקה קדמית של אף/אוזן/לוע": ["https://www.youtube.com/results?search_query="+quote_plus("ENT anterior rhinoscopy otoscopy oropharynx exam")],
    "בדיקת חדות ראייה": ["https://www.youtube.com/results?search_query="+quote_plus("visual acuity snellen osce")],
    "שדות ראייה ותנועות עיניים": ["https://www.youtube.com/results?search_query="+quote_plus("eye movements visual fields examination")],
    "פלואורסצאין/הפיכת עפעף": ["https://www.youtube.com/results?search_query="+quote_plus("eyelid eversion fluorescein")],
    # כללי
    "צילום חזה": ["https://www.youtube.com/results?search_query="+quote_plus("chest xray interpretation basics")],
}

def attach_video_links(block: Dict[str, Any]) -> None:
    for it in block.get("physical_exam", []):
        if isinstance(it, dict):
            label = (it.get("label") or "").strip()
            if label and not it.get("url"):
                url = (DEFAULT_VIDEO_MAP.get(label, []) or
                       ["https://www.youtube.com/results?search_query=" + quote_plus(label)])[0]
                it["url"] = url

# ========================= תוכן תלונות (ללא חלוקה למערכות) =========================
# אפשר להרחיב חופשי באותו פורמט. שמתי כאן סל רחב ונקי תחבירית.
COMPLAINTS: Dict[str, Dict[str, Any]] = {
    # --- לב וכלי דם ---
    "כאב בחזה": {
        "questions": [
            "מתי התחיל, משך, טריגר (מאמץ/מנוחה/לאחר אוכל)",
            "אופי כאב והקרנה (ליד/לסת/גב)",
            "תסמינים נלווים: הזעה/בחילה/קוצר נשימה/סינקופה",
            "רקע משפחתי/מחלות לב/מדללים/עישון"
        ],
        "physical_exam": [
            {"label":"האזנה ללב (קצב/אוושות)"},
            {"label":"האזנה לריאות (קראקלס)"},
            {"label":"JVP ובצקות היקפיות"},
            {"label":"מישוש דופן חזה"}
        ],
        "labs": [
            L("טרופונין סדרתי","אבחנת ACS","מידי"),
            L("BMP, גלוקוז","אלקטרוליטים/כליה"),
            L("CBC, קרישה","אנמיה/לפני התערבות")
        ],
        "imaging": [IMG("ECG מיידי","לכל כאב חזה חריג"), IMG("צילום חזה","חשד ריאתי/לבבי")],
        "scores": [
            S("HEART","סיכון ל-ACS","≥7 גבוה","0–3 נמוך"),
            S("Wells/PERC ל-PE","הסתברות ל-PE","CTA אם בינוני/גבוה","PERC לשלילה בסיכון נמוך")
        ],
        "notes": []
    },
    "דפיקות לב": {
        "questions": [
            "פתאומי/הדרגתי, משך, סדירות",
            "טריגרים: קפה/אלכוהול/מאמץ/לחץ",
            "סינקופה/קוצר נשימה/כאב בחזה/חרדה"
        ],
        "physical_exam": [
            {"label":"מדדים וסטורציה"},
            {"label":"האזנה ללב (קצב/אוושות)"}
        ],
        "labs": [L("TSH, FT4","תירוטוקסיקוזיס"), L("אלקטרוליטים כולל Mg","עוררות קצב"), L("CBC","אנמיה")],
        "imaging": [IMG("ECG 12 לידים","בעת תלונה"), IMG("Holter 24–48h","תלונות התקפיות")],
        "scores": [S("CHADS2-VASc","סיכון תרומבואמבולי בפרפור"), S("EHRA","חומרת תסמינים")],
        "notes": []
    },
    "בצקות ברגליים": {
        "questions": [
            "חד/דו צדדי, פתאומי/הדרגתי",
            "קוצר נשימה/עלייה במשקל/דיורזיס ירוד",
            "תרופות (CCB/NSAIDs/סטרואידים), מחלות רקע לב/כליה/כבד",
            "כאב/שינוי צבע/חום מקומי (DVT)"
        ],
        "physical_exam": [
            {"label":"JVP ובצקות היקפיות"},
            {"label":"האזנה ללב (קצב/אוושות)"},
            {"label":"האזנה לריאות (קראקלס)"}
        ],
        "labs": [
            L("BNP/NT-proBNP","אי ספיקת לב"),
            L("BMP","כליה/אלקטרוליטים"),
            L("תפקודי כבד + אלבומין","צירוזיס/מיימת"),
            L("CBC","אנמיה/זיהום")
        ],
        "imaging": [
            IMG("ECG","קצב/עומס"),
            IMG("Echo לב","EF ולחץ ריאתי"),
            IMG("US ורידי רגליים","בצקת חד צדדית/חשד ל-DVT")
        ],
        "scores": [S("Wells DVT","סיכון ל-DVT")],
        "notes": []
    },
    "סינקופה": {
        "questions": ["נסיבות/טריגרים/פרודרום", "משך אובדן הכרה והתאוששות", "רקע לבבי/קוצב/תרופות"],
        "physical_exam": [{"label":"מדדים כולל ל\"ד בעמידה"},{"label":"האזנה ללב (קצב/אוושות)"}],
        "labs": [L("ECG","Arrhythmia/בלוק"), L("גלוקוז","היפוגליקמיה"), L("Hb","אנמיה קשה")],
        "imaging": [IMG("Echo","אם חשד מבני"), IMG("מוניטור/הולטר","אירועים חוזרים")],
        "scores": [S("San Francisco Syncope","סיכון לאירוע חמור")],
        "notes": []
    },
    "יתר לחץ דם": {
        "questions": [
            "מדידות קודמות ומשכן",
            "תסמיני איבר מטרה: כאב חזה/קוצר נשימה/נוירולוגי/פגיעה בראייה/אוליגוריה?",
            "תרופות/החמצות/NSAIDs/קוקאין/סטימולנטים?"
        ],
        "physical_exam": [{"label":"מדדים כולל ל\"ד בשתי ידיים"},{"label":"האזנה ללב (קצב/אוושות)"},{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("BMP (Na⁺, K⁺, Cr)","כליה/אלקטרוליטים"), L("UA","חלבון/דם – פגיעה כלייתית"), L("טרופונין","לב","אם כאב חזה/תסמיני לב")],
        "imaging": [IMG("ECG","שינויים/עומס"), IMG("צילום חזה","בחשד לבצקת ריאות/קרדיומגליה")],
        "scores": [],
        "notes": [
            "Hypertensive Urgency – ל\"ד גבוה ללא פגיעה באיבר מטרה.",
            "Hypertensive Emergency – ל\"ד גבוה עם פגיעה באיבר מטרה (לב/מוח/כליה/עיניים/ריאות).",
            "Hypertensive Crisis – מטריה כללית; יש לאתר Target-organ damage."
        ]
    },

    # --- נשימה ---
    "קוצר נשימה": {
        "questions": ["פתאומי/הדרגתי? מנוחה/מאמץ?", "חום/כאב פלאוריטי/המופטיזיס/צפצופים", "PE risks: ניתוח/Immobilization/ממאירות/הריון"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"},{"label":"JVP ובצקות היקפיות"}],
        "labs": [
            L("ABG/VBG","אוורור/חמצון","מצוקה"),
            L("CBC, CRP","זיהום/דלקת"),
            L("BMP","אלקטרוליטים"),
            L("BNP/NT-proBNP","HF"),
            L("D-dimer","PE","סיכון נמוך/בינוני")
        ],
        "imaging": [IMG("צילום חזה","קו ראשון"), IMG("CT אנגיו חזה","Wells בינוני/גבוה או D-dimer חיובי"), IMG("POCUS לב/ריאות","סיוע לדיפרנציאל")],
        "scores": [S("Wells - PE","הסתברות ל-PE"), S("PERC","שלילת PE בסיכון נמוך")],
        "notes": []
    },
    "שיעול": {
        "questions": ["יבש/ליחתי, משך, חום, המופטיזיס?", "חשיפה לעישון/סביבה?"],
        "physical_exam": [{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("CRP, CBC","זיהום","לפי קליניקה")],
        "imaging": [IMG("צילום חזה","ממושך או חמור")],
        "scores": []
    },
    "המופטיזיס": {
        "questions": ["כמות/קרישים/משך", "Dyspnea/כאב פלאוריטי", "TB/ממאירות/קרישיות?"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה לריאות (קראקלס)"},{"label":"בדיקה ל-DVT ברגליים"}],
        "labs": [L("CBC","Hb/לויקוציטים"), L("קרישה","INR/aPTT"), L("סוג והצלבה","Massive"), L("D-dimer","PE","סיכון נמוך/בינוני")],
        "imaging": [IMG("צילום חזה","קו ראשון"), IMG("CTA חזה","חשד ל-PE/דימום פעיל")],
        "scores": []
    },
    "אסתמה – החמרה": {
        "questions": ["טריגר/אלרגנים/חשיפה", "שימוש במשאפים לאחרונה וכמות", "אשפוזים/אינטובציה בעבר"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"}],
        "labs": [L("ABG/VBG","חמצון/אוורור","מצוקה נשימתית")],
        "imaging": [IMG("צילום חזה","אם חשד לאטלקטזיס/פנאומוניה")],
        "scores": []
    },
    "COPD – החמרה": {
        "questions": ["כאבים בחזה","צבע ואופי כיח", "שימוש בחמצן ביתי/BiPAP", "אשפוזים קודמים"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"}],
        "labs": [
            L("ABG/VBG","Hypercapnia/Acidosis","מצוקה נשימתית"),
            L("CRP/CBC","דלקת/זיהום"),
            L("טרופונין","לב","לפי קליניקה")
        ],
        "imaging": [IMG("צילום חזה","לחיפוש סיבוך/זיהום")],
        "scores": []
    },
    "חשד לדלקת ריאות": {
        "questions": ["חום/צמרמורת/כיח", "כאב פלאוריטי/קוצר נשימה", "גורמי סיכון/aspiration"],
        "physical_exam": [{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("CBC, CRP","זיהום/דלקת")],
        "imaging": [IMG("צילום חזה","קו ראשון")],
        "scores": []
    },

    # --- נוירולוגיה ---
    "חולשת צד / חשד לשבץ": {
        "questions": ["זמן אחרון תקין (LKW)", "NIHSS: דיבור/ראייה/גפה/פנים", "אנטיקואגולציה/דימום/טראומה"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"},{"label":"לחץ דם"}],
        "labs": [L("CBC, קרישה, BMP","לפני טיפול/פרוצדורות")],
        "imaging": [IMG("CT ראש ללא ניגוד","שלילת דימום"), IMG("CTA ראש-צוואר","חשד ל-LVO")],
        "scores": [S("NIHSS","חומרת חסר")],
        "notes": []
    },
    "TIA - תסמינים שחלפו": {
        "questions": ["משך אירוע/תדירות", "יל\"ד/AF/DM/עישון", "Amaurosis fugax"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [L("גלוקוז, ליפידים, HbA1c","סיכון קרדיווסקולרי")],
        "imaging": [IMG("CTA/US קרוטידים","מקור אמבולי"), IMG("MRI דיפוזיה","אוטמים עדינים")],
        "scores": [S("ABCD2","סיכון לשבץ מוקדם","≥4 בינוני-גבוה")],
        "notes": []
    },
    "סחרחורת": {
        "questions": ["תנוחתי/התקפי/מתמשך", "שמיעה/טינטון/סימני גזע", "מדללים/לחצי דם לא מאוזנים"],
        "physical_exam": [{"label":"Dix-Hallpike"},{"label":"בדיקת ניסטגמוס"}],
        "labs": [],
        "imaging": [IMG("CTA/CTV מוח","חשד מרכזי/סימנים פוקליים")],
        "scores": [S("HINTS (למיומנים)","פריפרי מול מרכזי","Head-Impulse תקין/Skew","לא למתחילים")]
    },
    "כאב ראש": {
        "questions": ["thunderclap? החמרה חדשה?", "פוטופוביה/בחילה/חסך נוירולוגי", "דלקת כלי דם/הריון/מדללים"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"},{"label":"עורף - נוקשות"}],
        "labs": [L("CRP/ESR","Temporal arteritis >50y"), L("β-hCG","נשים בגיל הפוריות")],
        "imaging": [IMG("CT ראש","דגלים אדומים"), IMG("CTA/CTV","חשד ל-SAH/תרומבוזיס ורידי")],
        "scores": []
    },
    "פרכוס": {
        "questions": ["עדים/משך/פוסט-איקטלי", "תרופות/הפסקת אנטיאפילפטיים", "אלכוהול/סמים/חום"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [L("גלוקוז/לקטט/CK","Post-ictal"), L("אלקטרוליטים","דיסאלקטרולמיה"), L("שתן לטוקסיקולוגיה","חשד")],
        "imaging": [IMG("CT ראש","פגיעה/דימום/גידול")],
        "scores": []
    },

    # --- גסטרו ---
    "בחילות/הקאות": {
        "questions": ["משך, יכולת שתיה/אכילה", "דם בקיא/מרה/עצירות", "תרופות/הריון"],
        "physical_exam": [{"label":"סימני התייבשות"},{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [L("BMP","אלקטרוליטים/כליה"), L("גלוקוז","DKA?"), L("β-hCG","נשים בגיל הפוריות")],
        "imaging": [IMG("US/CT","לפי קליניקה")]
    },
    "כאב ברביע ימני עליון": {
        "questions": ["קוליקי/לא קוליקי, לאחר אוכל שמן", "חום/צהבת/הקאות"],
        "physical_exam": [{"label":"סימן מרפי"},{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [L("אנזימי כבד","כולסטטי/הפטוצלולרי"), L("ליפאז","דיפרנציאל לבלב"), L("CBC, CRP","דלקת")],
        "imaging": [IMG("US כיס מרה/דרכי מרה","קו ראשון"), IMG("MRCP/ERCP","חשד לאבן ב-CBD")]
    },
    "RLQ – חשד לאפנדיציטיס": {
        "questions": ["מעבר כאב מאיפיגסטריום ל-RLQ", "חום/בחילה/אנורקסיה"],
        "physical_exam": [{"label":"רגישות מקברני"},{"label":"סימני גירוי צפקי וריבאונד"}],
        "labs": [L("CBC","לויקוציטוזיס"), L("CRP","דלקת")],
        "imaging": [IMG("US/CT","לפי BMI וגיל")],
        "scores": [S("Alvarado","אפנדיציטיס","≥7 תומך","<5 מפחית")]
    },
    "דימום רקטלי": {
        "questions": ["כמות/צבע/כאב/עצירות", "מדללים/IBD/שלשולים"],
        "physical_exam": [{"label":"בדיקת PR"},{"label":"סימני היפוולמיה"}],
        "labs": [L("CBC","Hb"), L("קרישה","INR/aPTT"), L("סוג והצלבה","דימום משמעותי")],
        "imaging": [IMG("קולונוסקופיה/CT אנגיו","לפי יציבות")]
    },
    "כאב אפיגסטרי/דיספפסיה": {
        "questions": ["קשר לאוכל/NSAIDs", "ירידה במשקל/הקאות/מלנה","כאב בחזה"],
        "physical_exam": [{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [L("ליפאז","לבלב"), L("Hb","דימום כרוני")],
        "imaging": [IMG("US/CT","לפי קליניקה")]
    },

    # --- גניטואורינרי ---
    "דיזוריה/UTI": {
        "questions": ["תכיפות/צריבה/דם", "חום/כאב מותני/בחילות", "הריון/סוכרת/קטטר", "יחסי מין לא מוגנים/הפרשה"],
        "physical_exam": [{"label":"רגישות סופראפובית"},{"label":"רגישות CVA"}],
        "labs": [L("סטיק שתן + מיקרו","לויקוציטים/ניטריטים/דם"), L("תרבית שתן","אנטיביוגרמה"), L("CBC/CRP","חומרת זיהום")],
        "imaging": [IMG("US כליות/שלפוחית","Complicated/retention")]
    },
    "כאב מותני – חשד לאבן": {
        "questions": ["כאב התקפי מקרין למפשעה", "בחילות/המטוריה", "אבנים בעבר"],
        "physical_exam": [{"label":"רגישות CVA"}],
        "labs": [L("שתן כללית ותרבית","דם/זיהום"), L("קריאטינין","תפקודי כליה")],
        "imaging": [IMG("CT low-dose","רגישות גבוהה"), IMG("US","בהריון/להימנע מקרינה")]
    },

    # --- א.א.ג/עיניים ---
    "דימום אפי ספונטני": {
        "questions": ["חד/דו צדדי, טראומה/חיטוט/מדללים", "יתר ל\"ד?"],
        "physical_exam": [{"label":"בדיקה קדמית של אף/אוזן/לוע"},{"label":"טמפונדה קדמית אם צריך"}],
        "labs": [L("CBC","Hb"), L("קרישה","INR/aPTT","מדללים")]
    },
    "כאב גרון": {
        "questions": ["חום/דיספגיה/ריח רע/פריחה"],
        "physical_exam": [{"label":"בדיקת לוע ובלוטות"}],
        "labs": [L("Strep swab","אם חשד סטרפטוקוק"),L("CBC","זיהום אקוטי")]
    },
    "Red eye": {
        "questions": ["כאב/פוטופוביה/הפרשות/עדשות מגע", "טראומה/גוף זר"],
        "physical_exam": [{"label":"בדיקת חדות ראייה"},{"label":"פלואורסצאין/הפיכת עפעף"}],
        "notes": ["עדשות מגע - כיסוי פסאודומונס"]
    },

    # --- אנדוקריני ---
    "היפרגליקמיה": {
        "questions": ["פוליאוריה/פולידיפסיה/ירידה במשקל", "בחילות/כאבי בטן/ישנוניות (DKA/HHS)", "זיהום? סטרואידים? החמצת אינסולין?"],
        "physical_exam": [{"label":"מדדים"},{"label":"התייבשות/טורגור"},{"label":"נשימות קוסמאל"},{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [
            L("גלוקוז מיידי","אישור","מידי"),
            L("BMP","אלקטרוליטים/כליה"),
            L("VBG/ABG + pH","חמצת","חשד ל-DKA/HHS"),
            L("קטונים בדם/שתן","DKA"),
            L("CBC/CRP","מוקד זיהומי"),
            L("אוסמולריות","HHS"),
            L("ECG","K⁺ חריג")
        ],
        "scores": [S("qSOFA","אם חשד לזיהום")],
        "notes": ["אם DKA/HHS - נוזלים, K⁺, אינסולין IV, טיפול במוקד"]
    },

    # --- זיהומיות/עור ---
    "חום לא ברור": {
        "questions": ["משך/שעות/רעד/מסעות/חשיפות/חיות/אנטיביוטיקה", "מחלות רקע וחיסונים"],
        "physical_exam": [{"label":"בדיקה שיטתית מלאה"}],
        "labs": [
            L("CBC, CRP","דלקת/זיהום"),
            L("תרביות דם x2","אם חום גבוה/ספסיס"),
            L("שתן כללית ותרבית","מוקד"),
            L("כימיה/תפקודי כבד","מוקד")
        ],
        "imaging": [IMG("צילום חזה","מוקד נשימתי")],
        "scores": [S("qSOFA","ספסיס")]
    },
    "אבצס/צלוליטיס": {
        "questions": ["משך/כאב/חום מקומי או סיסטמי", "מחלת רקע/דיכוי חיסון"],
        "physical_exam": [{"label":"בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)"}],
        "labs": [L("CBC, CRP","דלקת/זיהום","אם חום/צלוליטיס")],
        "imaging": [IMG("US רקמות רכות","חשד לאבצס")]
    },

    # --- שריר-שלד / טראומה / כללי ---
    "כאב גב תחתון": {
        "questions": ["red flags: חום/ירידה במשקל/חסך נוירולוגי/אי שליטה בסוגרים", "טראומה/פעילות חריגה"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [],
        "imaging": [IMG("MRI/CT","אם red flags/חשד דחוף")]
    },
    "לחץ דם נמוך/שוק": {
        "questions": ["חום/זיהום/דימום/אלרגיה/טראומה", "נוזלים/תרופות"],
        "physical_exam": [{"label":"מדדים ושוק"},{"label":"בדיקה שיטתית מלאה"}],
        "labs": [L("CBC","Hb/לויקוציטים"), L("BMP","כליה/אלקטרוליטים"), L("לקטט","היפופרפוזיה"), L("תרביות דם","אם חום")],
        "imaging": [IMG("POCUS לב/ריאות","הכוונת דיפרנציאל")],
        "scores": [S("qSOFA","ספסיס")]
    },
}

# צרף קישורי וידאו אוטומטית לכל תלונה
for blk in COMPLAINTS.values():
    attach_video_links(blk)

# ========================= UI — שורה אחת בלבד =========================
st.title("🩺 Smart Anamnesis – תלונות (ללא חלוקה למערכות)")
st.caption(f"סה\"כ תלונות מוגדרות: {len(COMPLAINTS)}")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

names = sorted(COMPLAINTS.keys())
sel = st.selectbox("בחר תלונה להצגה", options=["— בחר תלונה —"] + names, index=0, key="complaint_select")

def render_questions(qs: List[str]) -> None:
    st.markdown("#### אנמנזה - מה לשאול")
    if not qs:
        st.write("- אין שאלות מוגדרות"); return
    for q in qs:
        st.write(f"- {q}")

def render_list_with_links(items: Any, title: str) -> None:
    st.markdown(f"#### {title}")
    if not items:
        st.write("- אין פריטים"); return
    for item in items:
        if isinstance(item, dict) and "label" in item:
            label = item.get("label",""); url = item.get("url","")
            st.markdown(f"- {'▶️ ' if url else ''}[{label}]({url})" if url else f"- {label}")
        elif isinstance(item, dict) and "test" in item:
            test=item.get("test",""); why=item.get("why",""); when=item.get("when","")
            line=f"- **{test}**"
            if why:  line += f" — למה: {why}"
            if when: line += f" — מתי: {when}"
            st.markdown(line)
        elif isinstance(item, dict) and "modality" in item:
            modality=item.get("modality",""); trig=item.get("trigger","")
            st.markdown(f"- **{modality}**" + (f" — מתי: {trig}" if trig else ""))
        else:
            st.markdown(f"- {str(item)}")

def render_scores(scores: Any) -> None:
    st.markdown("#### 📊 SCORES רלוונטיים")
    if not scores:
        st.write("- אין scores מוגדרים"); return
    for s in scores:
        if isinstance(s, dict):
            name = s.get("name","")
            about = s.get("about","")
            ri = s.get("rule_in","")
            ro = s.get("rule_out","")
            ref = s.get("ref","")
            st.markdown(f"- **{name}**" + (f" — {about}" if about else ""))
            if ri: st.caption(f"Rule-in: {ri}")
            if ro: st.caption(f"Rule-out: {ro}")
            if ref: st.caption(f"ⓘ {ref}")
        else:
            st.markdown(f"- **{str(s)}**")

def render_block_plain(blk: Dict[str,Any]) -> None:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    render_questions(blk.get("questions", []))
    st.markdown("</div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_list_with_links(blk.get("physical_exam", []), "🧍‍♂️ מה לבדוק (בדיקה גופנית)")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_list_with_links(blk.get("labs", []), "🧪 מעבדה")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_list_with_links(blk.get("imaging", []), "🖥️ הדמיה")
        st.markdown("</div>", unsafe_allow_html=True)

    if blk.get("notes"):
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown("#### 🧴 הערות והמלצות")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for n in blk["notes"]:
            st.write(f"- {n}")
        st.markdown("</div>", unsafe_allow_html=True)

    if blk.get("scores"):
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_scores(blk.get("scores", []))
        st.markdown("</div>", unsafe_allow_html=True)

# הצגה
if sel in COMPLAINTS:
    st.markdown(f"### {sel}")
    render_block_plain(COMPLAINTS[sel])

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Smart Anamnesis • התוכן להכוונה קלינית בלבד ואינו מחליף שיקול דעת רפואי • נכתב ע\"י לירן שחר")
