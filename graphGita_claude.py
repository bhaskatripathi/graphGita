import boto3
import json
import os
from botocore.exceptions import ClientError
import requests
import pandas as pd
import re
import logging
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
import jsonschema

# Define the chapter information with the correct structure - derived from original Gita book in gitrapress- Gorakhpur nad arhive.com sources after literature review
# Sources:https://gitapress.org/bookdetail/gita-shankarbhashya-hindi-10
# The Bhagavad Gita: The Original Sanskrit and an English Translation; Available at: https://archive.org/details/bhagavadgitaorig0000unse
# Bhagavad-Gita As It Is (Original 1972 Edition); Available at: https://archive.org/details/bhagavadgitaasitisoriginal1972edition
CHAPTER_INFO = {
    "chapters": [
        {"number": 1, "name": "Arjuna Visada Yoga", "total_shlokas": 47},
        {"number": 2, "name": "Sankhya Yoga", "total_shlokas": 72},
        {"number": 3, "name": "Karma Yoga", "total_shlokas": 43},
        {"number": 4, "name": "Jnana Yoga", "total_shlokas": 42},
        {"number": 5, "name": "Karma Sanyasa Yoga", "total_shlokas": 29},
        {"number": 6, "name": "Dhyana Yoga", "total_shlokas": 47},
        {"number": 7, "name": "Jnana Vijnana Yoga", "total_shlokas": 30},
        {"number": 8, "name": "Aksara Brahma Yoga", "total_shlokas": 28},
        {"number": 9, "name": "Raja Vidya Yoga", "total_shlokas": 34},
        {"number": 10, "name": "Vibhuti Yoga", "total_shlokas": 42},
        {"number": 11, "name": "Visvarupa Darsana Yoga", "total_shlokas": 55},
        {"number": 12, "name": "Bhakti Yoga", "total_shlokas": 20},
        {"number": 13, "name": "Ksetra Ksetrajna Vibhaga Yoga", "total_shlokas": 35},
        {"number": 14, "name": "Gunatraya Vibhaga Yoga", "total_shlokas": 27},
        {"number": 15, "name": "Purusottama Yoga", "total_shlokas": 20},
        {"number": 16, "name": "Daivasura Sampad Vibhaga Yoga", "total_shlokas": 24},
        {"number": 17, "name": "Sraddhatraya Vibhaga Yoga", "total_shlokas": 28},
        {"number": 18, "name": "Moksa Sanyasa Yoga", "total_shlokas": 78}
    ]
}

# AWS client to access S3 and Textract
class AWSClient:
    def __init__(self, region_name='eu-west-1'):
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.textract_client = boto3.client('textract', region_name=region_name)

    def list_s3_documents(self, bucket_name, prefix):
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents'] 
                        if obj['Key'].endswith('.json') and not obj['Key'].endswith('/')]
            return []
        except ClientError as e:
            print(f"Error accessing S3: {e}")
            return []

    def get_object(self, bucket_name, file_key):
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            print(f"Error getting object from S3: {e}")
            return None

# Claude API client to invoke the Claude model  
class ClaudeAPI:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def invoke_claude_model(self, prompt):
        try:
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 20000,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(self.api_endpoint, json=payload, headers=headers)
            
            if response.status_code == 200:
                claude_response = response.json()
                
                if 'content' in claude_response and isinstance(claude_response['content'], list):
                    return claude_response['content'][0]['text']
                elif 'completion' in claude_response:
                    return claude_response['completion']
                elif 'body' in claude_response:
                    body = json.loads(claude_response['body'])
                    if 'content' in body and isinstance(body['content'], list):
                        return body['content'][0]['text']
                    elif 'completion' in body:
                        return body['completion']
            
            print(f"Unexpected response format: {response.text}")
            return None
            
        except Exception as e:
            print(f"Error in Claude API call: {e}")
            return None

# Load the chapter information from the JSON file
with open("bhagavad_gita_meta_data.json", "r") as f:
    chapter_info = json.load(f)

# Function to call the Claude API
def claude_call(system_content, user_content, temperature=0.1, max_tokens=300):
    prompt = f"System: {system_content}\n\nUser: {user_content}"
    claude_api = ClaudeAPI('https://URL') # TODO: Replace with actual URL of API Gateway  
    response = claude_api.invoke_claude_model(prompt)
    return response.strip() if response else ""

