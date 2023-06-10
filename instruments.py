import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import configparser

cfg = configparser.RawConfigParser()
cfg.read(filenames='credentials.ini')

access_token = cfg['keys']['demo_key']
accountID = cfg['keys']['accountID']

client = API(access_token=access_token)

params = ''
r = accounts.AccountInstruments(accountID=accountID, params=params)
response = client.request(r)

df = pd.DataFrame(response['instruments'])

columns_name = df['tags'].apply(pd.Series)[0].apply(pd.Series)['type'][0]
df[columns_name] = df['tags'].apply(pd.Series)[0].apply(pd.Series)['name']

df = pd.concat([df,df['financing'].apply(pd.Series).iloc[:,:2]], axis=1)

weeks = df['financing'].apply(pd.Series)['financingDaysOfWeek'].apply(pd.Series)
for a in weeks:
    name  = weeks[a][0]['dayOfWeek']
    df[name] = weeks[a].apply(pd.Series)['daysCharged']

df.drop(columns=['tags', 'financing'], inplace=True)

df.to_csv('instruments.csv', index=False)