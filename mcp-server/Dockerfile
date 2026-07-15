FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml

COPY src ./src

EXPOSE 8100

CMD ["python", "-m", "src.server"]