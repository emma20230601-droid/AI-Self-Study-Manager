# ai_service.py
from sqlalchemy import text
from database import db
import google.generativeai as genai  # 改用 Google 官方套件

def get_ai_config(user_id):
    """ 從資料庫抓取該使用者的 AI 設定 """
    sql = text("SELECT api_key, system_prompt, model_name FROM ai_settings WHERE user_id = :uid")
    result = db.session.execute(sql, {'uid': user_id}).fetchone()
    return result

def ask_ai(user_id, prompt_message):
    """ Gemini 專用的 AI 請求函式 """
    config = get_ai_config(user_id)
    
    if not config or not config.api_key:
        return {"error": "尚未配置 API Key"}

    try:
        # 1. 配置 Gemini API Key
        genai.configure(api_key=config.api_key)

        # 2. 初始化模型 (預設使用 gemini-1.5-flash，速度快且便宜)
        model_name = config.model_name or "gemini-1.5-flash"
        
        # 3. 建立模型實例並設定 System Prompt
        # Gemini 的 System Prompt 是在初始化時定義的
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=config.system_prompt
        )

        # 4. 發送請求
        response = model.generate_content(prompt_message)
        
        return {"content": response.text}

    except Exception as e:
        return {"error": f"Gemini 請求失敗: {str(e)}"}