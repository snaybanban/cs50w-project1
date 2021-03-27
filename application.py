import os, requests
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
#engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))  

@app.route("/")
@login_required
def index():
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("index.html", books=books)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Usuario vacio")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Contraseña vacia")
            return render_template("login.html")    
        

        # Remember which user has logged in
        rows=db.execute("SELECT * FROM users WHERE username=:username", {"username":request.form.get("username")})
        rows=rows.fetchone()
        print(rows)
        ####check contraseña
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            print('error: contraseña incorrecta o usuario no registrado')
            return render_template("error.html")
       
        # Redirect user to home page
        print(rows[1])
        session["user_id"] = rows[0]
        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("username vacio")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("password vacio")
            return render_template("register.html")

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("No coincide")
            return render_template("register.html")

        # hash the password and insert a new user in the database
        paswordhash = generate_password_hash(request.form.get("confirmation"))
        rows = db.execute("INSERT INTO users (username, hashs) VALUES(:username, :paswordhash)",{"username":request.form.get("username"), "paswordhash":paswordhash})

        db.commit()

        return render_template("login.html")
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

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
        usuario = session["id"]

        rating = int(request.form.get("rating"))
        comment = ( request.form.get("reviews"))
        
        row = db.execute("SELECT * FROM reviews WHERE id_user = :user_id AND isbn = :isbn",{"user_id":session["id"], "isbn":isbn})

        print(row)

        if rows.rowcount == 1:
            flash("usted ya realizo un comentario a este libro")
            return redirect("/book/"+isbn)
        query = db.execute("INSERT INTO reviews (isbn,id_user,rating,comment,time) VALUES (:isbn,:user_id,:rating,:comment,now())",{"isbn":isbn, "user_id":usuario, "rating":rating, "comment":comment})
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

        print(contenido)
        print("")
        print(contenido['ratingsCount'])


        
        print("")
        print(contenido['averageRating'])

        imagen= contenido['imageLinks']
        print(imagen['thumbnail'])
    return render_template("book.html", query = query, review = review,imagen = imagen, contenido = contenido)
