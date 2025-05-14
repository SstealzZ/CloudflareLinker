FROM python:3.12-slim

# Récupération des arguments de construction
ARG BACKEND_PORT

# Définition des variables d'environnement
ENV PORT=$BACKEND_PORT

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./ /code/

# Set Python path to include current directory
ENV PYTHONPATH="${PYTHONPATH}:/code"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"] 