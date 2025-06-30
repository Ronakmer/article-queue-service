import pika, os
from app.config.logger import LoggerSetup


def get_rabbitmq_connection():
    # Get the current process ID
    pid = os.getpid()
    
    # Set up credentials
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "guest"), 
        os.getenv("RABBITMQ_PASS", "guest")
    )
    
    # Set up connection parameters with client properties
    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"), 
        port=int(os.getenv("RABBITMQ_PORT", 5672)), 
        credentials=credentials,
        client_properties={
            'pid': str(pid),
            'connection_name': f'worker-{pid}',
            'app_id': 'rabbitmq-flask-service',  
        }
    )
    print(parameters,'parameters')
    print(parameters,'parameters')
    
    # Create and return the connection
    return pika.BlockingConnection(parameters)

# import pika
# import os
# import time
# from app.config.logger import LoggerSetup
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()
# # Create logger
# logger_setup = LoggerSetup()
# logger = logger_setup.setup_logger()

# def get_rabbitmq_connection():
#     # Get the current process ID
#     pid = os.getpid()
    
#     # Log connection attempt
#     host = os.getenv("RABBITMQ_HOST", "localhost")
#     port = int(os.getenv("RABBITMQ_PORT", 5672))
#     logger.info(f"Attempting to connect to RabbitMQ at {host}:{port}")
    
#     # Set up credentials
#     credentials = pika.PlainCredentials(
#         os.getenv("RABBITMQ_USERNAME", "guest"), 
#         os.getenv("RABBITMQ_PASSWORD", "guest")
#     )
#       # Set up connection parameters with robust timeout settings
#     parameters = pika.ConnectionParameters(
#         host=host,
#         port=port,
#         credentials=credentials,
#         heartbeat=120,  # Increased heartbeat interval
#         blocked_connection_timeout=60,  # Increased timeout
#         socket_timeout=30.0,  # Increased socket timeout
#         connection_attempts=5,  # More retry attempts
#         retry_delay=2.0,
#         stack_timeout=60,  # Added stack timeout
#         tcp_options={'TCP_KEEPIDLE': 60,  # Keepalive settings
#                     'TCP_KEEPINTVL': 10,
#                     'TCP_KEEPCNT': 5},
#         client_properties={
#             'pid': str(pid),
#             'connection_name': f'worker-{pid}',
#             'app_id': 'rabbitmq-flask-service',
#             'connection_type': 'worker'
#         }
#     )
    
#     print(parameters,'parameters')
    
#     # Try to establish connection with retry logic
#     max_retries = 3
#     retry_delay = 2
#     last_error = None
    
#     for attempt in range(max_retries):
#         try:
#             logger.info(f"Connection attempt {attempt + 1} of {max_retries}")
#             connection = pika.BlockingConnection(parameters)
#             logger.info("Successfully established RabbitMQ connection")
#             print(connection,'connection')
#             return connection
        
            
#         except pika.exceptions.AMQPConnectionError as e:
#             last_error = e
#             logger.warning(f"""Connection attempt {attempt + 1} failed with AMQPConnectionError:
#                 Error message: {str(e)}
#                 Connection details:
#                 - Host: {host}
#                 - Port: {port}
#                 - Username: {os.getenv('RABBITMQ_USERNAME')}
#                 - Socket timeout: {parameters.socket_timeout}
#                 - Connection timeout: {parameters.blocked_connection_timeout}
#                 Error type: {type(e)._name_}""")
#             if attempt < max_retries - 1:
#                 time.sleep(retry_delay)
                
#         except Exception as e:
#             last_error = e
#             logger.error(f"""Unexpected error on connection attempt {attempt + 1}:
#                 Error message: {str(e)}
#                 Error type: {type(e)._name_}
#                 Connection details:
#                 - Host: {host}
#                 - Port: {port}""")
#             if attempt < max_retries - 1:
#                 time.sleep(retry_delay)
    

#     # If we get here, all retries failed
#     logger.error(f"""Failed to connect to RabbitMQ after {max_retries} attempts.
#         Last error: {str(last_error)}
#         Error type: {type(last_error)._name_}""")
#     return None