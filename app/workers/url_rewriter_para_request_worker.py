from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.url_rewriter_para_request_helpers.ai_message_request_send import AIRateLimiterService
from app.workers.core.selector_lambda.selector_lambda import ArticleSelectorService
from app.workers.core.wordpress.fetch_category.fetch_category import FetchCategory
from app.workers.core.scraper_lmabda.scraper_lmabda import ArticleScraperService  # ensure it's the class version

class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_para_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_para_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_para_worker")
        self.logger.info("url_rewriter_para_worker initialized and ready to process messages")
        self.selector_service = ArticleSelectorService()
        self.scraper_service = ArticleScraperService()
        self.ai_rate_limiter_service = AIRateLimiterService()
        self.fetch_category_service = FetchCategory()



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
            # target_category_ids = message.get("wp_category_id", [])

            is_category_selected_by_ai = message.get("is_category_selected_by_ai")

            
            # # Your processing logic here
            try:
                # Step 1: Get selectors
                selector_data = self.selector_service.get_selectors(data)
                # print(selector_data,'selector_dataxxxxx')
            except Exception as e:
                return {"status": "error", "step": "get_selectors", "message": str(e)}

            try:
                # Step 2: Scrape article data
                scraped_data = self.scraper_service.get_scraped_article_data(selector_data, data)
                # print(scraped_data,'scraped_dataxxxxxxxxxxxx')
            except Exception as e:
                return {"status": "error", "step": "get_scraped_article_data", "message": str(e)}

            try:
                # Step 3: Prepare content for AI
                process_content_data = self.ai_rate_limiter_service.fetch_and_process_content(scraped_data, data)
                # print(process_content_data,'process_content_dataxxxxxxxxxxxxxxxxxxxx')
            except Exception as e:
                return {"status": "error", "step": "fetch_and_process_content", "message": str(e)}

            try:
                # Step 4: Get AI response
                ai_response_json = self.ai_rate_limiter_service.send_ai_request(process_content_data)
                print(ai_response_json,'fffffffffffffffff^^^^^^^^^^^^^^^^^^^^^^^^^^^^^6')
            except Exception as e:
                return {"status": "error", "step": "send_ai_request", "message": str(e)}

            # try:
            #     # Step 5: Final formatting
            #     final_article_content_response = self.ai_rate_limiter_service.merge_and_sequence_ai_response(ai_response_json, process_content_data)
            # except Exception as e:
            #     return {"status": "error", "step": "merge_and_sequence_ai_response", "message": str(e)}
            
            
            # try:
            #     # Step 5: Find category 
            #     print(is_category_selected_by_ai,'is_category_selected_by_aizzzz')
            #     if is_category_selected_by_ai == True:
            #         fetch_all_categories = self.fetch_category_service.fetch_category(data)
                
            # except Exception as e:
            #     return {"status": "error", "step": "fetch_category", "message": str(e)}
            
            
            
            
            
            
            # self.logger.info(f"final_article_content_response: {final_article_content_response}")
            
            # Log successful completion
            # self.logger.info(f"Message processing completed successfully for data: {data}")
            self.logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_para_worker xxxxxxxxxxxxxxxxxxxxxxxxx")
            
            # Explicitly acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True
        except Exception as e:
            self.logger.error(f"Message processing failed for data: {body}. Error: {str(e)}")
            # Negative acknowledge the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False