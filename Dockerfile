FROM arm32v7/python

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN apt-get update && \
    apt-get install python3-opencv libzbar0 -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "/app/client.py" ]
