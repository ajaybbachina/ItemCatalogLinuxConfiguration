# Project - Linux Server Configuration

## Submission Goal
You will take a baseline installation of a Linux distribution on a virtual machine and prepare it to host your web applications, to include installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

## Submission 

- IP Address : 13.127.171.160

- SSH Port : 2200

- Application URL : http://13.127.171.160.xip.io/

- Softwares Installed
    - Ubuntu 16.04 LTS
    - Python 3.6.9
    - Apache2
    - SQLAlchemy
    - Flask
    - Oauth2Client
    - psycopg2

## Step followed 

### Secure the Server

1. Update and upgrade packages
  - ```sudo apt-get update```
   
  - ```sudo apt-get upgrade```

   Remove unwanted packages
  - ```sudo apt-get autoremove```

2. Change SSH port from 22 to 2200
   - Run ```sudo nano /etc/ssh/sshd_config```
    
   - Port 2200

   - Restart SSH - ```/etc/init.d/ssh restart```

3. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port      123).
    

   - `sudo ufw default deny incoming`
   - `sudo ufw default allow outgoing`
   - `sudo ufw allow ssh`
   - `sudo ufw allow 2200/tcp`
   - `sudo ufw allow www`
   - `sudo ufw allow ntp`
   - `sudo ufw deny 22`

4.  New User Grader
   - Create new user grader
   - ```sudo adduser grader --disabled-password```

   - Grant sudo access to grader
    - Create sudoers file for grader
     - ```sudo touch /etc/sudoers.d/grader```

    - Add below text to the file
    -  ```grader ALL=(ALL:ALL) ALL```

5. Create key pair for grader
   - Run ```ssh-keygen on local machine```

   - Install Public Key
   - Login as grader and run following commands
   - ```mkdir .ssh```
   
   - ```touch .ssh/authorized_keys```
   - Add the contents of the .pub file which was generated locally with ssh-keygen command to authorized_keys
   - ```chmod 700 .ssh```
   
   - ```chown 644 .ssh/authorized_keys```

   - Disable password based login - Edit configuration file with below command
   - ```sudo nano /etc/ssh/sshd_config ```

   - Change PasswordAuthentication from yes to no
   - ```PasswordAuthentication no```

    - Restart ssh service
    - ```sudo service ssh restart```

6.  Cofigure local timezone to UTC
    - Run ```sudo nano /etc/timezone``` and update it to ```Etc/UTC```

7.  Install and Configure Apache2

    - Run sudo apt-get install apache2

    - Install mod_wsgi for Python3
    - ```sudo apt-get install libapache2-mod-wsgi-py3```
sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
    - Create configuration file for Virual host
    - Run below commands
    
    - ```sudo touch /etc/apache2/sites-available/itemcatalog.conf```
    - ```sudo nano /etc/apache2/sites-available/itemcatalog.conf```

    - Paste below 
    ```
    <VirtualHost *:80>
        ServerName 13.127.171.160
        ServerAlias 13.127.171.160.xip.io
        ServerAdmin admin@13.127.171.160
        WSGIDaemonProcess ItemCatalog
        WSGIProcessGroup ItemCatalog
        WSGIScriptAlias / /var/www/ItemCatalog/itemcatalog.wsgi 
        <Directory /var/www/ItemCatalog/>
            Order allow,deny
            Allow from all
        </Directory>
        Alias /static /var/www/ItemCatalog/static
        <Directory /var/www/ItemCatalog/static/>
            Order allow,deny
            Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    ```

    - Enable virtual host
    - ```sudo a2ensite itemcatalog```

    - Restart Apache
    - ```sudo apache2ctl restart```

    - Verify Apache Status
    - ```sudo systemctl status apache2```

8.  Install git
    - ```sudo apt-get install git```

    - TO ensure .git is not accessible via browser add the following somewhere in the config file.
    
        ```sudo nano /var/www/ItemCatalog/ItemCatalog/.htaccess```
    Put this code in the .htaccess file
        ```RewriteEngine On```
        ```RedirectMatch 404 /\.git```

    - Restart apache: 
    - `sudo service apache2 restart`

9. Clone the project code
    - `cd /var/www`
    - `mkdir ItemCatalog`

    - Clone project from github
    - `sudo git clone https://github.com/ajaybbachina/ItemCatalog.git`

10. Create .wsgi
    - `sudo touch /var/www/ItemCatalog/itemcatalog.wsgi`
    - `sudo nano /var/www/ItemCatalog/itemcatalog.wsgi`

       - Paste below 
        ```
        #!/usr/bin/python3
        import sys
        import logging
        logging.basicConfig(stream=sys.stderr)
        sys.path.insert(0,"/var/www/ItemCatalog/")
        sys.path.append('/var/www/ItemCatalog/ItemCatalog')

        from webServer import app as application
        application.secret_key = 'super_secret_key'

        ```

11. Install all the dependancies
    - `sudo apt-get install python3-flask`
    - `sudo apt-get install python3-sqlalchemy`
    - `sudo apt-get install python3-sqlalchemy_utils`
    - `sudo apt-get install python3-psycopg2`
    - `sudo apt-get install python3-oauth2client`
    - `sudo apt-get install python3-httplib2`
    - `sudo apt-get install python3-flask`

12. Make all the necessary changes for the code to work.
    - `sudo service apache2 restart`


13. Goto: http://13.127.171.160.xip.io/

## References
1. Udacity
2. Github.com 
3. StackOverflow.com
