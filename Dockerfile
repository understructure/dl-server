
FROM amazonlinux:latest
LABEL maintainer Maashu Cloney <mcloney@captechconsulting.com>

# Update yum, install python, Apache 2.4, and the WSGI stuff
RUN yum update -y && yum install -y git \
                                    python35-virtualenv \
                                    httpd24 \
                                    mod24_wsgi-python35.x86_64

# default Python version to 3.5
RUN alternatives --set python /usr/bin/python3.5 && pip install \
                 --upgrade pip && /usr/local/bin/pip install flask \
                                                             pandas \
                                                             numpy \
                                                             tensorflow \
                                                             boto3 \
                                                             Pillow

# https://stackoverflow.com/questions/26302805/pip-broken-after-upgrading
# hash -r

# echo $(type pip)
# NOTE:  This may or may not be needed...
# alias pip=/usr/local/bin/pip3

# create a place for our Web app
RUN mkdir -p /var/www/tf && git clone https://github.com/understructure/dl-server.git /var/www/tf

# setup permissions for apache
RUN chown -R apache:apache /var/www/tf
COPY ./_support/vhost.conf /etc/httpd/conf.d/
COPY ./_support/httpd.conf /etc/httpd/conf/

# NOTE:  Not sure if this is necessary...
# chown apache:apache /etc/httpd/conf.d/vhost.conf

RUN git clone https://github.com/tensorflow/models.git && python ./models/tutorials/image/imagenet/classify_image.py


# get the public-hostname from the latest metadata and put that into the vhost.conf file
# curl http://169.254.169.254/latest/meta-data/public-hostname | xargs -I '{}' sed -i 's/${PUBLIC_DNS}/{}/' /etc/httpd/conf.d/vhost.conf
# start Apache Web Server
# service httpd start && chkconfig httpd on

