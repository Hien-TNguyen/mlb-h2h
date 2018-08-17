from flask import Flask, flash, redirect, render_template, request, session, abort
import MySQLdb
from config import *

app = Flask(__name__)
config = Config()

app.url_map

def connection():

    conn = MySQLdb.connect(host=config.dbhost,
                           user=config.dbuser,
                           passwd=config.dbpw,
                           #db = dbname,
                           port = config.dbport)
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

    query = """select distinct T.name, T.franchID, T.teamID
            from lahman2016.Teams T JOIN lahman2016.TeamsFranchises TF
            ON T.franchID = TF.franchID Where TF.active="Y"
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
    cur, conn = connection()
    query = """SELECT name, yearID, W , L, COALESCE(ROUND(W/(W+L),2)) as percentWin
                FROM lahman2016.Teams where teamID= '{}' GROUP BY yearID;""".format(teamID)
    cur.execute(query)
    records = cur.fetchall()

    team_query = """select distinct T.name, T.franchID, T.teamID from lahman2016.Teams T JOIN
            lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName AND T.teamID != '{}' ORDER BY T.name;""".format(teamID)
    cur.execute(team_query)
    all_teams = cur.fetchall()
    len_data = len(all_teams)
    conn.close()
    return render_template("record.html", record=records, teamID=teamID, teams=all_teams, len_data=len_data)

@app.route("/compare/<teamID1>/<teamID2>")
def displayComparison(teamID1, teamID2):
    cur, conn = connection()
    query = """SELECT any_value(home) as team1, any_value(visitor) as team2, max(YEAR(date)) as yearID,
                SUM(case when ((home_score>visitor_score and home='{0}') OR
                (home_score<visitor_score and home='{1}')) then 1 else 0 end) as Team1_WIN,
                SUM(case when ((home_score<visitor_score and home='{0}') OR
                (home_score>visitor_score and home='{1}')) then 1 else 0 end) as Team2_WIN
                from retrosheet.games where (visitor="{0}" OR visitor="{1}") and (home="{0}" OR home="{1}")
                GROUP BY YEAR(date);""".format(teamID1, teamID2)
    cur.execute(query)
    records = cur.fetchall()
    for year in records:
        total_games = year['Team1_WIN'] + year['Team2_WIN']
        year['percentWin'] = round((year['Team1_WIN']/total_games),3)
        year['total_games'] = total_games
    num_game = sum(game['total_games'] for game in records)

    name_query = """select distinct T.name, T.franchID, T.teamID from lahman2016.Teams T JOIN
            lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName AND (T.teamID = '{}' OR T.teamID = '{}');""".format(teamID1, teamID2)
    cur.execute(name_query)
    two_teams = cur.fetchall()
    if two_teams[0]['teamID'] == teamID1:
        team1_name = two_teams[0]['name'].upper()
        team2_name = two_teams[1]['name'].upper()
    elif two_teams[0]['teamID'] == teamID2:
        team2_name = two_teams[0]['name'].upper()
        team1_name = two_teams[1]['name'].upper()
    conn.close()
    return render_template("compare.html", record=records, team1=team1_name,
                           team2=team2_name, num_game=num_game)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
