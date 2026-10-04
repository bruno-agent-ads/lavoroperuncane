# Manda a Federico il video del giorno (coda/AAAA-MM-GG/) e il testo da copiare.
import datetime, json, os, pathlib, re, sys, urllib.request, uuid, zoneinfo

# La chiave incollata può avere spazi o testo intorno: prendo solo la parte numeri:lettere.
_trovata = re.search(r"\d{6,}:[A-Za-z0-9_-]{30,}", os.environ["TOKEN"])
if not _trovata:
    sys.exit("La chiave TELEGRAM_TOKEN non sembra una chiave di BotFather.")
TOKEN = _trovata.group(0)
API = f"https://api.telegram.org/bot{TOKEN}/"
CHAT_FILE = pathlib.Path("bot/chat_id.txt")

def chiama(metodo, dati=None, file=None):
    if file is None:
        req = urllib.request.Request(API + metodo, data=json.dumps(dati or {}).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        confine = uuid.uuid4().hex
        corpo = b""
        for k, v in (dati or {}).items():
            corpo += f"--{confine}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        corpo += (f"--{confine}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{file.name}\"\r\n"
                  "Content-Type: video/mp4\r\n\r\n").encode() + file.read_bytes() + f"\r\n--{confine}--\r\n".encode()
        req = urllib.request.Request(API + metodo, data=corpo,
                                     headers={"Content-Type": f"multipart/form-data; boundary={confine}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["result"]

def chat_id():
    if CHAT_FILE.exists():
        return CHAT_FILE.read_text().strip()
    for u in reversed(chiama("getUpdates")):
        chat = (u.get("message") or {}).get("chat", {})
        if chat.get("type") == "private":
            CHAT_FILE.write_text(str(chat["id"]))
            return str(chat["id"])
    sys.exit("Nessuna chat: Federico deve premere Avvia sul bot.")

oggi = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Rome")).date().isoformat()
cartella = pathlib.Path("coda") / oggi
cid = chat_id()
print("chat", cid)
if not cartella.exists():
    chiama("sendMessage", {"chat_id": cid, "text": "🐶 Oggi niente video in coda. Bruno riposa."})
    sys.exit(0)
testo = (cartella / "testo.txt").read_text().strip() if (cartella / "testo.txt").exists() else ""
video = next(iter(sorted(cartella.glob("*.mp4"))), None)
chiama("sendMessage", {"chat_id": cid, "text": f"🐶 Video del {oggi}. Salvalo, pubblicalo su TikTok e incolla il testo qui sotto."})
if video:
    chiama("sendVideo", {"chat_id": cid, "supports_streaming": "true"}, file=video)
if testo:
    chiama("sendMessage", {"chat_id": cid, "text": testo})
