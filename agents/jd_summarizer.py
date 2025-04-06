from utils.llm_interface import ask_llama_json


def summarize_jd(title, description):
    prompt = f"""
    Given the following Job Title and Job Description, extract:
    - Required Skills
    - Required Experience
    - Education
    - Job Responsibilities

    Strictly give Output as JSON:
    {{"title": "{title}", "skills": [...], "experience": ..., "education": ..., "responsibilities": [...]}}

    Job Description:
    {description}
    """
    return ask_llama_json(prompt)
