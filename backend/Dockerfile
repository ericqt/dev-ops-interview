# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install "fastapi[standard]"
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# TODO Use $BACKEND_PORT
CMD ["fastapi", "run", "app/main.py", "--port", "3000"]