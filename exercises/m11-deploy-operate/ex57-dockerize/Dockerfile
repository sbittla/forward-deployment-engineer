FROM python
ENV API_KEY=sk-live-please-dont
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python -m app
