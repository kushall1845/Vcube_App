# Application Deployment in docker (without a compose file)

## 1. Update the Machine
```
sudo apt update
```

## 2. Install Docker
```
sudo apt install docker.io -y
```

## 3. Check Docker Version
```
docker --version
```

## 4. Clone the Git Repository (docker branch)
```
git clone -b docker https://github.com/kushall1845/Vcube_App.git
```

## 5. Change Directory to the Project Folder
```
cd Vcube_App
```

## 6. Build front end (web server) image
```
docker build -t web_server ./web_server/
```

## 7. Build back end (app server) image
```
docker build -t app_server ./app_server
```

## 8. Create a Docker Network

All three containers (DB, backend, frontend) must be able to talk to each other.

```bash
docker network create vcube_network
```

## 9. DATABASE CONTAINER (MySQL)

You can keep database data in `/home/ubuntu/db_data` for persistence.

```
cd ..
```
```
mkdir -p /home/ubuntu/db_data
cd /home/ubuntu
```

Run the MySQL container:

```
docker run -d \
  --name mysql_db \
  --network vcube_network \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=appdb \
  -e MYSQL_USER=appuser \
  -e MYSQL_PASSWORD=app123 \
  -p 3306:3306 \
  -v $(pwd)/db_data:/var/lib/mysql \
  mysql:8.0
```

Verify:

```
docker ps
docker logs -f mysql_db
```

## 10. BACKEND (App Server)

Move into your backend folder:

```
cd /home/ubuntu/app_server
```



### Create `.env` file

```
vim .env
```

Paste this:

```bash
DATABASE_URL=mysql://appuser:app123@mysql_db/appdb
SECRET_KEY=supersecretkey
APP_HOST=0.0.0.0
APP_PORT=5001
```

### Build backend image

```bash
docker build -t app_server:latest .
```



### Run backend container (mount working dir)

```bash
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  app_server:latest
```

✅ Verify backend is up:

```bash
docker ps
docker logs -f app_server
```

You should see something like:

```
* Running on http://0.0.0.0:5001
```

## 11. FRONTEND (Web Server)

Move into your frontend folder:

```bash
cd /home/ubuntu/web_server
```

### Create `.env` file

```bash
vim .env
```

Paste this:

```bash
APP_INTERNAL=http://app_server:5001
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

### Run frontend container (mount working dir)

```bash
docker run -d \
  --name web_server \
  --network vcube_network \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd):/app \
  web_server:latest
```

✅ Check logs:

```bash
docker logs -f web_server
```

---

## 12. VERIFY END-TO-END CONNECTIVITY

### Check all containers

```bash
docker ps
```

Expected:

```
CONTAINER ID   IMAGE             PORTS                    NAMES
xxxxxx         web_server:latest 0.0.0.0:5000->5000/tcp   web_server
xxxxxx         app_server:latest 0.0.0.0:5001->5001/tcp   app_server
xxxxxx         mysql:8.0         0.0.0.0:3306->3306/tcp   mysql_db
```

---

### Check internal communication

```bash
# From app server to DB
docker exec -it app_server ping mysql_db

# From web server to backend
docker exec -it web_server curl http://app_server:5001/health
```

If you get valid responses → ✅ all good.

---

## 13. ACCESS IN BROWSER

Use your server’s public IP:

| Tier     | URL                                   | Description                 |
| -------- | ------------------------------------- | --------------------------- |
| Frontend | `http://<your-public-ip>:5000`        | Flask Web UI                |
| Backend  | `http://<your-public-ip>:5001/health` | Flask API                   |
| Database | Port `3306`                           | MySQL accessible via client |

> Make sure ports **5000, 5001, and 3306** are open in your cloud provider’s inbound security rules.

---

## 14. STOP / CLEANUP (if needed)

```bash
docker stop web_server app_server mysql_db
docker rm web_server app_server mysql_db
```

---

## ✅ FINAL STRUCTURE UNDER `/home/ubuntu`

```
/home/ubuntu/
 ├── db_data/
 ├── app_server/
 │   ├── Dockerfile
 │   ├── requirements.txt
 │   ├── app.py
 │   └── .env
 └── web_server/
     ├── Dockerfile
     ├── requirements.txt
     ├── app.py
     └── .env
```

| Tier     | Container    | Port | Network       | Mounted Directory         |
| -------- | ------------ | ---- | ------------- | ------------------------- |
| Database | `mysql_db`   | 3306 | vcube_network | `/home/ubuntu/db_data`    |
| Backend  | `app_server` | 5001 | vcube_network | `/home/ubuntu/app_server` |
| Frontend | `web_server` | 5000 | vcube_network | `/home/ubuntu/web_server` |

---





















