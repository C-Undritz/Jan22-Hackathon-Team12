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


# ---------- Global functions: ----------
def find_user():
    """
    Determines current user using the username value of the current session
    user and returns the current user as a dict.
    """
    current_user = mongo.db.users.find_one({"username": session["user"]})
    return current_user


def find_id():
    """
    Determines the ObjectId value of the current user and returns it as a
    string value.
    """
    user_id = str(find_user()['_id'])
    return user_id
# ---------------------------------------

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
        
        provider_status = request.form.get("provider_name")
        if provider_status:
            provider = True
        else:
            provider = False

        register = {
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "provider_name": request.form.get("provider_name").lower(),
            "address1": request.form.get("address1").lower(),
            "address2": request.form.get("address2").lower(),
            "address3": request.form.get("address3").lower(),
            "town_city": request.form.get("town_city").lower(),
            "county": request.form.get("county").lower(),
            "postcode": request.form.get("postcode").lower(),
            "phone": request.form.get("phone").lower(),
            "business_email": request.form.get("business_email").lower(),
            "description": request.form.get("description").lower(),
            "provider": provider,
        }
        mongo.db.users.insert_one(register)

        # put the new user in a session cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Successful!")
        return redirect(url_for("home", username=session["user"]))

    return render_template("signup.html")


@app.route("/profile")
def profile():
    """
    Checks session user and renders their profile page.
    """
    if session["user"]:
        user = find_user()
        # provider = user['provider']

        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


@app.route("/provider_profile", methods=["GET", "POST"])
def provider_profile():
    """
    Allows user to view and update their registration details. 
    """
    user = find_user()
    user_id = find_id()

    if request.method == "POST":
        fname = user['fname']
        lname = user['lname']
        email = user['email']
        username = user['username']
        password = user['password']
        provider = user['provider']
        if (user['provider_name'] == request.form.get("provider_name").lower()):
            updated_provider_name = user['provider_name']
        else:
            updated_provider_name = request.form.get("provider_name").lower()

        if (user['address1'] == request.form.get("address1").lower()):
            updated_address1 = user['address1']
        else:
            updated_address1 = request.form.get("address1").lower()

        if (user['address2'] == request.form.get("address2").lower()):
            updated_address2 = user['address2']
        else:
            updated_address2 = request.form.get("address2").lower()

        if (user['address3'] == request.form.get("address3").lower()):
            updated_address3 = user['address3']
        else:
            updated_address3 = request.form.get("address3").lower()

        if (user['town_city'] == request.form.get("town_city").lower()):
            updated_town_city = user['town_city']
        else:
            updated_town_city = request.form.get("town_city").lower()

        if (user['county'] == request.form.get("county").lower()):
            updated_county = user['county']
        else:
            updated_county = request.form.get("county").lower()

        if (user['postcode'] == request.form.get("postcode").lower()):
            updated_postcode = user['postcode']
        else:
            updated_postcode = request.form.get("postcode").lower()

        if (user['phone'] == request.form.get("phone").lower()):
            updated_phone = user['phone']
        else:
            updated_phone = request.form.get("phone").lower()

        if (user['business_email'] == request.form.get("business_email").lower()):
            updated_business_email = user['business_email']
        else:
            updated_business_email = request.form.get("business_email").lower()

        if (user['description'] == request.form.get("description").lower()):
            updated_description = user['description']
        else:
            updated_description = request.form.get("description").lower()

        profile_update = {
            "fname": fname,
            "lname": lname,
            "email": email,
            "username": username,
            "password": password,
            "provider_name": updated_provider_name,
            "address1": updated_address1,
            "address2": updated_address2,
            "address3": updated_address3,
            "town_city": updated_town_city,
            "county": updated_county,
            "postcode": updated_postcode,
            "phone": updated_phone,
            "business_email": updated_business_email,
            "description": updated_description,
            "provider": provider
        }

        mongo.db.users.update({"_id": ObjectId(user_id)}, profile_update)
        flash("Profile updated")
        return redirect(url_for("provider_profile"))

    return render_template("provider_profile.html", user=user)


@app.route("/add_pet", methods=["GET", "POST"])
def add_pet():
    """
    Allows providers, from their profile page to add a pet
    """
    user = find_user()
    provider = user["provider_name"]
    print(provider)

    if request.method == "POST":
        pet = {
            "name": request.form.get("name").lower(),
            "description": request.form.get("description").lower(),
            "image": request.form.get("image"),
            "provider": provider
        }
        mongo.db.pets.insert_one(pet)
        flash("Pet saved!")
        return redirect(url_for("add_pet"))

    return render_template("add_pet.html", user=user)


@app.route("/update_pet/<pet_id>/<provider_name>", methods=["GET", "POST"])
def update_pet(pet_id, provider_name):
    """
    Allows user to update their pet details. 
    """
    pet = mongo.db.pets.find_one({"_id": ObjectId(pet_id)})
    print(pet)
    print(provider_name)
    print("hello")

    if request.method == "POST":
        print("trying to update")
        updated_provider = provider_name
        if (pet["name"] == request.form.get("name").lower()):
            updated_name = pet['name']
        else:
            updated_name = request.form.get("name").lower()

        if (pet["description"] == request.form.get("description").lower()):
            updated_description = pet['description']
        else:
            updated_description = request.form.get("description").lower()

        if (pet["image"] == request.form.get("image")):
            updated_image = pet['image']
        else:
            updated_image = request.form.get("image")

        profile_update = {
            "name": updated_name,
            "description": updated_description,
            "image": updated_image,
            "provider": updated_provider
        }

        mongo.db.pets.update_one({"_id": ObjectId(pet_id)}, profile_update)
        flash("Pet profile updated")
        # return redirect(url_for("provider_view_pets", provider_name=provider_name))
        return redirect(url_for("home"))


    return render_template("update_pet.html", pet=pet)


@app.route("/providers")
def providers():
    providers = mongo.db.users.find()
    return render_template("providers.html", providers=providers)


@app.route("/provider_details/<provider_name>")
def provider_details(provider_name):
    provider = mongo.db.users.find_one({"provider_name": provider_name})
    return render_template("provider_details.html", provider=provider)


@app.route("/provider_pets/<provider_name>")
def provider_pets(provider_name):
    pets = list(mongo.db.pets.find({"provider": provider_name}))
    return render_template("provider_pets.html", pets=pets)


@app.route("/provider_view_pets/<provider_name>")
def provider_view_pets(provider_name):
    pets = list(mongo.db.pets.find({"provider": provider_name}))
    return render_template("provider_view_pets.html", pets=pets)


@app.route("/pet_profile/<pet_name>")
def pet_profile(pet_name):
    pet = mongo.db.pets.find_one({"name": pet_name})
    return render_template("pet_profile.html", pet=pet)


@app.route("/delete_pet/<pet_id>/<provider_name>", methods=["GET", "POST"])
def delete_pet(pet_id, provider_name):
    """
    Queries the database and deletes the selected pet.
    """
    if request.method == "POST":
        mongo.db.pets.remove({"_id": ObjectId(pet_id)})
        flash("Pet deleted from database")
        print("pet deleted")
        return redirect(url_for("provider_view_pets", provider_name=provider_name))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)
