FROM public.ecr.aws/lambda/python:3.12

ARG LAMBDA_TASK_ROOT=/var/task
WORKDIR ${LAMBDA_TASK_ROOT}

# Install Python dependencies into the Lambda task root
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application source (filtered by .dockerignore)
COPY . .

CMD ["wsgi_handler.handler"]
