"""Video Studio license client. Standard library only.

  boot.py activate <LICENSE KEY> --data <dir>   first run on this computer (the key is in your Whop orders)
  boot.py ensure --data <dir>                   check the license, fetch or update the studio; prints JSON paths
  boot.py status --data <dir>                   show license state without contacting the server

<dir> is the plugin's data folder (${CLAUDE_PLUGIN_DATA}); the studio is unpacked to <dir>/bundle.
"""
import hashlib, io, json, os, platform, shutil, subprocess, sys, time, urllib.error, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = (os.environ.get("STUDIO_SERVER") or json.load(open(os.path.join(HERE, "server.json"), encoding="utf-8-sig"))["url"]).rstrip("/")
GRACE_HOURS = 72          # keep working this long without reaching the server (flaky internet, travel)


def out(obj, code=0):
    print(json.dumps(obj, indent=1))
    sys.exit(code)


def hwid():
    """stable id of this computer, hashed so the raw id never leaves it"""
    raw = ""
    try:
        if os.name == "nt":
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography",
                                0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
                raw = winreg.QueryValueEx(k, "MachineGuid")[0]
        elif platform.system() == "Darwin":
            o = subprocess.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True).stdout
            raw = next(l.split('"')[-2] for l in o.splitlines() if "IOPlatformUUID" in l)
        else:
            raw = open("/etc/machine-id").read().strip()
    except Exception:
        raw = platform.node()
    return hashlib.sha256(("video-studio:" + raw).encode()).hexdigest()


def call(method, path, body=None, token=None, binary=False):
    req = urllib.request.Request(SERVER + path, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("content-type", "application/json")
    req.add_header("user-agent", "FLS-Studio/0.1 (+https://github.com/saim-sys/video-studio)")  # Cloudflare blocks Python's default
    req.add_header("x-hwid", hwid())
    if token:
        req.add_header("authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, (r.read() if binary else json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {"ok": False, "reason": f"http_{e.code}"}


def paths(data):
    b = os.path.join(data, "bundle")
    return {"bundle": b, "pipeline": os.path.join(b, "pipeline"), "playbook": os.path.join(b, "playbook"),
            "templates": os.path.join(b, "templates"), "version": open(os.path.join(b, "VERSION")).read().strip()}


def wipe(data):
    shutil.rmtree(os.path.join(data, "bundle"), ignore_errors=True)


MESSAGES = {
    "unknown_key": "That license key isn't recognised. Copy it again from your Whop orders.",
    "inactive": "Your membership isn't active, so the studio is locked. Renew it on Whop to continue.",
    "other_machine": "This key is already in use on another computer. Reset it from your Whop orders, then activate again.",
    "not_activated": "Not activated on this computer yet.",
}


def ensure(data, key=None):
    os.makedirs(data, exist_ok=True)
    lic_path = os.path.join(data, "license.json")
    lic = json.load(open(lic_path)) if os.path.exists(lic_path) else {}
    if key:
        lic = {"key": key.strip()}
    if not lic.get("key"):
        out({"ok": False, "reason": "not_activated", "message": MESSAGES["not_activated"]}, 2)
    now = time.time()
    if now >= lic.get("expires", 0) - 300:            # token missing or about to expire: ask the server
        try:
            code, r = call("POST", "/v1/activate", {"key": lic["key"], "hwid": hwid()})
        except Exception:
            code, r = 0, {}
        if code == 200 and r.get("ok"):
            lic.update(token=r["token"], expires=r["expires"], last_ok=now, server_version=r.get("bundle_version"))
        elif r.get("reason") in MESSAGES:             # a real "no": lock the studio
            wipe(data)
            lic.pop("token", None); lic["expires"] = 0
            json.dump(lic, open(lic_path, "w"))
            out({"ok": False, "reason": r["reason"], "message": MESSAGES[r["reason"]]}, 3)
        elif now - lic.get("last_ok", 0) > GRACE_HOURS * 3600 or not os.path.isdir(os.path.join(data, "bundle")):
            out({"ok": False, "reason": "offline", "message": "Can't reach the license server. Check your internet and try again."}, 4)
    json.dump(lic, open(lic_path, "w"))
    have = os.path.join(data, "bundle", "VERSION")
    local = open(have).read().strip() if os.path.exists(have) else None
    if lic.get("token") and (local is None or (lic.get("server_version") and lic["server_version"] != local)):
        code, blob = call("GET", "/v1/bundle", token=lic["token"], binary=True)
        if code != 200:
            if local is None:
                out({"ok": False, "reason": "download_failed", "message": "Couldn't download the studio. Try again in a minute."}, 5)
        else:
            tmp = os.path.join(data, "bundle.new")
            shutil.rmtree(tmp, ignore_errors=True)
            zipfile.ZipFile(io.BytesIO(blob)).extractall(tmp)
            wipe(data)
            os.replace(tmp, os.path.join(data, "bundle"))
    return {"ok": True, **paths(data), "license_valid_until": time.strftime("%Y-%m-%d %H:%M", time.localtime(lic.get("expires", 0)))}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--data" not in a:
        sys.exit(__doc__)
    data = a[a.index("--data") + 1]
    if a[0] == "activate" and len(a) >= 4:
        out(ensure(data, key=a[1]))
    elif a[0] == "ensure":
        out(ensure(data))
    elif a[0] == "status":
        p = os.path.join(data, "license.json")
        lic = json.load(open(p)) if os.path.exists(p) else {}
        out({"activated": bool(lic.get("key")), "valid_until": lic.get("expires"), "last_check": lic.get("last_ok"),
             "studio_installed": os.path.isdir(os.path.join(data, "bundle"))})
    else:
        sys.exit(__doc__)
