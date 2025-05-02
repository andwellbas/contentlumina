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


def generate_movie_recommendations(user_prompt: str) -> str:
    """
    Generates movie recommendations based on the users custom prompt.

    Args:
        user_prompt (str): Collected text with user wishes

    Returns:
        str: Response from GPT in the specified format
    """
    system_prompt = (
        "You are a movie recommender. The answer should be clearly structured. "
        "Don't make up movies. Use only real, existing movies. "
        "Titles must be original (in English). "
        "Format of each film:\n\n"
        "🎬Movie title\n"
        "Year: XXXX\n"
        "Genres: genre1, genre2, ...\n"
        "Description: a short description of the film (1-2 sentences)\n\n"
        "Answer in exactly the same format without explanations or introductions."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=600,
            temperature=0.8,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI Error: {str(e)}"