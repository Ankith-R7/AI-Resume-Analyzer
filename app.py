import time
import warnings
from urllib.parse import quote

import pandas as pd
import streamlit as st

from google import genai

from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space

from PyPDF2 import PdfReader

from selenium import webdriver
from selenium.webdriver.common.by import By

warnings.filterwarnings("ignore")


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# IMPORTANT:A
# Replace this with your NEW Gemini API key.
GEMINI_API_KEY = "Repalce Your API Key Here"

# Current model.
# The code below also contains fallback models.
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite"
]


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():

    if (
        not GEMINI_API_KEY
        or GEMINI_API_KEY == "YOUR_NEW_GEMINI_API_KEY"
    ):
        raise ValueError(
            "Please add your new Gemini API key to GEMINI_API_KEY "
            "at the top of app.py."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# GEMINI REQUEST
# ============================================================

def ask_gemini(prompt):

    client = get_gemini_client()

    last_error = None

    for model in GEMINI_MODELS:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                return response.text

        except Exception as e:

            last_error = e

            error_text = str(e)

            # If model is unavailable, try the next model.
            if (
                "404" in error_text
                or "NOT_FOUND" in error_text
                or "not available" in error_text.lower()
            ):
                continue

            # API key/quota errors should not be hidden.
            raise e

    raise RuntimeError(
        f"Gemini could not generate a response.\n\n"
        f"Last error: {last_error}"
    )


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

def streamlit_config():

    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide"
    )

    page_css = """
    <style>

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .section-title {
        color: orange;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    </style>
    """

    st.markdown(
        page_css,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">📄 AI Resume Analyzer</div>',
        unsafe_allow_html=True
    )


# ============================================================
# RESUME ANALYZER
# ============================================================