# Function to generate a summary of a chapter
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

    response = claude_call(system_content, user_content, temperature=0.7, max_tokens=500)

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

# Function to check if a chapter is complete based on the number of shlokas
def is_chapter_complete(shloka_count):
    system_content = "You are an expert on the Bhagavad Gita. Determine if the given number of shlokas completes Chapter 1."
    user_content = f"Does {shloka_count} shlokas complete Chapter 1 of the Bhagavad Gita? Respond with only 'Yes' or 'No'."
    response = claude_call(system_content, user_content, temperature=0.1, max_tokens=10)
    return response.lower() == "yes"

# Function to generate detailed graph schema information about a shloka
def generate_shloka_details(chapter_number, shloka_text, shloka_number):
    print(f"Generating details for Chapter {chapter_number}, Shloka {shloka_number}...")
    system_content = """You are an expert on the Bhagavad Gita. Provide detailed information about the given verse in a structured JSON format.
    Your response MUST be a valid JSON object strictly with the following keys:
    - transliteration: The Sanskrit verse written in Latin script (as a single line without line breaks).
    - interpretation: A deeper analysis of the verse's significance and implications.
    - meaning: A concise explanation of the verse's meaning without any prefixes or introductions.
    - keywords: An array of key philosophical teachings, themes, or abstract concepts presented in this shloka.
    - life_application: How the teachings of this shloka can be applied to solve real-life problems or questions.
    Do not include any text outside of this JSON structure. Do not use markdown code block syntax or any other formatting."""

    user_content = f"""Analyze the following Bhagavad Gita verse (Chapter {chapter_number}, Shloka {shloka_number}) and provide the details in the specified JSON format: {shloka_text}
    Remember, your entire response must be a valid JSON object without any additional formatting or text."""

    response = claude_call(system_content, user_content, temperature=0.1, max_tokens=800)
    
    try:
        # Clean up the response
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]
        
        # Replace newlines in the response with spaces
        response = re.sub(r'\n\s*', ' ', response)
        
        # Try to parse the JSON
        shloka_details = json.loads(response)
        
        # Extract the required fields with default values
        return (
            shloka_details.get("transliteration", ""),
            shloka_details.get("interpretation", ""),
            shloka_details.get("meaning", ""),
            shloka_details.get("keywords", []),
            shloka_details.get("life_application", "")
        )
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for Chapter {chapter_number}, Shloka {shloka_number}: {e}")
        print("Raw response:", response)
        # Return default values in case of error
        return (
            "Error parsing transliteration",
            "Error parsing interpretation",
            "Error parsing meaning",
            ["error"],
            "Error parsing life application"
        )
    except Exception as e:
        print(f"Unexpected error for Chapter {chapter_number}, Shloka {shloka_number}: {e}")
        return (
            "Error occurred",
            "Error occurred",
            "Error occurred",
            ["error"],
            "Error occurred"
        )

# Function to analyze the relationships between characters, themes, and shlokas in a chapter for creating a better graph struct schema   
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

    response = claude_call(system_content, user_content, temperature=0.3, max_tokens=2000)

    print("Raw Claude response:")
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

# Function to generate the Sanskrit text for a given shloka 
def generate_sanskrit_shloka(chapter_number, shloka_number):
    print(f"Generating Sanskrit text for Chapter {chapter_number}, Shloka {shloka_number}...")
    system_content = "You are an expert in Sanskrit and the Bhagavad Gita. Generate only the Sanskrit text for the specified shloka without any additional text or explanations."
    user_content = f"Generate the Sanskrit text for Bhagavad Gita Chapter {chapter_number}, Shloka {shloka_number}."
    return claude_call(system_content, user_content, temperature=0.1, max_tokens=300)

