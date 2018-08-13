from flask import Flask, flash, redirect, render_template, request, session, abort
import MySQLdb
from config import *

app = Flask(__name__)
config = Config()

def connection():

    conn = MySQLdb.connect(host=config.dbhost,
                           user=config.dbuser,
                           passwd=config.dbpw,
                           db = config.dbname)
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

    query = """select distinct T.name, T.franchID from Teams T JOIN
            TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName ORDER BY T.name;"""

    cur.execute(query)
    data = cur.fetchall()
    len_data = len(data)
    conn.close()
    print("inside show team")
    # return template and value for variables in the template
    return render_template('teams.html', teams=data, len_data=len_data)

@app.route("/team/<string:franchID>/")
def display_record(franchID):
    cur, conn = connection()
    query = """SELECT name, yearID, W , L, COALESCE(ROUND(W/(W+L),3)) as percentWin
                FROM Teams where franchID= '{}';""".format(franchID)
    cur.execute(query)
    records = cur.fetchall()
    conn.close()
    return render_template("record.html", record=records)

@app.route("/SFG-LAD")
def displayComparison():
    return render_template("compare.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
