FROM python:3.12
LABEL authors="gggg"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для Flask-приложения

ENV FLASK_APP=stub_server.py
# Устанавливаем команду для запуска приложения
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]