import pandas as pd

df = pd.read_csv('lines.csv')

df['from_trf_id'] = df['from_id'].where(df['from_id'].str.contains('TRF-', na=False), None)
df['from_sub_id'] = df['from_id'].where(df['from_id'].str.contains('SUB-', na=False), None)

df['to_trf_id'] = df['to_id'].where(df['to_id'].str.contains('TRF-',na=False),None)
df['to_sub_id'] = df['to_id'].where(df['to_id'].str.contains('SUB-',na=False),None)

df.drop(['from_id','to_id'], axis=1).to_csv('lines.csv',index=False)