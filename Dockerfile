FROM arm32v7/python

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN apt-get install libzbar0 -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "-u", "/app/client.py" ]
