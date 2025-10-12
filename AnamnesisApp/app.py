from __future__ import annotations
from typing import Dict, List, Any, Tuple
from urllib.parse import quote_plus
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
from datetime import datetime
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5 * 60 * 1000, limit=None, key="keepalive_5m")
    st.caption(f"⏱ רענון אחרון: {datetime.now().strftime('%H:%M:%S')}")
except Exception:
    # אם החבילה לא מותקנת – לא נקרוס
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
    "בדיקה נוירולוגית ממוקדת/עצבי גולגולת": ["https://www.youtube.com/results?search_query="+quote_plus("cranial nerve examination osce")],
    "עצבי גולגולת": ["https://www.youtube.com/results?search_query="+quote_plus("cranial nerve examination osce")],
    "Dix-Hallpike": ["https://www.youtube.com/watch?v=D6qEdlFVxig","https://www.youtube.com/watch?v=Ey7TlLJUErY"],
    "בדיקת ניסטגמוס": ["https://www.youtube.com/results?search_query="+quote_plus("nystagmus examination osce")],
    # בטן
    "מישוש בטן והערכת רגישות": ["https://www.youtube.com/results?search_query="+quote_plus("abdominal examination palpation osce")],
    "סימני גירוי צפקי וריבאונד": ["https://www.youtube.com/results?search_query="+quote_plus("peritoneal signs rebound guarding exam")],
    "סימן מרפי": ["https://www.youtube.com/results?search_query="+quote_plus("Murphy sign examination")],
    "US בטן": ["https://www.youtube.com/results?search_query="+quote_plus("abdominal ultrasound basics")],
    # גניטואורינרי
    "רגישות CVA": ["https://www.youtube.com/results?search_query="+quote_plus("CVA tenderness exam")],
    "בדיקת אזור השופכה והפניס/פרינאום": ["https://www.youtube.com/results?search_query="+quote_plus("male genitourinary exam osce")],
    # א.א.ג
    "טמפונדה קדמית אם צריך": ["https://www.youtube.com/results?search_query="+quote_plus("anterior nasal packing epistaxis")],
    "בדיקה קדמית של אף/אוזן/לוע": ["https://www.youtube.com/results?search_query="+quote_plus("ENT anterior rhinoscopy otoscopy oropharynx exam")],
    # עור
    "הערכת עור - מורפולוגיה והתפשטות": ["https://www.youtube.com/results?search_query="+quote_plus("skin examination osce")],
    "בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)": ["https://www.youtube.com/results?search_query="+quote_plus("soft tissue infection abscess exam")],
    "בדיקה ל-DVT ברגליים": ["https://www.youtube.com/results?search_query="+quote_plus("POCUS DVT compression ultrasound")],
    # עיניים
    "בדיקת חדות ראייה": ["https://www.youtube.com/results?search_query="+quote_plus("visual acuity snellen osce")],
    "שדות ראייה ותנועות עיניים": ["https://www.youtube.com/results?search_query="+quote_plus("eye movements visual fields examination")],
    "פלואורסצאין/הפיכת עפעף": ["https://www.youtube.com/results?search_query="+quote_plus("eyelid eversion fluorescein")],
    # עזר כללי
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

