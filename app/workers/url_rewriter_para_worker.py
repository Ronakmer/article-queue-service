from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.worker_url_rewriter_para.selector_lambda import ArticleSelectorService
from app.workers.worker_url_rewriter_para.scraper_lmabda import ArticleScraperService  # ensure it's the class version
from app.workers.worker_url_rewriter_para.ai_rate_limiter import AIRateLimiterService

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



    def process_message(self, ch, method, properties, body):
        try:
            # Process the message
            data = json.loads(body)  # Parse the JSON body
            self.logger.info(f"Processing message: {data}")
            
            # Your processing logic here
            try:
                # Step 1: Get selectors
                selector_data = self.selector_service.get_selectors(data)
            except Exception as e:
                return {"status": "error", "step": "get_selectors", "message": str(e)}

            try:
                # Step 2: Scrape article data
                scraped_data = self.scraper_service.get_scraped_article_data(selector_data, data)
            except Exception as e:
                return {"status": "error", "step": "get_scraped_article_data", "message": str(e)}

            try:
                # Step 3: Prepare content for AI
                process_content_data = self.ai_rate_limiter_service.fetch_and_process_content(scraped_data, data)
            except Exception as e:
                return {"status": "error", "step": "fetch_and_process_content", "message": str(e)}

            try:
                # Step 4: Get AI response
                ai_response_json = self.ai_rate_limiter_service.send_ai_request(process_content_data)
            except Exception as e:
                return {"status": "error", "step": "send_ai_request", "message": str(e)}

            try:
                # Step 5: Final formatting
                final_ai_response = self.ai_rate_limiter_service.merge_and_sequence_ai_response(ai_response_json, process_content_data)
            except Exception as e:
                return {"status": "error", "step": "merge_and_sequence_ai_response", "message": str(e)}
            
            
            
            self.logger.info(f"final_ai_response: {final_ai_response}")
            
            
            
            # Log successful completion
            # self.logger.info(f"Message processing completed successfully for data: {data}")
            self.logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            
            # Explicitly acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True
        except Exception as e:
            self.logger.error(f"Message processing failed for data: {body}. Error: {str(e)}")
            # Negative acknowledge the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False