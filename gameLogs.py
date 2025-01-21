from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import os
from flask import Flask, render_template, request

def findTblAndHeaders(teamReq):
    fullURL = ('https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2024%7C&hfSit='
                 '&player_type=batter&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=&game_date_lt=&hfMo=&hfTeam='
                    + teamReq + '%7C&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&metric_1=&group_by=name-event&min_pitches=0'
                 '&min_results=0&min_pas=0&sort_col=ba&player_event_sort=api_h_launch_speed&sort_order=desc&chk_event_release_speed=on&chk_event_launch_speed=on'
                 '&chk_event_estimated_ba_using_speedangle=on&chk_event_estimated_slg_using_speedangle=on#results')
    print('getting results from:', fullURL)
    page = requests.get(fullURL)
    soup = BeautifulSoup(page.content, 'html.parser') 
    results=soup.find(id="search-results")
    tbl=results.find("table")
    cells=results.find_all("td")
    headers=results.find_all("thead")    
    headerList = [h.text for h in headers[0].find_all("th")]
    return tbl, headerList

def checkRow(theRow):
    cols = theRow.find_all("td")
    if len(cols) > 1:        
        return True
    return False
    
def getRow(theRow):
    oneRow = []
    cols = theRow.find_all("td")
    for c in cols:
        oneRow.append(c.text)
    return oneRow

def getTable(theTable):
    rows = theTable.find_all("tr")
    dataRows = [] #get all current stats
    for r in rows: 
        if checkRow(r):
            dataRows.append(getRow(r))
    return dataRows

def getRawData(team):
    typeDict = {'Player':'string','Team':'string','Result':'string','Game Date':'string','Vs.':'string','Pitch (MPH)':'float16','EV (MPH)':'float16','xBA':'float16',
                'xSLG':'float16'}
    tbl, headerList = findTblAndHeaders(team)
    myTbl = getTable(tbl)
    newTbl = [[c.replace('\n', '').strip() for c in r] for r in myTbl]
    newHeaders = [h.replace('\n', '').strip() for h in headerList]
    rawLogsDf = pd.DataFrame(newTbl, columns= newHeaders)
    reqHeaders = [h for h in newHeaders if len(h) > 1 and h[:2] != 'Rk']
    rawLogsDf = rawLogsDf[reqHeaders]    
    rawLogsDf = rawLogsDf.astype(typeDict).sort_values(by = 'Game Date', ascending=False)
    
    return rawLogsDf
    
def writeToFile(output, fileName):
    with open(fileName, 'w') as f:        
        f.write(output)  
        f.close()
    
def DfToTbl(df):
    out = '<html><head><style>table {  font-family: arial, sans-serif;  border-collapse: collapse;  width: 100%;}'
    out += 'td, th {  border: 1px solid #dddddd;  text-align: left;  padding: 8px;} tr:nth-child(even) '
    out += '{background-color: #dddddd;}</style></head>'
    out += '<table>'
    headers = list(df.columns)
    out += '<tr>'
    for h in headers:
        out += '<th>' + h + '</th>'
    out += '</tr>'
    for r in range(len(df)):
        out += '<tr>'
        for c in range(len(headers)):
            out += '<td>' + str(df.iloc[r,c]) + '</td>'
        out += '</tr>'
    out += '</table></html>'

    return out
    
def makeDropDownFromList(vals):

    out = '<form method="post"> <select name = "team" onchange = "this.form.submit()">'

    for v in vals:
        out += '<option>' + v + '</option>'
    out += '</select></form>'
    
    return out

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():    
        
    teams = ['ATL', 'AZ', 'BAL', 'BOS', 'CHC', 'CIN', 'CLE', 'COL', 'CWS', 'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 		'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB ', 'TEX', 'TOR', 'WSH']
    
    htmlReq = '<h1> Game Logs </h1> <br><br> <h2> Please select team: <h2>'
    htmlReq = makeDropDownFromList(teams)
    
    htmlReq += '<br><br>'
    
    if request.method == 'POST':
        print('team is:', request.form['team'])
        df = getRawData(request.form['team'])
        htmlReq += DfToTbl(df)

    writeToFile(htmlReq, os.path.join(os.getcwd(), 'templates/rawData.html'))
    
    return render_template('rawData.html')

