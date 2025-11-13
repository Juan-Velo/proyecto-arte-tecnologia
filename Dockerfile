FROM public.ecr.aws/lambda/python:3.12

ARG LAMBDA_TASK_ROOT=/var/task
ENV LAMBDA_TASK_ROOT=${LAMBDA_TASK_ROOT}
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}

# Install Python dependencies into the Lambda task root
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application source (filtered by .dockerignore)
COPY . .

CMD ["wsgi_handler.handler"]
