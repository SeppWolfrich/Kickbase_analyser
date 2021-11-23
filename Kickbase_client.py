#https://www.youtube.com/watch?v=W--_EOzdTHk tutotial
# activate venv: source ./venv/bin/activate
# python3 -m pip install "SomeProject" installing packages
# streamlit run /Users/stephanschulz/Documents/30_Projekte/DataScience/LearningPython/MiniProjects/Kickbase/Kickbase_client.py outside of python3


## Standard Libraries-----------------------------------------------
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

## Bundesliga Libraries---------------------------------------------
from soccer_data_api import SoccerDataAPI # Bundesliga standings
import requests # Scrape Bundesliga fixtures
import lxml.html as lh # Scrape Bundesliga fixtures


## SCRAPE DATA
# Get bundesliga standing from API
bundesliga_standing = pd.DataFrame(SoccerDataAPI().bundesliga()).iloc[: , :-1]  #current bundesliga table


#Scaping Ligainsider page
ligainsider = 'https://www.ligainsider.de/stats/kickbase/marktwerte/gesamt/'
page_player_information = requests.get(ligainsider) #Create a handle, page, to handle the contents of the website

doc = lh.fromstring(page_player_information.content) #Store the contents of the website under doc

tr_elements = doc.xpath('//tr') #Parse data that are stored between <tr>..</tr> of HTML


#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
    col.append((name,[]))


#Since our first row is the header, data is stored on the second row onwards
for j in range(1,len(tr_elements)):
    #T is our j'th row
    T=tr_elements[j]
    
    #If row is not of size 8, the //tr data is not from our table 
    if len(T)!=9:
        break
    
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1


Dict={title:column for (title,column) in col}
Ligainsider=pd.DataFrame(Dict)

Ligainsider = Ligainsider[['Spieler','Verein','Position','Gesamtpunkte','Einsätze','Punkteschnitt','Marktwert']]


Ligainsider.loc[Ligainsider.Verein == 'FC Bayern München', 'Verein'] = 'Bayern Munich'#
Ligainsider.loc[Ligainsider.Verein == 'Borussia Dortmund', 'Verein'] = 'Dortmund'#
Ligainsider.loc[Ligainsider.Verein == 'Eintracht Frankfurt', 'Verein'] = 'Eint Frankfurt'#
Ligainsider.loc[Ligainsider.Verein == 'SC Freiburg', 'Verein'] = 'Freiburg'#
Ligainsider.loc[Ligainsider.Verein == 'Bayer 04 Leverkusen', 'Verein'] = 'Leverkusen'#
Ligainsider.loc[Ligainsider.Verein == 'VfB Stuttgart', 'Verein'] = 'Stuttgart'#
Ligainsider.loc[Ligainsider.Verein == 'VfL Wolfsburg', 'Verein'] = 'Wolfsburg'#
Ligainsider.loc[Ligainsider.Verein == 'FC Augsburg', 'Verein'] = 'Augsburg'#
Ligainsider.loc[Ligainsider.Verein == 'TSG 1899 Hoffenheim', 'Verein'] = 'Hoffenheim'#
Ligainsider.loc[Ligainsider.Verein == '1. FSV Mainz 05', 'Verein'] = 'Mainz 05'#
Ligainsider.loc[Ligainsider.Verein == 'SpVgg Greuther Fürth', 'Verein'] = 'Greuther Fürth'#
Ligainsider.loc[Ligainsider.Verein == 'Hertha BSC', 'Verein'] = 'Hertha BSC'#
Ligainsider.loc[Ligainsider.Verein == 'Arminia Bielefeld', 'Verein'] = 'Arminia'#
Ligainsider.loc[Ligainsider.Verein == 'VfL Bochum', 'Verein'] = 'Bochum'#
Ligainsider.loc[Ligainsider.Verein == '1. FC Köln', 'Verein'] = 'Köln'#
Ligainsider.loc[Ligainsider.Verein == '1. FC Union Berlin', 'Verein'] = 'Union Berlin'#
Ligainsider.loc[Ligainsider.Verein == 'RB Leipzig', 'Verein'] = 'RB Leipzig'#
Ligainsider.loc[Ligainsider.Verein == 'Borussia Mönchengladbach', 'Verein'] = "M'Gladbach" #

#Ligainsider_final = Ligainsider
Ligainsider_final = pd.merge(Ligainsider, bundesliga_standing, left_on='Verein',right_on='team') 
Ligainsider_final = Ligainsider_final.drop('Verein',1)


# Cleaning and converting
Ligainsider_final['Spieler'] = [x.replace('\n', '') for x in Ligainsider_final['Spieler']] #removes /n 
Ligainsider_final['Spieler'] = Ligainsider_final['Spieler'].astype(str)

Ligainsider_final['Gesamtpunkte'] = [x.replace('.', '') for x in Ligainsider_final['Gesamtpunkte'].astype(str)] #remove commas or dots
Ligainsider_final['Gesamtpunkte'] = Ligainsider_final['Gesamtpunkte'].astype(int)

