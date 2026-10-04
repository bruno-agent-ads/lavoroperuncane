# Per Bruno: decifra posta/*.json con la chiave privata (python3 bot/apri_posta.py CHIAVE.pem [file...]).
import base64, json, pathlib, subprocess, sys, tempfile
pem = sys.argv[1]
files = sys.argv[2:] or sorted(str(p) for p in pathlib.Path("posta").glob("*.json"))
for f in files:
    b = json.loads(pathlib.Path(f).read_text())
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / "k.enc").write_bytes(base64.b64decode(b["chiave"]))
        (d / "m.enc").write_bytes(base64.b64decode(b["dati"]))
        subprocess.run(["openssl", "pkeyutl", "-decrypt", "-inkey", pem, "-pkeyopt", "rsa_padding_mode:oaep",
                        "-in", d / "k.enc", "-out", d / "k"], check=True)
        out = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", f"file:{d / 'k'}",
                              "-in", d / "m.enc"], check=True, capture_output=True).stdout
    for m in json.loads(out):
        print(f"{pathlib.Path(f).name} | {m['quando']} | {m['testo']}")