class resume_analyzer:

    # --------------------------------------------------------
    # PDF TO TEXT
    # --------------------------------------------------------

    @staticmethod
    def pdf_to_text(pdf):

        reader = PdfReader(pdf)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if not text.strip():

            raise ValueError(
                "Could not extract text from this PDF. "
                "Please upload a text-based PDF."
            )

        return text


    # --------------------------------------------------------
    # LIMIT TEXT
    # --------------------------------------------------------

    @staticmethod
    def prepare_resume(text):

        # Prevent extremely large prompts.
        max_characters = 30000

        if len(text) > max_characters:

            text = text[:max_characters]

            text += (
                "\n\n[Resume text was shortened because it was "
                "too large for analysis.]"
            )

        return text


    # --------------------------------------------------------
    # GEMINI ANALYSIS
    # --------------------------------------------------------

    @staticmethod
    def gemini(resume_text, instruction):

        resume_text = resume_analyzer.prepare_resume(
            resume_text
        )

        prompt = f"""
You are an expert AI Resume Analyzer and professional
career advisor.

Analyze ONLY the resume provided below.

IMPORTANT RULES:

1. Do not invent information.
2. Do not invent skills.
3. Do not invent experience.
4. Do not invent projects.
5. Do not invent certifications.
6. Do not invent achievements.
7. Do not invent education.
8. If something is missing, clearly say "Not mentioned".
9. Give practical recommendations.
10. Keep the response professional.
11. Use headings and bullet points.
12. Focus on entry-level/fresher opportunities when appropriate.

============================================================
RESUME
============================================================

{resume_text}

============================================================
TASK
============================================================

{instruction}

============================================================

Return a clear and structured answer.
"""

        return ask_gemini(prompt)


    # --------------------------------------------------------
    # SUMMARY PROMPT
    # --------------------------------------------------------

    @staticmethod
    def summary_prompt():

        return """
Create a detailed professional summary of this resume.

Include:

1. Candidate Profile
2. Education
3. Technical Skills
4. Programming Languages
5. AI / Machine Learning Skills
6. Projects
7. Certifications
8. Experience
9. Achievements
10. Key Strengths
11. Career Direction

Finally provide:

Overall Candidate Conclusion
"""


    # --------------------------------------------------------
    # STRENGTH PROMPT
    # --------------------------------------------------------

    @staticmethod
    def strength_prompt():

        return """
Analyze the strengths of this resume.

Consider:

1. Technical skills
2. Programming languages
3. AI/ML skills
4. Projects
5. Education
6. Certifications
7. Achievements
8. Experience
9. Problem-solving ability
10. Career potential
11. Resume presentation

For each strength, explain why it is valuable.

Finally provide:

Overall Strength Assessment
"""


    # --------------------------------------------------------
    # WEAKNESS PROMPT
    # --------------------------------------------------------

    @staticmethod
    def weakness_prompt():

        return """
Analyze the weaknesses of this resume.

Check:

1. Missing skills
2. Weak technical sections
3. Weak project descriptions
4. Missing measurable achievements
5. Education presentation
6. Experience section
7. Certification gaps
8. Grammar
9. Wording
10. Formatting
11. ATS friendliness
12. Missing keywords
13. Career positioning

For every important weakness provide:

Problem:
Why it matters:
How to improve:

Finally create a prioritized improvement plan.
"""


    # --------------------------------------------------------
    # JOB TITLE PROMPT
    # --------------------------------------------------------

    @staticmethod
    def job_title_prompt():

        return """
Suggest suitable job roles for this candidate.

Rank them from MOST suitable to LEAST suitable.

For every role provide:

1. Job Title
2. Suitability percentage
3. Why the candidate matches
4. Skills already present
5. Skills that should be improved

Focus mainly on realistic entry-level and fresher roles.

Possible categories include:

- Software Developer
- Python Developer
- AI Engineer
- Machine Learning Engineer
- Data Analyst
- Data Scientist
- Backend Developer
- Full Stack Developer
- SQL Developer
- Business Analyst

Only recommend roles reasonably supported by the resume.
"""


    # --------------------------------------------------------
    # ATS PROMPT
    # --------------------------------------------------------

    @staticmethod
    def ats_prompt():

        return """
Act as an ATS-style resume evaluation system.

Give an ESTIMATED ATS score out of 100.

Scoring:

1. Keyword Optimization - 20
2. Technical Skills - 15
3. Job Title Alignment - 10
4. Project Relevance - 15
5. Resume Structure - 10
6. Education - 10
7. Achievements - 5
8. Certifications - 5
9. Experience - 5
10. ATS Readability - 5

Return:

ATS SCORE: XX/100

Then explain:

- What is good
- What reduces the score
- Missing keywords
- Weak sections
- Formatting issues
- Grammar issues
- How to improve the score

IMPORTANT:

This is an AI-estimated score.
It is NOT an official score from any ATS company.
"""


    # --------------------------------------------------------
    # SKILLS PROMPT
    # --------------------------------------------------------

    @staticmethod
    def skills_prompt():

        return """
Extract the skills actually present in the resume.

Organize them into:

1. Programming Languages
2. AI / Machine Learning
3. Data Science
4. Databases
5. Web Development
6. Cloud / DevOps
7. Tools
8. Frameworks
9. Soft Skills

Do not invent skills.

At the end provide:

Strongest Skills:
Skills To Improve:
Missing Important Skills:
"""


    # --------------------------------------------------------
    # RESUME PAGE
    # --------------------------------------------------------

    @staticmethod
    def resume_page(title, instruction, cache_key):

        st.markdown(
            f'<div class="section-title">{title}</div>',
            unsafe_allow_html=True
        )

        if "resume_text" not in st.session_state:
            return

        # Check if cached results exist
        if cache_key in st.session_state:
            st.write(st.session_state[cache_key])
        else:
            st.info("Please click the '🚀 Analyze Resume' button at the top of the page to generate the analysis.")


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    @staticmethod
    def resume_summary():

        resume_analyzer.resume_page(
            "📋 Resume Summary",
            resume_analyzer.summary_prompt(),
            "summary_result"
        )


    # --------------------------------------------------------
    # STRENGTH
    # --------------------------------------------------------

    @staticmethod
    def resume_strength():

        resume_analyzer.resume_page(
            "💪 Resume Strengths",
            resume_analyzer.strength_prompt(),
            "strength_result"
        )


    # --------------------------------------------------------
    # WEAKNESS
    # --------------------------------------------------------

    @staticmethod
    def resume_weakness():

        resume_analyzer.resume_page(
            "⚠️ Resume Weaknesses & Suggestions",
            resume_analyzer.weakness_prompt(),
            "weakness_result"
        )


    # --------------------------------------------------------
    # JOB TITLES
    # --------------------------------------------------------

    @staticmethod
    def job_title_suggestion():

        resume_analyzer.resume_page(
            "💼 Recommended Job Titles",
            resume_analyzer.job_title_prompt(),
            "job_title_result"
        )


    # --------------------------------------------------------
    # ATS
    # --------------------------------------------------------

    @staticmethod
    def ats_score():

        resume_analyzer.resume_page(
            "📊 ATS Resume Score",
            resume_analyzer.ats_prompt(),
            "ats_score_result"
        )


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    @staticmethod
    def skills():

        resume_analyzer.resume_page(
            "🧠 Resume Skills Analysis",
            resume_analyzer.skills_prompt(),
            "skills_result"
        )


# ============================================================
# LINKEDIN JOB SCRAPER
# ============================================================

