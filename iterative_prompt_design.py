# -*- coding: utf-8 -*-
"""
@author: j.
"""

import concurrent.futures
import pickle
import logging
import openai
import time
import json
import re
import os

# load your API key here
openai.api_key = None

# update this sample rubric based on your own use case and requirements
instruction_rubric = """
{
    "score_range": [1, 10],
    "rubric": [
        {
            "criterion": "Relevance",
            "description": "Does the response directly address the question or topic of the prompt?",
            "score": "<what's the relevance score?>"
        },
        {
            "criterion": "Coherence",
            "description": "Is the response logically consistent and does it flow well?",
            "score": "<what's the coherence score?>"
        },
        {
            "criterion": "Completeness",
            "description": "Does the response provide a complete answer or solution to the prompt?",
            "score": "<what's the completeness score?>"
        },
        {
            "criterion": "Accuracy",
            "description": "Is the information provided in the response correct?",
            "score": "<what's the accuracy score?>"
        },
        {
            "criterion": "Clarity",
            "description": "Is the response clear and easy to understand?",
            "score": "<what's the clarity score?>"
        },
        {
            "criterion": "Contextual Understanding",
            "description": "Does the response indicate a comprehension of the context provided in the prompt?",
            "score": "<what's the contextual understanding score?>"
        },
        {
            "criterion": "Specificity",
            "description": "Is the response specific and detailed rather than being generic and vague?",
            "score": "<what's the specificity score?>"
        },
        {
            "criterion": "Brevity",
            "description": "Does the response communicate the information concisely and avoid unnecessary verbosity?",
            "score": "<what's the brevity score?>"
        }
    ]
}
"""


# tests if rubric JSON is formatted correctly - this code will error if it's not formatted right
rubric_dict = json.loads(instruction_rubric)


def chat_request_(conversation, temperature=0.1, model='gpt-3.5-turbo'):
    # caching requests to save you API costs - delete this file if cache becomes annoying or 
    # you want to use different model
    cache_path = "./cache.pkl"  
    
    # Load cache if it exists, otherwise initialize an empty dict
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
    else:
        cache = {}

    # Convert conversation to string to use as key
    convo_key = str(conversation)

    # Check if the result is in the cache
    if convo_key in cache:
        return cache[convo_key]
    
    try:
        # If not in the cache, make the API request
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            messages=conversation
        )
        result = response.choices[0].message['content']
        
        # Save the result to the cache
        cache[convo_key] = result
        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)
        
        return result
    except Exception as e:
        logging.error(f"API request failed with error: {str(e)}")
        raise


def chat_request(conversations, temperature, model, max_retries, retry_interval):
    # Create a ThreadPoolExecutor instance, with the number of worker threads being the maximum of 5 and the number of conversations.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(5, len(conversations))) as executor:
        # Create a dictionary that maps each future (task) to its corresponding conversation.
        futures = {executor.submit(chat_request_, conversation, temperature, model): conversation for conversation in conversations}
        # Initialize a list to store the results.
        results = []
        # Iterate over the completed futures as they become available.
        for future in concurrent.futures.as_completed(futures):
            # Try to get the result of each future for a maximum number of retries.
            for attempt in range(max_retries):
                try:
                    # Append the result of the future to the results list.
                    results.append(future.result())
                    # If the result is obtained successfully, break the retry loop.
                    break
                except Exception as e:
                    # If an exception occurs, check if the maximum number of retries has been reached.
                    if attempt < max_retries - 1:
                        # If not, log a warning and wait for the retry interval before the next retry.
                        logging.warning(f"API request failed (attempt {attempt+1}/{max_retries}). Retrying in {retry_interval} seconds...")
                        time.sleep(retry_interval)
                    else:
                        # If the maximum number of retries has been reached, log an error and raise the exception.
                        logging.error(f"API request failed after {max_retries} attempts. Aborting.\r\n{e}")
                        raise
    # Return the list of results.
    return results


# The function `extract_json` is designed to extract a JSON object from a string.
# It first attempts to find the JSON object using a regular expression.
# If it fails to find a JSON object, it then attempts to parse the entire input string as a JSON object.
def extract_json(input_string):
    # Define a regular expression pattern to find a JSON object within a string.
    pattern = r'```json(.*?)```'
    
    # Attempt to find a JSON object in the input string using the defined pattern.
    json_string = re.search(pattern, input_string, re.DOTALL)
    
    # If a JSON object is found...
    if json_string:
        # ...remove leading and trailing whitespace, and load the JSON string into a Python dictionary.
        json_dict = json.loads(json_string.group(1).strip())
    else:
        # If no JSON object is found using the pattern, attempt to parse the entire input string as a JSON object.
        try:
            json_dict = json.loads(input_string)
        except json.JSONDecodeError:
            # If the input string cannot be parsed as a JSON object, return None.
            return None

    # Return the Python dictionary.
    return json_dict

# The function `sum_rubric_scores` is designed to calculate the total score of a completed rubric.
# It iterates over each criterion in the rubric and adds its score to the total score.
def sum_rubric_scores(completed_rubric):
    # Initialize the total score to 0.
    total_score = 0

    # Loop through each criterion in the rubric
    for criterion in completed_rubric['rubric']:
        # Add the score for this criterion to the total score
        total_score += criterion['score']

    return total_score

