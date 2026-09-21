"""
AI Resume Analyzer - Command Line Interface (CLI)
=================================================
A pure Python CLI tool to analyze resumes using Google Gemini.
No Flowgorithm, external flowcharts, or browser GUI required.

Usage:
    python cli_analyzer.py <path_to_resume_pdf>
    python cli_analyzer.py
"""

import os
import sys
import argparse
from PyPDF2 import PdfReader
from google import genai

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load .env file if available locally
if os.path.exists(".env"):
    try:
        with open(".env", "r", encoding="utf-8") as _env_file:
            for _line in _env_file:
                if _line.strip().startswith("GEMINI_API_KEY="):
                    os.environ["GEMINI_API_KEY"] = _line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() or "Add Your API Key Here"

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]


def get_gemini_client():
    api_key = GEMINI_API_KEY
    if not api_key or api_key in [
        "Add Your API Key Here",
        "Add Your API Key",
        "Replace Your API Key Here",
        "Repalce Your API Key Here",
        "YOUR_NEW_GEMINI_API_KEY",
        "YOUR_GEMINI_API_KEY"
    ]:
        raise ValueError(
            "Please set your Gemini API key in the GEMINI_API_KEY environment variable "
            "or edit the GEMINI_API_KEY constant at the top of cli_analyzer.py."
        )
    return genai.Client(api_key=api_key)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text content from a text-based PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    text = ""
    for page_idx, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("Could not extract any text from this PDF. Ensure it is a text-based PDF, not a scanned image.")

    return text.strip()


def ask_gemini(client, prompt: str) -> str:
    """Send prompt to Gemini with automatic model failover and retries."""
    import time
    last_error = None
    for model in GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                if "api_key_invalid" in error_msg or "api key not valid" in error_msg:
                    raise e

                is_transient = any(
                    err in error_msg for err in [
                        "503", "unavailable", "high demand", "spikes in demand",
                        "temporarily", "resource_exhausted", "429", "quota",
                        "404", "not_found", "not available", "overloaded", "internal", "500"
                    ]
                )
                if is_transient:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break

    raise RuntimeError(f"Failed to obtain a response from Gemini after trying multiple models. Last error: {last_error}")


def analyze_resume(client, resume_text: str, task_name: str, instruction: str) -> str:
    """Run an analysis task against the resume text."""
    max_chars = 30000
    if len(resume_text) > max_chars:
        resume_text = resume_text[:max_chars] + "\n\n[Resume text was shortened to fit analysis window]"

    prompt = f"""
You are an expert AI Resume Analyzer and professional career advisor.
Analyze ONLY the resume provided below.

IMPORTANT RULES:
1. Do not invent information or skills.
2. If something is missing, clearly state "Not mentioned".
3. Give practical, constructive recommendations.
4. Keep the response professional with clear markdown headings and bullet points.

============================================================
RESUME CONTENT
============================================================
{resume_text}

============================================================
TASK: {task_name}
============================================================
{instruction}
"""
    return ask_gemini(client, prompt)


TASKS = {
    "Summary": "Create a detailed professional summary covering Candidate Profile, Education, Technical Skills, Projects, Certifications, Experience, Key Strengths, and Career Direction.",
    "Strengths": "Analyze the strengths of this resume across technical skills, problem-solving, and career potential. Explain why each strength is valuable.",
    "Weaknesses": "Analyze weaknesses, missing skills, formatting gaps, and ATS readability. Provide Problem -> Why it matters -> How to improve, followed by a prioritized improvement plan.",
    "Job Titles": "Suggest suitable job roles ranked from most to least suitable, with suitability percentage, matching strengths, and skill gaps to work on.",
    "ATS Score": "Act as an ATS resume evaluator. Give an ESTIMATED score out of 100 with category breakdowns, and explain what is good, what hurts the score, and how to improve.",
    "Skills": "Extract verified skills from the resume categorized into Programming Languages, AI/ML, Data Science, Databases, Web, Cloud/DevOps, Tools, and Soft Skills."
}


def main():
    parser = argparse.ArgumentParser(description="Analyze a resume PDF using pure Python & Google Gemini.")
    parser.add_argument("pdf_path", nargs="?", default=None, help="Path to the PDF resume file.")
    parser.add_argument("--output", "-o", default=None, help="Path to save the analysis report as markdown or text.")
    parser.add_argument("--section", "-s", default="all", choices=["all", "summary", "strengths", "weaknesses", "jobs", "ats", "skills"],
                        help="Specific section to run (default: all).")

    args = parser.parse_args()

    pdf_path = args.pdf_path
    if not pdf_path:
        pdf_path = input("Enter path to your PDF resume: ").strip().strip('"')

    if not pdf_path:
        print("No file provided. Exiting.")
        sys.exit(1)

    print(f"\n[1/3] Reading PDF: {pdf_path}")
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        print(f"      Successfully extracted {len(resume_text)} characters.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("\n[2/3] Connecting to Gemini API...")
    try:
        client = get_gemini_client()
    except Exception as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    print("\n[3/3] Analyzing Resume...")
    results = {}

    selected_tasks = TASKS.items()
    if args.section != "all":
        key_map = {
            "summary": "Summary",
            "strengths": "Strengths",
            "weaknesses": "Weaknesses",
            "jobs": "Job Titles",
            "ats": "ATS Score",
            "skills": "Skills"
        }
        target = key_map[args.section]
        selected_tasks = [(target, TASKS[target])]

    for name, instruction in selected_tasks:
        print(f"      Running {name} analysis...")
        try:
            res = analyze_resume(client, resume_text, name, instruction)
            results[name] = res
        except Exception as e:
            results[name] = f"Error during {name} analysis: {e}"

    # Print results
    print("\n" + "=" * 60)
    print("RESUME ANALYSIS REPORT")
    print("=" * 60 + "\n")

    full_output = []
    for name, res in results.items():
        heading = f"## {name}"
        section_text = f"{heading}\n\n{res}\n\n"
        print(section_text)
        full_output.append(section_text)

    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("# AI Resume Analysis Report\n\n" + "".join(full_output))
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
