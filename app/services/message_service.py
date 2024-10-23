from fastapi import WebSocket, Depends, WebSocketDisconnect
from typing import Dict, Set, Union, List
from ..models.collections import Collections
from ..db.session import MongoDBClient, get_mongo_client
from ..services.group_service import GroupService
from ..utils.decorators import singleton
from collections import defaultdict
from uuid import uuid4
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from icecream import ic
ic.configureOutput(includeContext=True)

@singleton
class MessageService:
    def __init__(self, mongo_client: MongoDBClient) -> None:
        self.connection_pool: Dict[str, List[WebSocket]] = defaultdict(list)
        self.mongo_client = mongo_client
        self.messages_collection = self.mongo_client.get_collection(collectionName=Collections.MESSAGES)


    def prepare_final_message(self, message_doc: dict, sender_email: str) -> dict:
        message_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        message_doc.update({
            "id": message_id,
            "timestamp": timestamp,
            "sender_email": sender_email
        })

        return message_doc

    def handle_connection_disconnection(self, email: str, connection: WebSocket) -> None: 
        if connection in self.connection_pool.get(email, []):
            self.connection_pool[email].remove(connection)
            print(f"{connection=} removed for {email=}")

        # # If the list is now empty, delete the email key from the pool.
        # if not self.connection_pool[email]:
        #     del self.connection_pool[email]



    async def broadcast_message(self, data: dict, member_emails: List[str]):
        '''
            NOTE - the for loop below can be optimized further to broadcast messages using group tasks or gather
            get emails of group members 
            from emails get the websockets connections 
            broadcast message to these connections
        '''

        for receiver_email, connections in self.connection_pool.items(): 
            if receiver_email not in member_emails: 
                continue
            for connection in connections: 
                try:
                    await connection.send_json(data) 
                    print(f"sent to {connection=}")
                except WebSocketDisconnect: 
                    # remove connection to which there was failure `in message sending
                    # should log this failure
                    self.handle_connection_disconnection(email=receiver_email, connection=connection)
                except Exception as e: 
                    ic(f"Exception occured {e.args}")
                    ic(data)
                    return

    async def save_message_doc(self, message_doc: dict):  
        await self.messages_collection.insert_one(document=message_doc)
        if "_id" in message_doc:
            message_doc["_id"] = str(message_doc["_id"])

           
    async def handle_websocket_connection(self, websocket: WebSocket, user_info: dict, group_service: GroupService): 
        '''
        after the connction is accepted, fetch the headers. Headers must have a jwt, figure out the user email decoding this jwt. 
        group id will sent in message payload
        use group id to figure the group members
        iterate on all the group members, user their email to get the websocket connection from connection pool
        store the message in db 
        broadcast the message to all the clients 


        #NOTE - user could login from multiple devices, one way we can handle this to close the other websocket connection 
        when a user logs out we must remove the any active connection

        after the client closes the connection from its end check whether the connection is removed from the connection pool or not 
        '''
        
        await websocket.accept()
        
        ic(user_info, "connected")
        
        user_email = user_info["email"]
        self.connection_pool[user_email].append(websocket)


        while True:
            try:
                data: Dict[str, str] = await websocket.receive_json()
            except WebSocketDisconnect:
                    # remove connection to which there was failure in message sending
                    # should log this failure event
                    self.handle_connection_disconnection(email=user_email, connection=websocket)
                    return
            
            message_doc = self.prepare_final_message(message_doc=data, sender_email=user_email)

            try: 
                await self.save_message_doc(message_doc=message_doc)
            except PyMongoError as e:
                # should log this failure event
                # should send a message to client, asking for a retry.
                continue

            group_id = data.get("group_id")
            ic(group_id)
            group_members = await group_service.get_group_members(group_id=group_id)
            member_emails = [member["user_email"] for member in group_members]

            await self.broadcast_message(data=message_doc, member_emails=member_emails)
            print("returned after exception")

def get_message_service(mongo_client: MongoDBClient = Depends(get_mongo_client)) -> MessageService:
    return MessageService(mongo_client=mongo_client)