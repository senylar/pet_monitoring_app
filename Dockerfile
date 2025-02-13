FROM python:3.12

LABEL authors="ggggg"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]