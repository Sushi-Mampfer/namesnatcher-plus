import requests
import threading
import time
from MsAuth import login

drop = False

with open("accounts.txt") as f:
    accounts = f.readlines()

with open("proxies.txt") as f:
    proxies = f.readlines()

tokens = []
for i in accounts:
    data = login(i.split(":")[0], i.split(":")[1], i.split(":")[2])
    if data != None:
        tokens.append(data)


def check(name, proxy):
    global drop
    uuid = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}").json()["id"]
    while not drop:
        res = requests.get(f"https://api.mojang.com/user/profile/{uuid}", proxies={
            'http': proxy,
            'https': proxy,
        })
        if res.status_code == 204:
            drop = True
            print("Deletion has happened!")
        elif res.status_code == 200:
            if res.json()["name"] != name:
                drop = True
                print("Deletion has happened!")
            else:
                print("Request successful.")
        elif res.status_code == 429:
           print(f"Proxy {proxy} has hit a ratelimit.")
        else:
            print(f"Proxy {proxy} failed with statuscode {res.status_code} and body:\n{res.text}")

def account_refresher():
    global tokens
    for i in range(len(tokens)):
        if tokens[i]["time"] <= time.time():
            tokens[i] = login(tokens[i]["email"], tokens[i]["passwd"], tokens[i]["name"])

def claimer(acc):
    global tokens
    global drop
    while True:
        if drop:
            if tokens[acc]["username"] != None:
                res = requests.get(f"https://api.minecraftservices.com/minecraft/profile/name/{tokens[acc]["name"]}", headers={"Authorization": f"Bearer {tokens[acc]["access_token"]}"})
                if res.status_code == 200:
                    print(f"Claimed {tokens[acc]["name"]}!")
                    break
                else:
                    print(f"Couldn't claim {tokens[acc]["name"]}!")
                    break
            else:
                res = requests.post("https://api.minecraftservices.com/minecraft/profile", json={"profileName": tokens[acc]["name"]}, headers={"Authorization": f"Bearer {tokens[acc]["access_token"]}", "Accept": "application/json"})
                if res.status_code == 200:
                    print(f"Claimed {tokens[acc]["name"]}!")
                    break
                else:
                    print(f"Couldn't claim {tokens[acc]["name"]}!")
                    break

def main():
    name = input("Name that will be deleted: ")
    threads = int(input("Amount of threads to check(2-4x Amount of proxies, lower if you hit ratelimits): "))
    threading.Thread(target=account_refresher).start()
    for i in range(threads):
        threading.Thread(target=check, args=(name, proxies[len(proxies) % (i + 1) % len(proxies)])).start()
    for i in tokens:
        threading.Thread(target=claimer, args=(i,)).start()
    while True:
        continue

if __name__ == "__main__":
    main()
