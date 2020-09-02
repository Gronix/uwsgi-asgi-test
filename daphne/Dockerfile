FROM phusion/baseimage:master-amd64

CMD ["/sbin/my_init"]


# setup sshd for connection into container
RUN rm -f /etc/service/sshd/down && \
    # Avoid ERROR: "invoke-rc.d: policy-rc.d denied execution of start"
    sed -i "s/^exit 101$/exit 0/" /usr/sbin/policy-rc.d && \
    # [RUNLEVEL=1] -> Avoid ERROR: "invoke-rc.d: could not determine current runlevel"
    RUNLEVEL=1 /etc/my_init.d/00_regen_ssh_host_keys.sh && \
    /usr/sbin/enable_insecure_key


# setup environment
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    # we use python3.7
    apt install -y nginx python3.7 && \
    # install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && \
    # setup python dependencies
    python3.7 -m pip install python-socketio==4.6.0 daphne==2.5.0 && \
    # setup daphne runit service
    mkdir /etc/service/daphne && \
    ln -s /usr/src/daphne/conf/runit/daphne_run /etc/service/daphne/run && \
    # clean-up:
    rm -r get-pip.py ~/.cache && \
    apt-get clean


# setup nginx configuration
RUN cd /etc/nginx && \
    # setup selffigned key and cert
    openssl req -x509 -nodes -days 365 -newkey rsa:2048  \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Test/OU=test/CN=localhost" \
    -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt && \
    # remove default site config
    rm /etc/nginx/sites-enabled/default && \
    # prepare links for our nginx conf files (core and site)
    ln -sf /usr/src/daphne/conf/nginx/main.nginx_conf /etc/nginx/nginx.conf && \
    ln -s /usr/src/daphne/conf/nginx/nginx_site.nginx_conf /etc/nginx/sites-enabled/web-site.conf && \
    # create dir for nginx service and link runit service file
    mkdir /etc/service/nginx  && \
    ln -s /usr/src/daphne/conf/runit/nginx_run /etc/service/nginx/run


VOLUME /web

EXPOSE 22 443
