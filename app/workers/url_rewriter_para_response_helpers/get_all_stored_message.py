

import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.url_rewriter_para_request_helpers.get_single_ai_response import GetSingleAiResponse
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore

class StoredMessageFetcher:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        self.get_single_ai_response_service = GetSingleAiResponse()
        self.ai_message_response_store_service = AIMessageResponseStore()
 

    def get_all_stored_message(self, article_id, message_field_type):
        try:
           
            params = {
                'article_alug_id': article_id,
                'message_field_type': message_field_type,
            }

            all_messages = self.api_client.crud('ai-message', 'read', params=params)
            
            if all_messages.get("success") and "data" in all_messages:
                # Save the data to a JSON file
                with open('demo_json/all_message_data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_messages["data"], f, ensure_ascii=False, indent=4)

                # Filter only failed ai_response_status
                failed_messages = [msg for msg in all_messages["data"] if msg.get("ai_response_status") == "failed"]

                # Save failed messages to another file
                with open('demo_json/failed_message_data.json', 'w', encoding='utf-8') as f:
                    json.dump(failed_messages, f, ensure_ascii=False, indent=4)

                retry_failed_messages_data = None
                # Retry if any failures
                if len(failed_messages) > 0:
                    print(f"Found {len(failed_messages)} failed messages. Retrying...")
                    retry_failed_messages_data = self.retry_failed_messages(failed_messages)
                    print(retry_failed_messages_data,'retry_failed_messages_data')

                    
                    # Build a map of message_id to new retried success response
                    retried_success_map = {msg["message_id"]: msg for msg in retry_failed_messages_data if msg.get("ai_response_status") == "success"}

                    # Replace the failed messages in all_messages["data"] with their updated success version
                    updated_messages = []
                    for msg in all_messages["data"]:
                        if msg.get("ai_response_status") == "failed" and msg["message_id"] in retried_success_map:
                            updated_messages.append(retried_success_map[msg["message_id"]])  # use the retried successful message
                        else:
                            updated_messages.append(msg)  # keep original (either not failed or no retry data)

                    # Save updated messages to a new JSON file
                    with open('demo_json/updated_all_message_data.json', 'w', encoding='utf-8') as f:
                        json.dump(updated_messages, f, ensure_ascii=False, indent=4)

                    # Replace in-memory data as well
                    all_messages["data"] = updated_messages
                
                    
            return all_messages            

        except Exception as e:
            print(f"[get_all_stored_message] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}



    def retry_failed_messages(self, failed_messages):

        try:
            stored_responses = []  # List to collect all store_ai_response_data results

            for msg in failed_messages:
                try:
                    try:
                        # Load the original AI request details
                        send_single_ai_request_data = json.loads(msg.get("ai_request", "{}"))
                        message_id = send_single_ai_request_data.get("message_id")

                        if not message_id:
                            print(f"Missing message_id in ai_request for ID: {msg['id']}")
                            continue

                        # Attempt to fetch the AI response again
                        get_single_ai_response_data = self.get_single_ai_response_service.get_single_ai_response(message_id)
                        print(get_single_ai_response_data, 'get_single_ai_response_data')

                    except Exception as e:
                        print({"status": "error","step": "get_single_ai_response in retry_failed_messages","message": str(e)})
                        continue  # Skip storing step if get fails

                    try:
                        store_ai_response_data = self.ai_message_response_store_service.store_ai_message_response(get_single_ai_response_data)
                        print(store_ai_response_data, 'store_ai_response_data')
                        data = store_ai_response_data.get("data", {})

                        stored_responses.append(data)  # Add to list
                    except Exception as e:
                        print({"status": "error","step": "store_ai_message_response in retry_failed_messages","message": str(e)})

                except Exception as e:
                    print(f"Failed to retry message {msg.get('message_id', 'unknown')}: {e}")

            return stored_responses  # Return the list of stored responses

        except Exception as e:
            print(f"[retry_failed_messages] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

