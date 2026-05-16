from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BRING_API = "https://api.getbring.com/rest/v2"
HEADERS = {
    "X-BRING-CLIENT": "javascript",
    "X-BRING-CLIENT-SOURCE": "webApp",
    "X-BRING-COUNTRY": "DE",
    "X-BRING-API-KEY": "cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Og"
}

@app.route("/", methods=["POST", "OPTIONS"])
def proxy():
    if request.method == "OPTIONS":
        return "", 204
    data = request.json
    action = data.get("action")
    email = data.get("email")
    passwort = data.get("passwort")

    login = requests.post(f"{BRING_API}/bringauth",
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        data={"email": email, "password": passwort})
    ld = login.json()
    if "uuid" not in ld:
        return jsonify({"error": "Login fehlgeschlagen"}), 401

    auth = {**HEADERS, "Authorization": f"Bearer {ld['access_token']}"}

    if action in ("test", "listen"):
        r = requests.get(f"{BRING_API}/bringusers/{ld['uuid']}/lists", headers=auth)
        listen = [{"uuid": l["listUuid"], "name": l["name"]} for l in r.json().get("lists", [])]
        return jsonify({"ok": True, "anzahl_listen": len(listen), "listen": listen})

    if action == "senden":
        for item in data.get("items", []):
            requests.put(f"{BRING_API}/bringlists/{data['list_uuid']}",
                headers={**auth, "Content-Type": "application/x-www-form-urlencoded"},
                data={"purchase": item["name"], "specification": item.get("menge", "")})
        return jsonify({"ok": True})

    return jsonify({"error": "Unbekannte Aktion"}), 400

if __name__ == "__main__":
    app.run()
