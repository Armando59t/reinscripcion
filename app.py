from flask import Flask, request, render_template, redirect, session
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "secreto123"
CORS(app)

# =======================
# 🔗 CONEXIÓN MONGO (NO TIRA LA APP)
# =======================
MONGO_URI = "mongodb+srv://ricardopauljose92_db_user:sSondflxoc6PIFw6@cluster0.tmppfp7.mongodb.net/?retryWrites=true&w=majority"

alumnos = None  # 👈 valor por defecto

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000
    )
    client.server_info()
    print("✅ Mongo conectado")

    db = client["cbtis272"]
    alumnos = db["alumnos"]

except Exception as e:
    print("❌ Error Mongo:", e)
    alumnos = None  # 👈 evita que truene todo

# =======================
# 🧪 TESTS
# =======================
@app.route("/test")
def test():
    return "Servidor OK"

@app.route("/mongo-test")
def mongo_test():
    if alumnos is None:
        return "Mongo NO conectado ❌"

    try:
        alumnos.find_one()
        return "Mongo OK ✅"
    except Exception as e:
        return f"Error Mongo: {e}"

# =======================
# LOGIN
# =======================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if alumnos is None:
        return "Base de datos no disponible ❌"

    if request.method == "POST":
        curp = request.form.get("curp")

        if not curp:
            return "Falta CURP"

        alumno = alumnos.find_one({"curp": curp})

        if alumno:
            session["curp"] = curp
            return redirect("/perfil")
        else:
            return "Alumno no encontrado"

    return render_template("login.html")

# =======================
# REGISTRO
# =======================
@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/registrar", methods=["POST"])
def registrar():
    if alumnos is None:
        return "Base de datos no disponible ❌"

    data = request.form.to_dict()

    if "curp" not in data:
        return "Falta CURP"

    if alumnos.find_one({"curp": data["curp"]}):
        return "Ya existe este alumno"

    alumnos.insert_one(data)
    session["curp"] = data["curp"]
    return redirect("/perfil")

# =======================
# PERFIL
# =======================
@app.route("/perfil")
def perfil():
    if alumnos is None:
        return "Base de datos no disponible ❌"

    if "curp" not in session:
        return redirect("/login")

    alumno = alumnos.find_one({"curp": session["curp"]})
    return render_template("perfil.html", alumno=alumno)

# =======================
# EDITAR
# =======================
@app.route("/editar", methods=["GET", "POST"])
def editar():
    if alumnos is None:
        return "Base de datos no disponible ❌"

    if "curp" not in session:
        return redirect("/login")

    if request.method == "POST":
        data = request.form.to_dict()

        alumnos.update_one(
            {"curp": session["curp"]},
            {"$set": data}
        )

        return redirect("/perfil")

    alumno = alumnos.find_one({"curp": session["curp"]})
    return render_template("editar.html", alumno=alumno)

# =======================
# LOGOUT
# =======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =======================
# RUN (RENDER)
# =======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
