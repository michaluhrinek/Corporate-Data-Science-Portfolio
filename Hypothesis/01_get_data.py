#code to download data
#import libraries 
import polars as pl
import os

os.makedirs("data", exist_ok=True)
#defyne URL from where we get the data 
url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata"

#get downloaded data loaded into dataframe df 
print("Downloading data from ECB...")
df = pl.read_csv(url)

#select specific parameters from the dataframe 
df = df.select(["TIME_PERIOD", "OBS_VALUE"])
df = df.rename({"TIME_PERIOD": "date", "OBS_VALUE": "value"}) #rename them 

df = df.with_columns(pl.col("date").str.to_date())

df = df.drop_nulls() #drop null values 

df = df.sort("date") #sort by date 

df.write_csv("data/raw_data.csv") #save into file 

print(f"Done! Downloaded {len(df)} rows")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("Saved to data/raw_data.csv")
