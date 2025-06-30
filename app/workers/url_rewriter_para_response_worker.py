from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore 
from app.workers.url_rewriter_para_response_helpers.get_all_stored_message import StoredMessageFetcher 
from app.workers.url_rewriter_para_response_helpers.format_article_content import ArticleContentFormatter 

class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_para_response_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_para_response_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_para_response_worker")
        self.logger.info("url_rewriter_para_response_worker initialized and ready to process messages")
        self.ai_message_response_store_service = AIMessageResponseStore()
        self.get_all_stored_message_service = StoredMessageFetcher()
        self.article_content_formatter_service = ArticleContentFormatter()



    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ['true', '1', 'yes']
        return bool(value)
            


    def process_message(self, ch, method, properties, body):
        try:
            # Process the message
            data = json.loads(body)  # Parse the JSON body
            self.logger.info(f"Processing message: {data}")
            
        
            message = data.get("message", {})
            all_stored_message_data = None
            
            # # Your processing logic here

            
            # Step 1: store ai message response
            try:
                stored_message_data = self.ai_message_response_store_service.store_ai_message_response(data)
                # print(stored_message_data,'stored_message_dataXXXXXXXXXXXXXXXXXXXxx')
                print(stored_message_data,'----------------------stored_message_data----------------------')        
                
            except Exception as e:
                print({"status": "error", "step": "store_ai_message_response", "message": str(e)})
                # return {"status": "error", "step": "store_ai_message_response", "message": str(e)}


            # Step 2: get all stored ai message 
            try:
                # Check if data is successfully updated
                if (stored_message_data and stored_message_data.get("status_code") == 200 and stored_message_data.get("data", {}).get("success") == True):
                    # Get the actual message data inside stored_message_data
                    message_data = stored_message_data.get("data", {}).get("data", {})

                    article_message_count = message_data.get("article_message_count")
                    article_message_total_count = message_data.get("article_message_total_count")
                    article_id = message_data.get("article_id")
                    message_field_type = message_data.get("message_field_type")

                    if article_message_count == article_message_total_count:
                        print('this is yoooooooooooooooooooooooooo')

                        all_stored_message_data = self.get_all_stored_message_service.get_all_stored_message(article_id, message_field_type)
                        # print(stored_message_data,'stored_message_dataXXXXXXXXXXXXXXXXXXXxx')  

            except Exception as e:
                print({"status": "error", "step": "get_all_stored_message", "message": str(e)})
                # return {"status": "error", "step": "get_all_stored_message", "message": str(e)}



            # Step 3: convert json to html 
            try:
                formated_article_content = self.article_content_formatter_service.format_article_content(all_stored_message_data)
                # print(formated_article_content,'formated_article_contentXXXXXXXXXXXXXXXXXXXxx')
                print(formated_article_content,'----------------------formated_article_content----------------------')        
                
            except Exception as e:
                print({"status": "error", "step": "store_ai_message_response", "message": str(e)})
                # return {"status": "error", "step": "store_ai_message_response", "message": str(e)}







            # Log successful completion
            # self.logger.info(f"Message processing completed successfully for data: {data}")
            self.logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_para_response_worker xxxxxxxxxxxxxxxxxxxxxxxxx")
            
            # Explicitly acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True
        except Exception as e:
            self.logger.error(f"Message processing failed for data: {body}. Error: {str(e)}")
            # Negative acknowledge the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False