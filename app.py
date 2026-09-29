from flask import Flask, jsonify, render_template

# static_folder=None: na Vercel, os arquivos de public/ são servidos pela CDN,
# e a documentação recomenda não usar a pasta estática do Flask.
app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    # Só roda localmente (python app.py). Aqui não existe a CDN da Vercel,
    # então o próprio Flask serve public/ na raiz: public/css/style.css -> /css/style.css
    from flask import send_from_directory

    @app.route("/<path:filename>")
    def public_files(filename):
        return send_from_directory("public", filename)

    app.run(debug=True)
