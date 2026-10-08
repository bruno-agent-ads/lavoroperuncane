# Manda a Federico il video del giorno (coda/AAAA-MM-GG/) e il testo da copiare.
import datetime, json, os, pathlib, re, sys, urllib.request, uuid, zoneinfo

# La chiave incollata può avere spazi, a capo o testo intorno: prendo solo la parte numeri:lettere.
_trovata = re.search(r"\d{6,}:[A-Za-z0-9_-]{30,}", re.sub(r"\s", "", os.environ["TOKEN"]))
if not _trovata:
    _t = os.environ["TOKEN"]
    # Solo la forma, mai il contenuto: lunghezza, due punti, spazi, righe.
    print(f"forma: lunghezza={len(_t)} due_punti={_t.count(':')} spazi={_t.count(' ')} "
          f"righe={_t.count(chr(10)) + 1} cifre={sum(c.isdigit() for c in _t)}")
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
# CARTELLA (facoltativa) manda una cartella precisa, es. coda/diario/2026-10-08
cartella = pathlib.Path(os.environ.get("CARTELLA") or pathlib.Path("coda") / oggi)
if os.environ.get("CARTELLA"):
    oggi = cartella.name
cid = chat_id()
print("chat", cid)
if not cartella.exists():
    chiama("sendMessage", {"chat_id": cid, "text": "🐶 Oggi niente video in coda. Bruno riposa."})
    sys.exit(0)
def leggi(f):
    return f.read_text().strip() if f.exists() else ""

video = sorted(cartella.glob("*.mp4"))
chiama("sendMessage", {"chat_id": cid, "text": f"🐶 Video del {oggi}: {len(video)}. Il primo è quello principale, il secondo se hai tempo. Tieni premuto il video e salvalo, i testi da copiare sono sotto ognuno."})
for n, v in enumerate(video, 1):
    # Testi: NOME.txt e NOME_ig.txt (o testo.txt e testo_ig.txt per le cartelle vecchie)
    tt = leggi(v.with_suffix(".txt")) or leggi(cartella / "testo.txt")
    ti = leggi(v.with_name(v.stem + "_ig.txt")) or leggi(cartella / "testo_ig.txt")
    chiama("sendMessage", {"chat_id": cid, "text": f"🎬 Video {n} di {len(video)}"})
    chiama("sendVideo", {"chat_id": cid, "supports_streaming": "true"}, file=v)
    if tt:
        chiama("sendMessage", {"chat_id": cid, "text": "👇 Testo per TikTok"})
        chiama("sendMessage", {"chat_id": cid, "text": tt})
    if ti:
        chiama("sendMessage", {"chat_id": cid, "text": "👇 Testo per Instagram e Facebook"})
        chiama("sendMessage", {"chat_id": cid, "text": ti})
