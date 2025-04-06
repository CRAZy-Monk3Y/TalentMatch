# --- agents/recruiter.py ---
import json
import re

from utils.llm_interface import ask_llama_json


def process_resumes(resumes, jd_summary, progress_bar, progress_val, progress_segments):
    candidates = []
    increments = int(progress_segments / len(resumes))
    for text in resumes:
        prompt = f"""
        From the following resume, extract: Skills, Experience, Education. Then compare with the JD Summary below and calculate a match (0-100).

        Resume:
        {text}

        JD Summary:
        {jd_summary}

        Match value calculation weightage(out of 100):
        Skills - (0-35) 
        Experience - (0-35)
        Education - (0-30)
        match = Skills + Experience + Education

        Strictly give Output as JSON: {{"name":..., "email":..., "match":..., "skills": [...] }}

        Sample Output:
        {{"name":"John Doe", "email":"john@google.com","match": 20, "skills": ["Java","MySQL","Postman"]}}
        """
        result = ask_llama_json(prompt)
        try:
            pattern = r"json(.*?)```"
            matches = re.findall(pattern, result, re.DOTALL)
            result = matches[0]
        except:
            pass
        candidates.append(json.loads(result))
        progress_val += increments
        progress_bar.progress(
            progress_val,
            f"Overall completion {progress_val}% Processing resumes for Role: {json.loads(jd_summary)['title']}",
        )
    return candidates
