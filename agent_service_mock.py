import json
from todo_service import get_tasks, add_task, update_task, delete_task


def find_task_by_title(title: str):
    """מצא משימה לפי כותרת (חיפוש חלקי)"""
    tasks = get_tasks()["tasks"]
    title_lower = title.lower()
    
    for task in tasks:
        if title_lower in task["title"].lower():
            return task
    return None


async def agent_query_mock(message: str):
    """Mock agent for testing without OpenAI API"""
    
    message_lower = message.lower()
    
    # הצג משימות
    if "הצג" in message or "רשימה" in message or "משימות" in message:
        tasks = get_tasks()
        if tasks["tasks"]:
            task_list = "\n".join([f"{t['id']}. {t['title']} - {'✅ הושלם' if t['completed'] else '⏳ בתהליך'}" 
                                   for t in tasks["tasks"]])
            response = f"הנה המשימות שלך:\n{task_list}"
        else:
            response = "אין לך משימות כרגע. תוכל להוסיף משימה חדשה!"
    
    # הוסף משימה
    elif "הוסף" in message or "צור" in message or "חדש" in message or message_lower.startswith("צריך") or message_lower.startswith("צריכה"):
        if "." in message:
            title = message.split(".", 1)[1].strip()
        elif ":" in message:
            title = message.split(":", 1)[1].strip()
        elif message_lower.startswith("צריך") or message_lower.startswith("צריכה"):
            title = message.strip()
        else:
            title = message.replace("הוסף משימה", "").replace("הוסף", "").strip()
        
        if title:
            result = add_task(title)
            response = f"✅ המשימה '{title}' נוספה בהצלחה! (מזהה: {result['task']['id']})"
        else:
            response = "❌ לא הצלחתי להבין איזו משימה להוסיף. נסה שוב."
    
    # סמן כהושלם
    elif "סמן" in message or "השלם" in message or "הושלם" in message:
        task_id = None
        task = None
        
        # חיפוש לפי מספר
        words = message.split()
        for word in words:
            if word.isdigit():
                task_id = int(word)
                break
        
        # אם לא נמצא מספר, חפש לפי תיאור
        if not task_id:
            # נסה למצוא את התיאור
            if ":" in message:
                title_search = message.split(":", 1)[1].strip()
            elif "משימה" in message:
                parts = message.split("משימה", 1)
                if len(parts) > 1:
                    title_search = parts[1].replace("כהושלמה", "").replace("כהושלם", "").strip()
                else:
                    title_search = ""
            else:
                title_search = message.replace("סמן", "").replace("השלם", "").replace("כהושלמה", "").replace("כהושלם", "").strip()
            
            if title_search:
                task = find_task_by_title(title_search)
                if task:
                    task_id = task["id"]
        
        if task_id:
            result = update_task(task_id, completed=True)
            if result["success"]:
                response = f"✅ המשימה '{result['task']['title']}' סומנה כהושלמה!"
            else:
                response = f"❌ לא מצאתי משימה עם מזהה {task_id}"
        else:
            response = "❌ לא הצלחתי להבין איזו משימה לסמן. ציין מספר משימה או תיאור."
    
    # מחק משימה
    elif "מחק" in message or "הסר" in message:
        task_id = None
        task = None
        
        # חיפוש לפי מספר
        words = message.split()
        for word in words:
            if word.isdigit():
                task_id = int(word)
                break
        
        # אם לא נמצא מספר, חפש לפי תיאור
        if not task_id:
            if ":" in message:
                title_search = message.split(":", 1)[1].strip()
            elif "משימה" in message:
                parts = message.split("משימה", 1)
                if len(parts) > 1:
                    title_search = parts[1].strip()
                else:
                    title_search = ""
            else:
                title_search = message.replace("מחק", "").replace("הסר", "").strip()
            
            if title_search:
                task = find_task_by_title(title_search)
                if task:
                    task_id = task["id"]
        
        if task_id:
            result = delete_task(task_id)
            if result["success"]:
                response = f"✅ המשימה '{result['task']['title']}' נמחקה בהצלחה!"
            else:
                response = f"❌ לא מצאתי משימה עם מזהה {task_id}"
        else:
            response = "❌ לא הצלחתי להבין איזו משימה למחוק. ציין מספר משימה או תיאור."
    
    else:
        response = "לא הבנתי את הבקשה. נסה:\n- הצג משימות\n- הוסף משימה: [כותרת]\n- סמן משימה [מספר/תיאור] כהושלמה\n- מחק משימה [מספר/תיאור]"
    
    return {
        "choices": [{
            "message": {
                "content": response
            }
        }]
    }
