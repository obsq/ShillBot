import json
import time
import os
import datetime
import random
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
from telethon.errors.rpcerrorlist import ChannelInvalidError, ChannelPrivateError, UserKickedError, SlowModeWaitError, ChatWriteForbiddenError, ChatAdminRequiredError
from telethon.errors import FloodWaitError, UserNotParticipantError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.types import InputPeerChannel
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

print("""
######   ##   ##   ##   ##   ##        #######   #########  ##########
#        ##   ##   ##   ##   ##        ##    ##  ##     ##      ##    
######   #######   ##   ##   ##   ###  ##  ####  ##     ##      ##    
     #   ##   ##   ##   ##   ##        ##    ##  ##     ##      ##    
######   ##   ##   ##   #### ####      ########  #########      ##    
""")


client_number = int(input("[$]Input number of clients: "))

file = open("api.cfg", "r").read() #Extracting APP_ID and API_HASH from api.cfg(if present)
cfg = file.split()
try:
    api_id = int(cfg[0])
    api_hash = cfg[1]
except IndexError: #If not present, getting APP_ID and API_HASH as input
    api_id = int(input("Enter your tg APP_ID: "))
    api_hash = input("Enter your tg API_HASH: ")
    file_write = open("api.cfg", "w").write(f"{str(api_id)} {api_hash}") #Storing it in api.cfg file

clients = []
with open("string_session.txt") as file: #Extracting sessions from string_session.txt file
    session_file = file.read()
sessions = session_file.splitlines()

#/python -m pip install --upgrade pip' command

print("\n[$]Getting proxies")
proxy_pool = json.load(open("proxies"))


def create_new_proxy_client(session:StringSession, id, hash):
    proxy = random.choice(proxy_pool)
    proxy = proxy.split(":")
    try:
        client = TelegramClient(session, id, hash, proxy=('socks4', proxy[0], int(proxy[1])), auto_reconnect=False)    
        asyncio.get_event_loop().run_until_complete(client.connect())
        return client
    except Exception as e:
        return create_new_proxy_client(session, id, hash)

for session in sessions: #Running clients with extracted sessions
    global client
    string = str(session)
    client = create_new_proxy_client(StringSession(string), api_id, api_hash)
    client.start()
    clients.append(client)

if len(clients) < client_number: #Taking clients as input
    for i in range(client_number - len(clients)):
        client = create_new_proxy_client(StringSession(), api_id, api_hash)
        client.start()
        clients.append(client)
        str_session = client.session.save()
        with open("string_session.txt", "a") as f:
            f.writelines(f"{str_session}\n")
            f.close()

print("\n[$]Getting groups from `groups.txt`")
time.sleep(1)
with open("groups.txt", "r") as file: #Fetching groups from groups.txt
    raw_groups = file.readlines()
group_list = []
for groups in raw_groups:
    for group in groups.split(" "):
        group_list.append(group)

group_username = input("\n[$]Enter username of the public group whos lastest message is to be shilled: ") #Username/link of the public group
