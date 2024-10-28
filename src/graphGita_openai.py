from IPython.display import display, HTML
from openai import OpenAI
import json
import os
import re

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = "sk-"
client = OpenAI()

with open("bhagavad_gita_meta_data.json", "r") as f:
    chapter_info = json.load(f)

def gpt_call(system_content, user_content, temperature=0.1, max_tokens=300):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()
import json
from openai import OpenAI


def generate_chapter_summary(chapter_number, chapter_name):
    system_content = f"""You are an expert on the Bhagavad Gita. Provide a comprehensive analysis of Chapter {chapter_number}: {chapter_name} strictly in JSON format with the following structure and no other format:
    {{
        "summary": "Brief summary of the chapter",
        "main_theme": "The overarching theme of the chapter",
        "philosophical_aspects": ["List of key philosophical concepts addressed"],
        "life_problems_addressed": ["List of life problems or questions this chapter helps address"],
        "yoga_type": "The primary type of yoga (if any) discussed in this chapter (e.g., Bhakti Yoga, Karma Yoga, etc.)"
    }}"""
    user_content = f"Provide a comprehensive analysis of Chapter {chapter_number}: {chapter_name} of the Bhagavad Gita as specified."

    response = gpt_call(system_content, user_content, temperature=0.7, max_tokens=500)

    # Remove markdown code block delimiters if present
    response = response.strip('`')
    if response.startswith('json'):
        response = response[4:].strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for Chapter {chapter_number} summary: {e}")
        print("Raw response:", response)
        # Return a default structure if JSON parsing fails
        return {
            "summary": "Error generating summary",
            "main_theme": "Error generating main theme",
            "philosophical_aspects": ["Error generating philosophical aspects"],
            "life_problems_addressed": ["Error generating life problems addressed"],
            "yoga_type": "Error generating yoga type"
        }

def is_chapter_complete(shloka_count):
    system_content = "You are an expert on the Bhagavad Gita. Determine if the given number of shlokas completes Chapter 1."
    user_content = f"Does {shloka_count} shlokas complete Chapter 1 of the Bhagavad Gita? Respond with only 'Yes' or 'No'."
    response = gpt_call(system_content, user_content, temperature=0.1, max_tokens=10)
    return response.lower() == "yes"

def generate_shloka_details(chapter_number, shloka_text, shloka_number):
    print(f"Generating details for Chapter {chapter_number}, Shloka {shloka_number}...")
    system_content = """You are an expert on the Bhagavad Gita. Provide detailed information about the given verse in a structured JSON format.
    Your response MUST be a valid JSON object strictly with the following keys:
    - transliteration: The Sanskrit verse written in Latin script.
    - interpretation: A deeper analysis of the verse's significance and implications.
    - meaning: A concise explanation of the verse's meaning without any prefixes or introductions.
    - keywords: An array of key philosophical teachings, themes, or abstract concepts presented in this shloka (exclude specific names of individuals; include relevant keywords of philosophical teachings, themes, or abstract concepts).
    - life_application: How the teachings of this shloka can be applied to solve real-life problems or questions.
    Do not include any text outside of this JSON structure. Do not use markdown code block syntax or any other formatting."""

    user_content = f"""Analyze the following Bhagavad Gita verse (Chapter {chapter_number}, Shloka {shloka_number}) and provide the details in the specified JSON format: {shloka_text}
    Remember, your entire response must be a valid JSON object without any additional formatting or text."""

    response = gpt_call(system_content, user_content, temperature=0.1, max_tokens=800)

    try:
        shloka_details = json.loads(response)
        return (
            shloka_details.get("transliteration", ""),
            shloka_details.get("interpretation", ""),
            shloka_details.get("meaning", ""),
            shloka_details.get("concepts", []),
            shloka_details.get("life_application", "")
        )
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for Chapter {chapter_number}, Shloka {shloka_number}: {e}")
        print("Raw response:", response)
        return "", "", "", [], ""

