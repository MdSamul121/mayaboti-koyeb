FROM node:24-bookworm-slim AS webui-builder

WORKDIR /app
COPY src/webui/package.json src/webui/package-lock.json ./webui/
WORKDIR /app/webui
RUN npm ci
COPY src/webui/ ./
COPY src/packages/client-events/ /app/packages/client-events/
COPY src/mayaboti/channels/ /app/mayaboti/channels/
RUN mkdir -p /app/mayaboti/web && npm run build

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates openssh-client libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/pyproject.toml src/README.md src/LICENSE src/THIRD_PARTY_NOTICES.md src/hatch_build.py ./src/
COPY src/docs/ ./src/docs/
COPY src/mayaboti/ ./src/mayaboti/
COPY --from=webui-builder /app/mayaboti/web/dist/ ./src/mayaboti/web/dist/

RUN MAYABOTI_SKIP_WEBUI_BUILD=1 pip install --no-cache-dir ./src python-dotenv

COPY start.py Procfile README.md .env.example ./

RUN useradd -ms /bin/bash mayaboti && \
    chown -R mayaboti:mayaboti /app /home/mayaboti

USER mayaboti

ENV PORT=8080 PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1
EXPOSE 8080

CMD ["python", "start.py"]
