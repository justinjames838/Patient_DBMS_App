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
    @app.route('/add_medicine',methods=["POST"])
    def add_medicine():
        if request.method=="POST":

            existing=0

            existing_names= db.execute("select name from medicine")
            existing_names = [list(row) for row in existing_names]
            existing_names = [[str(bit) for bit in item] for item in existing_names]
            existing_names = [item[0] for item in existing_names]

            new_name = request.form.get("new_med_name")
            new_cost = request.form.get("new_med_cost")
            new_info = request.form.get("new_med_info")
            if new_name in existing_names:
                existing=1
            
            max_id = db.execute("select max(medicine_id) from medicine")
            max_id = [list(row) for row in max_id]
            max_id = [[int((str(bit))) for bit in item] for item in max_id]
            max_id = [item[0] for item in max_id]

            max_id = max_id[0] + 1

            if(existing == 0):
                db.execute("insert into medicine values ("+str(max_id)+","+new_cost+",'"+new_name+"'"+",'"+new_info+"'"+")")
            else:
                db.execute("update medicine set cost = "+new_cost+",info = '"+new_info+"'"+ "where name = '"+new_name+"'" )
            
            return render_template("med_insert_res.html",exists = existing)

    return app