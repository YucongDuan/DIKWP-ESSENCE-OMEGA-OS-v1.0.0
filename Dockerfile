FROM python:3.12-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "essence_omega_os"]
CMD ["inspect"]
