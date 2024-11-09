import os
import time
import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyD194W9zkMt0Gbud6IuNloJNyPfRblv9gU"
genai.configure(api_key=GEMINI_API_KEY)

def get_bot(files=None, model_name="gemini-1.5-pro", system_prompt=None):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 30,
        "max_output_tokens": 12000,
    }

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_prompt
    )

    history = []
    if files:
        history.append({
            "role": "user",
            "parts": [file for file in files]
        })
    


    chat = model.start_chat(history=history)
    return chat

def get_chat_response(chat, message, context=None):
    try:
        context_prompts = {
            'quiz': "You are helping create an educational quiz. ",
            'assignment': "You are helping create a learning assignment. ",
            'mock test': "You are helping create a mock test. ",
            'extra curricular': "You are helping create extracurricular activities. ",
            'general': "You are a helpful educational assistant. "
        }
        
        context_message = context_prompts.get(str(context).lower(), context_prompts['general'])
        full_message = f"{context_message}\nUser message: {message}"
        
        response = chat.send_message(full_message)
        print(response)
        return response.text if response.text else "I couldn't generate a response. Please try again."
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return "I'm having trouble responding right now. Please try again."