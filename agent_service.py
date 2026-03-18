import os
import requests
import logging
import json
from dotenv import load_dotenv
from agent_service_mock import agent_query_mock
from tools_todo import tools_todo
from todo_service import get_tasks, add_task, update_task, delete_task

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.getenv('OPENAI_KEY')
url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}


def execute_function(function_name: str, arguments: dict):
    try:
        if function_name == "get_tasks":
            return get_tasks()
        elif function_name == "add_task":
            return add_task(**arguments)
        elif function_name == "update_task":
            return update_task(**arguments)
        elif function_name == "delete_task":
            return delete_task(**arguments)
        else:
            return {"error": "Unknown function"}
    except ValueError as validation_error:
        return {"success": False, "error": str(validation_error)}
    except TypeError as type_error:
        return {"success": False, "error": str(type_error)}


async def agent_query(message: str):
    system_instruction = "אתה עוזר לניהול משימות. כשמשתמש מבקש להוסיף או לעדכן משימה עם תאריך יעד, העבר אותו לשדה due_date בפורמט ISO (YYYY-MM-DDTHH:MM:SS). אם לא צוין שעה, השתמש ב-09:00:00."

    if not api_key:
        logger.warning("OPENAI_KEY is missing, falling back to mock agent")
        return await agent_query_mock(message)
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": message}
            ],
            "tools": tools_todo,
            "tool_choice": "auto"
        })
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        logger.error(f"Response content: {response.text}")
        if response.status_code == 401:
            logger.warning("OpenAI authorization failed, falling back to mock agent")
            return await agent_query_mock(message)
        return {"error": str(http_err), "details": response.text}
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {"error": str(e)}

    completion = response.json()
    logger.info(f"Response: {completion}")
    
    if 'choices' not in completion or not completion['choices']:
        logger.error(f"Invalid response: {completion}")
        return {"error": "Invalid response from OpenAI"}
    
    choice = completion['choices'][0]
    message_response = choice['message']
    
    # בדיקה אם יש tool calls
    if 'tool_calls' in message_response and message_response['tool_calls']:
        tool_call = message_response['tool_calls'][0]
        function_name = tool_call['function']['name']
        arguments = json.loads(tool_call['function']['arguments'])
        
        result = execute_function(function_name, arguments)
        logger.info(f"Function result: {result}")
        
        # קריאה שנייה עם התוצאה
        try:
            response2 = requests.post(url, headers=headers, json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": message},
                    message_response,
                    {"role": "tool", "tool_call_id": tool_call['id'], "content": json.dumps(result)}
                ],
                "tools": tools_todo,
                "tool_choice": "auto"
            })
            response2.raise_for_status()
            completion2 = response2.json()
            
            if 'choices' in completion2 and completion2['choices']:
                return completion2
        except Exception as e:
            logger.error(f"Error in second call: {e}")
            return {"choices": [{"message": {"content": "הפעולה בוצעה בהצלחה"}}]}
    
    return completion