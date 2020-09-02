FROM phusion/baseimage:master-amd64

CMD ["/sbin/my_init"]


# setup sshd for connection into container
RUN rm -f /etc/service/sshd/down && \
    # Avoid ERROR: "invoke-rc.d: policy-rc.d denied execution of start"
    sed -i "s/^exit 101$/exit 0/" /usr/sbin/policy-rc.d && \
    # [RUNLEVEL=1] -> Avoid ERROR: "invoke-rc.d: could not determine current runlevel"
    RUNLEVEL=1 /etc/my_init.d/00_regen_ssh_host_keys.sh && \
    /usr/sbin/enable_insecure_key


# prepare - install dependecies
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    # we use python3.7
    apt install -y nginx python3.7 python3.7-dev build-essential libssl-dev libpcre3-dev unzip && \
    # install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && \
    # clean-up:
    rm get-pip.py && \
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
    ln -sf /usr/src/uwsgi/conf/nginx/main.nginx_conf /etc/nginx/nginx.conf && \
    ln -s /usr/src/uwsgi/conf/nginx/nginx_site.nginx_conf /etc/nginx/sites-enabled/web-site.conf && \
    # create dir for nginx service and link runit service file
    mkdir /etc/service/nginx  && \
    ln -s /usr/src/uwsgi/conf/runit/nginx_run /etc/service/nginx/run


# setup python environment
RUN python3.7 -m pip install greenlet==0.4.16 \
                             gevent==20.6.2 \
                             python-socketio==4.6.0 \
                             cffi==1.14.2  && \
    # clean-up:
    rm -r ~/.cache


ARG UWSGI_VERSION

ENV SRC_PATH=/usr/src/uwsgi/uwsgi-$UWSGI_VERSION

# build uwsgi
# download sources zip form github-repository
RUN curl -L https://github.com/dholth/uwsgi/archive/$UWSGI_VERSION.zip -o /tmp/$UWSGI_VERSION.zip && \
    # unzip archive
    unzip -q /tmp/$UWSGI_VERSION.zip -d /usr/src/uwsgi && \
    cd $SRC_PATH && \
    # build core (with "debug" option => more detailed logs)
    UWSGI_PROFILE_OVERRIDE=debug=true python3.7 uwsgiconfig.py --build gevent && \
    # build cffi plugin:
    # 1) deal with "missing" python binary
    ln -s /usr/bin/python3.7 /usr/bin/python && \
    # 2) build plugin itself
    UWSGI_PROFILE_OVERRIDE=debug=true python3.7 uwsgiconfig.py --plugin plugins/cffi gevent && \
    # make our uwsgi setup system-wide:
    # 1) link binary
    ln -s $SRC_PATH/uwsgi /usr/bin/uwsgi && \
    # 2) link cffi plugin
    mkdir -p /usr/lib/uwsgi && \
    ln -s $SRC_PATH/cffi_plugin.so /usr/lib/uwsgi/ && \
    # 3) create directories: first for vassals configs and second for pidfile
    mkdir -p /var/run/uwsgi /etc/uwsgi/vassals && \
    # fix privileges:
    chmod a+w /var/run/uwsgi && \
    # 4) link uwsgi configurations
    ln -s /usr/src/uwsgi/conf/services/emperor.ini /etc/uwsgi/ && \
    ln -s /usr/src/uwsgi/conf/services/socketio.ini /etc/uwsgi/vassals && \
    # 5) prepare runit service
    mkdir -p /etc/service/uwsgi && \
    ln -s /usr/src/uwsgi/conf/runit/uwsgi_run /etc/service/uwsgi/run && \
    # 6) create app user
    adduser --system --no-create-home uwsgi && \
    adduser --system --no-create-home socketio && \
    # clean-up
    rm /tmp/$UWSGI_VERSION.zip


# hook for pycharm debug
RUN pip3.7 install pydevd-pycharm~=202.6948.78

VOLUME /web

EXPOSE 22 443
