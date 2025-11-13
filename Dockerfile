FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code explicitly
COPY app.py ${LAMBDA_TASK_ROOT}/
COPY wsgi_handler.py ${LAMBDA_TASK_ROOT}/
COPY templates/ ${LAMBDA_TASK_ROOT}/templates/
COPY static/ ${LAMBDA_TASK_ROOT}/static/

CMD ["wsgi_handler.handler"]
