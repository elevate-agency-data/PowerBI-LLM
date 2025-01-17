import pandas as pd
import json
from typing import Dict, List
import openai
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
# Get API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Using your test dataframe
data = {
    'page name': ['Scope FA', 'Scope FA', 'Scope FA', 'Scope FA', 'Scope FA', 'Scope FA', 'Scope FA',
                  'Digital', 'Digital', 'Digital', 'Digital',
                  'Client Focus', 'Client Focus', 'Client Focus', 'Client Focus', 'Client Focus', 'Client Focus',
                  'Mirror', 'Mirror', 'Mirror', 'Mirror'],
    'visual name': ['Boutique Name', 'Date', 'InchanelBtq_Status', 'Boutique Name', 'InchanelBtq_Status', 'Country', 'Country',
                   'Date', 'Country', 'Boutique Name', 'Date.Date',
                   'Date', 'Date.Date', 'Boutique Name', 'Country', 'Date', 'Country',
                   'Date', 'Boutique Name', 'Date.Date', 'Country'],
    'visual type': ['slicer'] * 21
}

df_test = pd.DataFrame(data)
# test_prompt = "I want to make all the slicers in the Digital page and all the slicers in the FA Scope Page look like the Country slicer in the Client page"
test_prompt = "I want to update all the slicers in the dashboard so that their format match the 'Date' slicer on the 'Client Focus' page."
# test_prompt = "I want to uniform the format of all the Country slicers in the Dashboard with the same format as the Date slicer on the Scope FA page"

class Agent:
    """Base class for all agents"""
    def __init__(self, name: str):
        self.name = name
        
    def log_message(self, message: str):
        print(f"[{self.name}]: {message}")
