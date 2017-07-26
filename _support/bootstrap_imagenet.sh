#!/bin/bash

# Update yum, install python, Apache 2.4, and the WSGI stuff
yum update -y
yum install -y git python35-virtualenv httpd24
yum install -y mod24_wsgi-python35.x86_64

# default Python version to 3.5
alternatives --set python /usr/bin/python3.5

# upgrading pip doesn't call pip3 pip anymore, so you have to fix that
pip install --upgrade pip 


/usr/local/bin/pip install flask \
                           pandas \
                           numpy \
                           tensorflow \
                           boto3 \
                           Pillow

# https://stackoverflow.com/questions/26302805/pip-broken-after-upgrading
hash -r
echo $(type pip)
# NOTE:  This may or may not be needed...
# alias pip=/usr/local/bin/pip3

# create a place for our Web app
mkdir -p /var/www/tf
git clone https://github.com/understructure/dl-server.git /var/www/tf

# setup permissions for apache
chown -R apache:apache /var/www/tf
mv /var/www/tf/_support/vhost.conf /etc/httpd/conf.d/
mv /var/www/tf/_support/httpd.conf /etc/httpd/conf/

# NOTE:  Not sure if this is necessary...
chown apache:apache /etc/httpd/conf.d/vhost.conf

# get the public-hostname from the latest metadata and put that into the vhost.conf file
# curl http://169.254.169.254/latest/meta-data/public-hostname | xargs -I '{}' sudo sed -i 's/${PUBLIC_DNS}/{}/' /etc/httpd/conf.d/vhost.conf
curl http://169.254.169.254/latest/meta-data/public-hostname | xargs -I '{}' sed -i 's/${PUBLIC_DNS}/{}/' /etc/httpd/conf.d/vhost.conf

git clone https://github.com/tensorflow/models.git
python ./models/tutorials/image/imagenet/classify_image.py

# start Apache Web Server
service httpd start
chkconfig httpd on
