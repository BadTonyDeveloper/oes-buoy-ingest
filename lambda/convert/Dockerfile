# Use AWS base image for Python 3.12 Lambda
FROM public.ecr.aws/lambda/python:3.12

# Copy the Lambda function code and requirements file
COPY convert_function.py ./
COPY requirements.txt ./

# Install dependencies into the Lambda image
RUN pip install -r requirements.txt -t .

# Set the handler
CMD ["convert_function.lambda_handler"]