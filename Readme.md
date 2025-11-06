# WEB SERVER SETUP INSTRUCTIONS IN A UBUNTU MACHINE

## Clone the repository

```
git clone https://github.com/kushall1845/Vcube_App.git
```

## Change directory to Vcube_App

```
cd Vcube_App
```

## Change directory to web_server

```
cd web_server
```

## Make sure you have python3-full and pip installed

```
sudo apt update
sudo apt install python3-full -y
sudo apt install python3-pip -y
```

## Create a virtual environment

```
python3 -m venv venv
```

## Activate the virtual environment

```
source venv/bin/activate
```

## Install your requirements

```
pip install -r requirements.txt
```

## Run the app in background

```
nohup python3 app.py > app.log 2>&1 &
```

## Access the application

Open your browser and visit:

```
http://<public_IP_ec2>:5000
```
