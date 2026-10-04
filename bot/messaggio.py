# Manda a Federico un messaggio libero di Bruno (testo in TESTO).
import json, os, pathlib, re, sys, urllib.request

token = re.search(r"\d{6,}:[A-Za-z0-9_-]{30,}", re.sub(r"\s", "", os.environ["TOKEN"]))
if not token:
    sys.exit("La chiave TELEGRAM_TOKEN non sembra una chiave di BotFather.")
chat = pathlib.Path("bot/chat_id.txt").read_text().strip()
dati = json.dumps({"chat_id": chat, "text": os.environ["TESTO"].replace("\\n", "\n")}).encode()
req = urllib.request.Request(f"https://api.telegram.org/bot{token.group(0)}/sendMessage", data=dati,
                             headers={"Content-Type": "application/json"})
urllib.request.urlopen(req, timeout=60)
print("mandato")
