from flask import Flask, flash, redirect, render_template, request, session, abort
import MySQLdb

app = Flask(__name__)

def connection():
    #connection to RDS
    #conn = MySQLdb.connect(host="mlbh2h.ccr2bbshqt2i.us-west-1.rds.amazonaws.com",
    #                       user="barrybonds",
    #                       passwd="UShhjkY6",
    #                       db = "lahman2016")
    # connection to my local machine
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="Hanoi123",
                           db = "lahman2016")
    # save data output to dictionary
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    # save data to list
    #cur = conn.cursor()
    return cur, conn

@app.route("/")
def index():
    return "FLASK PROJECT"

@app.route("/teams")
def show_teams():
    cur, conn = connection()

    query = """select distinct T.name, T.teamID from Teams T JOIN
            TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName ORDER BY T.name;"""

    cur.execute(query)
    data = cur.fetchall()
    conn.close()
    # return template and value for variables in the template
    return render_template('teams.html', teams=data)

@app.route("/team/<string:teamID>/")
def display_record(teamID):
    cur, conn = connection()
    query = """SELECT name, yearID, W , L, COALESCE(ROUND(W/(W+L),2)) as percentWin
                FROM Teams where teamID= '{}';""".format(teamID)
    cur.execute(query)
    records = cur.fetchall()
    conn.close()
    return render_template("record.html", record=records)


if __name__ == "__main__":
    app.run(debug=True)