# Function to create a mapping of problems to their solutions based on authentic versions of the Bhagavad Gita available on archive.org 
def create_problem_solutions_map():
    """Complete mapping of problems to common human problems based on authentic versions of the Bhagavad Gita available on archive.org
    Problems covered:
    Source Texts:
    1. Sri Aurobindo's Bhagavad Gita
    URL: https://archive.org/details/sri-aurobindo-the-bhagavat-gita
    Addresses:
    - Anger: Managing and overcoming anger
    - Coping with death of a loved one
    - Guilt: Dealing with guilt and feelings of sinfulness
    - Laziness: Strategies to combat laziness and procrastination
    - Lust: Controlling desires and sensual cravings
    - Inner peace: Finding tranquility and inner peace

    2. Paramahansa Yogananda's Gita
    URL: https://archive.org/details/the-bhagavad-gita-paramahansa-yogananda
    Addresses:
    - Depression: Dealing with depression and mental suffering
    - Dealing with envy
    - Discrimination: Handling discrimination and unfair treatment
    - Fear: Overcoming fear and anxiety
    - Greed: Overcoming material attachment
    - Loneliness: Addressing feelings of isolation
    - Forgiveness: Learning and practicing forgiveness
    - Temptation: Dealing with various temptations

    3. Bhagavad Gita As It Is (1972)
    URL: https://archive.org/details/bhagavadgitaasitisoriginal1972edition
    Addresses:
    - Confusion: Gaining clarity
    - Lack of motivation: Strategies to stay motivated
    - Forgetfulness: Improving memory
    - Hopelessness: Finding renewed purpose
    - Pride: Managing ego and arrogance
    - Uncontrolled mind: Gaining mental mastery
    """
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
    try:
        # Ask user if they want to generate all chapters or specific chapters
        choice = input("Would you like to generate all chapters or specific chapters? (Enter 'all' or 'specific'): ").strip().lower()
        
        # Initialize the list of chapter numbers to be generated
        chapter_numbers = []
        if choice == 'all':
            chapter_numbers = [chapter["number"] for chapter in CHAPTER_INFO["chapters"]]
        elif choice == 'specific':
            chapter_input = input("Enter the chapter numbers of the Bhagavad Gita you would like to generate (e.g., 1, 2, 6): ")
            chapter_numbers = [int(ch.strip()) for ch in chapter_input.split(',') if ch.strip().isdigit()]
        else:
            print("Invalid choice. Please enter either 'all' or 'specific'.")
            return

        if not chapter_numbers:
            print("No valid chapter numbers found. Please try again.")
            return

        # Initialize gita_data
        gita_data = {
            "problem_solutions_map": create_problem_solutions_map(),
            "chapters": []
        }

        # Create reverse mapping for problem lookup
        shloka_problem_map = {}
        for problem, data in gita_data["problem_solutions_map"].items():
            for ref in data["references"]:
                key = f"{ref['chapter']}:{ref['shloka']}"
                if key not in shloka_problem_map:
                    shloka_problem_map[key] = []
                shloka_problem_map[key].append(problem)

        # Initialize API clients
        claude_api_endpoint = 'https://url' # TODO: Replace with actual URL of API Gateway of Claude which should also have a lambda handler for the Claude API  
        aws_client = AWSClient()       
        claude_api = ClaudeAPI(claude_api_endpoint)

        # Generate data for each chapter
        for chapter in CHAPTER_INFO["chapters"]:
            if chapter["number"] in chapter_numbers:
                chapter_number = chapter["number"]
                chapter_name = chapter["name"]
                total_shlokas = chapter["total_shlokas"]  # Updated key name

                print(f"\nGenerating Chapter {chapter_number}: {chapter_name}")

                try:
                    chapter_summary = generate_chapter_summary(chapter_number, chapter_name)
                    
                    chapter_data = {
                        "number": chapter_number,
                        "name": chapter_name,
                        "summary": chapter_summary.get("summary", ""),
                        "main_theme": chapter_summary.get("main_theme", ""),
                        "philosophical_aspects": chapter_summary.get("philosophical_aspects", []),
                        "life_problems_addressed": chapter_summary.get("life_problems_addressed", []),
                        "yoga_type": chapter_summary.get("yoga_type", ""),
                        "shlokas": []
                    }

                    for shloka_number in range(1, total_shlokas + 1):
                        print(f"Processing Shloka {shloka_number} of {total_shlokas}")
                        
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

                    print("Analyzing chapter relationships...")
                    chapter_analysis = analyze_chapter_relationships(chapter_data["shlokas"], chapter_summary)
                    chapter_data.update(chapter_analysis)
                    gita_data["chapters"].append(chapter_data)

                except Exception as e:
                    print(f"Error processing Chapter {chapter_number}: {str(e)}")
                    continue

        # Write to JSON file
        output_filename = "bhagavad_gita_complete.json"
        with open(output_filename, "w", encoding="utf-8") as json_file:
            json.dump(gita_data, json_file, indent=4, ensure_ascii=False)

        print(f"\nGeneration complete. Data saved to {output_filename}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
