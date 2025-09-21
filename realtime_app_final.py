import panel as pn
import threading
import time
import os
from dotenv import load_dotenv
from crew import BugAnalysisCrew

load_dotenv()
pn.extension('tabulator')

class RealTimeBugAnalysisApp:
    def __init__(self):
        self.crew = BugAnalysisCrew()
        self.agent_files = {
            "Bug Intelligence Specialist": "bug_intelligence_output.txt",
            "Context Intelligence Analyst": "context_analysis_output.txt", 
            "Code Forensics Architect": "code_forensics_output.txt",
            "Strategic Reporting Specialist": "strategic_reporting_output.txt"
        }
        self.agent_displays = {}
        self.is_running = False
    
    def read_agent_output(self, filename):
        """Read content from agent output file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                return content if content else None
            return None
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def format_content(self, content, agent_name):
        """Format content based on agent type"""
        if not content:
            return content
            
        # For Code Forensics Architect - format with steps and code blocks
        if "Code Forensics" in agent_name:
            return self.format_code_forensics_content(content)
        # For Bug Intelligence and Context Analysis - format with headings
        elif "Bug Intelligence" in agent_name or "Context Intelligence" in agent_name:
            return self.format_analysis_content(content)
        # For Strategic Reporting - format with structured sections
        elif "Strategic Reporting" in agent_name:
            return self.format_strategic_content(content)
        else:
            return content
    
    def format_code_forensics_content(self, content):
        """Format code forensics content with proper steps and code blocks"""
        import re
        
        # Format main report headers (ALL CAPS)
        content = re.sub(r'^([A-Z_\s]+REPORT|[A-Z_\s]+ANALYSIS|[A-Z_\s]+SOLUTION):', r'# **\1**', content, flags=re.MULTILINE)
        
        # Format major section headers
        content = re.sub(r'^(CODE ANALYSIS|AI-GENERATED BUG SOLUTION|ADDITIONAL RECOMMENDATIONS):', r'## **\1**', content, flags=re.MULTILINE)
        content = re.sub(r'^([A-Z][A-Z\s]+[A-Z]):', r'## **\1:**', content, flags=re.MULTILINE)
        
        # Format step headers with bold formatting
        content = re.sub(r'^(Step \d+[^\n]*)', r'### **\1**', content, flags=re.MULTILINE)
        content = re.sub(r'^(\d+\.)\s*([^\n]+)', r'### **\1** \2', content, flags=re.MULTILINE)
        
        # Format subsection headers (Title Case)
        content = re.sub(r'^([A-Z][a-z\s]+[a-z]):', r'### **\1:**', content, flags=re.MULTILINE)
        
        # Format field names: field_name: content -> **field_name:** content
        content = re.sub(r'^([a-z_]+):\s*(.+)$', r'**\1:** \2', content, flags=re.MULTILINE)
        content = re.sub(r'^([a-z_]+):\s*$', r'**\1:**', content, flags=re.MULTILINE)
        
        # Format bullet points with proper structure
        content = re.sub(r'^[-*•]\s+([^:]+):\s*(.+)', r'• **\1:** \2', content, flags=re.MULTILINE)
        content = re.sub(r'^[-*•]\s+(.+)', r'• \1', content, flags=re.MULTILINE)
        
        # Format technical solution steps
        content = re.sub(r'^(Verify|Check|Add|Deploy|Test|Monitor|Fix|Update|Install|Configure)\s+([^\n]+)', r'**\1** \2', content, flags=re.MULTILINE)
        
        # Preserve code blocks exactly as they are - don't modify anything between ```
        # The markdown renderer will handle the dark background automatically
        
        # Format single word technical terms
        content = re.sub(r'^([A-Z][a-z]+):\s*(.+)$', r'**\1:** \2', content, flags=re.MULTILINE)
        
        return content
    
    def format_analysis_content(self, content):
        """Format analysis content with proper headings and structure"""
        import re
        
        # Remove any existing code block markers that might cause black boxes
        content = re.sub(r'```[a-zA-Z]*\n', '', content)
        content = re.sub(r'```', '', content)
        
        # Format main report headers (ALL CAPS with underscores)
        content = re.sub(r'^([A-Z_\s]+REPORT|[A-Z_\s]+ANALYSIS):', r'# **\1**', content, flags=re.MULTILINE)
        
        # Format any field name pattern: field_name: content -> **field_name:** content
        # This catches any lowercase/underscore field followed by colon and content
        content = re.sub(r'^([a-z_]+):\s*(.+)$', r'**\1:** \2', content, flags=re.MULTILINE)
        
        # Format section headers that are standalone (field_name: with no content on same line)
        content = re.sub(r'^([a-z_]+):\s*$', r'**\1:**', content, flags=re.MULTILINE)
        
        # Format bullet points - make the label bold if it has a colon
        content = re.sub(r'^[-*•]\s+([^:]+):\s*(.+)', r'• **\1:** \2', content, flags=re.MULTILINE)
        content = re.sub(r'^[-*•]\s+(.+)', r'• \1', content, flags=re.MULTILINE)
        
        # Format bug IDs and issue keys
        content = re.sub(r'\b(SCRUM-\d+)\b', r'**\1**', content)
        
        # Format numbered lists
        content = re.sub(r'^(\d+\.)\s*(.+)', r'**\1** \2', content, flags=re.MULTILINE)
        
        return content
    
    def format_strategic_content(self, content):
        """Format strategic reporting content with executive structure"""
        import re
        
        # Format main report headers (ALL CAPS with underscores or spaces)
        content = re.sub(r'^([A-Z_\s]+REPORT|[A-Z_\s]+HANDBOOK|[A-Z_\s]+ANALYSIS):', r'# **\1**', content, flags=re.MULTILINE)
        
        # Format major section headers (ALL CAPS or Title Case)
        content = re.sub(r'^([A-Z][A-Z\s]+[A-Z]):', r'## **\1:**', content, flags=re.MULTILINE)
        content = re.sub(r'^([A-Z][a-z\s]+[a-z]):', r'## **\1:**', content, flags=re.MULTILINE)
        
        # Format field names: field_name: content -> **field_name:** content
        content = re.sub(r'^([a-z_]+):\s*(.+)$', r'**\1:** \2', content, flags=re.MULTILINE)
        content = re.sub(r'^([a-z_]+):\s*$', r'**\1:**', content, flags=re.MULTILINE)
        
        # Format step headers
        content = re.sub(r'^(Step \d+[^\n]*)', r'### **\1**', content, flags=re.MULTILINE)
        content = re.sub(r'^(\d+\.)\s*(.+)', r'**\1** \2', content, flags=re.MULTILINE)
        
        # Format bullet points
        content = re.sub(r'^[-*•]\s+([^:]+):\s*(.+)', r'• **\1:** \2', content, flags=re.MULTILINE)
        content = re.sub(r'^[-*•]\s+(.+)', r'• \1', content, flags=re.MULTILINE)
        
        # Format single word labels followed by colon
        content = re.sub(r'^([A-Z][a-z]+):\s*(.+)$', r'**\1:** \2', content, flags=re.MULTILINE)
        
        # Ensure code blocks remain properly formatted
        
        return content
    
    def update_agent_display(self, agent_name, content=None, status="⏳ Waiting"):
        """Update the display for a specific agent"""
        if agent_name == "Bug Intelligence Specialist":
            icon = "🔍"
            title = "Senior Bug Intelligence Specialist"
        elif agent_name == "Context Intelligence Analyst":
            icon = "🔗"
            title = "Master Context Intelligence Analyst"
        elif agent_name == "Code Forensics Architect":
            icon = "🤖"
            title = "Elite Code Forensics and Solution Architect"
        elif agent_name == "Strategic Reporting Specialist":
            icon = "📊"
            title = "Master Strategic Reporting Specialist"
        else:
            icon = "⚙️"
            title = agent_name
        
        if content:
            formatted_content = self.format_content(content, agent_name)
            display_content = f"""# {icon} {title}