def analyze_chapter_relationships(shlokas, chapter_summary):
    print("Analyzing chapter relationships...")
    system_content = """You are an expert on the Bhagavad Gita. Analyze the given shlokas from the chapter and identify overall relationships between characters, themes, and shlokas.
    Return a JSON object with the following structure:
    {
        "characters": [{"name": "Character Name", "description": "Brief description of the character's role in this chapter"}],
        "themes": [{"name": "Theme Name", "description": "Brief description of the theme's significance in this chapter"}],
        "character_relationships": [{"from": "Character A", "to": "Character B", "description": "Description of the relationship"}],
        "theme_relationships": [{"theme": "Theme Name", "shlokas": [shloka numbers], "description": "How the theme manifests in these shlokas"}],
        "key_events": [{"event": "Event description", "shlokas": [shloka numbers], "characters": ["Character names involved"]}],
        "philosophical_progression": "Description of how philosophical concepts develop through the chapter",
        "chapter_relevance": "Explanation of how this chapter fits into the broader context of the Bhagavad Gita"
    }
    Ensure your response is a valid JSON object. Do not include any text outside of the JSON structure."""

    user_content = f"""Analyze the following shlokas from the Bhagavad Gita chapter and provide the relationships as specified.
    Chapter Summary: {json.dumps(chapter_summary)}

    Shlokas:
    """
    for shloka in shlokas:
        user_content += f"Shloka {shloka['shloka_number']}:\n"
        user_content += f"Sanskrit: {shloka['sanskrit_text']}\n"
        user_content += f"Meaning: {shloka['meaning']}\n"
        user_content += f"Interpretation: {shloka['interpretation']}\n"
        user_content += f"Keywords: {', '.join(shloka['keywords'])}\n\n"

    response = gpt_call(system_content, user_content, temperature=0.3, max_tokens=2000)

    print("Raw GPT response:")
    print(response)

    try:
        # Remove markdown code block syntax if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]

        analysis = json.loads(response)
        print("Analysis completed successfully.")
        return analysis
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for chapter relationships: {e}")
        print("Attempting to fix JSON...")

        # Attempt to fix common JSON errors
        try:
            fixed_response = response.replace("'", '"')  # Replace single quotes with double quotes
            fixed_response = re.sub(r'(\w+):', r'"\1":', fixed_response)  # Add quotes to keys
            analysis = json.loads(fixed_response)
            print("JSON fixed successfully.")
            return analysis
        except Exception as fix_error:
            print(f"Failed to fix JSON: {fix_error}")

            # If fixing fails, return a default structure with error information
            return {
                "characters": [{"name": "Error", "description": f"Failed to parse characters. Error: {str(e)}"}],
                "themes": [{"name": "Error", "description": f"Failed to parse themes. Error: {str(e)}"}],
                "character_relationships": [{"from": "Error", "to": "Error", "description": f"Failed to parse relationships. Error: {str(e)}"}],
                "theme_relationships": [{"theme": "Error", "shlokas": [], "description": f"Failed to parse theme relationships. Error: {str(e)}"}],
                "key_events": [{"event": f"Error parsing events. Error: {str(e)}", "shlokas": [], "characters": []}],
                "philosophical_progression": f"Error parsing philosophical progression. Error: {str(e)}",
                "chapter_relevance": f"Error parsing chapter relevance. Error: {str(e)}"
            }

def generate_sanskrit_shloka(chapter_number, shloka_number):
    print(f"Generating Sanskrit text for Chapter {chapter_number}, Shloka {shloka_number}...")
    system_content = "You are an expert in Sanskrit and the Bhagavad Gita. Generate only the Sanskrit text for the specified shloka without any additional text or explanations."
    user_content = f"Generate the Sanskrit text for Bhagavad Gita Chapter {chapter_number}, Shloka {shloka_number}."
    return gpt_call(system_content, user_content, temperature=0.1, max_tokens=300)

