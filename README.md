```

           :~77777!!!^:.
        .~7J7^^::^^^~!77!~::::
      ^7JJ~7~        .^7?JY?^:
    ^7J5?. ^?:    .~7!~:..~?7.
   !?!J?.   !7. ^7?!^      ^J!.
  !?^JJ:    .JJ??~.         7Yx   NotForSale: Sustainable art for a sustainable future
 ^J^^Y7     ~J5?.           7Yx                                          notforsale.cc
.?J:^Y7.  :??^^J?:          7Yx
 !Y7^JJ^ ^J7.  :?Y~.       ^J7
  !YJJYJ7?^     .~J?~.    ~Y?.
   :!?Y55J!^:::...:!J?!~^7Y?:
      ^?77??JJJJJJJJJ?JYJ?^.
           ..:::^^^^^^::.

```

# Notforsale Client

## Requirements

Tested on Raspberry Pi 4 and Pimoroni Impression

To build and run the notforsale client image, please execute the following.

## How-to

First you want to build a docker image:

```
sudo docker build -t notforsale_cli:v3
```

Then to run container:

Make sure `BROKER` and `WEB` leads to correct host, in my case I used my local environment.

```bash
sudo docker container run -d --privileged -e USERNAME="notforsale" -e PASSWORD="notforsale" -e BROKER="192.168.1.143" -e WEB="http://localhost:8888" -v $(pwd)/:/app --restart unless-stopped notforsale_cli:v3
```
