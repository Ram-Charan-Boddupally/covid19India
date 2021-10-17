from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
import pandas as pd
import json
from .info import *
import os.path

today = {'date':datetime.today().strftime('%d  %b  %Y'),
            'weekday':datetime.today().strftime('%A')}

def catageoryVisulizer(request,catageory):
    
    catageory,state = catageory.split('-')
    location = str()
    
    
    if state == 'india':
        if catageory=='Deceased':
            catageory = 'Deaths'

        covidData = pd.read_csv(os.path.join("covidData","raw_data","state_wise.csv"),low_memory=False)
        covidData = covidData[['State',catageory]]
        covidData.rename(columns={'State':'Location'},inplace=True)
        covidData.drop(covidData.loc[covidData['Location'] == 'Total'].index,inplace=True)
        location = 'India'
    else:
        words = state.split("_")
        for word in words:
            if word == 'and':
                location += word
            else:
                location += word.capitalize()
            location+=" "
        
        state = location.strip()
        del location

        covidData = pd.read_csv(os.path.join("covidData","raw_data","district_wise.csv"),low_memory=False)
        covidData = covidData.loc[covidData['State'] == state]
        covidData = covidData.loc[covidData['District'] != 'Unknown']
        print(covidData.columns)
        print(catageory)

        covidData = covidData[['District',catageory]]
        covidData.rename(columns={'District':'Location'},inplace=True)
        if catageory=='Deceased':
            catageory = 'Deaths'
            covidData.rename(columns={'Deceased':'Deaths'},inplace=True)

    labels,data = [],[]
    for index,info in covidData.iterrows():
        labels.append(info['Location'])
        data.append(info[catageory])


    return render(request,'covidvisulizer/catageory.html',{'presentDate':today,
                                                            'catageory':catageory,
                                                            'catageoryData':{'labels':labels,
                                                                            'data':data,
                                                                            'location':state.upper()}})


def mainVisualizer(request):
    if(not isDataUpdated()):
        updateData()
    
    #vacinated data 
    vacineData = pd.read_csv(os.path.join("covidData","raw_data","vaccine_doses_statewise_v2.csv"),low_memory=False)
    vacineData = vacineData[['Vaccinated As of','State','Total Doses Administered']]
    vacineData['Vaccinated As of']=pd.to_datetime(vacineData['Vaccinated As of'], format='%d/%m/%Y')
    vacineData.dropna(axis='index',inplace=True)
    vacineData = vacineData.loc[vacineData['Vaccinated As of']<datetime.strftime(datetime.today(),'%d/%m/%Y')]

    vacineData.rename({'Total Doses Administered':'Vacinated','Vaccinated As of':'Date'},axis=1,inplace=True)

    vacineData = vacineData.sort_values(by='Date',ascending=False)
    
    date = vacineData.iloc[0].Date
    print(vacineData.head())
    vacineData = vacineData.loc[vacineData['Date']== date ]

    covidData = pd.read_csv(os.path.join("covidData","raw_data","state_wise.csv"),low_memory=False)
    covidData = pd.merge(covidData,vacineData,on='State')
    covidData = covidData[['State','Confirmed','Recovered','Deaths','Active','Vacinated']]
    print(covidData.head())
    
    """
    print(covidData.head())
    covidData = pandas(
                        State  Confirmed  Recovered  Deaths   Active    Vacinated
            0           Total   23004970   19023107  250087  3721977     172710066
            1     Maharashtra    5138973    4469425   76398   590818      18264212
            2          Kerala    1930116    1504160    5880   419725       8042237
            3       Karnataka    1973683    1383285   19372   571006      10630738
            4  Andhra Pradesh    1302589    1104431    8791   189367       7310220)
 
    """

    stateWiseDataToday = dict()
    for index,data in covidData.iterrows():
        state = data['State']
        data = data.drop(labels = ['State'])
        data = data.to_dict()
        stateWiseDataToday[state] = data
    
    """
    stateWiseDataToday = dict
    {'Total': {'Confirmed': 23004970, 'Recovered': 19023107, 'Deaths': 250087, 'Active': 3721977, 
                  'Vacinated': 172710066},
     'Maharashtra': {'Confirmed': 5138973, 'Recovered': 4469425, 'Deaths': 76398, 'Active': 590818,
                  'Vacinated': 18264212}
    """
    
    ## daily count
    vacineData = pd.read_csv(os.path.join("covidData","raw_data","vaccine_doses_statewise_v2.csv"),low_memory=False)
    vacineData = vacineData.loc[vacineData['State'] == 'Total']
    vacineData.drop('State',axis=1,inplace=True)
    vacineData = vacineData.squeeze()
    vacineData = vacineData.reset_index(0)
    vacineData.rename(columns={'index':'Date',37:'Daily Vacinated'},inplace=True)
    vacineData = pd.DataFrame(vacineData)
    # print(vacineData)

    for record in range(vacineData['Date'].size):
        date = str(vacineData['Vaccinated As of'].loc[record])
        date = datetime.strptime(date,'%d/%m/%Y')
        date = datetime.strftime(date,'%#d %B %Y')
        vacineData['Date'].loc[record] = date

    indiaDateWiseData = pd.read_csv(os.path.join("covidData","raw_data","case_time_series.csv"),low_memory=False)
    indiaDateWiseData = pd.merge(indiaDateWiseData,vacineData,on='Date',how='left')

    indiaDateWiseData['Total Doses Administered'].fillna(0,inplace=True)
    indiaDateWiseData['Total Doses Administered'] = indiaDateWiseData['Total Doses Administered'].astype(int)
    # indiaDateWiseData.to_csv('data.csv',index=False)
    """
        indiaDateWiseData = 
                                Date  Daily Confirmed  Daily Recovered  Daily Deceased  Daily Vacinated
            0    30 January 2020                1                0               0                0
            4    3 February 2020                1                0               0                0
            ..               ...              ...              ...             ...              ...
            462       6 May 2021           414280           328347            3923        164973058
    """

    date,confiremd,recovered,descesed,vacinated = [],[],[],[],[]
    for index,data in indiaDateWiseData.iterrows():
        date.append(datetime.strftime(datetime.strptime(data['Date'],'%d %B %Y'),'%d-%m-%Y'))
        confiremd.append(data['Daily Confirmed'])
        recovered.append(data['Daily Recovered'])
        descesed.append(data['Daily Deceased'])
        vacinated.append(data['Total Doses Administered'])

    indiaDateWiseData = {'labels':date,
                         'Confirmed':confiremd,
                         'Recovered':recovered,
                         'Descesed':descesed,
                         'Vacinated':vacinated}


    indiaData = stateWiseDataToday['Total']
    indiaData['location'] = 'INDIA'
    del stateWiseDataToday['Total']

    return render(request,'covidvisulizer/index.html',{'presentDate':today,
                                                'locationCatageoryData':indiaData,
                                                'subLocationData':json.dumps(stateWiseDataToday),
                                                'mainLocDateWiseCount':json.dumps(indiaDateWiseData)
                                                })



