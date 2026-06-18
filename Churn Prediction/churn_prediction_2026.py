#this code predicts customers churn
#if they churn and who
#when they churn 
#why they churn based on what? 
#we use logistic regression for churn prediction and why 
#later we use XGBClasifier to find who will churn with highest probability in next 30 days 

#import libraries
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import polars as pl
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, recall_score, precision_score, f1_score
)

# load data
df = pl.read_csv("syn_data.csv")
print(f"Loaded {len(df):,} customers")

#features
features = [
    "days_since_login", "features_used", "usage_trend", "support_tickets", "contract_days_left",
    "monthly_revenue", "price_increase"
]
X = df.select(features).to_numpy()

y = df["churned"].to_numpy()            

#train test split part...80% traub m 20% test 42 that every time this runs, it will be rundom numbers 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  
)

#scaler part   ----think of it like everything is different unit(kg, cm, dollars) but after scaler its all the same unit 
scaler    = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)   # apply only on test, never fit

#fitting the model
lr = LogisticRegression(random_state=42, max_iter=1000) #defaul value of sklearn is usually 100, but sometimes data is complex, features are many, scaling isnt perfect so we increase it

#prediction
y_pred_lr  = lr.predict(X_test_s)              
y_proba_lr = lr.predict_proba(X_test_s)[:, 1]

#measures / model evaluation
auc_lr = roc_auc_score(y_test, y_proba_lr)
rec_lr = recall_score(y_test, y_pred_lr)       
pre_lr = precision_score(y_test, y_pred_lr)
f1_lr  = f1_score(y_test, y_pred_lr)

print("How good is the model? ")
print("AUC:       ", round(auc_lr, 3))
print("Recall:    ", round(rec_lr, 3))
print("Precision: ", round(pre_lr, 3))
print("F1 Score:  ", round(f1_lr, 3))

print("Why customers churn?")
# which features drive churn most?
coef_df = pl.DataFrame({
    "feature":     features,
    "coefficient": lr.coef_[0].tolist()
}).sort("coefficient", descending=True)
print(f"\nWhat drives churn? (positive = increases risk, negative = protects):")
print(coef_df)

#who will churn and what is the financial impact? 
print("who will churn and what is the financial impact? ")

#we will apply the model on all the data so all 5000 customers and predict probability 
X_all     = df.select(features).to_numpy()
X_all_s   = scaler.transform(X_all)
proba_all = lr.predict_proba(X_all_s)[:, 1]

#add predictions to the dataframe 
df_pred = df.with_columns(
    pl.Series("churn_probability", proba_all)
)

# filter high risk customers
high_risk = df_pred.filter(pl.col("churn_probability") > 0.75)

# revenue at risk
revenue_at_risk = high_risk["monthly_revenue"].sum()
print(f"\nCustomers with >75% churn risk: {high_risk.height}")
print(f"Monthly revenue at risk:        ${revenue_at_risk:,.0f}")

# priority call list
priority = high_risk.with_columns(
    (pl.col("churn_probability") * pl.col("monthly_revenue")).alias("priority_score")
).sort("priority_score", descending=True)

print("\nTop 10 customers to call TODAY:")
print(priority.select(["customer_id", "churn_probability", "monthly_revenue", "priority_score"]).head(10))

#--------------------------------------------------------------------------------------------------------------------
#Which customers will churn in next 30 days? using XGBClassifier model 

#import libraries 
from xgboost import XGBClassifier

#create 30 days target label 
df=df.with_columns (
    (

    (pl.col("churned")==1 &
     (pl.col("days_to_churn")<=30)
    ).cast(pl.Int32).alias("will_churn_30_days")
    )
)

#define features
features = [
    "features_used", "usage_trend", "days_since_login","monthly_revenue"
]
#converts only needed columns to Numpy(required for sklearn)

X=df.select(features).to_numpy()
y=df.select("will_churn_30_days").to_numpy().ravel() #for flatening, 1D array 

#train test split 
X_train, X_test, y_train, y_test = train_test_split(
    X,y, test_size=0.2, random_state=42
)

#train the model 
model = XGBClassifier(
    random_state=42, #everytime generates random number 
    n_estimators=100, #number of trees 
    max_depth=4, #how many branches in the tree
    learning_rate=0.1, #learning rate of the tree/model 
    eval_metric='logloss'
)
#fit the model 
model.fit(X_train, y_train)

#Score for active users setting 
#filter active users who not churned yet 
active_users=df.filter(pl.col("churned")==0)

#convert features for prediction 
X_active = active_users.select(features).to_numpy()

#predict probabilities 
probabilities = model.predict_proba(X_active)[:,1]

#add prediction column back into polars 
active_users=active_users.with_columns(
    pl.Series(name="churn_probability_30_days",values=probabilities)
)
#create priority list 
sales_priority_list=(
    active_users
    .select(["customer_id", "churn_probability_30_days", "monthly_revenue"
    ])
    .sort("churn_probability_30_days", descending=True)
)
#TOP 20 customers (high risk)
top_20 = sales_priority_list.head(20)   # fix: .head(20) not (20)
print('Top 20 people who will churn in the next 30 days: ')
print(top_20)

#measures of the XGBoost model / model evaluation
y_pred_xgb  = model.predict(X_test)
y_proba_xgb = model.predict_proba(X_test)[:, 1]

auc_xgb = roc_auc_score(y_test, y_proba_xgb)
rec_xgb = recall_score(y_test, y_pred_xgb)
pre_xgb = precision_score(y_test, y_pred_xgb)
f1_xgb  = f1_score(y_test, y_pred_xgb)

print("\nHow good is the XGBoost model?")
print("AUC:       ", round(auc_xgb, 3))
print("Recall:    ", round(rec_xgb, 3))
print("Precision: ", round(pre_xgb, 3))
print("F1 Score:  ", round(f1_xgb, 3))
