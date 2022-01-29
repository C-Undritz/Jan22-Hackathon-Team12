import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    pets = mongo.db.pet_types.find()
    return render_template("index.html", pets=pets)


@app.route("/login", methods=["GET", "POST"])
def login():
    """------------- Log in -----------------------"""
    if request.method == "POST":
        # check if the username already exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            # check to see if hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}".format(request.form.get("username")))
                return redirect(url_for("home", username=session["user"]))
            else:
                # Invalid password match
                flash("Invalid Username and/or Password")
                return redirect(url_for("login"))

        else:
            # Username does not exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/provider_login", methods=["GET", "POST"])
def provider_login():
    """------------- Log in -----------------------"""
    if request.method == "POST":
        # check if the username already exists in the database
        existing_user = mongo.db.service_providers.find_one(
            {"name": request.form.get("name").lower()}
        )

        if existing_user:
            # check to see if hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("name").lower()
                flash("Welcome {}".format(request.form.get("name")))
                return redirect(url_for("home", username=session["user"]))
            else:
                # Invalid password match
                flash("Invalid Username and/or Password")
                return redirect(url_for("provider_login"))

        else:
            # Username does not exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("provider_login"))

    return render_template("provider_login.html")


@app.route("/logout")
def logout():
    """------------- Log out -----------------------"""
    # remove user session cookies
    flash("You Have Been Logged Out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """------------- Sign Up -----------------------"""
    if request.method == "POST":
        # Check if the username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()}
        )

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))
        if existing_email:
            flash("Email already exists")
            return redirect(url_for("signup"))

        register = {
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "provider": False
        }
        mongo.db.users.insert_one(register)

        # put the new user in a session cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Successful!")
        return redirect(url_for("home", username=session["user"]))

    return render_template("signup.html")


@app.route("/provider_signup", methods=["GET", "POST"])
def provider_signup():
    """------------- Provider Sign Up -----------------------"""
    if request.method == "POST":
        # Check if the username already exists
        existing_provider = mongo.db.service_providers.find_one(
            {"name": request.form.get("name").lower()}
        )
        existing_email = mongo.db.service_providers.find_one(
            {"email": request.form.get("email").lower()}
        )

        if existing_provider:
            flash("Provider already exists")
            return redirect(url_for("signup"))
        if existing_email:
            flash("Email already exists")
            return redirect(url_for("signup"))

        register = {
            "name": request.form.get("name").lower(),
            "address1": request.form.get("address1").lower(),
            "address2": request.form.get("address2").lower(),
            "address3": request.form.get("address3").lower(),
            "town_city": request.form.get("town_city").lower(),
            "county": request.form.get("county").lower(),
            "postcode": request.form.get("postcode").lower(),
            "phone": request.form.get("phone").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "description": request.form.get("description").lower(),
            "provider": True
        }
        mongo.db.service_providers.insert_one(register)

        # put the new user in a session cookie
        session["user"] = request.form.get("name").lower()
        flash("Sign Up Successful!")
        return redirect(url_for("home", username=session["user"]))
        
    return render_template("provider_signup.html")


@app.route("/providers")
def providers():
    providers = mongo.db.service_providers.find()
    return render_template("providers.html", providers=providers)


@app.route("/provider_details/<provider_name>")
def provider_details(provider_name):
    provider = mongo.db.service_providers.find_one({"name": provider_name})
    return render_template("provider_details.html", provider=provider)


@app.route("/provider_pets/<provider_name>")
def provider_pets(provider_name):
    pets = list(mongo.db.pets.find({"provider": provider_name}))
    return render_template("provider_pets.html", pets=pets)


@app.route("/pet_profile/<pet_name>")
def pet_profile(pet_name):
    pet = mongo.db.pets.find_one({"name": pet_name})
    return render_template("pet_profile.html", pet=pet)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)
