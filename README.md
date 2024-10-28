# Chat-Application
Code base for a chat app, developed using python, fastapi, websockets, and mongodb.

Steps to run this application. 


1. Create a .env file in root directory. The file should have the following variables -
    JWT_SECRET='{your generated secret}'
    JWT_ALGORITHM=HS256
    MONGO_HOST=mongodb://mongodb:27017
    MONGO_DB_NAME='{name of database to use}'

    note - you can adjust the value of MONGO_HOST as the per configuration defined in the docker-compose.yml file 

2. Install Docker engine, if not already present.

3. To build the image and run the container use the following command -
    docker-compose up --build 

If you wish to run this application without docker. 

1. Do Step 1 from above.

2. Ensure that python 3.12 or higher is installed. 

3. Create and activate your virtual env. 

4. Install dependecies, use command -
    pip install -r requirements.txt

5. Ensure MongoDB is running on the specified host.


6. Run uvicorn server using command - 
    uvicorn app.main:app 

