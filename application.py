import os, requests, json, datetime
from helpers import login_required

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import session
from tempfile import mkdtemp
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not ("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine("postgres://ajigwrxxtsfjgh:eef2bb35cd85a37e7d10b5699794a552f7dd4736560b44c88126e9f1228f8f51@ec2-54-145-102-149.compute-1.amazonaws.com:5432/d8tvv4bh4q66pr")
db = scoped_session(sessionmaker(bind=engine))  

@app.route("/")
@login_required
def index():
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("index.html", books=books)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Usuario vacio")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Contraseña vacia")
            return render_template("login.html")    
        

        rows=db.execute("SELECT * FROM users WHERE username=:username", {"username":request.form.get("username")})
        rows=rows.fetchone()
        print(rows)
        #check contraseña
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            print('error: contraseña incorrecta o usuario no registrado')
            return render_template("error.html")
       
        print(rows[1])
        session["user_id"] = rows[0]
        return render_template("index.html")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect(url_for("index"))



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            flash("username vacio")
            return render_template("register.html")

        elif not request.form.get("password"):
            flash("password vacio")
            return render_template("register.html")

        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("No coincide")
            return render_template("register.html")

        username = request.form.get("username")
        paswordhash = generate_password_hash(request.form.get("password"))
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        print(rows)
        if rows:
            flash("El usuario ya existe")
            return render_template("register.html")
        else:
            row2 = db.execute("INSERT INTO users (username, hashs) VALUES(:username, :password)", {"username": username, "password": paswordhash})
            db.commit()
            flash("Usuario registrado")
            return render_template("login.html")
    return render_template("register.html")

@app.route("/cambio", methods=["POST","GET"])
@login_required
def cambio():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("cambio.html")
        elif not request.form.get("password"):
            return render_template("cambio.html")
        elif not request.form.get("confirmation"):
            return render_template("cambio.html")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("cambio.html")

           
        query = db.execute("update users SET username = :username, hashs = :hashs WHERE id_user = :user_id",{"username":request.form.get("username") , "hashs":generate_password_hash(request.form.get("password")) , "user_id":session["user_id"]})
        db.commit()
        session.clear()
        flash("La Contraseña se a cambiado")
        
        return render_template("login.html")
                    
    return render_template("cambio.html")

@app.route("/busqueda", methods=["GET", "POST"])
@login_required
def busqueda():
    if request.method == "POST":

        if request.form.get("busqueda"):
            rows = "%" + request.form.get("busqueda").title() + "%"
            query = db.execute("SELECT isbn, title, author, year FROM books WHERE title LIKE :rows OR \
                author LIKE :rows OR isbn Like :rows",{"rows": rows}).fetchall()
            if query:
                return render_template("busqueda.html", query = query)
            else:
                flash("No se encontro el libro deseado")
                return render_template("index.html")

        flash("Ingrese el nombre de un libro")
        return render_template("error2.html")

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method == "POST":
        usuario = session["user_id"]
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment")
        print("ESTE ES EL COMENTARIO", comment)
        row = db.execute("SELECT * FROM reviews WHERE id_user = :user_id AND isbn = :isbn",{"user_id":session["user_id"], "isbn":isbn})

        print(row)

        if row.rowcount == 1:
            flash("usted ya realizo un comentario a este libro")
            return redirect("/book/"+isbn)
        fecha = datetime.datetime.now()
        print("Esta es la fecha de hoy", fecha)
        query = db.execute("INSERT INTO reviews (isbn,id_user,rating,comment,time) VALUES (:isbn,:user_id,:rating,:comment,:date)", {"isbn":isbn, "user_id":usuario, "rating":rating, "comment":comment, "date": datetime.datetime.now()})
        db.commit()
        
        flash("Su comentario se publico correctamente")
        return redirect("/book/"+isbn)
    else:
        query = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchall()
        print(query)
        review = db.execute("select users.username,reviews.comment, reviews.rating, to_char(reviews.time, 'DD Mon YYYY - HH24:MI:SS') as fecha from reviews inner join users on reviews.id_user = users.id_user where reviews.isbn = :isbn ORDER BY fecha DESC",{"isbn":isbn}).fetchall()
        print("Esta es la consulta del rows",review)
        contenido = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        contenido = (contenido['items'][0])
        contenido = contenido['volumeInfo']

        descripcion = contenido['description']
        imagen = contenido['imageLinks']
    return render_template("book.html", query=query, review=review, imagen=imagen, contenido=contenido, descripcion=descripcion)

@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):

    if 'user_id' in session:

        query1 = db.execute(
            "SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchall()
        print("Este es el query 1", query1)
        print("Este es el isbn 1", query1[0]['isbn'])
        if query1 == None:
            return ("No se encuentra")

        query2 = db.execute("SELECT COUNT(reviews) as cantidad_reviews,  AVG(reviews.rating) as promedio_puntiacion FROM reviews where isbn = :isbn", {"isbn": isbn}).fetchall()

        isbn = query1[0]['isbn'],
        title = query1[0]['title'],
        author = query1[0]['author'],
        year = query1[0]['year'],
        cantidad_reviews = query2[0]['cantidad_reviews'],
        promedio_puntiacion = [float('%.2f' % (query2[0]['promedio_puntiacion']))]

        requests = {
            "isbn": isbn,
            "title": title,
            "author": author,
            "year": year,
            "cantidad_reviews": cantidad_reviews,
            "promedio_puntiacion": promedio_puntiacion
        }
        return jsonify(requests)