FROM python:3.13-alpine

WORKDIR /app

COPY ./main.py ./pyproject.toml ./uv.lock ./

RUN pip install --upgrade pip && pip install --no-cache-dir uv
RUN uv sync --frozen

EXPOSE 7860

CMD ["uv", "run", "python", "main.py"]