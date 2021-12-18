# Loading Libraries
import datetime as dt
import pandas as pd

#Display Settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width',500)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


##### Data Understanding #####

# Read dataset
# We copied df because when we read again do not want to wait reading time
df_ = pd.read_excel('datasets/online_retail_II.xlsx', sheet_name='Year 2010-2011')
df = df_.copy()

# Data overview
print("##### DATA OVERVIEW ##### \n")
df.head()
df.shape
df.describe().T


##### Data Preparation #####

# Cleaning of null values
print("##### NUMBER OF NULL VALUES ##### \n")
df.isnull().sum()
df.dropna(inplace=True)

# Cleaning of outliers
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]
df = df[(df['Price'] > 0)]

# Define the Total Price
df["TotalPrice"] = df["Quantity"] * df["Price"]


##### Calculating RFM Metrics #####

# Recency : When was the last time the customer made a purchase?
# Frequency : How often does the customer shop?
# Monetary : How much money did the customer spend in total?
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.columns = ['recency', 'frequency', 'monetary']
rfm.head()

##### Calculating RFM Scores #####

rfm["recency_score"] = pd.qcut( rfm["recency"], 5, labels=[5,4,3,2,1])
rfm["frequency_score"] = pd.qcut( rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5] )
rfm["monetary_score"] = pd.qcut( rfm["monetary"], 5, labels=[1,2,3,4,5])

rfm["RFM_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm.head()


##### Creating & Analysing RFM Segments #####

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5'    : 'cant_loose',
    r'3[1-2]'    : 'about_to_sleep',
    r'33'        : 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41'        : 'promising',
    r'51'        : 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]'    : 'champions'
}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
rfm.head()

print("##### CUSTOMERS SEGMENTS ##### \n")
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])
