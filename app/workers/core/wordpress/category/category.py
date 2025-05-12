
import requests
import os
from app.workers.core.article_innovator_api_call.api_client import APIClient
import time
import json
import uuid


class Category:
    def __init__(self):
        self.api_client = APIClient()
        

    def fetch_Category(self, input_json_data):
        try:
            print(input_json_data,'sdsdsdsdeeewewee')
            params={
                'domain_slug_id':'08a2ed3d-ba1d-4077-83d0-defaae22b034',
                'workspace_slug_id':'77b4ad49-db8a-4434-aad5-c2351c953cc7'
            }
            step_result = self.api_client.crud('category', 'read', '', params)
            print(step_result,'step_result')

        except Exception as e:
            return f"An unexpected error occurred: {e}"