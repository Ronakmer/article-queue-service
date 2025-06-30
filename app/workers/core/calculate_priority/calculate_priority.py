import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient

class CalculatePriority:
    def __init__(self):
        self.api_client = APIClient()

    def calculate_priority(self, base_priority, data_type: str):
        DATA_WEIGHTS = {
            'content_message': 1,
            'retry_content_message': 2,
            'category': 3,
            'tag': 3,
            'author': 3,
            'primary_keyword': 4
        }

        base_priority = base_priority or 0  # default to 0 if None

        return base_priority + DATA_WEIGHTS.get(data_type, 0)

        # calculate_priority(12,'category')