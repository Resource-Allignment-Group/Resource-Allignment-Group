# EquipmentInventory

An inventory, tracking, and reservation system for the Maine Agricultural and Forest Experiment Station (MAFES).

# Starting The App

Clone the repository using '''git clone https://github.com/Resource-Allignment-Group/Resource-Allignment-Group.git'''

## Getting the backend set up

1. Create a virtual enviorment by running '''py -m venv venv'''
2. Enter the virtual enviorment by running '''.\venv\Scripts\activate'''
3. Install packages by typing '''py -m pip install -r reqiuirements.txt'''
4. Start the backend server by running '''cd .\backend''' and then '''py .\main.py'''

## Gettting React set up

1. Open a new terminal and run '''cd .\frontend''' and then '''npm install''' to get dependencies
2. Then run '''npm start''' to start up the development server


## container

on local:
- docker-compose build --no-cache
- docker-compose up
- docker commit <container_id_or_name> <new_image_name>:<tag>
- docker save -o flask:prod.tar flask:prod
in terminal
- scp Desktop\Programming\Resource-Allignment-Group\.tmp-flask_rag.tar651468999 opc@158.101.111.115:/home/opc/
- ssh 
-


etc:
- docker build -f frontend/Dockerfile.prod -t rag-frontend:prod frontend
- docker rm -f react_app
- docker run -d --name react_app -p 3000:80 rag-frontend:prod