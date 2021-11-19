from json import encoder
import os
import json
from sqlalchemy import create_engine
from flask import Flask,request,render_template,redirect,url_for,session


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
        session["Pharmacist"] = False
        session["Room_Manager"] = False
        session["Receptionist"] = False
        return render_template("login.html")
    
    @app.route('/login',methods = ["POST","GET"])
    def login():
        if request.method=="POST" :
            user = request.form.get("username")
            passwd = request.form.get("password")
            if(user=="Pharmacist" and passwd =="pharma"):
                session["Pharmacist"] = True
                return redirect(url_for("Pharmacist"))
            elif(user=="Room_Manager" and passwd =="room_manager"):
                session["Room_Manager"] = True
                return redirect(url_for("Room_Manager"))
            elif(user=="Receptionist" and passwd =="reception"):
                session["Receptionist"] = True
                return redirect(url_for("Receptionist"))
            else:
                return render_template("invalid_login.html")
        else:
            return render_template("login.html")

    @app.route('/Pharmacist',methods = ["POST","GET"])
    def Pharmacist():
        if request.method=="GET":
            if session["Pharmacist"] :
                return render_template("Pharmacist.html")
            else:
                return render_template("login.html")
                

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



    @app.route("/Room_Manager",methods=["POST","GET"])
    def Room_Manager():
        if request.method=="GET":
            if session["Room_Manager"] :
                return render_template("Room_Manager.html")
            else:
                return render_template("login.html")

    @app.route('/get_room',methods=["POST"])
    def get_room():
        if request.method=="POST":
            data = request.form.get("room_type")
            out = db.execute("select * from room where type="+"'"+data+"'")
            res = [list(row) for row in out]

            res = [[str(bit) for bit in item] for item in res]
            #db.execute("insert into medicine values (999,5000.00,'Test','Test desc')")
            res = {'data':res}
            
            return render_template("room_details.html",res = res)

    @app.route('/add_room',methods=["POST"])
    def add_room():
        if request.method=="POST":

            existing=0

            existing_names= db.execute("select type from room")
            existing_names = [list(row) for row in existing_names]
            existing_names = [[str(bit) for bit in item] for item in existing_names]
            existing_names = [item[0] for item in existing_names]

            new_type = request.form.get("new_room_type")
            new_cost = request.form.get("new_room_cost")
            
            if new_type in existing_names:
                existing=1
            
            max_id = db.execute("select max(room_id) from room")
            max_id = [list(row) for row in max_id]
            max_id = [[int((str(bit))) for bit in item] for item in max_id]
            max_id = [item[0] for item in max_id]

            max_id = max_id[0] + 1

            if(existing == 0):
                db.execute("insert into room values ("+str(max_id)+",'"+new_type+"',"+new_cost+")")
            else:
                db.execute("update room set cost = "+new_cost+ " where type = '"+new_type+"'" )
            
            return render_template("room_insert_res.html",exists = existing)

    @app.route('/assign_nurse',methods=["POST"])
    def assign_nurse():
        if request.method=="POST":
            nurse_fname = request.form.get("nurse_fname")
            nurse_mname = request.form.get("nurse_mname")
            nurse_lname = request.form.get("nurse_lname")

            room_type = request.form.get("n_room_type")

            

            rooms = db.execute("select type from room")
            rooms = [list(row) for row in rooms]
            rooms = [str(item[0]) for item in rooms]

            nurses = db.execute("select n_id from nurse where fname = '"+nurse_fname+"' and mname = '"+nurse_mname+"' and lname = '"+nurse_lname+"' ")
            nurses = [list(row)[0] for row in nurses]

            if room_type not in rooms:
                data = dict()
                data["room_not_exist"] = 1
                return render_template("room_nurse_assign.html",data = data)
            elif len(nurses)==0:
                data = dict()
                data["nurse_not_exist"] = 1
                return render_template("room_nurse_assign.html",data = data)
            else:
                data = dict()
                data["room_not_exist"] = 0
                data["nurse_not_exist"] = 0
                r_id = db.execute("select room_id from room where type = '"+room_type+"'")
                r_id = [str(list(row)[0]) for row in r_id]
                r_id = r_id[0]
                n_id = nurses[0]

                db.execute("update nurse set room_id = '"+ r_id +"' where n_id = '"+ n_id+"'")
                return render_template("room_nurse_assign.html",data =data)
                

    @app.route("/Receptionist",methods=["POST","GET"])
    def Receptionist():
        if request.method=="GET":
            if session["Receptionist"] :
                return render_template("Receptionist.html")
            else:
                return render_template("login.html")

    @app.route("/add_patient",methods=["POST"])
    def add_patient():
        if request.method=="POST":

            patient_fname = request.form.get("patient_fname")
          
            patient_mname = request.form.get("patient_mname")
       
            patient_lname = request.form.get("patient_lname")

            patients = db.execute("select patient_id from patient where fname = '"+patient_fname+"' and mname = '"+patient_mname+"' and lname = '"+patient_lname+"' ")
            patients = [list(row)[0] for row in patients]

            age = request.form.get("patient_age")
            phone = request.form.get("patient_phone")

            gender = request.form.get("patient_gender")
         

            if gender == "Male":
                gender = "M"
            else:
                gender = "F"
            

           
            admit_date = request.form.get("patient_admit_date")
            room_type = request.form.get("patient_room_type")


            rooms = db.execute("select type from room")
            rooms = [list(row) for row in rooms]
            rooms = [str(item[0]) for item in rooms]

            doc_fname = request.form.get("attending_doc_fname")
            doc_mname = request.form.get("attending_doc_mname")
            doc_lname = request.form.get("attending_doc_lname")


            docs = db.execute("select doctor_id from doctor where fname = '"+doc_fname+"' and mname = '"+doc_mname+"' and lname = '"+doc_lname+"' ")
            docs = [list(row)[0] for row in docs]

            max_id = db.execute("select max(patient_id) from patient")
            max_id = [list(row) for row in max_id]
            max_id = [[int((str(bit))) for bit in item] for item in max_id]
            max_id = [item[0] for item in max_id]

            max_id = max_id[0] + 1

            if len(patients)>0:
                data = dict()
                data["patient_already_exist"]  = 1
                return render_template("patient_insert_res.html",data = data)
            elif room_type not in rooms:
                data = dict()
                data["room_not_exist"] = 1
                return render_template("patient_insert_res.html",data = data)
            elif len(docs)==0:
                data = dict()
                data["doc_not_exist"] = 1
                return render_template("patient_insert_res.html",data = data)
            else:
                data = dict()
                data["room_not_exist"] = 0
                data["nurse_not_exist"] = 0
                r_id = db.execute("select room_id from room where type = '"+room_type+"'")
                r_id = [str(list(row)[0]) for row in r_id]
                r_id = r_id[0]
                doc_id = docs[0]

                db.execute("insert into patient values ('"+str(max_id)+"','"+patient_fname+"','"+patient_mname+"','"+patient_lname+"',NULL,NULL,'"+r_id+"','"+gender+"','"+phone+"','"+age+"',NULL,'"+doc_id+"','"+admit_date+"',NULL) ")
                return render_template("patient_insert_res.html",data =data)

    @app.route("/discharge_patient",methods=["POST"])
    def discharge_patient():
        if request.method=="POST":
            d_patient_fname = request.form.get("d_patient_fname")
          
            d_patient_mname = request.form.get("d_patient_mname")
       
            d_patient_lname = request.form.get("d_patient_lname")

            discharge_date = request.form.get("patient_discharge_date")

            patients = db.execute("select patient_id from patient where fname = '"+d_patient_fname+"' and mname = '"+d_patient_mname+"' and lname = '"+d_patient_lname+"' ")
            patients = [list(row)[0] for row in patients]

            if(len(patients)==0):
                data = dict()
                data["patient_not_exist"] = 1
                return render_template("patient_discharge_res.html",data = data)
            else:
                data = dict()
                data["patient_not_exist"] = 0
                db.execute("update patient set discharge_date = '"+discharge_date+"' where patient_id = '"+str(patients[0])+"'")
                return render_template("patient_discharge_res.html",data = data)
                



    return app