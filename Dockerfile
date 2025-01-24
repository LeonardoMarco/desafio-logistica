FROM python:3.11-slim

# Cria um usuário não-root para rodar a aplicação
RUN adduser --disabled-password --gecos '' celeryuser

WORKDIR /app

COPY . /app

# Instale dependências para o MySQL
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip && pip install -r requirements.txt

# Define o usuário não-root para rodar os processos
USER celeryuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
