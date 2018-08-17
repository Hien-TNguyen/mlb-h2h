from flask import Flask, flash, redirect, render_template, request, session, abort
import MySQLdb
from config import *

app = Flask(__name__)
config = Config()

def connection():
    conn = MySQLdb.connect(host=config.dbhost,
                           user=config.dbuser,
                           passwd=config.dbpw,
                           #db = dbname,
                           port = config.dbport)
    # save data output to dictionary
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
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

@app.route("/team/<franchID>")
def display_record(franchID):
    cur, conn = connection()
    query = """SELECT name, yearID, W , L, COALESCE(ROUND(W/(W+L),2)) as percentWin
                FROM lahman2016.Teams where franchID= '{}' GROUP BY yearID;""".format(franchID)
    cur.execute(query)
    records = cur.fetchall()

    team_query = """select distinct T.name, T.franchID, T.teamID from lahman2016.Teams T JOIN
            lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName AND T.franchID != '{}' ORDER BY T.name;""".format(franchID)
    cur.execute(team_query)
    all_teams = cur.fetchall()
    len_data = len(all_teams)
    conn.close()
    return render_template("record.html", record=records, franchID=franchID, teams=all_teams, len_data=len_data)

@app.route("/compare/<franchID1>/<franchID2>")
def displayComparison(franchID1, franchID2):
    cur, conn = connection()
    name_query = """select distinct T.name, T.franchID, T.teamID from lahman2016.Teams T JOIN
            lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID Where TF.active="Y"
            AND T.name=TF.franchName AND (T.franchID = '{}' OR T.franchID = '{}');""".format(franchID1, franchID2)
    cur.execute(name_query)
    two_teams = cur.fetchall()
    if two_teams[0]['franchID'] == franchID1:
        team1_name = two_teams[0]['name'].upper()
        teamID1 = two_teams[0]['teamID']
        team2_name = two_teams[1]['name'].upper()
        teamID2 = two_teams[1]['teamID']
    elif two_teams[0]['franchID'] == franchID2:
        team2_name = two_teams[0]['name'].upper()
        teamID2 = two_teams[0]['teamID']
        team1_name = two_teams[1]['name'].upper()
        teamID1 = two_teams[1]['teamID']

    query = """SELECT any_value(home) as team1, any_value(visitor) as team2, max(YEAR(date)) as yearID,
                SUM(case when ((home_score>visitor_score and home='{0}') OR
                (home_score<visitor_score and home='{1}')) then 1 else 0 end) as Team1_WIN,
                SUM(case when ((home_score<visitor_score and home='{0}') OR
                (home_score>visitor_score and home='{1}')) then 1 else 0 end) as Team2_WIN
                from retrosheet.games where (visitor="{0}" OR visitor="{1}") and (home="{0}" OR home="{1}")
                GROUP BY YEAR(date);""".format(teamID1, teamID2)

    # handle special team who change the teamID
    # Florida Marlins(FLO) changed to Miami Marlins(MIA)
    query_miami ="""SELECT any_value(home) as team1, any_value(visitor) as team2, max(YEAR(date)) as yearID,
                SUM(case when ((home_score>visitor_score and (home='{0}' or home='MIA')) OR
                (home_score<visitor_score and home='{1}')) then 1 else 0 end) as Team1_WIN,
                SUM(case when ((home_score<visitor_score and (home='{0}' or home='MIA')) OR
                (home_score>visitor_score and home='{1}')) then 1 else 0 end) as Team2_WIN
                from retrosheet.games where (visitor="{0}" OR visitor="{1}" or visitor='MIA')
                and (home="{0}" OR home="{1}" or home='MIA')
                GROUP BY YEAR(date);""".format(teamID1, teamID2)
    if franchID1 != "FLA":
        cur.execute(query)
    else:
        cur.execute(query_miami)

    records = cur.fetchall()
    for year in records:
        total_games = year['Team1_WIN'] + year['Team2_WIN']
        year['percentWin'] = round((year['Team1_WIN']/total_games),3)
        year['total_games'] = total_games
    num_game = sum(game['total_games'] for game in records)

    conn.close()
    return render_template("compare.html", record=records, team1=team1_name,
                           team2=team2_name, num_game=num_game)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
