import datetime
import imaplib
import email
import os
import sys
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import time
import getpass
# ______________________________________________________________________________________________________________________
imap_server = "imap.yandex.ru"

if os.path.exists("passwords.txt"):
    fin = open("passwords.txt", "r")
    login = fin.readline().strip()
    password = fin.readline().strip()
else:
    print("[+] Please, write your login.")
    login = input().strip()
    time.sleep(0.2)

    print("[+] Please, write your password.")
    password = getpass.getpass().strip()
    time.sleep(0.2)

# ______________________________________________________________________________________________________________________

print("[+] Trying to log in...")
try:
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(login, password)
except:
    print("[-] Can't log in")
    input()
    sys.exit(0)
print("[+] Login completed successfully!")

# ______________________________________________________________________________________________________________________

if not os.path.exists("passwords.txt"):
    while True:
        print("[+] Do you want to save the password? Please, answer 'yes' or 'no'.")
        a = input().lower()
        if a == 'yes':
            try:
                fout = open("passwords.txt", "w")
                print(login, password, sep='\n', file=fout)
                fout.close()
            except:
                print("[-] Can't save password :(")
                pass
            break
        elif a == 'no':
            break
# ______________________________________________________________________________________________________________________

print("List of mail boxes:\n")
boxlist = imap.list()[1]
for i in boxlist:
    i = i.decode('UTF-8')
    zn = i.find("|") + 3
    print(i[zn:])
# print("[-] HA-HA-HA, now I will send it to my owner!")
print("\n[+] Please, write a name of mail box")
box = input().strip()
time.sleep(0.2)

res, count = imap.select(box)
if (res != "OK"):
    print("[-] Can't open this box")
    input()
    sys.exit(0)

# ______________________________________________________________________________________________________________________

print("[+] Since when do I need to upload files?")
time.sleep(0.2)
print("[+] Please, write 'YYYY MM DD hh mm' without ''")
try:
    # d1 = datetime.datetime(1111, 1, 1)
    d1 = datetime.datetime(*list(map(int, input().strip().split())))
except:
    d1 = datetime.datetime(1000, 1, 1)
time.sleep(0.2)

print("[+] Before what time do I need to upload files?")
time.sleep(0.2)
print("[+] Please, write 'YYYY MM DD hh mm' without ''")
try:
    # d2 = datetime.datetime(2222, 2, 2)
    d2 = datetime.datetime(*list(map(int, input().strip().split())))
except:
    d2 = datetime.datetime.now()
time.sleep(0.5)
# ______________________________________________________________________________________________________________________


print("[+] What's the name of the student's work?")
work = input().strip()
# ______________________________________________________________________________________________________________________


res, mails = imap.uid('search', None, f'SINCE {d1.strftime("%d-%b-%Y")} BEFORE {d2.strftime("%d-%b-%Y")}')

if (res != "OK"):
    print("[-] Can't get mails")
    input()
    sys.exit(0)

# ______________________________________________________________________________________________________________________

mails = mails[0].split()
if not os.path.exists(work):
    try:
        os.mkdir(work)
    except:
        print("[-] Can't create the path")
        input()
        sys.exit(0)

os.chdir(f"./{work}")

for j in mails:
    try:
        res, msg = imap.uid('fetch', j, '(RFC822)')
        msg = email.message_from_bytes(msg[0][1])
        # Working with the theme:
        subj = decode_header(msg['Subject'])[0][0].decode().replace(" ", "").replace(" ", "").replace(" ", "")
        if work.lower() not in subj.lower():
            continue
        point = subj.rfind(".") + 1
        if point != 0 and len(subj) > point:
            subj = [subj[:6], subj[6:point], subj[point:].lower()]
        else:
            subj = [subj[:6], subj[6:], "unknown_work"]
        if not os.path.exists(subj[1]):
            try:
                os.mkdir(subj[1])
            except:
                print(f"Can't create/open path {subj[1]}")
                continue
        os.chdir(subj[1])
        # theme[0] - group number
        # theme[1] - student's name
        # theme[2] - name of work

        date = email.utils.parsedate_tz(msg["Date"])
        date = datetime.datetime(*date[0:7])

    except:
        continue


    if (d1 <= date and date <= d2):
        t = 0
        for part in msg.walk():
            # creating the student's file:
            file_name = f"{subj[2]}_{subj[1]}_{str(t)}.c"
            fout = open(file_name, "w+")
            try:
                # decoding mail, formatting and writing:
                htmml = base64.b64decode(part.get_payload()).decode()
                htmml = BeautifulSoup(htmml, "html.parser")
                if str(htmml).count("<br") >= 1 or str(htmml).count("<div") >= 1:
                    htmml = htmml.get_text(separator='\n')
                htmml = str(htmml).replace("\xa0", " ").replace(" \n", "\n"). \
                    replace(" \n", "\n").replace("\r", "\n").replace("\n\n", "\n"). \
                    replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n"). \
                    replace("\n\n", "\n")
                l, r = 0, 0
                for i in range(len(htmml)):
                    if htmml[i] == '#':
                        l = i
                        break
                k = ""
                for i in range(l, len(htmml)):
                    k += htmml[i]
                    if htmml[i] == "}":
                        print(k, file=fout)
                        k = ""
            except:
                pass

            fout.close()
            # if file empty:
            try:
                if os.stat(file_name).st_size <= 0:
                    os.remove(file_name)
            except:
                pass
            # rewriting date:
            try:
                os.utime(file_name,
                         (os.path.getatime(file_name),
                          date.timestamp()))
            except:
                pass
            t += 1
    os.chdir("../")
    print(f"Письмо от {subj[1]} было обработано")

os.chdir("../")
