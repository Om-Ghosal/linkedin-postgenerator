import re
import ollama
from llama_index.llms.ollama import Ollama
import json
def extract_content(text):
        # Use regular expressions to extract the title and body
        title_match = re.search(r"\*\*title:\*\*\s*(.+)", text)
        body_match = re.search(r"\*\*body:\*\*\s*(.+)", text, re.DOTALL)

        # Extracted title and body
        title = title_match.group(1).strip() if title_match else ""
        body = body_match.group(1).strip() if body_match else ""

        # Return the result as a dictionary
        return {
            "title": title,
            "body": body
        }
def llm_generete(app_name,app_context,tech_stack):
    model = Ollama(model="llama3.1",request_timeout=30.0,json_mode=True)

    instruction = f"""
Create a LinkedIn post about a new app launch. Below is the information about the app:

    1. **App Name**: {app_name}
    2. **Purpose of the App**: {app_context}
    3. **Tech Stack**: {tech_stack}
    4. **Project type**: Personal
    5. **Tone of the Post (e.g., professional, friendly, enthusiastic)**: Professional

Make sure the post is engaging, professional, and encourages readers to learn more or try the app. The post should be within 150-250 words and end with a strong call to action.and return the post as a dictionary with the keys "title" and "body".

    """

    response = model.complete(instruction)
    json_obj = json.loads(response.text)
    
    
    return json_obj


def post_maker_llm(title,body):
    model = Ollama(model="llama3.1",request_timeout=30.0,json_mode=True)
    instruction = f'''
Your a LinkedIn post creator. Tell your network what your article is about under 60 words.

    1. **title**: {title}
    2. **body**: {body}
'''
    response = model.complete(instruction)

    return response.text