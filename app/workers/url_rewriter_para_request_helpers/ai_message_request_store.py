import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class AIMessageRequestStore:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        self.api_client = APIClient()
        
      
    def store_ai_message_request(self, data):
        try:

            # Extract required fields from the incoming data
            article_id = str(data.get("article_id", "")).strip()
            message_id = str(data.get("message_id", "")).strip()

            if not article_id or not message_id:
                return {"success": False, "error": "Missing article_id or message_id"}

            request_data = {
                "article_id": article_id,
                "message_id": message_id,
                "article_message_total_count": data.get("article_message_total_count", 0),
                # "article_message_count": data.get("article_message_count", 1),
                # "ai_request": json.dumps(data.get("prompt", [])),  # store as JSON string
                "ai_request": json.dumps(data),  # store as JSON string
                "ai_request_status": data.get("ai_request_status", ""),
                "message_field_type": data.get("message_field_type", ""),
                "message_priority": data.get("message_priority", ""),
                # "article_message_count":1,
            }

            max_retries = 3
            stored_message = None

            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'ai-message',
                    'create',
                    data=request_data
                )

                print(f"[store_ai_message_request] Attempt {attempt}, Response: {stored_message}")

                if stored_message.get('status_code') == 200:
                    return stored_message
                else:
                    print(f"[store_ai_message_request] Attempt {attempt} failed. Retrying...")

            return {
                "success": False,
                "error": f"Failed to update after {max_retries} attempts",
                "last_response": stored_message,
            }


        except Exception as e:
            print(f"[store_ai_message_request] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