def create_problem_solutions_map():
    """Create a complete mapping of problems to their solutions in the Bhagavad Gita"""
    return {
        # Part 1
        "anger": {
            "description": "Managing and overcoming anger",
            "references": [
                {"chapter": 2, "shloka": 56},
                {"chapter": 2, "shloka": 62},
                {"chapter": 2, "shloka": 63},
                {"chapter": 5, "shloka": 26},
                {"chapter": 16, "shloka": 1},
                {"chapter": 16, "shloka": 2},
                {"chapter": 16, "shloka": 3},
                {"chapter": 16, "shloka": 21}
            ]
        },
        "depression": {
            "description": "Dealing with depression and mental suffering",
            "references": [
                {"chapter": 2, "shloka": 3},
                {"chapter": 2, "shloka": 14},
                {"chapter": 5, "shloka": 21}
            ]
        },
        "confusion": {
            "description": "Clearing confusion and gaining clarity",
            "references": [
                {"chapter": 2, "shloka": 7},
                {"chapter": 3, "shloka": 2},
                {"chapter": 18, "shloka": 61}
            ]
        },
        "dealing_with_envy": {
            "description": "Dealing with envy and jealousy",
            "references": [
                {"chapter": 12, "shloka": 13},
                {"chapter": 12, "shloka": 14},
                {"chapter": 16, "shloka": 19},
                {"chapter": 18, "shloka": 71}
            ]
        },
        "death_of_loved_one": {
            "description": "Coping with death of a loved one",
            "references": [
                {"chapter": 2, "shloka": 13},
                {"chapter": 2, "shloka": 20},
                {"chapter": 2, "shloka": 22},
                {"chapter": 2, "shloka": 25},
                {"chapter": 2, "shloka": 27}
            ]
        },
        "demotivated": {
            "description": "Dealing with lack of motivation",
            "references": [
                {"chapter": 11, "shloka": 33},
                {"chapter": 18, "shloka": 48},
                {"chapter": 18, "shloka": 78}
            ]
        },
        "discriminated": {
            "description": "Dealing with discrimination and unfair treatment",
            "references": [
                {"chapter": 5, "shloka": 18},
                {"chapter": 5, "shloka": 19},
                {"chapter": 6, "shloka": 32},
                {"chapter": 9, "shloka": 29}
            ]
        },
        # Part 2
        "fear": {
            "description": "Overcoming fear and anxiety",
            "references": [
                {"chapter": 4, "shloka": 10},
                {"chapter": 11, "shloka": 50},
                {"chapter": 18, "shloka": 30}
            ]
        },
        "feeling_sinful": {
            "description": "Dealing with guilt and feelings of sinfulness",
            "references": [
                {"chapter": 4, "shloka": 36},
                {"chapter": 4, "shloka": 37},
                {"chapter": 5, "shloka": 10},
                {"chapter": 9, "shloka": 30},
                {"chapter": 10, "shloka": 3},
                {"chapter": 14, "shloka": 6},
                {"chapter": 18, "shloka": 66}
            ]
        },
        "forgetfulness": {
            "description": "Dealing with forgetfulness",
            "references": [
                {"chapter": 15, "shloka": 15},
                {"chapter": 18, "shloka": 61}
            ]
        },
        "greed": {
            "description": "Overcoming greed and attachment",
            "references": [
                {"chapter": 14, "shloka": 17},
                {"chapter": 16, "shloka": 21},
                {"chapter": 17, "shloka": 25}
            ]
        },
        "laziness": {
            "description": "Overcoming laziness and procrastination",
            "references": [
                {"chapter": 3, "shloka": 8},
                {"chapter": 3, "shloka": 20},
                {"chapter": 6, "shloka": 16},
                {"chapter": 18, "shloka": 39}
            ]
        },
        "loneliness": {
            "description": "Dealing with feelings of loneliness",
            "references": [
                {"chapter": 6, "shloka": 30},
                {"chapter": 9, "shloka": 29},
                {"chapter": 13, "shloka": 16},
                {"chapter": 13, "shloka": 18}
            ]
        },
        # Part 3
        "losing_hope": {
            "description": "Dealing with hopelessness and despair",
            "references": [
                {"chapter": 4, "shloka": 11},
                {"chapter": 6, "shloka": 22},
                {"chapter": 9, "shloka": 34},
                {"chapter": 18, "shloka": 66},
                {"chapter": 18, "shloka": 78}
            ]
        },
        "lust": {
            "description": "Controlling lust and sensual desires",
            "references": [
                {"chapter": 3, "shloka": 37},
                {"chapter": 3, "shloka": 41},
                {"chapter": 3, "shloka": 43},
                {"chapter": 5, "shloka": 22},
                {"chapter": 16, "shloka": 21}
            ]
        },
        "practicing_forgiveness": {
            "description": "Learning and practicing forgiveness",
            "references": [
                {"chapter": 11, "shloka": 44},
                {"chapter": 12, "shloka": 13},
                {"chapter": 12, "shloka": 14},
                {"chapter": 16, "shloka": 1},
                {"chapter": 16, "shloka": 2},
                {"chapter": 16, "shloka": 3}
            ]
        },
        "pride": {
            "description": "Managing ego and pride",
            "references": [
                {"chapter": 16, "shloka": 4},
                {"chapter": 16, "shloka": 13},
                {"chapter": 16, "shloka": 14},
                {"chapter": 16, "shloka": 15},
                {"chapter": 18, "shloka": 26},
                {"chapter": 18, "shloka": 58}
            ]
        },
        "seeking_peace": {
            "description": "Finding inner peace and tranquility",
            "references": [
                {"chapter": 2, "shloka": 66},
                {"chapter": 2, "shloka": 71},
                {"chapter": 4, "shloka": 39},
                {"chapter": 5, "shloka": 29},
                {"chapter": 8, "shloka": 28}
            ]
        },
        "temptation": {
            "description": "Dealing with temptations",
            "references": [
                {"chapter": 2, "shloka": 60},
                {"chapter": 2, "shloka": 61},
                {"chapter": 2, "shloka": 70},
                {"chapter": 7, "shloka": 14}
            ]
        },
        "uncontrolled_mind": {
            "description": "Managing an uncontrolled mind",
            "references": [
                {"chapter": 6, "shloka": 5},
                {"chapter": 6, "shloka": 6},
                {"chapter": 6, "shloka": 26},
                {"chapter": 6, "shloka": 35}
            ]
        }
    }


