from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST", "OPTIONS"])
def proxy():
    if request.method == "OPTIONS":
        return "", 204
    
    data = request.json
    action = data.get("action")
    email = data.get("email")
    passwort = data.get("passwort")

    try:
        from python_bring_api.bring import Bring
        bring = Bring(email, passwort)
        bring.login()

        if action in ("test", "listen"):
            result = bring.loadLists()
            listen = [{"uuid": l["listUuid"], "name": l["name"]} for l in result.get("lists", [])]
            return jsonify({"ok": True, "anzahl_listen": len(listen), "listen": listen})

        if action == "senden":
            list_uuid = data.get("list_uuid")
            items = data.get("items", [])
            for item in items:
                bring.saveItem(list_uuid, item["name"], item.get("menge", ""))
            return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Unbekannte Aktion"}), 400

if __name__ == "__main__":
    app.run()
