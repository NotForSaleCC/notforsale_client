FROM arm32v7/python:3

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install -i https://test.pypi.org/simple/ inky==1.3.2

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "/app/client.py" ]