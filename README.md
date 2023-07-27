# Automated Prompt Refinement
## Project Overview

The Automated Prompt Refinement project is a prompt refinement system that uses OpenAI's GPT models to generate and refine prompts based on a given rubric. The system aims to improve the quality of generated completions by iteratively refining the prompt based on user feedback and rubric scores.

The provided Python script and rubric are designed to be a springboard, not a one-size-fits-all solution. They are meant to be manipulated and tailored according to the individual requirements of your project.  It's not necessarily meant to be runnable out-of-the-box, but instead designed to be a starting point for you to build upon and create a truly customized tool, so have fun with it!

Scoring with a rubric as opposed to more formal Natural Language Processing (NLP) methods provides several distinct advantages.

## Key Advantages

1. **Absence of Ground Truth Data Requirement**: The need for ground truth data is replaced with rubric scores, which provide an effective error signal for refining the generated prompts. This method allows our system to exhibit learning-like behavior without the necessity of labeled data, thus enabling it to adapt to a wide variety of contexts and tasks with ease.

2. **Dynamic Understanding**: Our system dynamically understands and adapts to various linguistic contexts and nuances, thanks to the GPT models' advanced language understanding capabilities. This flexibility surpasses rigid, rule-bound formal NLP methods.

3. **Generalizability**: The project handles a wide range of tasks, showcasing exceptional versatility compared to formal NLP methods. This broad applicability stems from the GPT models' diverse language understanding capabilities, honed through extensive training on a vast corpus of text data.

4. **Scalability**: Our system effectively scales to tackle larger or more complex tasks. Unlike scaling formal NLP methods, which often require manual adjustments to rules or algorithms, our system harnesses the inherent scalability of GPT models designed for handling large-scale data and generating diverse outputs.

5. **Nuanced Outputs**: Despite the complexity and reduced interpretability of GPT models compared to rule-based NLP methods, our system excels in delivering nuanced and contextually relevant outputs. This enhances the overall quality and relevance of the generated text.

## Key Features

1. **Rubric Scoring**: The system scores the generated completion using a rubric. The rubric consists of several criteria, such as relevance, coherence, completeness, accuracy, clarity, contextual understanding, specificity, and brevity. The scores for each criterion are calculated based on GPT's understanding of the rubric.

2. **Prompt Refinement**: If the rubric score does not meet the desired threshold, the system refines the prompt based on the feedback and rubric scores. It uses the refined prompt to generate a new completion and repeats the scoring and refinement process until the desired score is achieved or the maximum number of iterations is reached.

3. **Completion Generation**: The system generates a completion based on a given prompt and optional input data. It uses OpenAI's GPT models to generate relevant and coherent responses.

## Getting Started

To use the prompt refinement system, follow these steps (this is a walkthrough of the python code):

1. Load your OpenAI API key:
```python
# load your API key here
openai.api_key = None
```

2. Define the rubric for scoring the completions. The rubric should include criteria, descriptions, and initial placeholder scores for each criterion. Adapt the rubric to your specific project or requirements. Example rubric:
```python
instruction_rubric = """
{
    "score_range": [1, 10],
    "rubric": [
        {
            "criterion": "Relevance",
            "description": "Does the response directly address the question or topic of the prompt?",
            "score": "<what's the relevance score?>"
        },
        ...
    ]
}
"""
```

3. Initialize the system by specifying the GPT model to be used:
```python
model = "gpt-3.5-turbo"
```

4. Set the initial prompt and optional input data:
```python
prompt = "Summarize every book ever written."
prompt_data = None  # Set this to the input data if it's needed for the task
```

5. Set the maximum number of refinement iterations and the threshold score:
```python
max_iterations = 5
threshold_score = 10
```

6. Run the main loop to generate completions, score them, and refine the prompt:
```python
for i in range(max_iterations):
    # Generate completion
    completion = generate_completion(prompt, prompt_data)
    
    # Score completion
    score, completed_rubric = score_completion(prompt, completion, instruction_rubric, prompt_data)
    
    # Refine prompt if score threshold is not met
    if score >= threshold_score:
        break
    elif i+1 < max_iterations:
        prompt = refine_prompt(prompt, score, instruction_rubric, refinement_history, prompt_data)
```

## Functions

### `generate_completion(prompt, input_data=None)`

Generates a completion based on the given prompt and optional input data.

- `prompt`: The initial prompt for generating the completion.
- `input_data` (optional): Additional data that can be used to provide context for the completion.

Returns the generated completion. Refine the `system` prompt based on your own needs.

### `score_completion(prompt, completion, rubric, input_data=None)`

Scores the given completion using the provided rubric.

- `prompt`: The prompt used to generate the completion.
- `completion`: The generated completion to be scored.
- `rubric`: The rubric for scoring the completion.
- `input_data` (optional): Additional data used in the prompt or completion.

Returns the total score and the completed rubric.

### `refine_prompt(prompt, score, instruction_rubric, history, input_data=None)`

Refines the given prompt based on the rubric score, feedback, and refinement history.

- `prompt`: The current prompt to be refined.
- `score`: The rubric score of the current completion.
- `instruction_rubric`: The rubric used for scoring the completions.
- `history`: The history of prompt refinements and completions.
- `input_data` (optional): Additional data used in the prompt or completion.

Returns the refined prompt.

## Example Usage

```python
# Initialize system
model = "gpt-3.5-turbo"

prompt = "Summarize every book ever written."
original_prompt = prompt
prompt_data = None  # Set this to the input data if it's needed for the task

max_iterations = 5
threshold_score = 10
refinement_history = []  # To store history of refinements
separator = "#####"

# Main loop
for i in range(max_iterations):
    print(f"Refinement Step: {i+1}")
    
    # Generate a completion
    completion = generate_completion(prompt, prompt_data)
    
    # Score the completion with the rubric
    score, completed_rubric = score_completion(prompt, completion, instruction_rubric, prompt_data)
    
    # Remove the description from the rubric, no need for it now
    for criterion in completed_rubric['rubric']:
        if 'description' in criterion:
            del criterion['description']
    
    print(f"Prompt: {prompt} \n")
    print(f"Completion: {completion} \n")
    print(f"Rubric: {completed_rubric} \n")
    
    # Keep track of the history
    refinement_history.append({"prompt": prompt, "completion": completion, "score": score, "feedback": completed_rubric})
    
    # Return if the score threshold has been met
    if score >= threshold_score:
        print("Prompt refinement finished early!")
        break
    elif i+1 < max_iterations:
        prompt = refine_prompt(prompt, score, instruction_rubric, refinement_history, prompt_data)

print(f"Original Prompt: {original_prompt}")
print(f"THE NEW PROMPT: {prompt}")
```

## Conclusion

The Automated Prompt Refinement project combines rubric-based scoring and OpenAI's GPT models to provide a powerful tool for generating high-quality, refined prompts. This system demonstrates the potential of AI combined with rubric-based assessment, revolutionizing the process of content creation and refinement. With our innovative approach, we empower users to achieve exceptional results in their text generation tasks.

_"The versatility of the Automated Prompt Refinement system has transformed our content generation process. It's like having a creative and technical writer, all in one!"_ - Sarah, Content Manager

_"I was blown away by how the software adapted to our needs without requiring any labeled data. It's a game-changer for sure!"_ - Mark, Data Scientist
