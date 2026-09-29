from flask import Flask, jsonify, render_template, request

import pid

# static_folder=None: na Vercel, os arquivos de public/ são servidos pela CDN,
# e a documentação recomenda não usar a pasta estática do Flask.
app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


@app.route("/api/simular", methods=["POST"])
def simular():
    # silent=True: JSON ausente ou malformado vira None, tratado na validação
    dados = request.get_json(silent=True)
    try:
        parametros = pid.validar_parametros(dados)
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400
    return jsonify(pid.simular(**parametros))


if __name__ == "__main__":
    # Só roda localmente (python app.py). Aqui não existe a CDN da Vercel,
    # então o próprio Flask serve public/ na raiz: public/css/style.css -> /css/style.css
    from flask import send_from_directory

    @app.route("/<path:filename>")
    def public_files(filename):
        return send_from_directory("public", filename)

    app.run(debug=True)