## Status: {status}

---

{formatted_content}

---
*Analysis completed at {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        else:
            display_content = f"""# {icon} {title}

## Status: {status}

## Progress
Waiting for analysis results...

---
*Agent is processing your request...*
"""
        
        self.agent_displays[agent_name].object = display_content
    
    def monitor_output_files(self, status_text):
        """Monitor agent output files and update displays"""
        max_wait = 120  # Wait up to 2 minutes
        start_time = time.time()
        completed_agents = set()
        
        # Initialize all displays
        for agent_name in self.agent_files.keys():
            self.update_agent_display(agent_name, status="⏳ Running")
        
        while time.time() - start_time < max_wait and len(completed_agents) < len(self.agent_files):
            for agent_name, filename in self.agent_files.items():
                if agent_name not in completed_agents:
                    content = self.read_agent_output(filename)
                    
                    if content and len(content) > 50:  # File has meaningful content
                        self.update_agent_display(agent_name, content, "✅ Completed")
                        completed_agents.add(agent_name)
                        print(f"✅ {agent_name} completed - {len(content)} characters")
                    else:
                        self.update_agent_display(agent_name, status="⏳ Processing...")
            
            # Update status
            if len(completed_agents) == len(self.agent_files):
                status_text.object = "✅ All agents completed successfully!"
                break
            else:
                status_text.object = f"🔄 Analysis running... ({len(completed_agents)}/{len(self.agent_files)} agents completed)"
            
            time.sleep(3)  # Check every 3 seconds
        
        # Handle any incomplete agents
        for agent_name in self.agent_files.keys():
            if agent_name not in completed_agents:
                self.update_agent_display(agent_name, "No output generated or analysis incomplete", "⚠️ Incomplete")
    
    def run_analysis(self, status_text):
        """Run the CrewAI analysis"""
        if self.is_running:
            return
        
        self.is_running = True
        status_text.object = "🔄 Starting CrewAI analysis..."
        
        try:
            # Clear any existing output files
            for filename in self.agent_files.values():
                if os.path.exists(filename):
                    os.remove(filename)
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.monitor_output_files, args=(status_text,), daemon=True)
            monitor_thread.start()
            
            # Run CrewAI analysis
            result = self.crew.run()
            print("CrewAI analysis completed")
            
            # Wait for monitoring to complete
            monitor_thread.join(timeout=10)
            
        except Exception as e:
            status_text.object = f"❌ Error: {str(e)}"
            for agent_name in self.agent_files.keys():
                self.update_agent_display(agent_name, f"Analysis failed: {str(e)}", "❌ Error")
        
        finally:
            self.is_running = False
    
    def create_dashboard(self):
        """Create the Panel dashboard"""
        # Create button and status
        run_button = pn.widgets.Button(
            name="🔍 Start Bug Analysis", 
            button_type="primary", 
            width=200,
            height=50
        )
        
        status_text = pn.pane.Markdown(
            "**Ready to analyze bugs...** Click the button to start.",
            width=400
        )
        
        # Create agent displays
        for agent_name in self.agent_files.keys():
            self.agent_displays[agent_name] = pn.pane.Markdown(
                "",
                sizing_mode='stretch_width',
                height=600,
                styles={'overflow-y': 'auto', 'padding': '10px'}
            )
            self.update_agent_display(agent_name)
        
        def start_analysis(event):
            """Start analysis in background thread"""
            if self.is_running:
                return
            
            run_button.disabled = True
            run_button.name = "🔄 Analysis Running..."
            
            def run_and_enable():
                try:
                    self.run_analysis(status_text)
                finally:
                    run_button.disabled = False
                    run_button.name = "🔍 Start Bug Analysis"
            
            thread = threading.Thread(target=run_and_enable, daemon=True)
            thread.start()
        
        run_button.on_click(start_analysis)
        
        # Create template
        template = pn.template.MaterialTemplate(
            title="🐛 AI Bug Analysis Platform",
            sidebar=[
                pn.pane.Markdown("## 🎛️ Control Panel"),
                run_button,
                pn.Spacer(height=20),
                pn.pane.Markdown("## 📊 Status"),
                status_text,
                pn.Spacer(height=20),
                pn.pane.Markdown("""
## 📋 How it works
1. Click **Start Bug Analysis**
2. CrewAI agents analyze your Jira bugs
3. Each agent writes results to output files
4. Results appear in tabs as files are completed

## 🔧 Output Files
- `bug_intelligence_output.txt`
- `context_analysis_output.txt`
- `code_forensics_output.txt`
- `strategic_reporting_output.txt`
""")
            ],
            main=[
                pn.Tabs(
                    ("🔍 Bug Intelligence", self.agent_displays["Bug Intelligence Specialist"]),
                    ("🔗 Context Analysis", self.agent_displays["Context Intelligence Analyst"]),
                    ("🤖 Code Forensics", self.agent_displays["Code Forensics Architect"]),
                    ("📊 Strategic Report", self.agent_displays["Strategic Reporting Specialist"]),
                    dynamic=True
                )
            ]
        )
        
        return template

def create_app():
    """Create the Panel application"""
    try:
        app = RealTimeBugAnalysisApp()
        return app.create_dashboard()
    except Exception as e:
        return pn.pane.Markdown(f"""
# ❌ Application Error

**Error:** {str(e)}

**Check:**
- Environment variables in `.env` file
- Required packages: `pip install -r requirements.txt`
- Config files in `config/` directory
""")

# Make app servable
create_app().servable()