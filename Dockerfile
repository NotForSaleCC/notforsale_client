FROM arm32v7/python

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN apt-get update && \
    apt-get install libzbar0 supervisor -y

RUN mkdir -p /var/log/supervisor
RUN pip install --no-cache-dir -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "-u", "/app/client.py" ]
