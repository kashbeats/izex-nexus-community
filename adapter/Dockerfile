FROM python:3.12-alpine
WORKDIR /app
COPY server.py /app/server.py
USER 65532:65532
CMD ["python3","/app/server.py","--config","/config/config.json","--bind","0.0.0.0"]
