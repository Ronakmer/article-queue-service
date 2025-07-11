
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class FetchSupportivePrompt:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_supportive_prompt(self, supportive_prompts_slug_id, domain_slug_id=None):
        try:
            collected_supportive_prompts = []
            # print(slug_id,'slug_idxx')
            # for supportive_prompt_slug_id in target_supportive_prompt_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                # 'workspace_slug_id': workspace_slug_id,
                'slug_id':supportive_prompts_slug_id   
            }

            all_supportive_prompts = self.api_client.crud('supportive-prompt-variable', 'read', params=params)
            if isinstance(all_supportive_prompts, list):
                collected_supportive_prompts.extend(all_supportive_prompts)
            elif isinstance(all_supportive_prompts, dict):
                collected_supportive_prompts.append(all_supportive_prompts)

            return {
                "supportive_prompts": collected_supportive_prompts
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
