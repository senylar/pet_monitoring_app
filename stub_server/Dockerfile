FROM python:3.12
LABEL authors="gggg"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для Flask-приложения
EXPOSE 5000

# Устанавливаем команду для запуска приложения
CMD ["python", "stub_server/stub_server.py"]