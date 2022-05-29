To build and run the notforsale client image, please execute the following.

First you want to build a docker image:

```
sudo docker build -t notforsale_cli:v2
```

Then to run container:

```bash
sudo docker container run -d --privileged -e USERNAME="notforsale" -e PASSWORD="notforsale" -e BROKER="192.168.1.143" -e WEB="http://localhost:8888" -v $(pwd)/:/app --restart unless-stopped notforsale_cli:v2
```