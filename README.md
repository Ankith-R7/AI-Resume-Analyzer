# AI Resume Analyzer and LinkedIn Scraper using Generative AI

**Introduction**

Developed an advanced AI application that leverages Large Language Models (LLM) powered by Google Gemini for comprehensive resume analysis. It excels at summarizing the resume, evaluating strengths, identifying weaknesses, offering personalized improvement suggestions, estimating ATS scores, organizing skills, and recommending the most suitable job titles. Additionally, it seamlessly employs Selenium to extract vital LinkedIn data, including company names, job titles, locations, job URLs, and detailed job descriptions. This application simplifies the job-seeking journey by equipping users with comprehensive insights to elevate their career opportunities.

<br />

**Table of Contents**

1. Key Technologies and Skills
2. Installation
3. Usage
4. Features
5. Contributing
6. License
7. Contact

 <br />

**Key Technologies and Skills**
- Python
- Pandas
- Google GenAI SDK (`google-genai`)
- Large Language Models (Google Gemini)
- Selenium Webdriver
- PyPDF2
- Streamlit
- Streamlit Option Menu
- Streamlit Extras

<br />

**Installation**

To run this project, you need to install the following packages:

```python
pip install pandas
pip install streamlit
pip install streamlit_option_menu
pip install streamlit_extras
pip install PyPDF2
pip install google-genai
pip install selenium
```

<br />

**Usage**

To use this project, follow these steps:

1. Clone the repository:
2. Install the required packages: pip install -r requirements.txt
3. Set your Gemini API key in app.py:
   Python
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
4. Run the Streamlit app: streamlit run app.py
5. Access the app in your browser at http://localhost:8501

<br />

**Features**

**Easy User Experience:**
- Resume Analyzer AI makes it easy for users. Simply upload your text-based PDF resume and navigate between tools using the sidebar menu. The application is designed to be intuitive and clean so that anyone can use its powerful analysis features.

-It uses the PyPDF2 library to quickly extract clean text from your uploaded resume, which serves as the foundational text for subsequent AI evaluation.

**Google Gemini Multi-Model Integration:**

- The application utilizes the official google-genai SDK and supports automatic model failover (starting with gemini-3.6-flash and falling back to gemini-3.5-flash-lite).

- This resilient pipeline ensures zero downtime during traffic spikes or regional endpoint variations.

**Comprehensive Resume Analysis Modules:**

- **Summary:** Provides a structured profile breakdown covering candidate background, education, technical skills, programming languages, AI/ML tools, projects, certifications, experience, key strengths, and career direction.

- **Strength:** Pinpoints technical and non-technical strengths across 11 key criteria, providing detailed explanations for why each asset brings practical value to recruiters.

- **Weakness & Suggestions:** Evaluates missing keywords, formatting issues, certification gaps, and weak project descriptions using a structured Problem -> Why it matters -> How to improve action plan.

- **Job Titles:** Suggests ranked, realistic job roles (Software Engineer, AI/ML Engineer, Data Analyst, etc.) paired with percentage suitability match, existing strengths, and skill gaps.

- **ATS Score:** Acts as an automated applicant tracking system, computing an estimated score out of 100 based on keyword optimization, structure, relevance, and formatting with actionable advice for improvement.

- **Skills Breakdown:** Extracts and categorizes verified resume skills into Programming Languages, AI/ML, Databases, Web Development, Cloud/DevOps, Tools, and Soft Skills without hallucinating missing data.

<br />

**Selenium-Powered LinkedIn Data Scraping:**
- Utilizing Selenium with headless Chrome options, users can specify target job titles, locations (e.g., India), and job counts.
- It dynamically queries LinkedIn, automatically scrolls through results, and extracts company names, job titles, locations, links, and detailed expandable job descriptions.

<br />

**Contributing**

- Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please feel free to submit a pull request.

<br />

**License**

- This project is licensed under the MIT License. Please review the LICENSE file for more details.

<br />

**Contact**

📧 Email: saiankith277@gmail.com

🌐 LinkedIn: www.linkedin.com/in/sai-ankith-r7

For any further questions or inquiries, feel free to reach out. We are happy to assist you with any queries.