# 🚀 הוראות הרצה - מערכת ניהול משימות

## שלב 1: התקנת Python
ודאי שיש לך Python 3.8 ומעלה מותקן:
```bash
python --version
```

## שלב 2: יצירת סביבה וירטואלית (מומלץ)
```bash
python -m venv venv
venv\Scripts\activate
```

## שלב 3: התקנת חבילות
```bash
pip install -r requirements.txt
```

## שלב 4: הגדרת API Key
1. צור קובץ בשם `.env` בתיקיית הפרויקט
2. הוסף את המפתח שלך:
```
OPENAI_KEY=sk-your-actual-api-key-here
```

## שלב 4.1: הגדרת תזכורות מייל (אופציונלי אך מומלץ)
כדי שתזכורות יישלחו בפועל למשימות עם `due_date`, הוסף ל-`.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
REMINDER_FROM_EMAIL=your_email@example.com
REMINDER_TO_EMAIL=recipient@example.com
```

אם משתני ה-SMTP לא מוגדרים, המערכת עדיין תרוץ רגיל אך לא תשלח מיילי תזכורת.

## שלב 5: הרצת השרת

### אופציה 1: דרך run.bat
```bash
run.bat
```

### אופציה 2: ישירות
```bash
uvicorn main:app --reload
```

## שלב 6: בדיקת השרת
פתח דפדפן וגש ל:
- http://localhost:8000
- http://localhost:8000/docs (Swagger UI)

## שימוש ב-API

### דוגמאות עם curl:

**הוספת משימה:**
```bash
curl -X POST http://localhost:8000/agent ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"הוסף משימה: לקנות חלב\"}"
```

**הצגת משימות:**
```bash
curl -X POST http://localhost:8000/agent ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"הצג את כל המשימות\"}"
```

**עדכון משימה:**
```bash
curl -X POST http://localhost:8000/agent ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"סמן משימה 1 כהושלמה\"}"
```

**הוספת משימה עם תאריך יעד (לתזכורת):**
```bash
curl -X POST http://localhost:8000/agent ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"הוסף משימה: לשלם ארנונה עד 2026-03-20 09:00\"}"
```

**מחיקת משימה:**
```bash
curl -X POST http://localhost:8000/agent ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"מחק משימה 1\"}"
```

### דוגמאות עם Postman:
1. פתח Postman
2. צור בקשה חדשה: POST
3. URL: `http://localhost:8000/agent`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
```json
{
  "message": "הוסף משימה חדשה: ללמוד Python"
}
```

## פתרון בעיות

### שגיאה: "OPENAI_KEY not found"
- ודא שיצרת קובץ `.env`
- ודא שהמפתח נכון

### תזכורות לא נשלחות
- ודא שהוגדרו משתני `SMTP_*` ו-`REMINDER_TO_EMAIL`
- ודא שלמשימה יש `due_date` תקין בפורמט ISO
- תזכורות נבדקות כל 5 דקות

### שגיאה: "Module not found"
```bash
pip install -r requirements.txt
```

### השרת לא עולה
- ודא שפורט 8000 פנוי
- נסה פורט אחר: `uvicorn main:app --reload --port 8001`

## 🎉 מוכן לשימוש!
