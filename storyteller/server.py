from pathlib import Path
import urllib

from flask import Flask, jsonify, request

app = Flask(
    __name__,
    template_folder=Path(__file__).parent / "data/www",
    static_folder=Path(__file__).parent / "data/www/assets",
)


@app.route("/", methods=["GET"])
def arguments():
    text = request.args.get("text", "")
    if not text:
        # TODO: Move to config
        return Path(__file__).parent.parent / "data" / "www" / "index.html").read_text(
            encoding="utf-8"
        )

    text = urllib.parse.unquote(text)
    generation = model.autocomplete(text)
    out = {"generation": generation}
    return jsonify(out)


def serve(port: int = 9000):
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
