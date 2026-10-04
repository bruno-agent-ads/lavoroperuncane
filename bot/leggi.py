# Legge i messaggi che Federico scrive al bot e li salva CIFRATI in posta/ (il repo è pubblico).
# Solo Bruno ha la chiave privata per leggerli (nella cartella del progetto, non qui).
import base64, datetime, json, os, pathlib, re, subprocess, sys, tempfile, urllib.request

token = re.search(r"\d{6,}:[A-Za-z0-9_-]{30,}", re.sub(r"\s", "", os.environ["TOKEN"]))
if not token:
    sys.exit("La chiave TELEGRAM_TOKEN non sembra una chiave di BotFather.")
API = f"https://api.telegram.org/bot{token.group(0)}/"
chat = pathlib.Path("bot/chat_id.txt").read_text().strip()
offset_file = pathlib.Path("bot/offset.txt")
offset = int(offset_file.read_text()) if offset_file.exists() else 0

def chiama(metodo, dati):
    req = urllib.request.Request(API + metodo, data=json.dumps(dati).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["result"]

aggiornamenti = chiama("getUpdates", {"offset": offset, "timeout": 0})
messaggi = []
for u in aggiornamenti:
    offset = max(offset, u["update_id"] + 1)
    m = u.get("message") or u.get("edited_message") or {}
    if str(m.get("chat", {}).get("id")) != chat:
        continue
    testo = m.get("text") or m.get("caption") or ""
    if m.get("photo"): testo += " [foto]"
    if m.get("video"): testo += " [video]"
    if m.get("voice"): testo += " [vocale]"
    if testo.strip() and not testo.startswith("/start"):
        messaggi.append({"quando": datetime.datetime.fromtimestamp(m["date"], datetime.timezone.utc).isoformat(),
                         "testo": testo.strip()})
offset_file.write_text(str(offset))
if not messaggi:
    print("nessun messaggio nuovo"); sys.exit(0)

# Cifratura: chiave AES a caso, cifrata con la chiave pubblica di Bruno.
with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    chiave = os.urandom(32).hex()
    (d / "k").write_text(chiave)
    (d / "m").write_text(json.dumps(messaggi, ensure_ascii=False))
    subprocess.run(["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", "bot/posta_pubblica.pem",
                    "-pkeyopt", "rsa_padding_mode:oaep", "-in", d / "k", "-out", d / "k.enc"], check=True)
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", f"file:{d / 'k'}",
                    "-in", d / "m", "-out", d / "m.enc"], check=True)
    busta = {"chiave": base64.b64encode((d / "k.enc").read_bytes()).decode(),
             "dati": base64.b64encode((d / "m.enc").read_bytes()).decode()}
posta = pathlib.Path("posta"); posta.mkdir(exist_ok=True)
nome = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S") + ".json"
(posta / nome).write_text(json.dumps(busta))
chiama("sendMessage", {"chat_id": chat, "text": "🐶 Ricevuto. Bruno legge e ti risponde qui."})
print(f"{len(messaggi)} messaggi salvati in posta/{nome}")
