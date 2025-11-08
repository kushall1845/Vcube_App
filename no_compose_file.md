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
























## 🧱 STEP 1 — Create a Docker Network

All three containers (DB, backend, frontend) must be able to talk to each other.

```bash
docker network create vcube_network
```

---

## 🗄️ STEP 2 — DATABASE CONTAINER (MySQL)

You can keep database data in `/home/ubuntu/db_data` for persistence.

```bash
mkdir -p /home/ubuntu/db_data
cd /home/ubuntu
```

Run the MySQL container:

```bash
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

✅ Verify:

```bash
docker ps
docker logs -f mysql_db
```

---

## ⚙️ STEP 3 — BACKEND (App Server)

Move into your backend folder:

```bash
cd /home/ubuntu/app_server
```

---

### 🧾 Create `.env` file

```bash
nano .env
```

Paste this:

```bash
DATABASE_URL=mysql://appuser:app123@mysql_db/appdb
SECRET_KEY=supersecretkey
APP_HOST=0.0.0.0
APP_PORT=5001
```

---

### 🐳 Create `Dockerfile` in `/home/ubuntu/app_server`

```bash
vim Dockerfile
```

Paste:

```dockerfile
# Dockerfile for App Server (Backend)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir mysqlclient && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]
```

---

### 🧱 Build backend image

```bash
docker build -t app_server:latest .
```

---

### 🚀 Run backend container (mount working dir)

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

---

## 🌐 STEP 4 — FRONTEND (Web Server)

Move into your frontend folder:

```bash
cd /home/ubuntu/web_server
```

---

### 🧾 Create `.env` file

```bash
vim .env
```

Paste this:

```bash
APP_INTERNAL=http://app_server:5001
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

---

### 🐳 Create `Dockerfile` in `/home/ubuntu/web_server`

```bash
nano Dockerfile
```

Paste:

```dockerfile
# Dockerfile for Web Server (Frontend)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
```

---

### 🧱 Build frontend image

```bash
docker build -t web_server:latest .
```

---

### 🚀 Run frontend container (mount working dir)

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

## 🧠 STEP 5 — VERIFY END-TO-END CONNECTIVITY

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

## 🌍 STEP 6 — ACCESS IN BROWSER

Use your server’s public IP:

| Tier     | URL                                   | Description                 |
| -------- | ------------------------------------- | --------------------------- |
| Frontend | `http://<your-public-ip>:5000`        | Flask Web UI                |
| Backend  | `http://<your-public-ip>:5001/health` | Flask API                   |
| Database | Port `3306`                           | MySQL accessible via client |

> Make sure ports **5000, 5001, and 3306** are open in your cloud provider’s inbound security rules.

---

## 🧹 STEP 7 — STOP / CLEANUP (if needed)

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

Would you like me to now extend this same setup using **named Docker volumes** (so `/home/ubuntu` mounts aren’t used and Docker manages persistent data instead)?
That would be your next step toward a more production-ready setup.


















Excellent question, Kushal 👏 — this shows you’re thinking like a real DevOps engineer.

You’re absolutely right:
If you’ve created a **`.env` file** inside your folders (like `/home/ubuntu/web_server/.env` and `/home/ubuntu/app_server/.env`), you still need to **make the container read those variables** somehow.

There are **3 valid ways** to do this in Docker — and since you specifically said you’re mounting your working directory (`-v $(pwd):/app`), we’ll use that approach first, then I’ll show 2 alternatives.

---

## 🧩 OPTION 1 — App Automatically Reads `.env` (Recommended)

### ✅ Works If:

Your Flask code uses something like this near the top of `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()  # This loads variables from .env in current directory
```

If that’s already there, you’re **done**.

Why? Because you’re mounting your folder (`-v $(pwd):/app`) directly into the container, which means:

* `/home/ubuntu/app_server/.env` (host) → `/app/.env` (container)
* Flask automatically reads those env vars using `load_dotenv()`

So the container already “sees” your `.env` file, and no extra flag is needed.

✅ Example:

```bash
cd /home/ubuntu/app_server
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  -v $(pwd):/app \
  app_server:latest
```

That’s enough — because `/app/.env` is mounted and Flask reads it automatically.

👉 **So this works if your code uses `python-dotenv`.**

---

## 🧩 OPTION 2 — Explicitly Pass `.env` Using `--env-file`

If your Flask app doesn’t use `load_dotenv()` (or you want Docker to inject env vars instead of the app reading `.env`),
you can use the `--env-file` flag during container creation.

✅ Example (Backend):

```bash
cd /home/ubuntu/app_server
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  app_server:latest
```

✅ Example (Frontend):

```bash
cd /home/ubuntu/web_server
docker run -d \
  --name web_server \
  --network vcube_network \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd):/app \
  web_server:latest
```

Now Docker reads your `.env` file and injects the variables into the container’s environment,
even if your Python app doesn’t use `load_dotenv()`.

---

## 🧩 OPTION 3 — Pass Each Env Variable Manually Using `-e`

This is less convenient but works in all cases.

✅ Example (Backend):

```bash
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  -e DATABASE_URL="mysql://appuser:app123@mysql_db/appdb" \
  -e SECRET_KEY="supersecretkey" \
  -e APP_HOST="0.0.0.0" \
  -e APP_PORT="5001" \
  -v $(pwd):/app \
  app_server:latest
```

✅ Example (Frontend):

