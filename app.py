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

@app.route("/about")
def aboutPage():
    return render_template("about.html")

@app.route("/")
def show_teams():
    cur, conn = connection()

    query = """SELECT distinct T.name, T.franchID, T.teamID
               FROM lahman2016.Teams T JOIN lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID
               WHERE TF.active="Y" AND T.name=TF.franchName
               ORDER BY T.name;"""
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
               FROM lahman2016.Teams
               WHERE franchID= '{}'
               GROUP BY yearID;""".format(franchID)
    cur.execute(query)
    records = cur.fetchall()

    team_query = """SELECT distinct T.name, T.franchID, T.teamID
                    FROM lahman2016.Teams T JOIN lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID
                    WHERE TF.active="Y" AND T.name=TF.franchName
                        AND T.franchID != '{}' ORDER BY T.name;""".format(franchID)
    cur.execute(team_query)
    all_teams = cur.fetchall()
    len_data = len(all_teams)
    conn.close()
    return render_template("record.html", record=records, franchID=franchID, teams=all_teams, len_data=len_data)

@app.route("/compare/<franchID1>/<franchID2>")
def displayComparison(franchID1, franchID2):
    cur, conn = connection()
    name_query = """SELECT distinct T.name, T.franchID, T.teamID
                    FROM lahman2016.Teams T JOIN lahman2016.TeamsFranchises TF ON T.franchID = TF.franchID
                    WHERE TF.active="Y" AND T.name=TF.franchName
                            AND (T.franchID = '{}' OR T.franchID = '{}');""".format(franchID1, franchID2)
    cur.execute(name_query)
    two_teams = cur.fetchall()
    for team in two_teams:
        if team['franchID'] == franchID1:
            team1_name = team['name'].upper()
        elif team['franchID'] == franchID2:
            team2_name = team['name'].upper()

    query =  """SELECT any_value(home) as team1,
                       any_value(visitor) as team2,
                       max(YEAR(date)) as yearID,
                       SUM(case when ((home_score>visitor_score and home in (select teamID from lahman2016.Teams where franchID="{0}"))
                            OR (home_score<visitor_score
                                AND home in (select teamID from lahman2016.Teams where franchID="{1}"))) then 1 else 0 end) as Team1_WIN,
                       SUM(case when ((home_score<visitor_score and home in(select teamID from lahman2016.Teams where franchID="{0}"))
                            OR (home_score>visitor_score
                                AND home in (select teamID FROM lahman2016.Teams WHERE franchID="{1}"))) then 1 else 0 end) as Team2_WIN
                FROM retrosheet.games
                WHERE (visitor in (select teamID from lahman2016.Teams where franchID="{0}") OR visitor in (select teamID from
                        lahman2016.Teams where franchID="{1}")) and (home in (select teamID from lahman2016.Teams where franchID="{0}")
                        OR home in (select teamID from lahman2016.Teams where franchID="{1}"))
                GROUP BY YEAR(date);""".format(franchID1, franchID2)
    cur.execute(query)
    records = cur.fetchall()

    for year in records:
        total_games = year['Team1_WIN'] + year['Team2_WIN']
        year['percentWin'] = round((year['Team1_WIN']/total_games),3)
        year['total_games'] = total_games
    total1_win = sum(game['Team1_WIN'] for game in records)
    total2_win = sum(game['Team2_WIN'] for game in records)
    num_game = sum(game['total_games'] for game in records)
    percent1_win = round(total1_win/num_game, 3)

    conn.close()
    return render_template("compare.html", record=records, team1=team1_name,
                           team2=team2_name, num_game=num_game, total1_win=total1_win,
                           total2_win=total2_win, percent1_win=percent1_win)

@app.route("/compare/<startYear>/<endYear>")
def showBetweenYears(startYear, endYear):
    cur, conn = connection()
    query = """SELECT any_value(home) as team1,
                    any_value(visitor) as team2,
                    max(YEAR(date)) as yearID,
                    SUM(case when ((home_score>visitor_score and home in (select teamID from lahman2016.Teams WHERE franchID="{0}"))
                        OR (home_score<visitor_score and home in (select teamID from lahman2016.Teams WHERE franchID="{1}"))) then 1 else 0 end) as Team1_WIN,
                    SUM(case when ((home_score<visitor_score and home in(select teamID from lahman2016.Teams where franchID="{0}"))
                        OR (home_score>visitor_score and home in (select teamID from lahman2016.Teams where franchID="{1}"))) then 1 else 0 end) as Team2_WIN
                FROM retrosheet.games
                WHERE (visitor in (select teamID from lahman2016.Teams where franchID="{0}")
                        OR visitor in (select teamID from lahman2016.Teams where franchID="{1}"))
                        AND (home in (select teamID from lahman2016.Teams where franchID="{0}")
                        OR home in (select teamID from lahman2016.Teams where franchID="{1}"))
                        AND (YEAR(date) between '{2}' and '{3}')
                GROUP BY YEAR(date);""".format(franchID1, franchID2, startYear, endYear)
    cur.execute(query)
    year_range = cur.fetchall()

    return "test"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
