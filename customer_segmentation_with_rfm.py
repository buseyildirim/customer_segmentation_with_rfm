import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Data preparation and understanding

# Read data
df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

#Examine the descriptive statistics of the data set.
df.head()
df.shape
df.describe().T

# Are there any missing observations in the dataset? If yes, how many missing observations in which variable?

df.isnull().values.any()
df.isnull().sum()

# Subtract Missing Observations from the Data Set.
df.dropna(inplace=True)

# How many unique items?
"""" We expect it to be the same, but it's not the same. 
There may be products written incorrectly in the description. It makes more sense to use StackCode """


df["Description"].nunique()
df["StockCode"].nunique()

# How Many of Which Product Are There?
df["Description"].value_counts()

# Rank the 5 most ordered products from most to least.
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head(5)

# The 'C' in the invoices shows the canceled transactions. Remove the canceled transactions from the dataset.
df = df[~df["Description"].str.contains("C", na=False)]

# Create a variable named 'Total Price' that represents the total earnings per invoice.

df["TotalPrice"] = df["Quantity"] * df["Price"]


# Calculating RFM metrics
df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice : Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice : TotalPrice.sum()
                                     })
rfm.columns = ['recency', 'frequency', 'monetary']
rfm = rfm[(rfm['monetary'] > 0)]
rfm


# Generating RFM scores
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

# Defining RFM scores as segments
seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)


""" Segments that I find important :
champions,
new_customers
cant_loose
"""

rfm

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

"""
champions : As expected, it is the segment with the largest frequency value and the smallest recency value.
We can say that these are the most important customers. They shop actively and frequently. These customers are premium customers.
We can think like Discount coupons can be defined for these users. 

new_customers : Since there are new customers, it is important to make these customers loyal customers.
In this respect, welcome campaigns can be organized by email marketing to these customers.


cant_loose : These customers are customers with a high frequency of shopping. 
So when they shop, they can earn us well. But they haven't been shopping for a long time.
With this in mind, an email marketing can be done here as well.
It's time to buy a new one considering the products you bought in your previous shopping. 
If you buy this product again, 10% discount can be provided.
"""

# Select the customer IDs of the "Loyal Customers" segment and get the excel output.
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index

new_df.to_csv("loyal_customers.csv", index=False)
