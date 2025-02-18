"""
This module provides a set of functions to interact with OpenAI's API for modifying a Power BI dashboard.
"""

import json
import pandas as pd
import openai
import copy
from typing import Dict, List

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
        {df[['page name', 'visual id', 'visual name']].drop_duplicates().to_string()}

        Step 1: Determine the scope
        A. Page Scope Analysis:
           - If request mentions "in the dashboard" or "all pages" → ALL pages in dashboard (INCLUDING the source page)
           - If request mentions specific pages → ONLY those pages
        
        B. Visual Scope Analysis (for each mentioned page):
           - If request EXPLICITLY mentions "all slicers" or "all visuals" → include ALL visuals in that page
           - If request mentions specific visuals → include ONLY those specific visuals
           - For dashboard-wide updates: include ALL visuals from ALL pages (including the source page)
           - Using the user prompt, identify the visual name closest to the one mentioned by the user and include the corresponding visual id EXACTLY as written in the provided data.

        Step 2: Identify source
        - Extract exactly one source visual id and its page that will be used as reference

        Return only a JSON object with:
        {{
            "source": {{
                "page": "exact page name",
                "visual": "exact visual id"
            }},
            "page_scope": "dashboard/specific_pages",
            "targets": [
                {{
                    "page": "exact page name", // if page_scope is dashboard, MUST include all the pages
                    "include_all_visuals": true/false,
                    "specific_visuals": ["visual_id1", "visual_id2"]  // only if include_all_visuals is false
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
                {{"page": "Page1", "include_all_visuals": false, "specific_visuals": ["id of Date visual in Page1"]}},
                {{"page": "Page2", "include_all_visuals": false, "specific_visuals": ["id of Date visual in Page2"]}},
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
                (df['visual id'] == extracted_info['source']['visual'])
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
                    page_visuals = df[df['page name'] == target['page']]['visual id'].unique()
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
    "1. Do the visual ids in the generated configuration exist in the dashboard data ? The ids must not be invented."

    def review_config(self, config: Dict, user_prompt: str, df: pd.DataFrame) -> Dict:
        review_prompt = f"""
        Given:
        1. Original user request: "{user_prompt}"
        2. Available dashboard data:
        {df[['page name', 'visual name', 'visual id']].drop_duplicates().to_string()}
        3. Generated configuration:
        {json.dumps(config, indent=2)}
        
        1. Is the page_scope field correctly interpreted ? If its value is 'dashboard' then all pages must appear in the generated configuration (the source page can also be a target page). Else, if its value are specified pages then only theses pages must appear in the generated configuration.
        2. For each page, is the 'include_all_visuals' field correctly interpreted ? If it is true then all visual ids must appear in the generated configuration, else only the visual ids corresponding to the visuals mentionned by the user must appear in the generated configuration.
        3. Since there could also be target visuals in the source page, are these target visuals correctly identified in the generated configuration?
        4. Do the visual ids in the generated configuration exist in the dashboard data ? The ids must not be invented.
        5. Are the visual ids associated with the right page ?
    
        
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
        # self.critic = CriticAgent("Critic")
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
