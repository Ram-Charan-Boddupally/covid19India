from datetime import datetime 
import os
import requests
import pandas as pd
import re

lastUpdated = '2021-10-17 07:21:11.760628' 

def isDataUpdated():
    timeDiff = datetime.today() - datetime.strptime(lastUpdated, '%Y-%m-%d %H:%M:%S.%f')
    timeDiff = (timeDiff.days*24*60*60+timeDiff.seconds)//3600

    if timeDiff >= 12:
        return False
    return True

def updateDataFiles():
    #attaching state wise covid data and state wise vacination data
    covidData = pd.read_csv(os.path.join("covidData","raw_data","states.csv"),low_memory=False)
    covidData = covidData[['Date','State','Confirmed','Recovered','Deceased']]
    covidData.rename({'Deceased':'Deaths'},axis=1,inplace=True)

    vacineData = pd.read_csv(os.path.join("covidData","raw_data","cowin_vaccine_data_statewise.csv"),low_memory=False)
    vacineData = vacineData[['Updated On','State','Total Doses Administered']]
    vacineData.rename(columns={'Updated On':'Date','Total Doses Administered':'Vacinated'},inplace=True)
    vacineData = vacineData.loc[vacineData['Date'] <= datetime.today().strftime('%d/%m/%Y')]
    vacineData.reset_index(inplace=True)

    for index,data in vacineData.iterrows():
        date = datetime.strptime(data['Date'],'%d/%M/%Y')
        date = datetime.strftime(date,'%Y-%M-%d')
        vacineData['Date'].iloc[index] = date

    covidData = pd.merge(covidData,vacineData,
                    on=['Date','State'],how='left')
    
    del vacineData
    covidData.fillna(0,inplace=True)
    covidData = covidData.astype({'Vacinated':'int64'})
    covidData.sort_values(['State','Date'],axis=0,inplace=True)
    covidData.to_csv(os.path.join(os.getcwd(),"covidData","modified_data","states_data.csv"),index=False)
    

    covidData = pd.read_csv(os.path.join("covidData","raw_data","districts.csv"),low_memory=False)
    covidData = covidData[['Date','State','District','Confirmed','Recovered','Deceased']]
    covidData.rename({'Deceased':'Deaths'},axis=1,inplace=True)
    vacineData = pd.read_csv(os.path.join("covidData","raw_data","cowin_vaccine_data_districtwise.csv"),low_memory=False)
    vacineData.drop(['S No','State_Code','District_Key','Cowin Key'],inplace=True,axis=1)
    vacineData.drop([0],inplace=True,axis=0)

    dataList = list()
    pattern ='^[\d]{2}/[\d]{2}/[\d]{4}$'
    for index,data in vacineData.iterrows():
        data = data.to_dict()
        for date in data.keys():
            if re.search(pattern,date) and (datetime.strptime(date,'%d/%m/%Y') <= datetime.today()):
                record = dict()
                record['Date'],record['State'],record['District'] = date,data['State'],data['District']
                record['Vacinated'] = data[date+'.3']+data[date+'.4']
                dataList.append(record)

    vacineData = pd.DataFrame(dataList)
    # print(vacineData.head(20))
    """
            Date                        State  District Vacinated
    0   16/01/2021  Andaman and Nicobar Islands  Nicobars        00
    1   17/01/2021  Andaman and Nicobar Islands  Nicobars        00
    2   18/01/2021  Andaman and Nicobar Islands  Nicobars        00
    3   19/01/2021  Andaman and Nicobar Islands  Nicobars        10
    4   20/01/2021  Andaman and Nicobar Islands  Nicobars        10
    """

    covidData = pd.merge(covidData,vacineData,
                        on=['Date','State','District'],how='left')
    covidData[['Vacinated']] =covidData[['Vacinated']].fillna(0)
    covidData[['State','District' ]] = covidData[['State','District' ]].astype('string')
    covidData[['Date']] = covidData[['Date']].astype('datetime64[ns]')

    covidData.sort_values(by=['Date','State','District'],ascending=False,axis=0,inplace=True)
    covidData.reset_index(drop=True)
    # print(covidData.head(5))

    covidData.to_csv(os.path.join(os.getcwd(),"covidData","modified_data","districts_data.csv"),index=False)

    covidData = pd.read_csv(os.path.join("covidData","raw_data","vaccine_doses_statewise_v2.csv"),low_memory=False)    

    
def updateData():
    
    urlsList = ['https://api.covid19india.org/csv/latest/case_time_series.csv',
                'https://api.covid19india.org/csv/latest/states.csv',
                'https://api.covid19india.org/csv/latest/districts.csv',
                'https://api.covid19india.org/csv/latest/state_wise.csv',
                'https://api.covid19india.org/csv/latest/district_wise.csv',
                'http://api.covid19india.org/csv/latest/vaccine_doses_statewise_v2.csv',
                'http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv',
                'http://api.covid19india.org/csv/latest/cowin_vaccine_data_districtwise.csv'
                ]
   
    for url in urlsList:
        fileName = url.split('/')[-1]
        data = requests.get(url)
        data = data.content.decode('utf-8')
        with open(os.path.join(os.getcwd(),"covidData","raw_data","fileName").replace("fileName",fileName),'w') as file:
            file.write(data)
            print("data downloaded ",file.name)

    updateDataFiles()

    with open(os.path.join(os.getcwd(),"covidvisulizer","info.py"),'rb+') as file:
        line = file.readline()
        while True:   
            line = file.readline()
            if line.startswith(b'lastUpdated'):
                file.seek(-31, os.SEEK_CUR)
                replaceValue = bytes(str('\''+str(datetime.now())+ '\''),'utf-8')
                file.write(replaceValue)
                break
