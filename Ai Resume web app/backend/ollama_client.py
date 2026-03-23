import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="mistral:latest"):
        self.base_url = base_url
        self.model = model
        self.generate_url = f"{self.base_url}/api/generate"

    def generate_response(self, prompt, system_prompt=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.generate_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return None

    def analyze_resume(self, resume_text):
        system_prompt = "You are a professional HR manager and resume expert. Analyze the following resume text and provide a structured review."
        prompt = f"""
        Analyze the following resume text. 
        Provide the response in the following format:
        1. Overall Score (out of 10)
        2. Strengths
        3. Weaknesses
        4. Suggestions for improvement

        Resume Text:
        {resume_text}
        """
        return self.generate_response(prompt, system_prompt)

    def generate_resume_content(self, user_data):
        system_prompt = "You are a professional resume writer. Create a clean, well-structured resume using the following sections: NAME, TITLE, CONTACT (Phone, Email, Location), ABOUT ME, EDUCATION, WORK EXPERIENCE, and SKILLS."
        prompt = f"""
        Create a professional resume using the following details:
        Name: {user_data.get('name')}
        Education: {user_data.get('education')}
        Skills: {user_data.get('skills')}
        Experience: {user_data.get('experience')}
        Projects: {user_data.get('projects')}

        FORMATTING RULES:
        1. Start with the NAME and a professional TITLE (infer from skills/experience).
        2. Include a CONTACT line with placeholders for Phone, Email, and Location if not provided.
        3. Use clear headers: ABOUT ME, EDUCATION, WORK EXPERIENCE, SKILLS.
        4. For EDUCATION and WORK EXPERIENCE, use the format: "Institution/Company | Dates" followed by a "Role" line and bullet points.
        5. Keep the SKILLS section as a concise list.
        
        Provide the output in a structured text format that clearly separates these sections.
        """
        return self.generate_response(prompt, system_prompt)
