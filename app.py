from flask import Flask, flash, redirect, render_template, request, session, abort
import MySQLdb
from config import *

app = Flask(__name__)
config = Config()

app.url_map

def connection(dbname):

    conn = MySQLdb.connect(host=config.dbhost,
                           user=config.dbuser,
                           passwd=config.dbpw,
                           db = dbname)
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
    cur, conn = connection("lahman2016")

    query = """select distinct T.name, T.franchID, T.teamID from Teams T JOIN
            TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName ORDER BY T.name;"""

    cur.execute(query)
    data = cur.fetchall()
    len_data = len(data)
    conn.close()
    print("inside show team")
    # return template and value for variables in the template
    return render_template('teams.html', teams=data, len_data=len_data)

@app.route("/team/<teamID>")
def display_record(teamID):
    cur, conn = connection("lahman2016")
    query = """SELECT name, yearID, W , L, COALESCE(ROUND(W/(W+L),2)) as percentWin
                FROM Teams where teamID= '{}' GROUP BY yearID;""".format(teamID)
    cur.execute(query)
    records = cur.fetchall()

    team_query = """select distinct T.name, T.franchID, T.teamID from Teams T JOIN
            TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName AND T.teamID != '{}' ORDER BY T.name;""".format(teamID)
    cur.execute(team_query)
    all_teams = cur.fetchall()
    len_data = len(all_teams)
    conn.close()
    return render_template("record.html", record=records, teamID=teamID, teams=all_teams, len_data=len_data)

@app.route("/compare/<teamID1>/<teamID2>")
def displayComparison(teamID1, teamID2):
    cur, conn = connection("retrosheet")
    query = """SELECT any_value(home) as team1, any_value(visitor) as team2, max(YEAR(date)) as yearID,
                SUM(case when ((home_score>visitor_score and home='{0}') OR
                (home_score<visitor_score and home='{1}')) then 1 else 0 end) as Team1_WIN,
                SUM(case when ((home_score<visitor_score and home='{0}') OR
                (home_score>visitor_score and home='{1}')) then 1 else 0 end) as Team2_WIN
                from games where (visitor="{0}" OR visitor="{1}") and (home="{0}" OR home="{1}")
                GROUP BY YEAR(date);""".format(teamID1, teamID2)
    cur.execute(query)
    records = cur.fetchall()
    conn.close()

    return render_template("compare.html", record=records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
