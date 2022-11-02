from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/home/rezayogaswara/python_projects/chatbotmanagement.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
accesslog = '/home/rezayogaswara/python_projects/backend-chatbot-management/access_log'
errorlog = '/home/rezayogaswara/python_projects/backend-chatbot-management/error_log'
capture_output = True
loglevel = 'info'
reload = True
