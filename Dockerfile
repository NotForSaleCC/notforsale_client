FROM balenalib/raspberry-pi-debian-python

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "/app/client.py" ]
