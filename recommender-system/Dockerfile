FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ${LAMBDA_TASK_ROOT}
COPY modules ${LAMBDA_TASK_ROOT}/modules/

CMD ["main.handler"]