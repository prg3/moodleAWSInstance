#!/bin/bash

# Install some packages that we will need and then stop Apache until Moodle is installed
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y pwgen apache2 postgresql php7.0 libapache2-mod-php7.0
apt-get install -y graphviz aspell php7.0-pspell php7.0-curl php7.0-gd php7.0-intl php7.0-mysql php7.0-xml php7.0-xmlrpc php7.0-ldap php7.0-zip php7.0-pgsql
phpenmod pgsql
systemctl stop apache2

#Checkout Moodle - Disabled because Git takes too long
#cd /var/www/html
#rm -rf /var/www/html/*
#git clone https://github.com/moodle/moodle.git .
#git branch --track MOODLE_31_STABLE origin/MOODLE_31_STABLE
#git checkout MOODLE_31_STABLE

# Alternative install, using wget
cd /var/www/html
rm -rf /var/www/html/*
curl https://download.moodle.org/download.php/direct/stable31/moodle-latest-31.tgz | tar xzf -
mv moodle/* .
mv moodle/.??* .
rmdir moodle

#Fixup some permissions
mkdir /moodledata
chown www-data:www-data /moodledata
chown -R www-data:www-data /var/www/html
chmod 0777 /moodledata
chmod -R 0755 /var/www/html

# Create Database
PASSWORD=`pwgen 20 1`
echo "CREATE USER root" | sudo -u postgres psql
echo "ALTER USER root WITH PASSWORD '$PASSWORD'" | sudo -u postgres psql
echo "CREATE DATABASE moodle OWNER root" | sudo -u postgres psql

# Auto Install moodle
# admin/myM00dleP@ssword
HOSTNAME=`curl http://169.254.169.254/latest/meta-data/public-hostname`

sudo -u www-data php /var/www/html/admin/cli/install.php --lang=en --wwwroot=http://$HOSTNAME --dataroot=/moodledata \
  --dbtype=pgsql --dbpass=$PASSWORD --fullname="Test Moodle Site" --shortname="TestMoodle" --adminuser=admin \
  --adminpass=myM00dleP@ssword --adminemail=no@nowhere.com --non-interactive --agree-license

systemctl start apache2

#Install Cron
echo "* * * * * /usr/bin/php  /var/www/html/admin/cli/cron.php >/dev/null" > /etc/cron.d/moodle