```bash
docker run -d \
  --name web_server \
  --network vcube_network \
  -p 5000:5000 \
  -e APP_INTERNAL="http://app_server:5001" \
  -e WEB_HOST="0.0.0.0" \
  -e WEB_PORT="5000" \
  -v $(pwd):/app \
  web_server:latest
```

---

## 🔍 How to Verify Inside the Container

Once the container is running, you can confirm your variables are visible:

```bash
docker exec -it app_server env | grep DATABASE_URL
```

or for frontend:

```bash
docker exec -it web_server env | grep APP_INTERNAL
```

You should see the variables you passed or loaded from `.env`.

---

## 🧠 Summary Table

| Method                            | When to Use                                 | Command               |
| --------------------------------- | ------------------------------------------- | --------------------- |
| **Auto-load via `python-dotenv`** | App already uses `.env` and `load_dotenv()` | `-v $(pwd):/app` only |
| **Docker injects vars**           | You want Docker to manage env vars          | `--env-file .env`     |
| **Manual env flags**              | For debugging or simple test runs           | `-e VAR=value`        |

---

### ✅ Recommended for You (based on your setup)

Since you said:

> “I want to pass environment variables through volume or by mapping the working directory of the docker host”

👉 The **best approach** is **Option 1**:

* Keep `.env` inside `/home/ubuntu/app_server` and `/home/ubuntu/web_server`
* Mount working directory with `-v $(pwd):/app`
* Make sure your Flask apps include:

  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

That’s clean, easy, and perfectly fits your workflow.

---

Would you like me to quickly show where exactly to add the `load_dotenv()` lines in your Flask app (both backend and frontend) so it auto-picks `.env` values?



































Excellent follow-up, Kushal 👏 — you’re thinking in the **right DevOps direction**.

Let’s go step-by-step because what you’re asking is **a subtle but advanced Docker concept**:
You want to **mount** your working directory (via `-v $(pwd):/app`)
👉 and still make your **container use the `.env` file** inside that mounted directory
👉 **without modifying your Python code** (i.e., no `load_dotenv()`).

That’s totally possible ✅ — we’ll do it using **Docker features only**, no code change needed.

---

# 🎯 GOAL

You want:

* `.env` file located inside your mounted folder (e.g. `/home/ubuntu/app_server/.env`)
* Container to read that `.env` file automatically as environment variables
* No modification in `app.py`

---

# 🧩 HOW DOCKER TREATS ENV FILES

Docker itself doesn’t automatically load `.env` files *from mounted volumes* unless you tell it to.
However, you can instruct it to do so using the `--env-file` flag during `docker run`.

So — even though you’re mounting your folder (via volume) —
you can **still use the `.env` file from that same folder** as the `--env-file`.

---

# ✅ EXAMPLE SETUP (Your Case)

Let’s assume you are in `/home/ubuntu/app_server`
and it already contains:

```
app.py
requirements.txt
.env
Dockerfile
```

---

## 🧱 Step 1 — Build the Docker image

(only once)

```bash
cd /home/ubuntu/app_server
docker build -t app_server:latest .
```

---

## 🧩 Step 2 — Run container using **mounted working directory** + `.env` file

```bash
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  app_server:latest
```

✅ Explanation:

* `--env-file .env` → tells Docker to read `.env` from your current directory (on host)
* `-v $(pwd):/app` → mounts your current directory inside container (so code updates are live)
* You **didn’t change app.py**, but Flask still gets `os.environ` variables injected by Docker

Now inside the container, `os.getenv("DATABASE_URL")` will return the value from your `.env`.

---

## 🧩 Step 3 — Same for Frontend (Web Server)

```bash
cd /home/ubuntu/web_server
docker build -t web_server:latest .

docker run -d \
  --name web_server \
  --network vcube_network \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd):/app \
  web_server:latest
```

✅ This will:

* Mount your `/home/ubuntu/web_server` folder
* Load all variables from `.env`
* Make them available in Flask automatically via `os.environ`

---

# 🧠 VERIFY INSIDE CONTAINERS

### For backend:

```bash
docker exec -it app_server env | grep DATABASE_URL
```

You should see:

```
DATABASE_URL=mysql://appuser:app123@mysql_db/appdb
```

### For frontend:

```bash
docker exec -it web_server env | grep APP_INTERNAL
```

You should see:

```
APP_INTERNAL=http://app_server:5001
```

That confirms the `.env` variables are injected successfully, even without `load_dotenv()`.

---

# ✅ Final Summary

| Task                            | Command / Concept                 | Purpose                                |
| ------------------------------- | --------------------------------- | -------------------------------------- |
| Mount host working dir          | `-v $(pwd):/app`                  | Use live source code from host         |
| Load `.env` without code change | `--env-file .env`                 | Docker injects vars into container env |
| Verify vars inside              | `docker exec -it <container> env` | Check they’re available                |
| Network communication           | `--network vcube_network`         | Links DB ↔ Backend ↔ Frontend          |

---

# 💡 Recommended Run Commands for You

### Database:

```bash
cd /home/ubuntu
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

### Backend:

```bash
cd /home/ubuntu/app_server
docker run -d \
  --name app_server \
  --network vcube_network \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  app_server:latest
```

### Frontend:

```bash
cd /home/ubuntu/web_server
docker run -d \
  --name web_server \
  --network vcube_network \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd):/app \
  web_server:latest
```

---

✅ **Result:**

* No code change in your Flask apps
* `.env` files are still host-controlled
* Containers get all required environment variables
* Live code sync works via `-v $(pwd):/app`

---

Would you like me to show you how to **persist these run commands using a simple Bash script** (so you can start all 3 containers automatically with one command)?