Ligainsider_final['Einsätze'] = Ligainsider_final['Einsätze'].replace('', 0)  #replace blanks with 0
Ligainsider_final['Einsätze'] = Ligainsider_final['Einsätze'].astype(int)

Ligainsider_final['Punkteschnitt'] = Ligainsider_final['Gesamtpunkte']/Ligainsider_final['Einsätze']
Ligainsider_final['Punkteschnitt'] = Ligainsider_final['Punkteschnitt'].fillna(0)
Ligainsider_final['Punkteschnitt'] = Ligainsider_final['Punkteschnitt'].round(2)

Ligainsider_final['Marktwert'] = [x.replace('.', '') for x in Ligainsider_final['Marktwert']] #remove commas or dots
Ligainsider_final['Marktwert'] = Ligainsider_final['Marktwert'].str.replace('€', '') #remove € sign
Ligainsider_final['Marktwert'] = Ligainsider_final['Marktwert'].astype(int)

Ligainsider_final['PreisProPunkt'] = (Ligainsider_final['Marktwert']/Ligainsider_final['Gesamtpunkte']).round(2) #compute price per point
Ligainsider_final.loc[Ligainsider_final.PreisProPunkt == np.inf, 'PreisProPunkt'] = 0
#Ligainsider_final.dtypes #check data types of columns
#Ligainsider_final['Spieler']
df = Ligainsider_final

# Importing Data
#df = pd.read_csv('/Users/stephanschulz/Documents/30_Projekte/DataScience/LearningPython/MiniProjects/Kickbase/ligainsider.csv')
#df = df.set_index('Spieler') #set Column to be displayed on chart as index


# Visualise
st.title("Kickbase Analyser v1.0 (WIP)")

# General analysis
#st.header('Generelle Analyse aller Spieler der Bundesliga unabhängig vom Verein')
st.subheader('Durchschnittliche Punkte (gesamte Bundesliga)')

col1, col2, col3, col4 = st.columns(4)
col1.metric("Torhüter Punkte", df.loc[(df['Position'] == 'Torhüter') & (df['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col2.metric("Verteidiger Punkte", df.loc[(df['Position'] == 'Abwehrspieler') & (df['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col3.metric("Mittelfeld Punkte", df.loc[(df['Position'] == 'Mittelfeldspieler') & (df['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col4.metric("Stürmer Punkte", df.loc[(df['Position'] == 'Stürmer') & (df['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))

#st.caption('Überraschenderweise schneiden Stürmer aktuell am schlechtesten ab.')


# Per Team Deep Dive
st.subheader('Team Analyse')

col = st.selectbox("Select Team", (df['team'].unique()))
df1 = df[df['team']==col]


# Show table of team if clicked
if st.checkbox("Show Rawdata"):
    st.write(df1[['Spieler','Marktwert','Gesamtpunkte','Punkteschnitt', 'PreisProPunkt', 'Einsätze']].sort_values('Gesamtpunkte', ascending = False))


col1, col2, col3 = st.columns(3)
col1.metric('Tabellenplatz', df1['pos'].iloc[0])

Gesamtpunkte = df1['Gesamtpunkte'].astype(float).sum().round(2)
Gesamtpunkte_adjusted = "{:,.0f}".format(Gesamtpunkte)
col2.metric('Gesamtpunkte', Gesamtpunkte_adjusted)

Marktwert = df1['Marktwert'].astype(float).sum().round(2)
Marktwert_EUR = "€{:,.0f}".format(Marktwert)
col3.metric('Gesamtmarktwert', Marktwert_EUR)


col1, col2, col3, col4 = st.columns(4)
col1.metric("Torhüter Punkte", df1.loc[(df1['Position'] == 'Torhüter') & (df1['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col2.metric("Verteidiger Punkte", df1.loc[(df1['Position'] == 'Abwehrspieler') & (df1['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col3.metric("Mittelfeld Punkte", df1.loc[(df1['Position'] == 'Mittelfeldspieler') & (df1['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))
col4.metric("Stürmer Punkte", df1.loc[(df1['Position'] == 'Stürmer') & (df1['Einsätze'] != 0), 'Gesamtpunkte'].mean().round(2))


# Visuals
st.altair_chart(alt.Chart(df1).mark_bar().encode(
    x=alt.X('Spieler', sort='-y'),
    y='Gesamtpunkte', color = 'Position',
    tooltip=["Spieler","Gesamtpunkte",'PreisProPunkt',"Position"]
).interactive(),use_container_width=True)

st.altair_chart(alt.Chart(df1).mark_bar().encode(
    x=alt.X('Spieler', sort='-y'),
    y='Punkteschnitt', color = 'Position',
    tooltip=["Spieler","Punkteschnitt",'PreisProPunkt',"Position"]
).interactive(),use_container_width=True)

st.altair_chart(alt.Chart(df1).mark_bar().encode(
    x=alt.X('Spieler', sort='-y'),
    y='Marktwert', color = 'Position',
    tooltip=["Spieler","Gesamtpunkte",'Marktwert','PreisProPunkt',"Position"]
).interactive(),use_container_width=True)