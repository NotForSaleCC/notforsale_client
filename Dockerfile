FROM arm32v7/python:3

WORKDIR /app

COPY requirements.txt ./
COPY docker-entrypoint.sh /

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -i https://test.pypi.org/simple/ inky==1.3.2

COPY . .

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD [ "python", "/app/client.py" ]