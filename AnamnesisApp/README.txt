הרצה ידנית אם תרצה:
1) פתח Anaconda Prompt או CMD
2) cd "%USERPROFILE%\Desktop\AnamnesisApp"
3) .venv\Scripts\python -m pip install -r requirements.txt
4) .venv\Scripts\python -m streamlit run app.py
אם הפורט תפוס: הוסף --server.port 8502
כתובת: http://localhost:8501

עדכון תוכן:
- knowledge.json לעריכת שאלות, בדיקות, מעבדה, הדמיה ו-scors.
- video_links.json להוספת קישורי וידאו. ה-label חייב להתאים ל-label שב-knowledge.
- באפליקציה: רענון תוכן בסרגל הצד. אין שמירת היסטוריה בין חולים.
