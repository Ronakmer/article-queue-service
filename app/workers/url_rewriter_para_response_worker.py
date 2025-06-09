from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore 

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

            
            # # Your processing logic here
            try:
                # Step 1: Get selectors
                stored_message_data = self.ai_message_response_store_service.store_ai_message_response(data)
                print(stored_message_data,'stored_message_dataXXXXXXXXXXXXXXXXXXXxx')
            except Exception as e:
                return {"status": "error", "step": "get_selectors", "message": str(e)}

                        
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