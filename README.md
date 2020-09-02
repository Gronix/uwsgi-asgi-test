## Test uWSGI + ASGI

We use [Python-Socketio](https://python-socketio.readthedocs.io/en/latest/) on Server-side and socket.io client in web-browser. 
* `docker-compose.yml` - key-part of this repo
* `socketio_application/main_socketio.py` - simplification of our app
* `uwsgi/` and `daphne/` - directories contains conf files for uWSGI and Daphne respectively    
 
For this docker-images i'm using [baseimage](https://github.com/phusion/baseimage-docker) as parent. Runit as init system. You can login into running container via _ssh_ using [docker-ssh](https://github.com/phusion/baseimage-docker#docker_ssh) (all configurations have already been made). 

uWSGI built with flag `debug` - for verbosity

Front-end server - Nginx      (listening on :8007 - host,  :443 - container). Connect via `https://localhost:8007`

You can connect directly to uWSGI/Daphne via `http://localhost:8800`

Also you can force client to open only Websockets connections - see commented line in `socketio_application/index.html`

P.S. Daphne here just for a proof of concept that the socketio app works
