from json import encoder
import os
import json
from sqlalchemy import create_engine
from flask import Flask,request,render_template,redirect,url_for,jsonify


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    DATABASE_URI = "postgresql://postgres:root@localhost:5432/patient"
    db = create_engine(DATABASE_URI)
    



    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    #print(db.execute("select * from medicine"))
    # a simple page that says hello
    @app.route('/')
    def hello():
        return render_template("login.html")
    
    @app.route('/login',methods = ["POST","GET"])
    def login():
        if request.method=="POST" :
            user = request.form.get("username")
            passwd = request.form.get("password")
            if(user=="Pharmacist" and passwd =="pharma"):
                return redirect(url_for("Pharmacist"))
            else:
                return render_template("invalid_login.html")
        else:
            return render_template("login.html")

    @app.route('/Pharmacist',methods = ["POST","GET"])
    def Pharmacist():
        if request.method=="GET":
            return render_template("Pharmacist.html")

    @app.route('/get_medicine',methods=["POST"])
    def get_medicine():
        if request.method=="POST":
            data = request.form.get("med_name")
            out = db.execute("select * from medicine where Name="+"'"+data+"'")
            res = [list(row) for row in out]

            res = [[str(bit) for bit in item] for item in res]
            #db.execute("insert into medicine values (999,5000.00,'Test','Test desc')")
            res = {'data':res}
            
            return render_template("med_data.html",res = res)

    return app