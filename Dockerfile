# meta
FROM fedora:latest
LABEL cache-key=2019-08-17

# system level setup
RUN dnf update -y
RUN dnf install -y git rsync
RUN adduser user
WORKDIR /home/user

# upload data
COPY . env
RUN chown user:user -R env

# user level setup
USER user
WORKDIR /home/user/env

# if buildout.cfg exists rebuild the python venv otherwise do a bin/bootstrap
# this allows pre bootstraping the build in order to bring in git repo dependencies
# for which we may not have SSH keys for.
RUN (test -e buildout.cfg && rm -rf buildout/py && python3 -m venv buildout/py) || bin/bootstrap
RUN buildout/py/bin/pip install -U pip
RUN buildout/py/bin/pip install -U setuptools
RUN buildout/py/bin/easy_install -U zc.buildout

RUN bin/build