def subLoc(request, locName):

    locName = locName.replace("+"," ")
    covidData = pd.read_csv(os.path.join("covidData","modified_data","districts_data.csv"),low_memory=False) 
    covidData = covidData.loc[covidData['State'] == locName]
    covidData.drop(['State'],axis=1,inplace=True)
    covidData = covidData.sort_values(by='Date',ascending=False)
    date = covidData.iloc[0].Date
    distCovidData = covidData.loc[covidData['Date']== date ]
    print(distCovidData.head())
    
    distWiseCovidData = dict()
    for index,data in distCovidData.iterrows():
        district = data['District']
        data = data.drop(labels = ['District'])
        data = data.to_dict()
        data['Active'] = data['Confirmed']-(data['Recovered']+data['Deaths'])
        distWiseCovidData[district] = data
    
    stateCovidData = covidData.loc[covidData['Date'] == date].to_dict(orient='records')[0]
    stateCovidData['Active'] = stateCovidData['Confirmed']-(stateCovidData['Recovered']+stateCovidData['Deaths'])
    stateCovidData['location'] = locName

    covidDateData = pd.read_csv(os.path.join("covidData","modified_data","states_data.csv"),low_memory=False)
    covidDateData = covidDateData.loc[covidDateData['State'] == locName]
    covidDateData.drop(['State'],axis=1,inplace=True)

    date,confiremd,recovered,descesed,vacinated = [],[],[],[],[]
    for index,data in covidDateData.iterrows():
        date.append(datetime.strftime(datetime.strptime(data['Date'],'%Y-%m-%d'),'%d-%m-%Y'))
        confiremd.append(data['Confirmed'])
        recovered.append(data['Recovered'])
        descesed.append(data['Deaths'])
        vacinated.append(data['Vacinated'])

    stateDateWiseData = {'labels':date,
                         'Confirmed':confiremd,
                         'Recovered':recovered,
                         'Descesed':descesed,
                         'Vacinated':vacinated}
    
    return render(request,'covidvisulizer/index.html',{'presentDate':today,
                                                'locationCatageoryData':stateCovidData,
                                                 'subLocationData':json.dumps(distWiseCovidData),
                                                 'mainLocDateWiseCount':json.dumps(stateDateWiseData)})

