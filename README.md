# AI Bug Analysis Platform

Automated bug analysis using CrewAI, Jira integration, and Gemini AI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Run the platform:
```bash
python main.py
```

## Architecture

- **Bug Collector**: Fetches open bugs from Jira
- **Context Enricher**: Links bugs to GitHub code and related issues  
- **Analysis Agent**: Uses Gemini for root cause analysis and solutions
- **Reporting Agent**: Updates Jira and displays results in web UI

## Environment Variables

- `JIRA_URL`: Your Atlassian instance URL
- `JIRA_EMAIL`: Your Jira email
- `JIRA_API_TOKEN`: Jira API token
- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPO`: Repository in format "owner/repo"
- `GEMINI_API_KEY`: Google Gemini API key
- `CREWAI_API_KEY`: CrewAI Enterprise API key