class linkedin_scraper:

    # --------------------------------------------------------
    # WEBDRIVER
    # --------------------------------------------------------

    @staticmethod
    def webdriver_setup():

        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            options=options
        )

        return driver


    # --------------------------------------------------------
    # USER INPUT
    # --------------------------------------------------------

    @staticmethod
    def get_userinput():

        with st.form(
            key="linkedin_scraper_form"
        ):

            col1, col2, col3 = st.columns(
                [0.5, 0.3, 0.2]
            )

            with col1:

                job_title = st.text_input(
                    "Job Title",
                    placeholder=(
                        "Python Developer, AI Engineer"
                    )
                )

            with col2:

                job_location = st.text_input(
                    "Job Location",
                    value="India"
                )

            with col3:

                job_count = st.number_input(
                    "Job Count",
                    min_value=1,
                    max_value=20,
                    value=5,
                    step=1
                )

            submit = st.form_submit_button(
                "🔎 Search Jobs"
            )

        return (
            job_title,
            job_location,
            int(job_count),
            submit
        )


    # --------------------------------------------------------
    # BUILD URL
    # --------------------------------------------------------

    @staticmethod
    def build_url(
        job_title,
        job_location
    ):

        keywords = quote(
            job_title.strip()
        )

        location = quote(
            job_location.strip()
        )

        return (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={keywords}"
            f"&location={location}"
        )


    # --------------------------------------------------------
    # OPEN LINK
    # --------------------------------------------------------

    @staticmethod
    def open_link(
        driver,
        link
    ):

        driver.get(link)

        driver.implicitly_wait(5)

        time.sleep(4)


    # --------------------------------------------------------
    # SCROLL
    # --------------------------------------------------------

    @staticmethod
    def scroll_page(
        driver,
        job_count
    ):

        for _ in range(
            min(job_count, 10)
        ):

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(2)


    # --------------------------------------------------------
    # SCRAPE JOB DATA
    # --------------------------------------------------------

    @staticmethod
    def scrap_company_data(
        driver,
        job_location
    ):

        companies = driver.find_elements(
            By.CSS_SELECTOR,
            "h4.base-search-card__subtitle"
        )

        titles = driver.find_elements(
            By.CSS_SELECTOR,
            "h3.base-search-card__title"
        )

        locations = driver.find_elements(
            By.CSS_SELECTOR,
            "span.job-search-card__location"
        )

        links = driver.find_elements(
            By.CSS_SELECTOR,
            "a.base-card__full-link"
        )

        data = []

        count = min(
            len(companies),
            len(titles),
            len(locations),
            len(links)
        )

        for i in range(count):

            company = companies[i].text.strip()
            title = titles[i].text.strip()
            location = locations[i].text.strip()
            url = links[i].get_attribute("href")

            if (
                job_location.lower()
                in location.lower()
            ):

                data.append({
                    "Company Name": company,
                    "Job Title": title,
                    "Location": location,
                    "Website URL": url
                })

        return pd.DataFrame(data)


    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    @staticmethod
    def scrap_job_description(
        driver,
        df,
        job_count
    ):

        if df.empty:

            return df

        descriptions = []

        urls = df["Website URL"].tolist()

        for url in urls[:job_count]:

            try:

                driver.get(url)

                time.sleep(3)

                description_elements = (
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.show-more-less-html__markup"
                    )
                )

                if description_elements:

                    description = (
                        description_elements[0].text
                    )

                else:

                    description = (
                        "Description Not Available"
                    )

            except Exception:

                description = (
                    "Description Not Available"
                )

            descriptions.append(
                description
            )

        result = df.iloc[
            :len(descriptions)
        ].copy()

        result["Job Description"] = descriptions

        return result


    # --------------------------------------------------------
    # DISPLAY JOBS
    # --------------------------------------------------------

    @staticmethod
    def display_data_userinterface(df):

        if df.empty:

            st.warning(
                "No matching jobs found."
            )

            return

        st.success(
            f"Found {len(df)} job listings."
        )

        for index, row in df.iterrows():

            st.markdown(
                f"### 💼 Job Posting {index + 1}"
            )

            st.write(
                f"**Company:** {row['Company Name']}"
            )

            st.write(
                f"**Job Title:** {row['Job Title']}"
            )

            st.write(
                f"**Location:** {row['Location']}"
            )

            st.markdown(
                f"[Open Job Posting]({row['Website URL']})"
            )

            with st.expander(
                "Job Description"
            ):

                st.write(
                    row["Job Description"]
                )

            st.markdown("---")


    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

    @staticmethod
    def main():

        st.markdown(
            '<div class="section-title">'
            '🔎 LinkedIn Jobs'
            '</div>',
            unsafe_allow_html=True
        )

        (
            job_title,
            job_location,
            job_count,
            submit
        ) = linkedin_scraper.get_userinput()

        if not submit:

            return

        if not job_title.strip():

            st.warning(
                "Please enter a job title."
            )

            return

        if not job_location.strip():

            st.warning(
                "Please enter a job location."
            )

            return

        driver = None

        try:

            with st.spinner(
                "Starting Chrome..."
            ):

                driver = (
                    linkedin_scraper.webdriver_setup()
                )

            link = (
                linkedin_scraper.build_url(
                    job_title,
                    job_location
                )
            )

            with st.spinner(
                "Searching LinkedIn jobs..."
            ):

                linkedin_scraper.open_link(
                    driver,
                    link
                )

                linkedin_scraper.scroll_page(
                    driver,
                    job_count
                )

            with st.spinner(
                "Collecting job information..."
            ):

                df = (
                    linkedin_scraper.scrap_company_data(
                        driver,
                        job_location
                    )
                )

                df = (
                    linkedin_scraper.scrap_job_description(
                        driver,
                        df,
                        job_count
                    )
                )

            linkedin_scraper.display_data_userinterface(
                df
            )

        except Exception as e:

            st.error(
                f"LinkedIn scraper error: {e}"
            )

        finally:

            if driver:

                driver.quit()


