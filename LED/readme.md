### Installing all software
sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools

sudo apt-get install python3-bluez

### Installing radicale

sudo apt-get install python3-radicale

mkdir ~/.config/radicale/

nano ~/.config/radicale/config

sudo chmod a+rwx ~/.config/radicale/

[server]

hosts = XXX.XXX.X.XXX

max_connections = 20

max_content_length = 1000000000

timeout = 30

[auth]

delay = 1

type = htpasswd

htpasswd_filename = ~/.config/radicale/users

htpasswd_encryption = plain

[storage]

filesystem_folder = ~/Radicale/storage

USERNAME:PASSWORD

###Installing Apache

sudo apt-get install apache2 

sudo chmod a+rwx /var/www/html 

