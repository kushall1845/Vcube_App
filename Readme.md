# Docker Installation and Application Deployment Guide

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
sudo su
```
```
docker --version
```

## 4. Check for Docker Compose
```
docker compose version
```


If the above command doesn’t work, follow the next steps to enable Docker’s official repository and install Docker Compose.

## 5. Enable Docker’s Official Repository (if not already)
```
sudo apt update
sudo apt install ca-certificates curl gnupg -y
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
```

## 6. Install Docker Compose Plugin (v2)
```
sudo apt install docker-compose-plugin -y
```

## 7. Verify Docker Compose Installation
```
docker compose version
```

## 8. Clone the Git Repository (docker branch)
```
git clone -b docker https://github.com/kushall1845/Vcube_App.git
```

## 9. Change Directory to the Project Folder
```
cd Vcube_App
```
### You can keep database data in `/home/ubuntu/db_data` for persistence.

```
mkdir db_data

```

## 10. Start Your Docker Stack
```
docker compose up -d --build
```

## 11. Confirm Everything is Running
```
docker ps
```

---

## 12. To view data in the db container

```
docker exec -it mysql_db mysql -u appuser -p
```
it askd for password 
```
app123
```


```
USE appdb;
```

```
SELECT * FROM user;
```

to exit 
```
exit
```


---


## 13. To clean everything

```
docker compose down 
```