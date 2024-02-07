# Base Image
FROM python:3.11

# Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create Working Directory
WORKDIR /code

# 시스템 의존성 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev

# Install Poetry
RUN pip install poetry
# RUN curl -sSL -o get-poetry.py https://install.python-poetry.org \
#     && python3 get-poetry.py \
#     && rm get-poetry.py
#RUN curl -sSL https://install.python-poetry.org | python3 -
#RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
#ENV PATH="/root/.poetry/bin:$PATH"

#Upgrade python and Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy Poetry Files
COPY poetry.lock pyproject.toml ./

# Set Python Version for Poetry
# RUN poetry env use 3.11
RUN pip wheel --no-use-pep517 coreschema==0.0.4 && pip install coreschema-0.0.4-*.whl
# Install Dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy Application Code
COPY . .
EXPOSE 8000
# Set Startup Command
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#docker-compose up
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]