# Function to generate completion
def generate_completion(prompt, input_data=None):
    # Define system and user prompts

    system_prompt = f"""You are a helpful assistant. 
Your replies are relevant, coherent, complete, accurate, clear, with contextual understanding, specificity, and brief.
Important details are separated by '{separator}'."""

    # user prompt is included every time
    user_prompt = f"{separator} USER PROMPT \n"
    user_prompt += f"{prompt} \n"
    
    # additional data is optional
    if input_data is not None:
        user_prompt += f"{separator} DATA \n"
        user_prompt += f"{input_data} \n"
        
    user_prompt += f"{separator}"

    # Generate conversation
    conversation = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    # Make API request
    completion = chat_request([conversation])[0]

    return completion


# Function to score completion
def score_completion(prompt, completion, rubric, input_data=None):
    # Define system and user prompts

    system_prompt = f"""Score the following completion, that was generated by LLM given the prompt, using the given rubric. 
Be extremely critical when scoring any completion. 
Important details are separated by '{separator}'."""
    
    user_prompt = f"{separator} PROMPT \n"
    user_prompt += f"{prompt} \n"
    
    # additional data is optional
    if input_data is not None:
        user_prompt += f"{separator} DATA \n"
        user_prompt += f"{input_data} \n"
    
    user_prompt += f"{separator} COMPLETION \n"
    user_prompt += f"{completion} \n"
    
    user_prompt += f"{separator} RUBRIC \n"
    user_prompt += json.dumps(rubric, indent=4) + " \n"
    
    # final separator
    user_prompt += f"{separator} \n\n"
    
    user_prompt += "Reply with the rubric JSON only, including the calculated score for each criterion. \nYour reply begins like this: \n"
    user_prompt += "```json"
    
    # Generate conversation
    conversation = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    # Make API request
    response = chat_request([conversation])[0]

    # Load the JSON response into a dict
    completed_rubric = extract_json(response)

    # add up all the scores from the returned rubric
    score = sum_rubric_scores(completed_rubric)

    return score, completed_rubric


# Function to refine prompt
def refine_prompt(prompt, score, instruction_rubric, history, input_data=None):
    # Define system and user prompts
    system_prompt = "Given the rubric score and feedback on the current prompt, as well as the rubric and history of refinements, refine the prompt to improve the rubric scores."
    
    user_prompt = f"{separator} CURRENT PROMPT \n"
    user_prompt += f"{prompt} \n"
    
    user_prompt += f"{separator} SCORE \n"
    user_prompt += f"{score} \n"
    
    user_prompt += f"{separator} RUBRIC \n" 
    user_prompt += json.dumps(instruction_rubric, indent=4) + " \n"
    
    if input_data is not None:
        user_prompt += f"{separator} DATA \n"
        user_prompt += f"{input_data} \n"
    
    user_prompt += f"{separator} REFINEMENT HISTORY \n"
    user_prompt += json.dumps(history, indent=4) + " \n"
    
    # final separator
    user_prompt += f"{separator} \n\n"
    
    # instructions for output
    user_prompt += "Reply with the refined prompt and nothing more."

    # Generate conversation
    conversation = [
        { 'role': 'system', 'content': system_prompt },
        { 'role': 'user', 'content': user_prompt }
    ]

    # Make API request
    refined_prompt = chat_request([conversation])[0]

    return refined_prompt


# Initialize system
# use 'gpt-4' for highest quality. use 'gpt-3.5-turbo-16k' for longer documents and completions
#####  Always Remember That Using the API Incurs Cost ! #####

model = 'gpt-3.5-turbo' 
prompt = "Summarize every book ever written."
original_prompt = prompt
prompt_data = None  # Set this to the input data if it's needed for the task

max_iterations = 5
threshold_score = 80  
refinement_history = []  # To store history of refinements
separator = "#####"

# Main loop
for i in range(max_iterations):
    print(f"Refinement Step: {i+1}")
    
    # generate a completion
    completion = generate_completion(prompt, prompt_data)
    
    # score the completion with the rubric
    score, completed_rubric = score_completion(prompt, completion, instruction_rubric, prompt_data)
    
    # remove the description from the rubric, no need for it now
    for criterion in completed_rubric['rubric']:
        # Remove the description for this criterion
        if 'description' in criterion:
            del criterion['description']
    
    print(f"Prompt: {prompt} \n")
    print(f"Completion: {completion} \n")
    print(f"Score: {score}")
    print(f"Rubric: {completed_rubric} \n")
    
    # keep track of the history
    refinement_history.append({"prompt": prompt, "completion": completion, "score": score, "feedback": completed_rubric})
    
    # return if the score threshold has been met
    if score >= threshold_score:
        print("prompt refinement finished early!")
        break
    elif i+1 < max_iterations:
        prompt = refine_prompt(prompt, score, instruction_rubric, refinement_history, prompt_data)

# take a look at the original vs newly refined prompt
print(f"Original Prompt: {original_prompt}")
print(f"THE NEW PROMPT: {prompt}")
