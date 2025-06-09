import requests
import os
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor
import time
import json
import uuid
from app.config.config import AI_RATE_LIMITER_URL
import logging
import json
import time

class AIRateLimiterService:
    def __init__(self):
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.content_handler = ContentProcessor()
        

    def fetch_and_process_content(self, scraped_content, input_json_data):
        try:
            print('2222222222222222222222222222222222')
            # Fetch content
            content_data = self.content_handler.fetch_content(scraped_content)
            if not content_data:
                return None, False
                    
            if isinstance(content_data, dict):
                request_data = self.content_handler.process_content(content_data, input_json_data)

            # for tesing  
            with open('result_data.json', 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=4)
                    
            return request_data

            # return request_data
            # return_data = self.send_ai_request(request_data)

        except Exception as e:
            return f"An unexpected error occurred: {e}"
        
        
        
    def send_ai_requests(self, request_json_data):
        try:
            submit_data_responses = []

            for single_request_data in request_json_data.get("ai_requests", []):
                try:
                    url = f'{self.ai_rate_limiter_url}/message/publish'
                    response = requests.post(url, json=single_request_data, headers=self.headers)

                    if response.status_code not in [200, 201]:
                        return f"AI request error: {response.status_code} - {response.text}"

                    merged_entry = {
                        "ai_request": single_request_data,
                        "ai_response": response.json()
                    }

                    submit_data_responses.append(merged_entry)

                except requests.RequestException as e:
                    return f"Request failed: {e}"
                except Exception as e:
                    return f"Error during processing: {e}"


            # Save the file directly to the existing 'demo_json' folder
            with open('demo_json/send_ai_requests_data.json', 'w', encoding='utf-8') as f:
                json.dump(submit_data_responses, f, ensure_ascii=False, indent=4)

            return submit_data_responses

        except requests.RequestException as e:
            return f"Request failed: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
