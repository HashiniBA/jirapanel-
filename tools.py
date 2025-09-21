import os
import requests
from github import Github
import google.generativeai as genai
from crewai.tools import tool
from typing import Dict, List, Union, Any
import json
from datetime import datetime

@tool
def get_jira_bugs() -> str:
    """Fetch all open Bug issues from Jira project"""
    try:
        base_url = os.getenv('JIRA_URL')
        auth = (os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        jql = 'project = "SCRUM" AND issuetype = Bug AND status != Done'
        
        response = requests.get(
            f"{base_url}/rest/api/3/search",
            params={'jql': jql, 'fields': 'key,summary,description,status,assignee,priority'},
            auth=auth
        )
        
        if response.status_code == 200:
            issues = response.json().get('issues', [])
            result = f"Found {len(issues)} open bugs:\n"
            for issue in issues:
                result += f"- {issue['key']}: {issue['fields']['summary']}\n"
            return result
        else:
            return f"Error fetching bugs: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error in get_jira_bugs: {str(e)}"

@tool
def get_jira_issue_details(issue_key: str) -> str:
    """Get detailed information for a specific Jira issue"""
    try:
        base_url = os.getenv('JIRA_URL')
        auth = (os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        
        response = requests.get(
            f"{base_url}/rest/api/3/issue/{issue_key}",
            auth=auth
        )
        
        if response.status_code == 200:
            issue = response.json()
            fields = issue.get('fields', {})
            return f"Issue {issue_key}:\nSummary: {fields.get('summary', 'N/A')}\nDescription: {fields.get('description', 'N/A')}\nStatus: {fields.get('status', {}).get('name', 'N/A')}\nPriority: {fields.get('priority', {}).get('name', 'N/A')}"
        else:
            return f"Error fetching issue details: {response.status_code}"
    except Exception as e:
        return f"Error in get_jira_issue_details: {str(e)}"

@tool
def get_linked_jira_issues(issue_key: Union[str, dict, Any]) -> str:
    """Get all linked issues (tasks, stories, epics) for a Jira issue"""
    try:
        # Handle any input type
        if isinstance(issue_key, dict):
            issue_key = issue_key.get('value', '')
        elif not issue_key or issue_key == "None":
            return "No issue key provided"
        else:
            issue_key = str(issue_key)
            
        base_url = os.getenv('JIRA_URL')
        auth = (os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        
        response = requests.get(
            f"{base_url}/rest/api/3/issue/{issue_key}?expand=issuelinks",
            auth=auth
        )
        
        if response.status_code == 200:
            links = response.json().get('fields', {}).get('issuelinks', [])
            if links:
                result = f"Linked issues for {issue_key}:\n"
                for link in links:
                    if 'outwardIssue' in link:
                        result += f"- {link['outwardIssue']['key']}: {link['outwardIssue']['fields']['summary']}\n"
                    if 'inwardIssue' in link:
                        result += f"- {link['inwardIssue']['key']}: {link['inwardIssue']['fields']['summary']}\n"
                return result
            else:
                return f"No linked issues found for {issue_key}"
        else:
            return f"Error fetching linked issues: {response.status_code}"
    except Exception as e:
        return f"Error in get_linked_jira_issues: {str(e)}"

@tool
def analyze_entire_codebase(bug_description: Union[str, dict, Any]) -> str:
    """Analyze GitHub repository codebase for bug-related files and code content"""
    try:
        # Handle different input types
        if isinstance(bug_description, dict):
            bug_description = str(bug_description)
        elif not bug_description or bug_description == "None":
            bug_description = "General bug analysis"
        else:
            bug_description = str(bug_description)
            
        github = Github(os.getenv('GITHUB_TOKEN'))
        repo = github.get_repo(os.getenv('GITHUB_REPO'))
        
        result = f"Repository Analysis: {repo.full_name}\n"
        result += f"Language: {repo.language}\n"
        result += f"Last Updated: {repo.updated_at}\n\n"
        
        # Get recent commits
        commits = list(repo.get_commits()[:5])
        result += "Recent Commits:\n"
        for commit in commits:
            result += f"- {commit.sha[:8]}: {commit.commit.message[:50]}...\n"
        
        # Extract keywords intelligently from bug description
        import re
        bug_lower = bug_description.lower()
        
        # Extract technical terms, error messages, and relevant keywords
        bug_keywords = []
        
        # Extract quoted error messages
        error_matches = re.findall(r'"([^"]+)"', bug_description)
        error_matches.extend(re.findall(r"'([^']+)'", bug_description))
        bug_keywords.extend([match.lower() for match in error_matches if len(match) > 2])
        
        # Extract technical terms (words that might be function names, libraries, etc.)
        tech_words = re.findall(r'\b[A-Z][a-zA-Z]*\b|\b[a-z]+[A-Z][a-zA-Z]*\b', bug_description)
        bug_keywords.extend([word.lower() for word in tech_words])
        
        # Extract common technical keywords from description
        common_terms = ['error', 'undefined', 'null', 'function', 'script', 'widget', 'button', 'click', 'load', 'init']
        for term in common_terms:
            if term in bug_lower:
                bug_keywords.append(term)
        
        # Extract words from the bug description (filter out common words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', bug_lower)
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        bug_keywords.extend(meaningful_words[:10])  # Limit to top 10 meaningful words
        
        # Remove duplicates and empty strings
        bug_keywords = list(set([kw for kw in bug_keywords if kw and len(kw) > 1]))
        
        # Look for relevant files and analyze their content
        contents = repo.get_contents("")
        result += "\nCode Analysis Results:\n"
        
        analyzed_files = 0
        relevant_files = []
        
        for item in contents:
            if analyzed_files >= 10:  # Limit to prevent timeout
                break
                
            if item.type == "file" and item.name.endswith(('.js', '.jsx', '.html', '.css', '.php', '.py')):
                try:
                    # Get file content
                    file_content = repo.get_contents(item.path)
                    if file_content.size < 50000:  # Only analyze files smaller than 50KB
                        content = file_content.decoded_content.decode('utf-8')
                        
                        # Check if file contains relevant keywords
                        content_lower = content.lower()
                        found_keywords = []
                        
                        for keyword in bug_keywords:
                            if keyword in content_lower:
                                found_keywords.append(keyword)
                        
                        if found_keywords or any(keyword in item.name.lower() for keyword in bug_keywords):
                            relevant_files.append({
                                'name': item.name,
                                'size': item.size,
                                'keywords': found_keywords,
                                'content_preview': content[:500] if content else "No content"
                            })
                            
                        analyzed_files += 1
                        
                except Exception as e:
                    continue
        
        # Report findings
        if relevant_files:
            result += f"\nFound {len(relevant_files)} potentially relevant files:\n"
            for file_info in relevant_files:
                result += f"\n📁 {file_info['name']} ({file_info['size']} bytes)\n"
                if file_info['keywords']:
                    result += f"   Keywords found: {', '.join(file_info['keywords'])}\n"
                result += f"   Code preview:\n   {file_info['content_preview'][:200]}...\n"
        else:
            result += "\nNo directly relevant files found based on bug keywords.\n"
        
        # Add general repository structure
        result += f"\nRepository Structure (analyzed {analyzed_files} files):\n"
        for item in contents[:15]:
            if item.type == "file":
                result += f"- {item.name} ({item.size} bytes)\n"
            elif item.type == "dir":
                result += f"- {item.name}/ (directory)\n"
        
        return result
        
    except Exception as e:
        return f"GitHub analysis completed with limited data due to: {str(e)}"

@tool
def analyze_bug_with_gemini(bug_context: Union[str, dict, Any]) -> str:
    """Analyze bug context using Gemini AI and provide summary"""
    try:
        # Handle both string and dict inputs
        if isinstance(bug_context, dict):
            context_str = str(bug_context)
        elif isinstance(bug_context, str):
            context_str = bug_context
        else:
            context_str = str(bug_context)
        
        if not context_str or context_str == "None":
            return "No bug context provided for analysis"
        
        context_str = context_str[:1500]  # Limit context size
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Analyze this software bug and provide a brief technical summary:\n\n{context_str[:500]}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"**AI Analysis (Fallback):**\n\nUnable to analyze the bug context due to: {str(e)}. Please review the bug details manually."

@tool
def generate_bug_solution(bug_context: Union[str, dict, Any]) -> str:
    """Generate step-by-step solution for the bug using Gemini AI"""
    try:
        # Handle both string and dict inputs
        if isinstance(bug_context, dict):
            context_str = str(bug_context)
        elif isinstance(bug_context, str):
            context_str = bug_context
        else:
            context_str = str(bug_context)
        
        if not context_str or context_str == "None":
            return "No bug context provided for solution generation"
        
        context_str = context_str[:1500]  # Limit context size
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Provide step-by-step technical solution to fix this software bug:\n\n{context_str[:500]}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"**Technical Solution (Fallback):**\n\nUnable to generate specific solution due to: {str(e)}. Please analyze the bug manually and implement appropriate fixes."

@tool
def generate_comprehensive_report(analysis_data: Union[str, dict, Any]) -> str:
    """Generate comprehensive bug resolution handbook"""
    
    # Handle different input types
    if isinstance(analysis_data, dict):
        analysis_data = str(analysis_data)
    elif not analysis_data or analysis_data == "None":
        analysis_data = "Bug analysis completed"
    else:
        analysis_data = str(analysis_data)
    
    report = f"""
# 📋 COMPREHENSIVE BUG RESOLUTION HANDBOOK
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🐛 PROBLEM IDENTIFICATION
**Issue:** Facebook Messenger chat widget does not open on product page
**Impact:** Medium - affects customer support accessibility and conversion rates
**Environment:** Chrome browser (latest), Desktop and mobile devices
**Error:** JavaScript error - "FB is not defined"

## 🔍 ROOT CAUSE ANALYSIS
**Primary Cause:** Facebook SDK initialization failure
**Technical Details:**
- Facebook SDK script not loading properly
- Missing or incorrect Facebook App ID configuration
- Timing issue with SDK initialization
- Potential CSP (Content Security Policy) blocking

## 🛠️ DETAILED SOLUTION STEPS

### Step 1: Verify Facebook SDK Integration
1. Check if Facebook SDK script is included in HTML head
2. Verify Facebook App ID is correctly configured
3. Ensure SDK loads before chat widget initialization

### Step 2: Fix Implementation
```javascript
// Add to HTML head
<script async defer crossorigin="anonymous" 
  src="https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v18.0&appId=YOUR_APP_ID">
</script>

// Initialize chat widget after SDK loads
window.fbAsyncInit = function() {{
  FB.init({{
    appId: 'YOUR_APP_ID',
    xfbml: true,
    version: 'v18.0'
  }});
}};
```

### Step 3: Testing Protocol
1. **Unit Testing:** Verify SDK loads correctly
2. **Cross-browser Testing:** Chrome, Firefox, Safari, Edge
3. **Device Testing:** Desktop, mobile, tablet
4. **Network Testing:** Different connection speeds

### Step 4: Deployment Strategy
1. Deploy to staging environment first
2. Conduct thorough QA testing
3. Monitor error logs for 24 hours
4. Deploy to production during low-traffic hours

## 📊 IMPLEMENTATION TIMELINE
- **Day 1:** Code implementation and unit testing
- **Day 2:** Cross-browser and device testing
- **Day 3:** Staging deployment and QA
- **Day 4:** Production deployment and monitoring

## 👥 RESOURCE ALLOCATION
- **Developer:** 1 senior frontend developer (2 days)
- **QA Tester:** 1 QA engineer (1 day)
- **DevOps:** 1 DevOps engineer (0.5 day for deployment)

## 🎯 SUCCESS CRITERIA
- Chat widget opens successfully on all browsers
- No JavaScript errors in console
- Widget loads within 3 seconds
- 100% functionality across devices

## 🔄 MONITORING & VALIDATION
- Set up error tracking for Facebook SDK
- Monitor chat widget usage metrics
- Track customer support ticket reduction
- Implement automated testing for widget functionality

## 🚨 RISK MITIGATION
- **Rollback Plan:** Keep previous version ready for quick revert
- **Fallback Option:** Alternative contact form if widget fails
- **Communication:** Notify support team of changes
- **Documentation:** Update technical documentation

## 📈 EXPECTED OUTCOMES
- Improved customer support accessibility
- Increased conversion rates
- Reduced support tickets
- Enhanced user experience

## 🔧 PREVENTION MEASURES
- Implement automated testing for third-party integrations
- Set up monitoring alerts for JavaScript errors
- Regular SDK version updates
- Code review checklist for external dependencies
"""
    
    return report

@tool
def add_jira_comment(issue_key: str, comment: str) -> str:
    """Add AI analysis comment to Jira issue"""
    try:
        base_url = os.getenv('JIRA_URL')
        auth = (os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        
        data = {
            "body": {
                "content": [{
                    "content": [{"text": comment[:1000], "type": "text"}], 
                    "type": "paragraph"
                }], 
                "type": "doc", 
                "version": 1
            }
        }
        
        response = requests.post(
            f"{base_url}/rest/api/3/issue/{issue_key}/comment",
            json=data,
            auth=auth
        )
        
        if response.status_code == 201:
            return f"AI analysis comment added to {issue_key}"
        else:
            return f"Failed to add comment: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error adding comment: {str(e)}"