# ============================================================
# MAIN APPLICATION
# ============================================================

streamlit_config()

add_vertical_space(2)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🤖 AI Resume"
    )

    st.markdown("---")

    option = option_menu(
        menu_title="Resume Tools",

        options=[
            "Summary",
            "Strength",
            "Weakness",
            "Job Titles",
            "ATS Score",
            "Skills",
            "Linkedin Jobs"
        ],

        icons=[
            "file-text",
            "check-circle",
            "exclamation-triangle",
            "briefcase",
            "bar-chart",
            "gear",
            "linkedin"
        ],

        default_index=0
    )


# ============================================================
# GLOBAL RESUME UPLOADER
# ============================================================

if option != "Linkedin Jobs":

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        uploaded_pdf = st.file_uploader(
            "Upload Your Resume",
            type=["pdf"],
            key="global_resume_uploader"
        )

        if uploaded_pdf:
            if (
                "resume_pdf_name" not in st.session_state
                or st.session_state["resume_pdf_name"] != uploaded_pdf.name
            ):
                try:
                    with st.spinner("Extracting text from resume..."):
                        text = resume_analyzer.pdf_to_text(uploaded_pdf)
                        st.session_state["resume_text"] = text
                        st.session_state["resume_pdf_name"] = uploaded_pdf.name
                        # Clear any cached analysis results
                        st.session_state.pop("summary_result", None)
                        st.session_state.pop("strength_result", None)
                        st.session_state.pop("weakness_result", None)
                        st.session_state.pop("job_title_result", None)
                        st.session_state.pop("ats_score_result", None)
                        st.session_state.pop("skills_result", None)
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")

            # Check if all analysis results exist
            is_analyzed = all(
                key in st.session_state
                for key in ["summary_result", "strength_result", "weakness_result", "job_title_result", "ats_score_result", "skills_result"]
            )

            if not is_analyzed:
                if st.button("🚀 Analyze Resume", key="global_analyze_button", use_container_width=True):
                    try:
                        with st.spinner("Analyzing resume with Gemini (this will take a moment)..."):
                            # Run summary
                            st.session_state["summary_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.summary_prompt()
                            )
                            # Run strengths
                            st.session_state["strength_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.strength_prompt()
                            )
                            # Run weaknesses
                            st.session_state["weakness_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.weakness_prompt()
                            )
                            # Run job titles
                            st.session_state["job_title_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.job_title_prompt()
                            )
                            # Run ATS score
                            st.session_state["ats_score_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.ats_prompt()
                            )
                            # Run skills
                            st.session_state["skills_result"] = resume_analyzer.gemini(
                                st.session_state["resume_text"],
                                resume_analyzer.skills_prompt()
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
            else:
                col_btn1, col_btn2 = st.columns([3, 1])
                with col_btn1:
                    st.success("✅ Analysis completed successfully!")
                with col_btn2:
                    if st.button("🔄 Re-analyze", key="global_reanalyze_button", use_container_width=True):
                        st.session_state.pop("summary_result", None)
                        st.session_state.pop("strength_result", None)
                        st.session_state.pop("weakness_result", None)
                        st.session_state.pop("job_title_result", None)
                        st.session_state.pop("ats_score_result", None)
                        st.session_state.pop("skills_result", None)
                        st.rerun()
        else:
            st.session_state.pop("resume_text", None)
            st.session_state.pop("resume_pdf_name", None)

    st.markdown("---")


# ============================================================
# PAGE ROUTING
# ============================================================

if option == "Summary":

    resume_analyzer.resume_summary()


elif option == "Strength":

    resume_analyzer.resume_strength()


elif option == "Weakness":

    resume_analyzer.resume_weakness()


elif option == "Job Titles":

    resume_analyzer.job_title_suggestion()


elif option == "ATS Score":

    resume_analyzer.ats_score()


elif option == "Skills":

    resume_analyzer.skills()


elif option == "Linkedin Jobs":

    linkedin_scraper.main()