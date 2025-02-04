import json
import pandas as pd
import openai
import copy
from typing import Dict, List

# Path to the JSON file
file_path = "jsons_test/contenus_ftv.json"

openai.api_key = "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"

# Open and read the JSON file
with open(file_path, 'r', encoding="utf-8") as file:
    original_json_data = json.load(file)

def build_df(json_data):
    dict_page_slicers = {}

    for section in json_data.get("sections", []):
        # Only include pages that are not hidden in the dashboard
        page_config = json.loads(section['config'])
        if page_config.get('visibility') != 1:
            slicer_list_per_page = []

            # Process each visual container in the section
            for visual in section.get("visualContainers", []):
                # Parse config if it's a string
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                
                if visual_type in visual_type_to_be_included:
                    slicer_name = None
                    slicer_name_key = None
                    header_present = False
                    title_present = False

                    # Determine slicer name and key
                    try :
                        if ("title" in config_data['singleVisual']["vcObjects"] and 
                            'text' in config_data['singleVisual']["vcObjects"]["title"][0]["properties"] and 
                            config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"] != "''"):
                            
                            slicer_name = config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                            slicer_name_key = "title"
                            title_present = True
                    except :
                        pass

                    if slicer_name is None :
                        try :
                            if ('header' in config_data['singleVisual']['objects'] and 
                                'text' in config_data['singleVisual']['objects']['header'][0]['properties']) :
                                # and config_data['singleVisual']['objects']['header'][0]['properties']['show']['expr']['Literal']['Value'] != "false"):
                                slicer_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                                slicer_name_key = "header"
                                header_present = True
                        except :
                            pass
                    
                    if slicer_name is None :
                        try :
                            if 'NativeReferenceName' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                                slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                                slicer_name_key = "NativeReferenceName"
                        except :
                            pass
                    if slicer_name is None :
                        try :
                            if 'Name' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                                slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                                slicer_name_key = "Name"
                        except :
                            pass
                              
                    if slicer_name and slicer_name_key:
                        slicer_list_per_page.append({
                            "visual name": slicer_name,
                            "visual name key": slicer_name_key,
                            "visual type": visual_type,
                            "header present": header_present,
                            "title present": title_present
                        })

            # Add slicer visuals for the current page
            dict_page_slicers[section.get("displayName", "")] = slicer_list_per_page

    # List to store each row as a dictionary
    rows = []

    # Loop through each page and its visuals
    for page_name, visuals in dict_page_slicers.items():
        for visual in visuals:
            rows.append({
                "page name": page_name,
                "visual name": visual["visual name"],
                "visual name key": visual["visual name key"],
                "visual type": visual["visual type"],
                "header present": visual["header present"],
                "title present": visual["title present"]
            })

    # Convert list of dictionaries into a DataFrame
    df = pd.DataFrame(rows)

    return df


pd.set_option('display.max_columns', None)
df = build_df(original_json_data)
print(df)

##### Agent pour avoir le json source/target

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
           - If request mentions "in the dashboard" or "all pages" → ALL pages in dashboard (INCLUDING the source page)
           - If request mentions specific pages → ONLY those pages
        
        B. Visual Scope Analysis (for each mentioned page):
           - If request EXPLICITLY mentions "all slicers" or "all visuals" → include ALL visuals in that page
           - If request mentions specific visuals → include ONLY those specific visuals
           - For dashboard-wide updates: include ALL visuals from ALL pages (including the source page)
           - Include the visual names exactly as written in the dashboard data. They can be slightly different but similar to the user's request. For example if the user mentions "Date" and there is "date:" in the dashboard data, include "date:" in the result.

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

    """Does the generated configuration correctly indentify the source visual and extract all the target visuals mentionned by the user without forgetting or adding anything?
        1. Is the page_scope field correctly interpreted ? If its value is 'dashboard' then all pages must appear in the generated configuration (the source page can also be a target page). Else, if its value are specified pages then only theses pages must appear in the generated configuration.
        2. For each page, is the 'include_all_visuals' field correctly interpreted ? If it is true then all visuals must appear in the generated configuration, else only the visuals mentionned by the user must appear in the generated configuration.
        3. Are the visual names in the generated configuration identical to the ones in the dashboard data ?
        4. Since there could also be target visuals in the source page, are these target visuals correctly identified in the generated configuration?"""
    
    def review_config(self, config: Dict, user_prompt: str, df: pd.DataFrame) -> Dict:
        review_prompt = f"""
        Given:
        1. Original user request: "{user_prompt}"
        2. Available dashboard data:
        {df[['page name', 'visual name']].drop_duplicates().to_string()}
        3. Generated configuration:
        {json.dumps(config, indent=2)}

        1. Is the generated configuration correctly reflects the user intent? Does it correctly indentify the source visual and extract all the target visuals without forgetting or adding anything?
        2. Since there could also be target visuals in the source page, are these target visuals correctly identified in the generated configuration?
        3. Are the visual names in the generated configuration identical to the ones in the dashboard data ?
        
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
        self.max_iterations = 5
        
    def process_request(self, user_prompt: str, df: pd.DataFrame) -> Dict:
        # return self.parser.parse_request(user_prompt, df)

        # Initialize the iteration counter and the current configuration
        iteration = 0
        current_config = None
        
        while iteration < self.max_iterations:
            iteration += 1
            self.log_message(f"Starting iteration {iteration}")
            
            # Get initial or revised configuration
            current_config = self.parser.parse_request(user_prompt, df)
            
            # Have the critic review it
            review = self.critic.review_config(current_config, user_prompt, df)
            
            if not review:
                self.log_message("Review failed, returning current configuration")
                return current_config
                
            if not review['requires_revision']:
                self.log_message("Configuration approved by critic")
                return current_config
            
            # If revision is needed, create a new prompt for the parser
            revision_prompt = f"""
            Original request: {user_prompt}
            
            The current configuration has these issues:
            {json.dumps(review['issues'], indent=2)}
            
            Please revise the configuration to fix these issues.
            """
            
            user_prompt = revision_prompt  # Update prompt for next iteration
            self.log_message("Requesting revision from parser")
        
        self.log_message(f"Reached maximum iterations ({self.max_iterations})")
        return current_config
    
def process_dashboard_request(user_prompt: str, df: pd.DataFrame) -> Dict:
    coordinator = EnhancedCoordinatorAgent()
    result = coordinator.process_request(user_prompt, df)

    return result

user_prompt = (
    "I want to update the slicers 'Campagne', 'Offre', 'Typologie de vidéos', 'Plateforme' and 'Catégorie' in the dashboard so that their format match the 'Catégorie' slicer on the 'Vision hebdo' page."
)

user_prompt = (
    "I want to update the slicers 'Mois' and 'Offre' on the page 'Vision mensuelle' so that their format match the 'Catégorie' slicer on the 'Vision hebdo' page."
)

# Test the function
result = process_dashboard_request(user_prompt, df)
print("\nFinal Configuration:")
print(json.dumps(result, indent=2, ensure_ascii=False))

