import asyncio
from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest, InviteToChannelRequest
from telethon.errors.rpcerrorlist import FloodWaitError, PeerFloodError, UserDeactivatedBanError
from telethon.sessions import StringSession
import random
import time
import json
import os
from pathlib import Path
import  logging
logging.basicConfig(level= "DEBUG")

print("""
#######     ####    ####     #######  #######     ####    ####    ####      ######    ########  ##########
##     ##   ## ##  ## ##     #        ##    ##   ##  ##   ##  ## ## ##      ##    ##  ##    ##      ##
##     ##   ##   ##   ##     #######  #######   ########  ##   ##   ##      #######   ##    ##      ##
##     ##   ##        ##           #  ##        ##    ##  ##        ##      ##    ##  ##    ##      ##
#######     ##        ##     #######  ##        ##    ##  ##        ##      #######   ########      ##
""")



filter0 = ["UserStatusOffline", "UserStatusOnline", "UserStatusRecently", "UserStatusLastWeek", "UserStatusLastMonth", "UserStatusEmpty", "None"]
filter1 = ["UserStatusOffline", "UserStatusOnline", "UserStatusRecently", "UserStatusLastWeek", "UserStatusLastMonth", "UserStatusEmpty"]
filter2 = ["UserStatusOffline", "UserStatusOnline", "UserStatusRecently"]
filter3 = ["UserStatusOnline"]
filter4 = ["None"]


f2 = open("api.cfg", "r").read() #APP_ID API_HASH
cfg = f2.split()
try:
    api_id = int(cfg[0])
    api_hash = str(cfg[1])
except IndexError:
    api_id = int(input("\n[$]Input your tg APP_ID: "))
    api_hash = str(input("[$]Input your tg API_HASH: "))
    file_write = open("api.cfg", "w").write(f"{str(api_id)} {api_hash}")


with open("usernames.txt", "r+") as file:
    reading = file.read()
usernames = reading.splitlines()

client_number = int(input("\n[$]Enter number of clients: "))

clients = []
with open("string_session.txt") as file:
    session_file = file.read()
sessions = session_file.splitlines()

print("\n[$]Getting proxies")
proxy_pool = json.load(open("proxies.txt"))


def create_new_proxy_client(session:StringSession, id, hash): #proxy implimentation
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

#if not os.path.exists("ACCOUNTS"):
#    os.mkdir("ACCOUNTS")

#session_files = [s.stem for s in Path("ACCOUNTS").glob("*.session")]
#print(session_files)
#clients = []
#print(clients)

#for session_file in session_files[: min(len(session_files), client_number)]:
#    print(session_file)
#    client = TelegramClient(f"ACCOUNTS/{session_file}", api_id=api_id, api_hash=api_hash)
#    try:
#        client.connect()
#        client.send_message("obsquriel", "teshting")
#        clients.append(client)
#    except UserDeactivatedBanError as e:
#        print(str(e))
#        continue
#    client.send_message("obsquriel", "teshting")
#    clients.append(client)


#if len(clients) < client_number:
#    for i in range(client_number - len(clients)):
#        client = TelegramClient(
#            str(len(clients)), api_id=api_id, api_hash=api_hash
#        )
#        client.start()
#        clients.append(client)


print(f"\n[$]Running spam-bot check")
check = 0
for i in range(len(clients)):
    name = (clients[check].get_me()).first_name
    try:
        clients[check].send_message("@SpamBot", "/start")
        time.sleep(1)
        m = clients[check].get_messages("@SpamBot", 1)
        if "no limits are currently applied to your account" in m[0].message:
            print(f"--->No limits from telegram for account {name}")
            check = check + 1
            pass
        else:
            print(f"--->Account {name} is limited by telegram, so removing")
            clients.remove(clients[check])
    except IndexError:
        break

if len(clients) == 0:
    print("\n[$]ERROR: No accounts available for DMing")
    exit(1)


c = input("\n[$]Enter the username of the public group whose latest message is to be DMed: ")
t = clients[0].get_messages(c, 1)
msg = t[0].message
print(f"Message: {msg}\n--->Above message will be DMed")

time.sleep(2)
