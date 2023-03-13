FROM python:3.9

COPY start.sh /
COPY . /usr/src/app
WORKDIR /usr/src/app

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
ENV PYTHONIOENCODING=utf-8

#RUN pip3 install --upgrade pip
#RUN pip3 install -i https://pypi.douban.com/simple -U pip
#RUN pip3 install -i https://pypi.douban.com/simple -U setuptools
RUN pip3 download -d offline_pkg -i https://pypi.douban.com/simple -r requirement.txt
RUN pip3 install --no-index --find-links=./offline_pkg -r requirement.txt

#RUN mkdir /var/log/python
#RUN touch /var/log/python/python-alg-tradetask.log
#RUN touch /var/log/python/gunicorn.pid
#RUN touch /var/log/python/access.log
#RUN touch /var/log/python/debug.log
