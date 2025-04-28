from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(prompt_text):
    """
    Generates text using OpenAI

    Args:
        prompt_text (str): User request text.

    Returns:
        str: AI-generated response.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        ai_text = response.choices[0].message.content
        return ai_text

    except Exception as e:
        return f"OpenAI Error: {str(e)}"