def main():
    choice = input("Would you like to generate all chapters or specific chapters? (Enter 'all' or 'specific'): ").strip().lower()
    
    chapter_numbers = []
    if choice == 'all':
        # Get all chapter numbers from chapter_info
        chapter_numbers = [chapter["number"] for chapter in chapter_info["chapters"]]
    elif choice == 'specific':
        chapter_input = input("Enter the chapter numbers of the Bhagavad Gita you would like to generate (e.g., 1, 2, 6): ")
        chapter_numbers = [int(ch.strip()) for ch in chapter_input.split(',') if ch.strip().isdigit()]
    else:
        print("Invalid choice. Please enter either 'all' or 'specific'.")
        return

    if not chapter_numbers:
        print("No valid chapter numbers found. Please try again.")
        return

    # Initialize gita_data with problem_solutions_map
    gita_data = {
        "problem_solutions_map": create_problem_solutions_map(),
        "chapters": []
    }

    # Create reverse mapping for efficient problem lookup
    shloka_problem_map = {}
    for problem, data in gita_data["problem_solutions_map"].items():
        for ref in data["references"]:
            key = f"{ref['chapter']}:{ref['shloka']}"
            if key not in shloka_problem_map:
                shloka_problem_map[key] = []
            shloka_problem_map[key].append(problem)

    for chapter in chapter_info["chapters"]:
        if chapter["number"] in chapter_numbers:
            chapter_number = chapter["number"]
            chapter_name = chapter["name"]
            total_shlokas = chapter["shlokas"]

            print(f"\nGenerating Chapter {chapter_number}: {chapter_name}")

            try:
                chapter_summary = generate_chapter_summary(chapter_number, chapter_name)
                chapter_data = {
                    "number": chapter_number,
                    "name": chapter_name,
                    "summary": chapter_summary["summary"],
                    "main_theme": chapter_summary["main_theme"],
                    "philosophical_aspects": chapter_summary["philosophical_aspects"],
                    "life_problems_addressed": chapter_summary["life_problems_addressed"],
                    "yoga_type": chapter_summary["yoga_type"],
                    "shlokas": []
                }

                for shloka_number in range(1, total_shlokas + 1):
                    shloka_text = generate_sanskrit_shloka(chapter_number, shloka_number)
                    transliteration, interpretation, meaning, keywords, life_application = generate_shloka_details(
                        chapter_number, shloka_text, shloka_number)

                    # Add problems addressed by this shloka
                    shloka_key = f"{chapter_number}:{shloka_number}"
                    problems_addressed = shloka_problem_map.get(shloka_key, [])

                    shloka_data = {
                        "name": f"Shloka {shloka_number}",
                        "chapter": chapter_number,
                        "shloka_number": shloka_number,
                        "sanskrit_text": shloka_text,
                        "transliteration": transliteration,
                        "interpretation": interpretation,
                        "meaning": meaning,
                        "keywords": keywords,
                        "life_application": life_application,
                        "addresses_problems": problems_addressed
                    }

                    chapter_data["shlokas"].append(shloka_data)
                    print(f"Generated Shloka {shloka_number} of {total_shlokas}")

                print("Analyzing chapter relationships...")
                chapter_analysis = analyze_chapter_relationships(chapter_data["shlokas"], chapter_summary)
                chapter_data.update(chapter_analysis)
                gita_data["chapters"].append(chapter_data)

            except Exception as e:
                print(f"Error generating Chapter {chapter_number}: {e}")
                continue

    # Write everything to a single JSON file
    with open("bhagavad_gita_complete.json", "w", encoding="utf-8") as json_file:
        json.dump(gita_data, json_file, indent=4, ensure_ascii=False)

    print("Generation of selected chapters of the Bhagavad Gita is complete.")

if __name__ == "__main__":
    main()
