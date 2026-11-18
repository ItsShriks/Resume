import json
import re
import os
import requests
from typing import Dict, Any, Optional
from app.config import DEFAULT_GEMINI_MODEL, GEMINI_API_KEY
from app.services.profile_service import ProfileService

class GeminiService:
    @staticmethod
    def _call_gemini_api(
        prompt: str,
        system_instruction: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        key = api_key or os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
        if not key:
            raise ValueError("Google Gemini API Key is required. Please provide it in Settings or set GEMINI_API_KEY.")
            
        model_name = model or DEFAULT_GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        
        contents = [{"parts": [{"text": prompt}]}]
        body: Dict[str, Any] = {"contents": contents}
        
        if system_instruction:
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        generation_config: Dict[str, Any] = {
            "temperature": 0.2,
            "maxOutputTokens": 8192,
        }
        if json_mode:
            generation_config["responseMimeType"] = "application/json"
            
        body["generationConfig"] = generation_config
        
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        
        if resp.status_code != 200:
            err_msg = resp.text
            try:
                err_json = resp.json()
                if "error" in err_json and "message" in err_json["error"]:
                    err_msg = err_json["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(f"Gemini API Error ({resp.status_code}): {err_msg}")
            
        res_json = resp.json()
        try:
            candidates = res_json.get("candidates", [])
            if not candidates:
                raise ValueError("No response candidates received from Gemini API.")
            content_parts = candidates[0].get("content", {}).get("parts", [])
            full_text = "".join([p.get("text", "") for p in content_parts])
            return full_text
        except Exception as e:
            raise RuntimeError(f"Failed to parse Gemini response: {str(e)}\nRaw: {res_json}")

    @classmethod
    def analyze_job(
        cls,
        jd_text: str,
        master_profile: Dict[str, Any],
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyzes Job Description and computes ATS match score and extracted keywords for any industry."""
        system_instruction = (
            "You are an Elite Global Recruiter, Hiring Executive, and ATS (Applicant Tracking System) Optimization Expert. "
            "You analyze candidate qualifications against Job Descriptions across any domain, including Software Engineering, "
            "Data Science & AI, Robotics, Hardware, Product Management, Business & Operations, Finance, Marketing, Design, "
            "Healthcare, and Science. Provide objective, high-signal, actionable feedback."
        )
        
        prompt = f"""
Candidate Profile:
Name: {master_profile.get('name', 'Candidate')}
Title/Background: {master_profile.get('title', 'Professional')}
Summary & Experience:
{master_profile.get('sections', {}).get('personal_info', '')}
{master_profile.get('sections', {}).get('work_experience', '')}
{master_profile.get('sections', {}).get('projects', '')}
{master_profile.get('sections', {}).get('skills', '')}

Job Description:
\"\"\"{jd_text}\"\"\"

Provide an in-depth analysis formatted as strict JSON with the following keys:
{{
  "job_title": "Extracted target job title",
  "company_name": "Extracted company name (or 'Company' if not stated)",
  "industry_domain": "Detected domain (e.g. Software / Data / Product / Marketing / Finance / Engineering / Design / Healthcare)",
  "match_score": 85 (an integer from 0 to 100 based on realistic technical fit),
  "match_summary": "2-3 concise sentences summarizing why the candidate is a strong fit and where the main alignment is",
  "required_keywords": ["list", "of", "vital", "skills", "tools", "and", "qualifications", "from", "JD"],
  "matching_strengths": ["list", "of", "strongest", "matching", "experiences", "or", "skills"],
  "missing_or_gap_keywords": ["list", "of", "keywords", "in", "JD", "that", "need", "emphasis", "or", "gap"],
  "actionable_tips": [
    "Tip 1 on how to adjust experience bullets",
    "Tip 2 on which project/achievement to prioritize",
    "Tip 3 on skill or qualification ordering"
  ]
}}
"""
        raw_output = cls._call_gemini_api(
            prompt=prompt,
            system_instruction=system_instruction,
            api_key=api_key,
            model=model,
            json_mode=True
        )
        
        try:
            return json.loads(raw_output)
        except Exception:
            cleaned = re.sub(r"^```json\s*", "", raw_output.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)

    @classmethod
    def tailor_resume(
        cls,
        jd_text: str,
        master_profile: Dict[str, Any],
        target_role: Optional[str] = None,
        language: str = "English",
        focus_area: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tailors Summary, Experience, Projects, and Skills for ANY industry or field to match the Job Description.
        """
        sections = master_profile.get("sections", {})
        
        system_instruction = (
            "You are an Elite Resume Strategist & LaTeX Specialist across all technical and non-technical disciplines "
            "(Software, Tech, Product, Engineering, Science, Business, Marketing, Finance, Design, Healthcare, Operations). "
            "Your task is to tailor the candidate's resume sections specifically for the target job description. "
            "CRITICAL RULES:\n"
            "1. NEVER invent fake companies, degrees, or years of experience. Keep facts 100% grounded in the candidate's actual history.\n"
            "2. Reword, sharpen, and reorder bullet points to prominently feature relevant keywords, metrics, and responsibilities from the JD.\n"
            "3. Output valid LaTeX for each section matching the exact commands used in the original LaTeX snippets "
            "(\\resumeSubheading for jobs/degrees, \\resumeProject{title}{link or dates}{tech}{context} for projects, \\resumeItem, \\resumeItemPlain, \\resumeSubItem, \\resumeSubHeadingListStart, \\resumeItemListStart, etc.).\n"
            "The master content in refs/ is plain English notes (\"## Title\" blocks with When / Where / Link / Tech lines, "
            "bullets and Notes). Write every entry out in full LaTeX; follow the Notes but never copy them. "
            "Never use facts that are not in refs/.\n"
            "4. Escape special LaTeX characters properly (e.g. \\& for &, \\% for %, \\_ for _).\n"
            "5. Return a strict JSON object containing the updated LaTeX code for each section."
        )

        prompt = f"""
TARGET JOB DESCRIPTION:
\"\"\"{jd_text}\"\"\"

TARGET ROLE: {target_role or 'As deduced from JD'}
PRIMARY FOCUS AREA: {focus_area or 'Auto-align to JD industry and role'}
LANGUAGE: {language}

CANDIDATE'S MASTER CONTENT (refs/, source of truth):
{ProfileService.refs_text(master_profile)}

CANDIDATE'S CURRENT TAILORED LATEX SECTIONS (tex/):

--- [Personal_Info.tex (Summary)] ---
{sections.get('personal_info', '')}

--- [Work_Experience.tex] ---
{sections.get('work_experience', '')}

--- [Projects.tex] ---
{sections.get('projects', '')}

--- [Skills.tex] ---
{sections.get('skills', '')}

TASK:
Produce a tailored version of these 4 sections to maximize ATS match and impact for this specific job description.
Return a strict JSON object with:
{{
  "tailored_summary_tex": "Full LaTeX code for Summary section",
  "tailored_work_experience_tex": "Full LaTeX code for Work Experience section",
  "tailored_projects_tex": "Full LaTeX code for Projects/Key Achievements section (prioritize top 3-4 most relevant)",
  "tailored_skills_tex": "Full LaTeX code for Skills section (categorized and ordered to highlight JD technologies/competencies first)",
  "tailoring_notes": [
    "Brief explanation of changes made in experience bullets",
    "Brief explanation of project selection rationale",
    "Keywords highlighted"
  ]
}}
"""
        raw_output = cls._call_gemini_api(
            prompt=prompt,
            system_instruction=system_instruction,
            api_key=api_key,
            model=model,
            json_mode=True
        )
        
        try:
            return json.loads(raw_output)
        except Exception:
            cleaned = re.sub(r"^```json\s*", "", raw_output.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)

    @classmethod
    def generate_cover_letter(
        cls,
        jd_text: str,
        master_profile: Dict[str, Any],
        company_name: Optional[str] = None,
        role_title: Optional[str] = None,
        language: str = "English",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a matching Cover Letter (or German Anschreiben) for any profession."""
        system_instruction = (
            "You are a professional Career Coach and Executive Copywriter across all industries. "
            "Write a persuasive, highly tailored, professional Cover Letter (or German Anschreiben) "
            "based on the candidate's background and the target job description. "
            "Ensure the letter strictly follows standard professional conventions in Europe / International standards, "
            "demonstrates deep interest in the company, cites concrete achievements from their background, "
            "and outputs clean LaTeX suitable for compilation with the provided template."
        )

        template_tex = master_profile.get("cover_letter_tex", "")
        candidate_name = master_profile.get("name", "Candidate")
        candidate_location = master_profile.get("location", "Bonn, Germany")
        candidate_email = master_profile.get("email", "candidate@example.com")
        sections = master_profile.get("sections", {})

        prompt = f"""
TARGET JOB DESCRIPTION:
\"\"\"{jd_text}\"\"\"

COMPANY: {company_name or 'Hiring Company'}
ROLE TITLE: {role_title or 'Target Role'}
LANGUAGE: {language} (If German, write a fluent, authentic German Anschreiben. If English, write an impactful English Cover Letter).

CANDIDATE BACKGROUND:
Name: {candidate_name}
Location: {candidate_location}
Email: {candidate_email}
Summary:
{sections.get('personal_info', '')}
Experience:
{sections.get('work_experience', '')}
Projects:
{sections.get('projects', '')}
Skills:
{sections.get('skills', '')}
Master content (refs/, source of truth):
{ProfileService.refs_text(master_profile)}

REFERENCE LATEX TEMPLATE:
{template_tex}

TASK:
Produce a customized, complete standalone LaTeX document for the Cover Letter matching the styling and layout of the template.
Ensure all special characters are escaped (\\&, \\%, \\_).
Return strict JSON:
{{
  "cover_letter_tex": "Full LaTeX code for the standalone cover letter",
  "subject_line": "Re: Application for ...",
  "salutation": "Dear Hiring Team, / Sehr geehrte Damen und Herren,",
  "highlights_summary": "Brief 2-sentence summary of the key pitch in this letter"
}}
"""
        raw_output = cls._call_gemini_api(
            prompt=prompt,
            system_instruction=system_instruction,
            api_key=api_key,
            model=model,
            json_mode=True
        )
        
        try:
            return json.loads(raw_output)
        except Exception:
            cleaned = re.sub(r"^```json\s*", "", raw_output.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)

    @classmethod
    def parse_raw_resume(
        cls,
        raw_cv_text: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Takes raw text of any person's CV/Resume and converts it into structured LaTeX sections
        compatible with the application's clean LaTeX template.
        """
        system_instruction = (
            "You are an Elite Resume Parser and LaTeX Specialist. "
            "Extract and convert the candidate's raw resume into clean, valid LaTeX sections "
            "using standard LaTeX commands (\\resumeSubheading, \\resumeItem, \\resumeItemPlain, \\resumeSubItem, \\resumeSubHeadingListStart, etc.). "
            "Escape all special characters (\\&, \\%, \\_). "
            "Output strict JSON with candidate metadata and LaTeX sections."
        )

        prompt = f"""
RAW RESUME TEXT:
\"\"\"{raw_cv_text}\"\"\"

TASK:
Extract the candidate's information and produce valid LaTeX sections for:
1. personal_info: Short summary paragraph
2. work_experience: Full work experience section with \\resumeSubheading and \\resumeItemListStart
3. projects: Key projects or achievements with \\resumeSubItem and \\resumeItemListStart
4. education: Education history
5. skills: Categorized skills with \\resumeSubItem

Return a strict JSON object:
{{
  "name": "Extracted candidate full name",
  "title": "Extracted professional title or target field",
  "location": "City, Country",
  "email": "candidate email",
  "linkedin": "LinkedIn URL or handle (or empty)",
  "github": "GitHub/Portfolio URL (or empty)",
  "sections": {{
    "personal_info": "\\section{{Summary}}\\n...",
    "work_experience": "\\section{{Experience}}\\n\\resumeSubHeadingListStart\\n...",
    "projects": "\\section{{Projects}}\\n\\resumeSubHeadingListStart\\n...",
    "education": "\\section{{Education}}\\n\\resumeSubHeadingListStart\\n...",
    "skills": "\\section{{Skills}}\\n\\resumeSubHeadingListStart\\n..."
  }}
}}
"""
        raw_output = cls._call_gemini_api(
            prompt=prompt,
            system_instruction=system_instruction,
            api_key=api_key,
            model=model,
            json_mode=True
        )

        try:
            return json.loads(raw_output)
        except Exception:
            cleaned = re.sub(r"^```json\s*", "", raw_output.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)

