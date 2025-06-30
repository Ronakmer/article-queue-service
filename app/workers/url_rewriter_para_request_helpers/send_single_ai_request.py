import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.config.logger import LoggerSetup
from app.config.config import AI_RATE_LIMITER_URL
from app.workers.url_rewriter_para_request_helpers.ai_rate_limiter_scale_worker import AIRateLimiterScaleWorker

class SendSingleAiRequest:
    def __init__(self):
        self.api_client = APIClient()

        # logger_setup = LoggerSetup()
        self.ai_rate_limiter_scale_worker = AIRateLimiterScaleWorker()
        # self.logger = logger_setup.setup_worker_logger(self.pid)
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }

       
    def send_single_ai_request(self, single_request_data, workspace_slug_id):
        try:
            
            # print(single_request_data,'akajsisndf')
            
            url = f'{self.ai_rate_limiter_url}/message/publish'

            single_ai_response = requests.post(url, json=single_request_data, headers=self.headers)

            # print("send_ai_request single_ai_Response Body:", single_ai_response.json())
                
            # if single_ai_response.status_code not in [200, 201]:
            #     error_data = single_ai_response.json() if single_ai_response.text else {}
            #     if isinstance(error_data, dict) and "No workers" in str(error_data.get("error", "")):
            #         # self.logger.warning("No worker available, attempting to scale up...")
            #         print("No worker available, attempting to scale up...")
                    
            #         # Try to scale up worker using the workspace ID
            #         if self.ai_rate_limiter_scale_worker(str(workspace_slug_id)):
            #             # self.logger.info("Successfully initiated worker scale up")
            #             print("Successfully initiated worker scale up")
                        
            #             # Retry the request after scaling
            #             single_ai_response = requests.post(url, json=single_request_data, headers=self.headers)


            if single_ai_response.status_code not in [200, 201]:
                try:
                    error_data = single_ai_response.json() if single_ai_response.text else {}
                except ValueError:
                    error_data = {}

                # Fix: Check for "worker_required" field or message string directly
                no_worker_error = (
                    isinstance(error_data, dict) and (
                        error_data.get("worker_required") is True or 
                        "no worker available" in str(error_data.get("message", "")).lower()
                    )
                )

                if no_worker_error:
                    print("No worker available, attempting to scale up...")

                    scaled = self.ai_rate_limiter_scale_worker.scale_worker(str(workspace_slug_id))

                    if scaled:
                        print("Successfully initiated worker scale up")
                        single_ai_response = requests.post(
                            url,
                            json=single_request_data,
                            headers=self.headers,
                            timeout=30
                        )

            return single_ai_response.json()

        except requests.RequestException as e:
            return f"Request to ai lambda failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"