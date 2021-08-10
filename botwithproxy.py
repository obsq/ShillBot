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
######   ##    ##   ##   ##         ##                #######     #########   ##########
#        ##    ##   ##   ##         ##                ##    ##    ##     ##       ## 
######   ########   ##   ##         ##         ###    ######      ##     ##       ##
     #   ##    ##   ##   ##         ##                ##    ##    ##     ##       ##
######   ##    ##   ##   ########   ########          #######     #########       ##
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
proxy_pool = json.load(open("proxies.txt"))
ip = None
port = None


def rotate_proxy():
 global client, ip, port
 proxy = random.choice(proxy_pool)
 proxy = proxy.split(":")
 client = TelegramClient(StringSession(string), api_id, api_hash, proxy=('socks4', proxy[0], int(proxy[1])), auto_reconnect=False)
 ip = str(proxy[0])
 port = int(proxy[1])


async def rotate_proxy_endpoint():
    try:
      rotate_proxy()
      await client.connect()
      print("got")
    except Exception as e:
      print("REROTATING")
      rotate_proxy_endpoint()

for session in sessions: #Running clients with extracted sessions
    global client
    string = str(session)
    rotate_proxy_endpoint()
    client = TelegramClient(StringSession(string), api_id, api_hash, proxy=('socks4', ip, port))
    client.start()
    clients.append(client)

if len(clients) < client_number: #Taking clients as input
    for i in range(client_number - len(clients)):
        client = TelegramClient(StringSession(), api_id, api_hash, proxy=("socks4", "1.10.140.43", 4145))
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

async def bot():
    iid = await clients[0].get_messages(group_username, 1) #Getting message_id of the latest message in the public group
    id = iid[0].id
    shill_message = await clients[0].get_messages(group_username, ids=int(id))
    print(f"\n[$]Shilling the latest message in `{group_username}` with id {id}")
    print(f"--->Message: {shill_message.message}")
    await asyncio.sleep(random.randint(5, 10))

    print("\n[$]Verifying groups")
    for group in group_list: #Verifying groups. Removes invalid groups
        try:
            await clients[0].get_entity(group)
            await asyncio.sleep(random.randint(2, 5))
            pass
        except Exception as e:
            print(str(e))
            group_list.remove(group)
            continue
    group_count = len(group_list)
    client_count = len(clients)
    usable = group_count//client_count

    print("\n[$]Joining groups")
    present_client = 0
    for grp in group_list:
        name = (await clients[present_client].get_me()).first_name
        print(f"--->Joining {grp} from account {name}")
        await asyncio.sleep(1)
        try:
            await clients[present_client](
                GetParticipantRequest(channel=grp, participant=(await clients[present_client].get_me()).id)) #Checking whether client is already a participant
            present_client += 1
            await asyncio.sleep(random.randint(1, 3))
        except UserNotParticipantError:
            try:
                await clients[present_client](JoinChannelRequest(channel=grp)) #Joining groups
                present_client += 1
                print("\n")
                await asyncio.sleep(random.randint(5, 15))
            except FloodWaitError as e:
                print(f"--->LastError: {str(e)}\n")
                await asyncio.sleep(e.seconds) #Sleeping for flood time
                await asyncio.sleep(5)
                try:
                    await clients[present_client](JoinChannelRequest(channel=grp))
                    present_client += 1
                    await asyncio.sleep(random.randint(9, 15))
                except Exception as e: #If Exception, removes that group
                    print(f"--->LastError: {str(e)}\n")
                    group_list.remove(grp)
            except ChannelInvalidError as e:
                print(f"--->LastError: {str(e)}\n")
                group_list.remove(grp)
            except Exception as e:
                print(f"--->LastError: {str(e)}\n")
                group_list.remove(grp)
        except ChannelInvalidError as e:
            print(f"--->LastError: {str(e)}\n")
            group_list.remove(grp)
        except Exception as e:
            print(f"--->LastError: {str(e)}\n")
            group_list.remove(grp)
        present_client = present_client % client_count

    print("\n[$]Getting group entities")
    group_entities = []
    cn = 0
    for group in group_list:
        group_entity = await clients[cn].get_input_entity(group) #Getting verified joined groups' entities
        group_entities.append(group_entity)
        cn = cn + 1
        cn = cn % client_count
        await asyncio.sleep(1)

    await asyncio.sleep(random.randint(10, 20))
    print("\n[$]Starting to shill\n")
    group_number = 0
    interval = 60 #int(input("[$]Enter interval (in seconds): "))
    shill_client_number = 0
    e = None
    while True:
        for entity in group_entities:
            name = (await clients[shill_client_number].get_me()).first_name #Getting clients first name
            print(f"--->Shilling in {group_list[group_number]} using account {name}")
            await asyncio.sleep(1)
            try:
                await clients[shill_client_number].send_message(entity, shill_message) #Sending message
                print(f"---->Shilled at {datetime.datetime.now()}")

            except SlowModeWaitError as e:
                print(f"--->LastError: {str(e)}")
            except ChatWriteForbiddenError as e:
                print(f"--->LastError: {str(e)}")
            except ChatAdminRequiredError as e:
                print(f"--->LastError: {str(e)}")
            except FloodWaitError as e:
                print(f"--->LastError: {str(e)}")
            except Exception as e:
                print(f"--->LastError: {str(e)}")

            shill_client_number += 1
            shill_client_number = shill_client_number % client_count
            group_number += 1
            group_number = group_number % group_count
            print("\n\n")
            await asyncio.sleep(1)

        shill_client_number = 0
        print("------------------------------------------------------------------------------------\n\n")
        await asyncio.sleep(interval) #Sleeping for interval

asyncio.get_event_loop().run_until_complete(bot())
