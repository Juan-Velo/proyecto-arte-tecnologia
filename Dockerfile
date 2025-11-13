FROM public.ecr.aws/lambda/python:3.12

# Install system deps (if any) and Python packages
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application sources
COPY app.py ${LAMBDA_TASK_ROOT}/
COPY wsgi_handler.py ${LAMBDA_TASK_ROOT}/
COPY static ${LAMBDA_TASK_ROOT}/static
COPY templates ${LAMBDA_TASK_ROOT}/templates

CMD ["wsgi_handler.handler"]
