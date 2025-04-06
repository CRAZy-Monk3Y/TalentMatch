import json

from utils.llm_interface import ask_llama


# --- agents/scheduler.py ---
def generate_emails(
    shortlisted, jd_summary, progress_bar, progress_val, progress_segments
):
    emails = {}
    increments = int(progress_segments / len(shortlisted))
    for c in shortlisted:
        user_name = c["name"] if "name" in c else "<USER NAME>"
        jd_title = json.loads(jd_summary)["title"]
        user_email = c["email"] if "email" in c else "<USER EMAIL>"
        prompt = f"""
        Write a professional interview invitation email for {user_name} regarding the position '{jd_title}'.

        INSTRUCTIONS:
        Strictly give output in below format. Don't describe or write your comments with the output.

        FORMAT:
        Subject: <Email Subject>

        Dear <candidate>,

        We are pleased to inform you that you have been selected as a candidate for the position of <job-position> at Accenture Public Limited Company, as part of our ongoing recruitment process.

        As we move forward in our search for the ideal candidate, we would like to invite you to an interview with our team. The purpose of this interview is to further assess your skills and experience in <job-position>, and to discuss how you can contribute to our organization's success. Please find the interview invite attached with this mail.

        We are excited about the possibility of having you join our team as a <job-position> and look forward to meeting you soon.

        Best regards,

        Recruitment Team
        Accenture Public Limited Company

        """
        emails[user_email] = ask_llama(prompt)
        progress_val += increments
        progress_bar.progress(
            progress_val,
            f"Overall completion {progress_val}% writing emails for the shortlistedcandidates...",
        )
    return emails
