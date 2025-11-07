
---

# VCUBE APP — 3-TIER DEPLOYMENT (WEB SERVER + APP SERVER + MYSQL DB SERVER)

---

# OVERVIEW

```
+--------------------+         +--------------------+         +--------------------+
|    Web Server      |  --->   |    App Server      |  --->   |    DB Server       |
|  (Flask Frontend)  |         | (Flask + SQLAlchemy|         |    (MySQL DB)      |
|  Port: 5000        |         |  + JWT Auth)       |         |  Port: 3306        |
+--------------------+         +--------------------+         +--------------------+
```

---

# STEP 1: DATABASE SERVER SETUP (MySQL 8+)

## 1. Install MySQL

```
sudo apt update
sudo apt install mysql-server -y
sudo systemctl enable mysql
sudo systemctl start mysql
```

## 2. Secure MySQL 

```
sudo mysql_secure_installation
```


VALIDATE PASSWORD COMPONENT can be used to test passwords
and improve security. It checks the strength of password
and allows the users to set only those passwords which are
secure enough. Would you like to setup VALIDATE PASSWORD component?

Press y|Y for Yes, any other key for No: n



Remove anonymous users? (Press y|Y for Yes, any other key for No) : y
Success.


Disallow root login remotely? (Press y|Y for Yes, any other key for No) : y
Success.

.
Remove test database and access to it? (Press y|Y for Yes, any other key for No) : y
 

Reload privilege tables now? (Press y|Y for Yes, any other key for No) : y
Success.

All done!

If it doesn’t ask for a root password — that’s fine (Ubuntu uses auth_socket authentication).

## 3. Log into MySQL as root

```
sudo mysql
```

## 4. Create application database and user

Inside MySQL shell:

```
CREATE DATABASE appdb;
CREATE USER 'appuser'@'%' IDENTIFIED WITH mysql_native_password BY 'app123';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'%';
FLUSH PRIVILEGES;
EXIT;
```

## 5. Enable remote connections

```
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
```

Find this line:

```
bind-address = 127.0.0.1
```

Change it to:

```
bind-address = 0.0.0.0
```

Then restart MySQL:

```
sudo systemctl restart mysql
```

## 6. Verify user and plugin

```
sudo mysql
```

```
SELECT user, host, plugin FROM mysql.user;
```

You should see:

```
| appuser | % | mysql_native_password |
```

That means Flask’s mysqlclient driver can connect successfully.

---

# STEP 2: APP SERVER SETUP (Flask Backend)

## 1. Install Python and build dependencies

```
sudo apt update
sudo apt install python3-full python3-pip pkg-config python3-dev default-libmysqlclient-dev build-essential -y
```

## 2. Clone repository and move to app_server folder

```
git clone https://github.com/kushall1845/Vcube_App.git
cd Vcube_App/app_server
```

## 3. Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

## 4. Install dependencies including mysqlclient

```
pip install -r requirements.txt
pip install mysqlclient
```

To verify installation:

```
pip show mysqlclient
```

## 5. Set environment variables

```
export DATABASE_URL="mysql://appuser:app123@<DB_SERVER_PRIVATE_IP>/appdb"
export SECRET_KEY="supersecretkey"
export APP_HOST="0.0.0.0"
export APP_PORT=5001
```

(Replace <DB_SERVER_PRIVATE_IP> with your MySQL instance’s private IP)

## 6. Initialize database tables

```
python3
```
```
from app import app, db
with app.app_context():
    db.create_all()
```
double click on enter after pasting 

To exit 

```
exit()
```

If no error, tables are created in appdb.

You can verify on DB server:

```
sudo mysql
```

```
USE appdb;

```
```
SHOW TABLES;
```

Should show:

```
| user |
```

## 7. Run app in background (APP SERVER)

```
nohup python3 app.py > app_server.log 2>&1 &
```

---

# STEP 3: WEB SERVER SETUP (Frontend + Proxy)

## 1. Install Python

```
sudo apt update
sudo apt install python3-full python3-pip -y
```

## 2. Clone repository and move to web_server folder

```
git clone https://github.com/kushall1845/Vcube_App.git
cd Vcube_App/web_server
```

## 3. Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

## 4. Install dependencies

```
pip install -r requirements.txt
```

## 5. Set environment variables

```
export APP_INTERNAL="http://<APP_SERVER_PRIVATE_IP>:5001"
export WEB_HOST="0.0.0.0"
export WEB_PORT=5000
```

## 6. Allow port and run frontend in background

```
nohup python3 app.py > web_server.log 2>&1 &
```

---

# STEP 4: ACCESS THE APPLICATION

Open your browser and visit:

```
http://<PUBLIC_IP_OF_WEB_SERVER>:5000
```

The Web Server proxies API requests to:

```
http://<APP_SERVER_PRIVATE_IP>:5001
```

which connects to:

```
<DB_SERVER_PRIVATE_IP>:3306
```

---

# STEP 5: VERIFY CONNECTIVITY

## From App Server → DB Server

```
mysql -h <DB_SERVER_PRIVATE_IP> -u appuser -p
```

## From Web Server → App Server

```
curl http://<APP_SERVER_PRIVATE_IP>:5001/api/health
```

Expected:

```
{"status": "ok"}
```

## From Browser → Web Server

```
http://<PUBLIC_IP_WEB_SERVER>:5000
```

You should see the VCube App interface.

---

# RESULT SCREENSHOT

![Result Screenshot](https://github.com/kushall1845/Vcube_App/blob/master/web_server/result.png?raw=true)


NOTE

Make sure the following ports are accessible in your AWS Security Groups or Firewall settings:

Port 5000 → Web Server (Frontend)

Port 5001 → App Server (Flask Backend)

Port 3306 → DB Server (MySQL)

Port 22 → SSH (for remote access to all servers)

These ports must be open for communication between respective servers.

---

# SUMMARY OF IP FLOW

| Component  | Example Private/Public IP | Port | Description               |
| ---------- | ------------------------- | ---- | ------------------------- |
| Web Server | <public_ip_web>           | 5000 | User interface (frontend) |
| App Server | <private_ip_app>          | 5001 | Flask API + JWT + Logic   |
| DB Server  | <private_ip_db>           | 3306 | MySQL database            |

---
