FROM public.ecr.aws/lambda/python:3.12

# Install Python dependencies into the Lambda task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy full application source (filtered by .dockerignore)
COPY . ${LAMBDA_TASK_ROOT}/

CMD ["wsgi_handler.handler"]