class RequestParserAgent(Agent):
    def parse_request(self, user_prompt: str, df: pd.DataFrame) -> Dict:
        # Create a prompt for the LLM to extract key information
        analysis_prompt = f"""
        Given this user request: "{user_prompt}"
        And these available pages and visuals in the dashboard:
        {df[['page name', 'visual name']].drop_duplicates().to_string()}

        Step 1: Determine the scope
        A. Page Scope Analysis:
           - If request mentions "in the dashboard" or similar → ALL pages in dashboard (INCLUDING the source page)
           - If request mentions specific pages → ONLY those pages
        
        B. Visual Scope Analysis (for each mentioned page):
           - If request EXPLICITLY mentions "all slicers" or "all visuals" → include ALL visuals in that page
           - If request mentions specific visuals → include ONLY those specific visuals
           - For dashboard-wide updates: include ALL visuals from ALL pages (including source page)

        Step 2: Identify source
        - Extract exactly one source visual and its page that will be used as reference

        Return only a JSON object with:
        {{
            "source": {{
                "page": "exact page name",
                "visual": "exact visual name"
            }},
            "page_scope": "dashboard/specific_pages",
            "targets": [
                {{
                    "page": "exact page name", // if page_scope is dashboard, MUST include all the pages
                    "include_all_visuals": true/false,
                    "specific_visuals": ["visual1", "visual2"]  // only if include_all_visuals is false
                }}
            ]
        }}

        Examples:
        1. "all slicers in the dashboard" → 
           - page_scope: "dashboard"
           - targets: ALL pages (including source page) with include_all_visuals: true
           - Note: Source page should also be included with all its visuals

        2. "Date slicer in the dashboard" → 
           - page_scope: "dashboard"
           - targets: MUST include ALL pages with specific_visuals: ["Date"]
           - Like this:
             "targets": [
                {{"page": "Page1", "include_all_visuals": false, "specific_visuals": ["Date"]}},
                {{"page": "Page2", "include_all_visuals": false, "specific_visuals": ["Date"]}},
                // ... one entry for EACH page in the dashboard
             ]

        3. "all slicers in Digital page" → 
           - page_scope: "specific_pages"
           - targets: only Digital page with include_all_visuals: true
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.1
        )
        
        try:
            extracted_info = json.loads(completion.choices[0].message.content)
            self.log_message(f"Extracted information: {extracted_info}")
            
            # Verify source visual exists
            source_exists = df[
                (df['page name'] == extracted_info['source']['page']) & 
                (df['visual name'] == extracted_info['source']['visual'])
            ].shape[0] > 0
            
            if not source_exists:
                self.log_message(f"Warning: Source visual '{extracted_info['source']['visual']}' not found in '{extracted_info['source']['page']}'")
                return None
            
            # Get target visuals
            targets = []
            
            # Process each target based on whether it's all visuals or specific visuals
            for target in extracted_info['targets']:
                if target['include_all_visuals']:
                    # Get all visuals for this page
                    page_visuals = df[df['page name'] == target['page']]['visual name'].unique()
                    for visual in page_visuals:
                        if not (target['page'] == extracted_info['source']['page'] and 
                               visual == extracted_info['source']['visual']):
                            targets.append({
                                "target_page": target['page'],
                                "target_visual": visual
                            })
                else:
                    # Only include the specific visuals mentioned
                    for visual in target['specific_visuals']:
                        if not (target['page'] == extracted_info['source']['page'] and 
                               visual == extracted_info['source']['visual']):
                            targets.append({
                                "target_page": target['page'],
                                "target_visual": visual
                            })
            
            return {
                "source": {
                    "source_page": extracted_info['source']['page'],
                    "source_visual": extracted_info['source']['visual']
                },
                "target": targets
            }
            
        except Exception as e:
            self.log_message(f"Error processing request: {str(e)}")
            return None
class CriticAgent(Agent):
    """Agent responsible for reviewing and challenging the parser's work"""
    
    def review_config(self, config: Dict, user_prompt: str, df: pd.DataFrame) -> Dict:
        review_prompt = f"""
        Given:
        1. Original user request: "{user_prompt}"
        2. Available dashboard data:
        {df[['page name', 'visual name']].drop_duplicates().to_string()}
        3. Generated configuration:
        {json.dumps(config, indent=2)}
        1. STRICT: Verify there is exactly one source visual
        2. Is the generated configuration correctly understood the user intent? Does it correctly indentify the source visual and extract all the target visuals without forgetting or misuderstanding anything?
        3. Since there could also be target visuals in the source page, are these target visuals correctly identified in the generated configuration?
        Return a JSON with:
        {{
            "is_correct": false if ANY validation fails, true otherwise,
            "issues": ["list specific issues found"],
            "requires_revision": true if ANY validation fails
        }}
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": review_prompt}],
            temperature=0.1
        )
        
        try:
            review_result = json.loads(completion.choices[0].message.content)
            self.log_message(f"Review completed: {review_result}")
            return review_result
        except Exception as e:
            self.log_message(f"Error during review: {str(e)}")
            return None
class EnhancedCoordinatorAgent(Agent):
    """Coordinator that manages the interaction between Parser and Critic"""
    
    def __init__(self):
        super().__init__("Coordinator")
        self.parser = RequestParserAgent("Parser")
        self.critic = CriticAgent("Critic")
        self.max_iterations = 3
        
    def process_request(self, user_prompt: str, df: pd.DataFrame) -> Dict:
        return self.parser.parse_request(user_prompt, df)

        # # Initialize the iteration counter and the current configuration
        # iteration = 0
        # current_config = None
        
        # while iteration < self.max_iterations:
        #     iteration += 1
        #     self.log_message(f"Starting iteration {iteration}")
            
        #     # Get initial or revised configuration
        #     current_config = self.parser.parse_request(user_prompt, df)
            
        #     # Have the critic review it
        #     review = self.critic.review_config(current_config, user_prompt, df)
            
        #     if not review:
        #         self.log_message("Review failed, returning current configuration")
        #         return current_config
                
        #     if not review['requires_revision']:
        #         self.log_message("Configuration approved by critic")
        #         return current_config
            
        #     # If revision is needed, create a new prompt for the parser
        #     revision_prompt = f"""
        #     Original request: {user_prompt}
            
        #     The current configuration has these issues:
        #     {json.dumps(review['issues'], indent=2)}
            
        #     Please revise the configuration to fix these issues.
        #     """
            
        #     user_prompt = revision_prompt  # Update prompt for next iteration
        #     self.log_message("Requesting revision from parser")
        
        # self.log_message(f"Reached maximum iterations ({self.max_iterations})")
        # return current_config
def process_dashboard_request(user_prompt: str, df: pd.DataFrame) -> Dict:
    coordinator = EnhancedCoordinatorAgent()
    result = coordinator.process_request(user_prompt, df)

    return result
# Test the function
result = process_dashboard_request(test_prompt, df_test)
print("\nFinal Configuration:")
print(json.dumps(result, indent=2))
