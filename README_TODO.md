# מערכת ניהול משימות עם Function Calling

## תיאור הפרויקט
מערכת ניהול משימות המשתמשת ב-GPT עם Function Calling לביצוע פעולות CRUD על משימות, כולל תמיכה בתאריך יעד (`due_date`) ותזכורות מייל.

## מבנה הפרויקט

### todo_service.py
שירות ניהול המשימות עם הפונקציות:
- `get_tasks()` - קבלת כל המשימות
- `add_task(title, description, due_date)` - הוספת משימה חדשה
- `update_task(task_id, title, description, completed, due_date)` - עדכון משימה
- `delete_task(task_id)` - מחיקת משימה

### email_reminder_service.py
שירות תזכורות שמריץ בדיקה תקופתית, מזהה משימות שהגיע מועד ה-`due_date` שלהן, ושולח מייל דרך SMTP (פעם אחת לכל משימה).

### tools_todo.py
הגדרת הכלים (tools) עבור GPT בפורמט JSON

### agent_service.py
שירות ה-Agent שמתקשר עם GPT ומבצע Function Calling

### main.py
FastAPI server עם endpoint חדש: `/agent`

## שימוש

### הרצת השרת
```bash
uvicorn main:app --reload
```

### דוגמאות לשימוש

**POST /agent**
```json
{
  "message": "הוסף משימה חדשה: לקנות חלב"
}
```

```json
{
  "message": "הצג את כל המשימות שלי"
}
```

```json
{
  "message": "סמן את משימה מספר 1 כהושלמה"
}
```

```json
{
  "message": "מחק את המשימה עם מזהה 2"
}
```

## דרישות
- Python 3.8+
- FastAPI
- OpenAI API Key
- python-dotenv
- requests

## הגדרת .env
```
OPENAI_KEY=your_api_key_here

# Reminder Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
REMINDER_FROM_EMAIL=your_email@example.com
REMINDER_TO_EMAIL=recipient@example.com
```
