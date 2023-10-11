#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 13:37:50 2023

@author: michaelmcgarry
"""

import streamlit as st
import pandas as pd
#import datetime
#from matplotlib import pyplot as plt
#import matplotlib.patches as patches
#import seaborn as sns
import base64
import io

#Define Functions Here
weekdays = {0: 'Mon',
           1: 'Tue',
           2: 'Wed',
           3: 'Thu',
           4: 'Fri',
           5: 'Sat',
           6: 'Sun'}

def get_comp_fixtures_by_month(df,sport,country,competition):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")
        
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    _['Month'] = _['StartDateTime'].apply(lambda x: x.month)
    
    total_events = len(_)
    
    #Group by Months and total the number of events each month
    _ = _.groupby(['Sport','Country','Competition','Month']).agg(NumEvents=('Description','count')).reset_index()
    
    #Calculate Percentage of Events
    _['PctEvents'] = round(_['NumEvents'] / total_events*100,2)
    
    # Create a reference DataFrame with all months
    all_months = pd.DataFrame({'Month': range(1, 13)})
    
    # Merge the reference DataFrame with the original DataFrame
    merged_df = _.merge(all_months, on='Month', how='outer')
    
    # Fill missing values with 0 and set Sport, Country, and Competition
    merged_df['NumEvents'].fillna(0, inplace=True)
    merged_df['PctEvents'].fillna(0, inplace=True)
    merged_df['Sport'].fillna(sport, inplace=True)
    merged_df['Country'].fillna(country, inplace=True)
    merged_df['Competition'].fillna(competition, inplace=True)
    
    # Sort the DataFrame by 'Month' in ascending order
    merged_df.sort_values(by='Month', inplace=True)
    
    return merged_df

def get_pct_matches_weekdays(df,weekdays,sport,country,competition):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")   
    
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    
    total_events = len(_)        
    
    #Group by Weekdays and get a count of fixtures each day
    _ = _.groupby(['Sport','Country','Competition','Weekday']).agg(NumEvents=('Description','count')).reset_index()
    
    #Calc Percentage of Events on each day
    _['PctEvents'] = round(_['NumEvents'] / total_events * 100,2)
    
    # Create a reference DataFrame with all days
    all_months = pd.DataFrame({'Weekday': range(7)})
    
    # Merge the reference DataFrame with the original DataFrame
    merged_df = _.merge(all_months, on='Weekday', how='outer')
    
    # Fill missing values with 0 and set Sport, Country, and Competition
    merged_df['NumEvents'].fillna(0, inplace=True)
    merged_df['PctEvents'].fillna(0, inplace=True)
    merged_df['Sport'].fillna(sport, inplace=True)
    merged_df['Country'].fillna(country, inplace=True)
    merged_df['Competition'].fillna(competition, inplace=True)
    
    # Sort the DataFrame by 'Month' in ascending order
    merged_df.sort_values(by='Weekday', inplace=True)
    
    merged_df['Weekday'] = merged_df['Weekday'].apply(lambda x: weekdays[x])
    
    return merged_df

def get_concurrency_percentile_rank(row,df):
    sport = row['Sport']
    country = row['Country']
    competition = row['Competition']
    region = df.loc[df['Country']==country]['Region'].unique().item()
    
    Self = row['AvgConcurrentSelf']
    s = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)]['ConcurrentSelf']
    self_rank = round((s > Self).sum() / len(s) * 100,2)
    
    All = row['AvgConcurrentAll']
    s = df['ConcurrentAll']
    all_rank = round((s > All).sum() / len(s) * 100,2)
    
    Sport = row['AvgConcurrentSport']
    s = df.loc[df['Sport']==sport]['ConcurrentSport']
    sport_rank = round((s > Sport).sum() / len(s) * 100,2)
    
    Country = row['AvgConcurrentCountry']
    s = df.loc[df['Country']==country]['ConcurrentCountry']
    country_rank = round((s > Country).sum() / len(s) * 100,2)
    
    Region = row['AvgConcurrentRegion']
    s = df.loc[df['Region'] == region]['ConcurrentRegion']
    region_rank = round((s > Region).sum() / len(s) * 100,2)
    
    SportCountry = row['AvgConcurrentSportCountry']
    s = df.loc[(df['Sport']==sport)&(df['Country']==country)]['ConcurrentSportCountry']
    sportcountry_rank = round((s > SportCountry).sum() / len(s) * 100,2)
    
    SportRegion = row['AvgConcurrentSportRegion']
    s = df.loc[(df['Sport']==sport)&(df['Region']==region)]['ConcurrentSportRegion']
    sportregion_rank = round((s > SportRegion).sum() / len(s) * 100,2)
    
    return pd.Series([self_rank, all_rank, sport_rank, country_rank, region_rank, sportcountry_rank, sportregion_rank])


def get_pct_matches_start_times(df,weekdays,sport,country,competition,threshold=0.0):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")   
    
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    _['StartTime'] = _['StartDateTime'].apply(lambda x: x.time())
    total_events = len(_)        
    
    #Group by Weekdays and Start Times and get a count of fixtures for each start time
    #Get Avg Concurrency for each Concurrency Type also
    _ = _.groupby(['Sport','Country','Competition','Weekday','StartTime']).agg(NumEvents=('Description','count'),
                                                                              AvgConcurrentSelf=('ConcurrentSelf','mean'),
                                                                              AvgConcurrentAll=('ConcurrentAll','mean'),
                                                                              AvgConcurrentSport=('ConcurrentSport','mean'),
                                                                              AvgConcurrentCountry=('ConcurrentCountry','mean'),
                                                                              AvgConcurrentRegion=('ConcurrentRegion','mean'),
                                                                              AvgConcurrentSportCountry=('ConcurrentSportCountry','mean'),
                                                                              AvgConcurrentSportRegion=('ConcurrentSportRegion','mean')).reset_index()
    
    #Get Percentile Ranks For Each Concurrency View
    ranks = _.apply(lambda x: get_concurrency_percentile_rank(x,df),axis=1)
    
    #Add percentile ranks to dataframe
    _ = pd.concat([_,ranks],axis=1)
    
    #Calculate Average Concurrency Rank
    AvgRank = round(_[[0,1,2,3,4,5,6]].mean(axis=1),0)
    
    col_names = {0: 'RankSelf',
                1: 'RankAll',
                2: 'RankSport',
                3: 'RankCountry',
                4: 'RankRegion',
                5: 'RankSportCountry',
                6: 'RankSportRegion'}
    
    #Rename percentile ranks columns
    _ = _.rename(columns=col_names)
    
    
    #Calc Percentage of Events on each day
    PctEvents = round(_['NumEvents'] / total_events * 100,2)
    _.insert(loc=6, column='PctEvents', value=PctEvents)
    
    #Insert Average Concurrency Rank
    _.insert(loc=5,column='AvgConcurrencyRank',value=AvgRank)
    
    _.sort_values(by=['Weekday','StartTime'], inplace=True)
    
    _['Weekday'] = _['Weekday'].apply(lambda x: weekdays[x])
    
    _ = _.loc[_['PctEvents']>=threshold].copy()
    
    return _

#Import Data Here
#Import from Boto3 AWS S3 Bucket in Final State!
df = pd.read_csv('MFL_With_Concurrency.csv',parse_dates=['StartDateTime','EndDateTime'])
df['Weekday'] = df['StartDateTime'].apply(lambda x: x.weekday())

#Get Unique List of Sports
sportlist = sorted(df['Sport'].unique())
sportlist.insert(0,"--Please Select--")

sport = "--Please Select--"
country = "--Please Select--"
competition = "--Please Select--"

with st.sidebar:
    image = st.image("IGM Primary Inv logotype.png")

    sport = st.selectbox("Select A Sport:",sportlist)
    
    #If a sport has been selected, prompt user to select a country
    if sport != "--Please Select--":
        countrylist = sorted(df.loc[df['Sport']==sport]['Country'].unique())
        countrylist.insert(0,"--Please Select--")
        
        country = st.selectbox("Select A Country:",countrylist)
        
        #If a country has been selected, prompt user to select a competition
        if country != "--Please Select--":
            complist = sorted(df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique())
            complist.insert(0,"--Please Select--")
            competition = st.selectbox("Select A Competition:",complist)

#Once a sport, country, and competition have been selected
#Call functions to output analysis of this competition.            
with st.container():
    st.title("Competition Concurrency Tool")
    st.write("Select filters from the sidebar before generating results here.")
    if "--Please Select--" not in [sport, country, competition]:
        threshold = st.slider("What is the minimum % of a competitions fixtures on a given day of the week and time you would like to see?",
                              min_value = 0.0, max_value = 10.0, value = 0.0, step=0.1,
                              help = """For example: Selecting 5.0% would only display start times which have at least 5% of the 
                              competitions total fixtures played on them. If a Sunday at 10pm only had 1% of the fixtures played then it 
                              would not be shown. Selecting 0.0 displays all start times.""")
        
        if st.button(f"Click Here To Generate Reports For {country} {competition} {sport}"):
            total_fixtures = len(df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)])
            st.write(f"Total Annual Fixtures: {total_fixtures}")
            
            #Get Monthly Fixtures Data & Download Excel Link
            monthly_fixtures = get_comp_fixtures_by_month(df,sport,country,competition)
            st.dataframe(monthly_fixtures)
            
            towrite = io.BytesIO()
            downloaded_file = monthly_fixtures.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0) # reset pointer
            b64 = base64.b64encode(towrite.read()).decode() # some strings
            filename = "MonthlyFixtures{country}{competition}{sport}"
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={filename}>Download Monthly Fixtures</a>'
            st.markdown(linko, unsafe_allow_html=True)
            
            #Get Daily Fixtures
            daily_fixtures = get_pct_matches_weekdays(df,weekdays,sport,country,competition)
            st.dataframe(daily_fixtures)
            
            towrite = io.BytesIO()
            downloaded_file = daily_fixtures.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0) # reset pointer
            b64 = base64.b64encode(towrite.read()).decode() # some strings
            filename = "DailyFixtures{country}{competition}{sport}"
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={filename}>Download Daily Fixtures</a>'
            st.markdown(linko, unsafe_allow_html=True)
                
            #Get Concurrency Info
            st.write("Calculating Concurrency Info......")
            concurrency_df = get_pct_matches_start_times(df, weekdays, sport, country, competition, threshold=threshold)
            st.dataframe(concurrency_df)

            towrite = io.BytesIO()
            downloaded_file = concurrency_df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0) # reset pointer
            b64 = base64.b64encode(towrite.read()).decode() # some strings
            filename = "ConcurrencyData{country}{competition}{sport}"
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={filename}>Download Concurrency Report</a>'
            st.markdown(linko, unsafe_allow_html=True)
            
            conc_score = round(sum(concurrency_df['AvgConcurrencyRank'] * concurrency_df['NumEvents']) / sum(concurrency_df['NumEvents']),2)
            conc_score_all = round(sum(concurrency_df['ConcurrencyRankAll'] * concurrency_df['NumEvents']) / sum(concurrency_df['NumEvents']),2)
            conc_score_sport = round(sum(concurrency_df['ConcurrencyRankSport'] * concurrency_df['NumEvents']) / sum(concurrency_df['NumEvents']),2)
            
            st.subheader("Weighted Average Concurrency Scores")
            st.write(f"Overall Average Concurrency Score: {conc_score}")
            st.write(f"Overall Concurrency Score vs All Sports: {conc_score_all}")
            st.write(f"Overall Concurrency Score vs Other {sport}: {conc_score_sport}")