# ========================= תוכן התלונות (ללא חלוקה למערכות) =========================
# הערה: זהו seed רחב ומוכן לעבודה. ניתן להרחיב/לשנות כל תלונה בקלות.
COMPLAINTS: Dict[str, Dict[str, Any]] = {
    # --- לב וכלי דם ---
    "כאב בחזה": {
        "questions": ["מחלת חום או שיעול","רקע משפחתי","מתי התחיל", "אופי כאב והקרנה", "טריגר - מאמץ/מנוחה/לאחר אוכל", "הזעה/בחילה/קוצר נשימה"],
        "physical_exam": [{"label":"האזנה ללב (קצב/אוושות)"},{"label":"האזנה לריאות (קראקלס)"},{"label":"JVP ובצקות היקפיות"},{"label":"מישוש דופן חזה"}],
        "labs": [L("טרופונין סדרתי","אבחנת ACS","מידי"), L("BMP, גלוקוז","אלקטרוליטים/כליה"), L("CBC, קרישה","אנמיה/לפני התערבות")],
        "imaging": [IMG("ECG מיידי","לכל כאב חזה חריג"), IMG("צילום חזה","חשד ריאתי/לבבי")],
        "scores": [S("HEART","סיכון ל-ACS","≥7 גבוה","0-3 נמוך"), S("Wells/PERC ל-PE","הסתברות ל-PE","CTA אם בינוני/גבוה","PERC לשלילה בסיכון נמוך")],
        "notes": []
    },
    "דפיקות לב": {
        "questions": [" פתאומי/הדרגתי, משך", "קצב סדיר/לא סדיר", "טריגרים - קפה/אלכוהול/מאמץ/לחץ", "סינקופה/קוצר נשימה/כאב בחזה"],
        "physical_exam": [{"label":"מדדים וסטורציה"},{"label":"האזנה ללב (קצב/אוושות)"}],
        "labs": [L("TSH, T4","תירוטוקסיקוזיס"), L("אלקטרוליטים כולל Mg","עוררות קצב"), L("CBC","אנמיה")],
        "imaging": [IMG("ECG 12 לידים","בעת תלונה"), IMG("Holter 24-48h","תלונות התקפיות")],
        "scores": [S("CHADS2-VASc","סיכון תרומבואמבולי בפרפור","גבוה - אנטיקואגולציה","0 בגבר לרוב ללא"), S("EHRA","חומרת תסמינים")],
        "notes": []
    },
    "בצקות ברגליים": {
        "questions": ["פתאומי/הדרגתי, חד/דו צדדי", "קוצר נשימה/עלייה במשקל/דיורזיס ירוד", "תרופות: CCB/NSAIDs/סטרואידים", "אי ספיקת לב/כליות/כבד", "כאב/חום מקומי/שינוי צבע (DVT)"],
        "physical_exam": [{"label":"JVP ובצקות היקפיות"},{"label":"האזנה ללב (קצב/אוושות)"},{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("BNP/NT-proBNP","אי ספיקת לב","בכל חשד"), L("BMP","כליה/אלקטרוליטים","מקרה חדש"), L("תפקודי כבד + אלבומין","צירוזיס/מיימת"), L("CBC","אנמיה/זיהום")],
        "imaging": [IMG("ECG","קצב/עומס"), IMG("Echo לב","EF ולחץ ריאתי"), IMG("US ורידים תחתונים","בצקת חד צדדית")],
        "scores": [S("Framingham HF","קריטריונים ל-HF","≥2 גדולים"), S("NYHA","דרגת תפקוד"), S("Wells DVT","סיכון ל-DVT","≥2 - US","<2 + D-dimer שלילי")],
        "notes": []
    },
    "סינקופה": {
        "questions": ["נסיבות האירוע, טריגרים, פרודרום", "משך אובדן הכרה והתאוששות", "רקע לבבי/קוצב/תרופות"],
        "physical_exam": [{"label":"אורתוסטטזים-מדדים כולל לחץ דם בעמידה"},{"label":"האזנה ללב (קצב/אוושות)"}],
        "labs": [L("ECG","Arrhythmia/בלוק"), L("גלוקוז","היפוגליקמיה"), L("Hb","אנמיה קשה")],
        "imaging": [IMG("Echo","אם חשד מבני"), IMG("מוניטור/הולטר","אירועים חוזרים")],
        "scores": [S("San Francisco Syncope","סיכון לאירוע חמור","נוכחות קריטריון מעלה סיכון")],
        "notes": []
    },
    "יתר לחץ דם": {
        "questions": ["מדידות קודמות ומשכן", "תסמיני איבר מטרה: כאב חזה/קוצר נשימה/נוירולוגי/פגיעה בראייה/אוליגוריה?", "תרופות/החמצות/NSAIDs/קוקאין/סטימולנטים?"],
        "physical_exam": [{"label":"מדדים כולל ל\"ד בשתי ידיים"},{"label":"האזנה ללב (קצב/אוושות)"},{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("BMP (Na⁺, K⁺, Cr)","כליה/אלקטרוליטים"), L("UA","חלבון/דם – פגיעה כלייתית"), L("טרופונין","לב","אם כאב חזה/תסמיני לב")],
        "imaging": [IMG("ECG","שינויים/עומס"), IMG("צילום חזה","בחשד לבצקת ריאות/קרדיומגליה")],
        "scores": [],
        "notes": [
            "סיווג: **Hypertensive Urgency** – ל\"ד גבוה ללא פגיעה באיבר מטרה.",
            "סיווג: **Hypertensive Emergency** – ל\"ד גבוה עם פגיעה באיבר מטרה (לב/מוח/כליה/עיניים/ריאות).",
            "סיווג: **Hypertensive Crisis** – מטריה כללית; יש לאתר Target-organ damage."
        ]
    },

    # --- נשימה ---
    "קוצר נשימה": {
        "questions": ["פתאומי/הדרגתי? מנוחה/מאמץ?", "חום/כאב פלאוריטי/המופטיזיס/צפצופים", "PE risks: ניתוח/Immobilization/סרטן/הריון"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"},{"label":"JVP ובצקות היקפיות"}],
        "labs": [L("ABG/VBG","אוורור/חמצון","מצוקה"), L("CBC, CRP","זיהום/דלקת"), L("BMP","אלקטרוליטים"), L("BNP/NT-proBNP","HF"), L("D-dimer","PE","סיכון נמוך/בינוני")],
        "imaging": [IMG("צילום חזה","קו ראשון"), IMG("CT אנגיו חזה","Wells בינוני/גבוה או D-dimer חיובי"), IMG("POCUS לב/ריאות","סיוע לדיפרנציאל")],
        "scores": [S("Wells - PE","הסתברות ל-PE","CTA אם בינוני/גבוה","PERC לשלילה בסיכון נמוך"), S("PERC","שלילת PE בסיכון נמוך","", "כל הקריטריונים שליליים")],
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
        "questions": ["טריגר/אלרגנים/חשיפה", "שימוש במשאפים לאחרונה וכמות משאפים", "אשפוזים/אינטובציה בעבר"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"}],
        "labs": [L("ABG/VBG","גזים מהירים","חמצון/אוורור","מצוקה נשימתית")],
        "imaging": [IMG("צילום חזה","אם יש חשד לאטלקטזיס/פנאומוניה ")],
        "scores": []
    },
    "COPD – החמרה": {
        "questions": ["כאבים בחזה","צבע ואופי כיח/מחלת חום", "שימוש בחמצן ביתי/BiPAP", "אשפוזים קודמים"],
        "physical_exam": [{"label":"סטורציה ו-RR"},{"label":"האזנה - צפצופים/קראקלס"}],
        "labs": [L("ABG/VBG","Hypercapnia/Acidosis","מצוקה נשימתית","טרופונין","גזים מהירים")],
        "imaging": [IMG("צילום חזה","לחיפוש סיבוך/זיהום")],
        "scores": []
    },
    "חשד לדלקת ריאות ": {
        "questions": ["חום/צמרמורת","חום/צמרמורות/כיח", "כאב פלאוריטי/קוצר נשימה", "גורמי סיכון/ Aspiration"],
        "physical_exam": [{"label":"האזנה לריאות (קראקלס)"}],
        "labs": [L("CBC, CRP","זיהום/דלקת")],
        "imaging": [IMG("צילום חזה","קו ראשון")],
        "scores": []
    },

    # --- נוירולוגיה ---
    "חולשת צד / חשד לשבץ": {
        "questions": ["זמן אחרון תקין (LKW)", "תסמיני NIHSS - דיבור/ראייה/גפה/פנים", "אנטיקואגולציה/דימום/טראומה?"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"},{"label":"לחץ דם"}],
        "labs": [L("CBC, קרישה, BMP","לפני טיפול תרופתי/פרוצדורות")],
        "imaging": [IMG("CT ראש ללא ניגוד","דימום"), IMG("CTA ראש-צוואר","חשד ל-LVO")],
        "scores": [S("NIHSS","חומרת חסר","גבוה - הסלמה")],
        "notes": []
    },
    "TIA - תסמינים שחלפו": {
        "questions": ["משך אירוע, תדירות", "יל\"ד/AF/DM/עישון", "Amaurosis fugax"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [L("גלוקוז, ליפידים, HbA1c","סיכון קרדיווסקולרי")],
        "imaging": [IMG("CTA/US קרוטידים","מקור אמבולי"), IMG("MRI דיפוזיה","אוטמים עדינים")],
        "scores": [S("ABCD2","סיכון לשבץ מוקדם","≥4 בינוני-גבוה")],
        "notes": []
    },
    "סחרחורת": {
        "questions": ["שימוש במדללי דם או לחצי דם לא מאוזנים","תנוחתי/אי יציבות? התקפי/מתמשך?", "שמיעה/טינטון/נוירו נוספים?"],
        "physical_exam": [{"label":"Dix-Hallpike"},{"label":"בדיקת ניסטגמוס"}],
        "labs": [],
        "imaging": [IMG("CTA/CTV מוח","חשד מרכזי/סימנים פוקליים")],
        "scores": [S("HINTS (למיומנים)","פריפרי מול מרכזי","Head-Impulse תקין/Skew","לא למתחילים")]
    },
    "כאב ראש": {
        "questions": ["צד/מעיר משינה /מגיב לאנלגטיקה/ משתנה במגע","thunderclap? החמרה חדשה?", "פוטופוביה/בחילה/חסך נוירולוגי פוקלי", "דלקת כלי דם/הריון/מדללים?"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"},{"label":"עורף - נוקשות"}],
        "labs": [L("CRP/ESR","Temporal arteritis >50y"), L("β-hCG","נשים בגיל הפוריות")],
        "imaging": [IMG("CT ראש","red flags"), IMG("CTA/CTV","חשד ל-SAH/תרומבוזיס ורידי")]
    },
    "פרכוס": {
        "questions": ["עדים/משך/פוסט-איקטלי", "תרופות/הפסקת אנטיאפילפטיים", "אלכוהול/סמים/חום"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [L("גזים מהירים ולקטט","CK","גלוקוז","היפוגליקמיה"), L("שתן לטוקסיקולוגיה","אלקטרוליטים","דיסאלקטרולמיה")],
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
    "RLQ - חשד לאפנדיציטיס": {
        "questions": ["מעבר כאב מאיפיגסטריום ל-RLQ", "חום/חולשה/בחילה"],
        "physical_exam": [{"label":"רגישות מקברני"},{"label":"סימני גירוי צפקי וריבאונד"}],
        "labs": [L("CBC","לויקוציטוזיס"), L("CRP","דלקת")],
        "imaging": [IMG("US/CT","לפי BMI וגיל")],
        "scores": [S("Alvarado","אפנדיציטיס","≥7 תומך","<5 מפחית")]
    },
    "דימום רקטלי": {
        "questions": ["כמות/צבע/כאב/עצירות", "מדללים/IBD/שלשולים/פאיחה"],
        "physical_exam": [{"label":" PR-בדיקת"},{"label":"סימני היפוולמיה"}],
        "labs": [L("CBC","Hb"), L("קרישה","INR/aPTT"), L("סוג והצלבה","דימום משמעותי")],
        "imaging": [IMG("קולונוסקופיה/CT אנגיו","לפי יציבות")]
    },
    "כאב אפיגסטרי/דיספפסיה": {
        "questions": ["קשר לאוכל/NSAIDs", "ירידה במשקל/הקאות/מלנה","כאב בחזה"],
        "physical_exam": [{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [L("ליפאז","לבלב"), L("Hb","דימום כרוני")],
        "imaging": [IMG("US/CT","לפי קליניקה","ECG")]
    },

    # --- גניטואורינרי ---
    "דיזוריה/UTI": {
        "questions": ["תכיפות/צריבה/דם?", "חום/כאב מותני/בחילות?", "הריון/סוכרת/קטטר?","יחסי מין לא מוגנים","הפרשה וגינאלית/פין"],
        "physical_exam": [{"label":"רגישות סופראפובית"},{"label":"רגישות CVA"}],
        "labs": [L("סטיק שתן + מיקרו","לויקוציטים/ניטריטים/דם"), L("תרבית שתן","אנטיביוגרמה"), L("CBC/CRP","חומרת זיהום"), L("STD פאנל")],
        "imaging": [IMG("US כליות/שלפוחית","Complicated/retention")]
    },
    "כאב מותני - חשד לאבן": {
        "questions": ["כאב התקפי מקרין למפשעה", "בחילות/המטוריה", "אבנים בעבר","חום/הקאות/כאב בחזה],
        "physical_exam": [{"label":"רגישות CVA"}],
        "labs": [L("שתן כללית ותרבית","דם/זיהום"), L("קרטינין","תפקודי כליה"),],
        "imaging": [IMG("CT low-dose","רגישות גבוהה"), IMG("US","בהריון/להימנע מקרינה"),IMG("ECG/POCUS","מעל גיל 50 עם חשד לדיסקציה")]
    },
    "שליפת קטטר שתן": {
        "questions": ["זמן החדרה וסיבה", "קושי בהטלה/כאב/דם", "זיהומים קודמים"],
        "physical_exam": [{"label":"בדיקת אזור השופכה והפניס/פרינאום"}],
        "labs": [],
        "imaging": [],
        "notes": ["אספטיקה, תיאום אורולוגי אם קושי"]
    },
    "נפרוסטום": {
        "questions": ["סיבה/מועד החלפה אחרון/חום/כאב גב"],
        "physical_exam": [{"label":"בדיקת אתר הניקוז"}],
        "labs": [L("תרבית שתן/נוזל מנפרוסטום","אם הפרשה/חום")]
    },
    "ליין דיאליזה": {
        "questions": ["כאב/אודם/הפרשה/חום", "מועד דיאליזה אחרון"],
        "physical_exam": [{"label":"הערכת אתר הקטטר/פיסטולה"}],
        "labs": [L("תרביות דם","אם חום")],
        "scores": [S("qSOFA","ספסיס")]
    },

    # --- א.א.ג ועיניים ---
    "דימום אפי ספונטני": {
        "questions": ["שימוש במדללי דם","חד/דו צדדי, טראומה/חיטוט/מדללים", "יתר ל\"ד?"],
        "physical_exam": [{"label":"בדיקה קדמית של אף/אוזן/לוע"},{"label":"טמפונדה קדמית אם צריך"}],
        "labs": [L("CBC","Hb"), L("קרישה","INR/aPTT","מדללים")]
    },
    "כאב גרון": {
        "questions": ["חום/דיספגיה/ריח רע/פריחה"],
        "physical_exam": [{"label":"בדיקת לוע ובלוטות"}],
        "labs": [L("Strep swab","אם חשד סטרפטוקוק"),L("CBC","זיהום אקוטי")]
    },
    "כאב אוזן": {
        "questions": ["חום/הפרשה/ירידה בשמיעה"],
        "physical_exam": [{"label":"בדיקת טימפאנום"}]
    },
    "גוף זר באף/אוזן/לוע": {
        "questions": ["סוג וזמן, קוצר נשימה"],
        "physical_exam": [{"label":"בדיקה קדמית של אף/אוזן/לוע"}],
        "imaging": [IMG("צילום","לפי סוג")]
    },
    "Red eye": {
        "questions": ["כאב/פוטופוביה/הפרשות/עדשות מגע", "טראומה/גוף זר"],
        "physical_exam": [{"label":"בדיקת חדות ראייה"},{"label":"פלואורסצאין/הפיכת עפעף"}],
        "notes": ["עדשות מגע - כיסוי פסאודומונס"]
    },
    "ירידה חדה בראייה": {
        "questions": ["פתאומי/הדרגתי, חד/דו עיני", "וילון שחור/פוטופסיות", "כאב עיני"],
        "physical_exam": [{"label":"בדיקת חדות ראייה"},{"label":"שדות ראייה ותנועות עיניים"}],
        "imaging": [IMG("OCT/US עיני","לפי זמינות")]
    },
    "גוף זר בעין": {
        "questions": ["מהירות/חומר, עדשות מגע"],
        "physical_exam": [{"label":"פלואורסצאין/הפיכת עפעף"}],
        "imaging": [IMG("צילום/CT מסלול","חשד מתכתי חדיר")]
    },

    # --- אנדוקריני ---
    "היפרגליקמיה": {
        "questions": ["פוליאוריה/פולידיפסיה/ירידה במשקל", "בחילות/כאבי בטן/ישנוניות (DKA/HHS)", "זיהום? סטרואידים? החמצת אינסולין?"],
        "physical_exam": [{"label":"מדדים"},{"label":"התייבשות/טורגור"},{"label":"נשימות קוסמאל"},{"label":"מישוש בטן והערכת רגישות"}],
        "labs": [L("גלוקוז מיידי","אישור","מידי"), L("BMP","אלקטרוליטים/כליה"), L("VBG/ABG + pH","חמצת","חשד ל-DKA/HHS"), L("קטונים בדם/שתן","DKA"), L("CBC/CRP","מוקד זיהומי"), L("אוסמולריות","HHS"), L("ECG","K⁺ חריג")],
        "scores": [S("qSOFA","אם חשד לזיהום")],
        "notes": ["אם DKA/HHS - נוזלים, K⁺, אינסולין IV, טיפול במוקד"]
    },
    "תירוטוקסיקוזיס ": {
        "questions": ["ירידה במשקל/טכיקרדיה/אי שקט/זיעה", "אמיאודרון/לבותירוקסין/יוד", "עין גרייבס, הריון/פוסט-פרטום"],
        "physical_exam": [{"label":"דופק/ל\"ד/טמפ'"},{"label":"רטיטת אצבעות דקה (fine tremor)"},{"label":"בלוטת התריס - הגדלה/רגישות/איוושה"},{"label":"עיניים - פרופטוזיס/לג אופתלמוס"}],
        "labs": [L("TSH","סקר","מידי"), L("FT4/FT3","אישור יתר","TSH נמוך"), L("אלקטרוליטים/גלוקוז","טריגרים"), L("טרופונין/BNP","מעורבות לבבית")],
        "imaging": [IMG("ECG","טכיקרדיה/פלפיטציות"), IMG("US תירואיד","קשריות/דלקת"), IMG("RAIU/סינטיגרפיה","אבחנת מקור")],
        "scores": [S("Burch–Wartofsky","סיכון למשבר תירוטוקסי","≥45 סביר מאוד","<25 לא סביר")],
        "notes": ["בלוקר בטא לפי התוויה; חשד למשבר - טיפול דחוף"]
    },
    "משבר אדרנלי": {
        "questions": ["סטרואידים כרוניים/הפסקה", "לחץ/זיהום/ניתוח לאחרונה"],
        "physical_exam": [{"label":"ל\"ד נמוך/שוק"},{"label":"התייבשות"}],
        "labs": [L("Na⁺/K⁺/גלוקוז","היפונתרמיה/היפרקלמיה/היפוגליקמיה"), L("קורטיזול","לפני סטרואידים אם אפשר")]
    },

    # --- המטולוגיה / זיהומיות / כלליות / עור ---
    "דימום ספונטני": {
        "questions": ["מיקום/כמות/משך", "מדללים/מחלות כבד/כליה", "פציעות/טראומה","המטומות בגפיים/חלל הפה /לחמיות העין "],
        "physical_exam": [{"label":"סימני דימום עוריים/ריריות"}],
        "labs": [L("CBC","טסיות/Hb"), L("PT/INR, aPTT","קרישה"), L("כימיה/כבד","סיבה משנית")]
    },
    "דימום מפצע": {
        "questions": ["מועד/נסיבות","סטטוס טטנוס", "מדללים", "לחץ ישיר/תפרים קיימים"],
        "physical_exam": [{"label":"הערכת פצע ועומק"}],
        "labs": [L("CBC","Hb"), L("קרישה","INR/aPTT")]
    },
    "חום לא ברור": {
        "questions": ["משך/שעות/רעד/מסעות/חשיפות/חיות/אנטיביוטיקה", "מחלות רקע וחיסונים"],
        "physical_exam": [{"label":"בדיקה שיטתית מלאה"}],
        "labs": [L("CBC, CRP","דלקת/זיהום"), L("תרביות דם x2","אם חום גבוה/ספסיס"), L("שתן כללית ותרבית","מוקד"), L("כימיה/תפקודי כבד","מוקד")],
        "imaging": [IMG("צילום חזה","מוקד נשימתי")],
        "scores": [S("qSOFA","ספסיס")]
    },
    "נשיכת כלב": {
        "questions": ["מתי ננשך? בעל חיים מוכר? חיסון כלבת? מיקום הפצע ועומקו? דיכוי חיסון?"],
        "physical_exam": [{"label":"בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)"},{"label":"הערכת עור - מורפולוגיה והתפשטות"}],
        "labs": [L("CBC","לויקוציטוזיס","אם חום/אודם/נפיחות"), L("CRP","דלקת","חשד לצלוליטיס")],
        "imaging": [IMG("צילום","חשד לשן/גוף זר/חדירה עמוקה")],
        "scores": [S("qSOFA","ספסיס")],
        "notes": ["ניקוי 10–15 דק', הטריה עדינה, אנטיביוטיקה מתאימה", "PEP כלבת לפי לשכת בריאות", "טטנוס לפי סטטוס"]
    },
    "פריחה בעור": {
        "questions": ["משך/החמרה, גרד/כאב","פגיעת בעל חיים עקיצה/נשיכה ","חזרה מחוץ לארץ", "חום/תרופות או חומר חדשות/חשיפות"],
        "physical_exam": [{"label":"הערכת עור - מורפולוגיה והתפשטות"}],
        "labs": []
    },
    "אבצס/צלוליטיס": {
        "questions": ["משך/כאב/חום מקומי או סיסטמי", "מחלת רקע/דיכוי חיסון"],
        "physical_exam": [{"label":"בדיקת זיהום רקמות רכות (צלוליטיס/אבצס)"}],
        "labs": [L("CBC, CRP","דלקת/זיהום","אם חום/צלוליטיס")],
        "imaging": [IMG("US רך","חשד לאבצס")]
    },

    # --- שריר-שלד / טראומה / חירום כללי ---
    "כאב גב תחתון": {
        "questions": ["red flags: חום/ירידה במשקל/חסך נוירולוגי /אי שליטה בסוגרים/ גרירת רגל ", "טראומה/פעילות חריגה"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": [],
        "imaging": [IMG("MRI/CT","red flags/חשד דחוף")]
    },
    "כאב צוואר": {
        "questions": ["טראומה/הקרנה ליד/נוירו"],
        "physical_exam": [{"label":"בדיקה נוירולוגית ממוקדת"}],
        "labs": []
        "imaging": [IMG("CT/XRAY","עמוד שדרה צווארי")]
    },
    "כאב מפרק חד": {
        "questions": ["טראומה/חום/פרוצדורה", "Gout/Pseudogout בעבר"],
        "physical_exam": [{"label":"בדיקת מפרק: חום/נפיחות/טווח"}],
        "labs": [L("חומצה אאורית,CBC, CRP","דלקת"), L("שאיבת נוזל","קריסטלים/תרבית")],
        "imaging": [IMG("צילום מפרק","לשבר/ארתרוזיס")]
    },
    "התייבשות": {
        "questions": ["צריכה תרופות/שימוש בסים או אלכהול /שלשול/הקאות/חום", "תרופות משתנות"],
        "physical_exam": [{"label":"התייבשות/טורגור"},{"label":" מדדים וחום רקטאלי "}],
        "labs": [L("BMP","אוראה/קרטנין,אלבומין/Na/K"), L("Hb","המוקונסנטראציה")]
    },
    "לחץ דם נמוך/שוק": {
        "questions": ["חום/זיהום/דימום/אלרגיה/טראומה", "נוזלים/תרופות"],
        "physical_exam": [{"label":"מדדים ושוק"},{"label":"בדיקה שיטתית מלאה"}],
        "labs": [L("CBC","Hb/לויקוציטים"), L("BMP","כליה/אלקטרוליטים"), L("לקטט","היפופרפוזיה"), L("תרביות דם","אם חום")],
        "imaging": [IMG("POCUS לב/ריאות","הכוונת דיפרנציאל")],
        "scores": [S("qSOFA","ספסיס")]
    },
    "הרעלת אופיאטים חשד": {
        "questions": ["שימוש לאחרונה/תרופות זמינות", "אלכוהול/סמים נוספים"],
        "physical_exam": [{"label":"סטורציה ו-RR,בדיקת אישונים"}],
        "labs": [],
        ,"imaging": [IMG("ECG/")]
        "notes": ["נלוקסון לפי צורך, ניטור נשימתי"]
    },
    "מכת חום": {
        "questions": ["חשיפה לחום/מאמץ", "תרופות נוגדות כולינרגי/נוירולפטי"],
        "physical_exam": [{"label":"מדדים, טמפ' גבוהה"}],
        "labs": [L("CK","Rhabdo"), L("BMP","אלקטרוליטים/כליה")],
        "notes": ["קירור אקטיבי מהיר + נוזלים"]
    },
}

# צרף קישורי וידאו אוטומטית לכל תלונה
for blk in COMPLAINTS.values():
    attach_video_links(blk)

# ========================= UI =========================
st.title("🩺 Smart Anamnesis – תלונות (ללא חלוקה למערכות)")
st.caption(f"סה\"כ תלונות מוגדרות: {len(COMPLAINTS)}")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

names = sorted(COMPLAINTS.keys())
search = st.text_input("חפש תלונה", placeholder="כאב חזה, סחרחורת, UTI...").strip()
if search:
    names = [n for n in names if search in n]
st.caption(f"נמצאו {len(names)} תלונות")

# בחירה מהירה + 'פתח הכול'
c0, c1 = st.columns([2,1])
with c0:
    sel = st.selectbox("בחר תלונה להצגה", ["—"] + names, index=0)
with c1:
    open_all = st.toggle("פתח הכול", value=(len(names) <= 3))

def render_questions(qs: List[str]) -> None:
    st.markdown("#### אנמנזה - מה לשאול")
    if not qs: st.write("- אין שאלות מוגדרות"); return
    for q in qs: st.write(f"- {q}")

def render_list_with_links(items: Any, title: str) -> None:
    st.markdown(f"#### {title}")
    if not items: st.write("- אין פריטים"); return
    for item in items:
        if isinstance(item, dict) and "label" in item:
            label = item.get("label",""); url = item.get("url","")
            st.markdown(f"- {'▶️ ' if url else ''}[{label}]({url})" if url else f"- {label}")
        elif isinstance(item, dict) and "test" in item:
            test=item.get("test",""); why=item.get("why",""); when=item.get("when","")
            line=f"- **{test}**"; 
            if why: line+=f" — למה: {why}"
            if when: line+=f" — מתי: {when}"
            st.markdown(line)
        elif isinstance(item, dict) and "modality" in item:
            modality=item.get("modality",""); trig=item.get("trigger","")
            st.markdown(f"- **{modality}**" + (f" — מתי: {trig}" if trig else ""))
        else:
            st.markdown(f"- {str(item)}")

def render_scores(scores: Any) -> None:
    st.markdown("#### 📊 SCORES רלוונטיים")
    if not scores: st.write("- אין scores מוגדרים"); return
    for s in scores:
        name = (s.get("name") if isinstance(s, dict) else str(s)) or ""
        st.markdown(f"- **{name}**")

def render_block(name: str, blk: Dict[str,Any], expand: bool=False) -> None:
    with st.expander(f"• {name}", expanded=expand):
        st.markdown("<div class='card'>", unsafe_allow_html=True); render_questions(blk.get("questions", [])); st.markdown("</div>", unsafe_allow_html=True)
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
            for n in blk["notes"]: st.write(f"- {n}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True); render_scores(blk.get("scores", [])); st.markdown("</div>", unsafe_allow_html=True)

# הצגה
if sel != "—":
    render_block(sel, COMPLAINTS[sel], expand=True)

if open_all or sel == "—":
    for n in names:
        render_block(n, COMPLAINTS[n], expand=open_all and sel=="—")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Smart Anamnesis • התוכן להכוונה קלינית בלבד ואינו מחליף שיקול דעת רפואי.נכבת עי לירן שחר")


