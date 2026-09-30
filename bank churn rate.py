import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
from faker import Faker
from matplotlib.ticker import PercentFormatter

df = pd.read_csv('bank file.csv')

#First understanding of the dataset
df.info()
df.shape
df.columns
df.head(3)

#There are columns with spaces at the end or the begining
df.columns = df.columns.str.strip()

#Columns that might be numbers and are objects
df['Balance'].head(10)
df['Outstanding Loans'].head(10)
df['NumOfProducts'].head(10)

#We undestood that they are talking about money amounts, so we cleaned and covert it to float
money_cols = ['Outstanding Loans', 'Balance']
for col in money_cols:
    df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

df['Balance'].head(10)
df['Outstanding Loans'].head(10)

#Converting time columns into time data type
df['Date of Birth'] = pd.to_datetime(df['Date of Birth'])
df['Churn Date'] = pd.to_datetime(df['Churn Date'])


#there were columns that are object and we wanted to covenrt it to string
text_cols = df.select_dtypes(include='object').columns
print(text_cols)
df[text_cols] = df[text_cols].astype("string")

#Want to check how are written the categorial columns inside the data
categorical_cols = ['Gender', 'Marital Status', 'Occupation', 'Education Level',
                     'Customer Segment', 'Preferred Communication Channel']

for col in categorical_cols:
    print(f"\n{col}:")
    print(df[col].unique())
    

#Any duplicate rows?
print("Duplicate rows:", df.duplicated().sum()) #they are not duplicates rows
    
    
#Confirming the results
df.info()
    
#We realized that the Address belong to USA addresses even thought it is a Botswana (Africa) bank
#so we used faker to bring Botswana addresses that even if they are not true are more reliable 
#than USA addresses in a Botswana bank



botswana_regions = [
    'Gaborone', 'Francistown', 'Molepolole', 'Maun', 'Serowe',
    'Selebi-Phikwe', 'Kanye', 'Mahalapye', 'Mogoditshane',
    'Mochudi', 'Lobatse', 'Palapye', 'Ramotswa', 'Kasane'
]

df['Region'] = [random.choice(botswana_regions) for _ in range(len(df))]
df['Address'] = [
    f"{Faker().building_number()} {Faker().street_name()}, {region}, Botswana"
    for region in df['Region']
]

df['Region'].value_counts()
df[['Address', 'Region']].head()

#creating an age columns
today = pd.Timestamp.today()
df['Age'] = (today - df['Date of Birth']).dt.days // 365

df['Churn Status'] = df['Churn Flag'].replace({1: 'Churned', 0: 'Non Churned'})

#Confirming the results
df.info()
#=================================================================================================
#Second cleaning, trying to understand the data deeply to build business questions

#Overall churn rate
df['Churn Flag'].mean()

#Churn rate by region (even if it's faker data, we still want to make the exercise)
df.groupby('Region')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by marital status
df.groupby('Marital Status')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by occupation
df.groupby('Occupation')['Churn Flag'].mean().sort_values(ascending=False)
df['Occupation'].value_counts()

#Churn rate by gender
df.groupby('Gender')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by Education
df.groupby('Education Level')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by Customer Segment
df.groupby('Customer Segment')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by Communication Channel
df.groupby('Preferred Communication Channel')['Churn Flag'].mean().sort_values(ascending=False)

#Churn rate by numeric columns
numeric_cols = ['Income', 'Credit Score', 'Balance', 'Outstanding Loans',
                 'Customer Tenure', 'Credit History Length', 'NumOfProducts',
                 'NumComplaints', 'Age', 'Number of Dependents']

df.groupby('Churn Flag')[numeric_cols].mean().T


#Checking if churned customers have churned date
missing_date = df[(df['Churn Flag'] == 1) & (df['Churn Date'].isna())]
extra_date   = df[(df['Churn Flag'] == 0) & (df['Churn Date'].notna())]
print("Churned but no date:", len(missing_date))
print("Not churned but has a date:", len(extra_date))

#Check numeric ranges for anything that can be not realistic
pd.set_option('display.max_columns', None)
df.describe().T

pd.set_option('display.max_columns', 3)

#Last check before starting to ask the business questions
df.info()
df.shape
df.columns
df.head(3)

#With this analysis we realized 2 things:
#We cannot trust the Occupation column to make an analysis
#of what they leave, because is around 600 hundred jobs and only between 140-220 workers in each
#(too many types of work with little amount of employees)

#And second thing is that the region, marital status, gender, education or customer segment doesn't really 
#matter in the churn rate

overall_rate = df['Churn Flag'].mean()
variables = ['Region', 'Marital Status', 'Gender', 'Education Level', 'Customer Segment']

for v in variables:
    rates = df.groupby(v)['Churn Flag'].mean().sort_values(ascending=False)

    plt.bar(rates.index, rates.values, color='#71D3FF')
    plt.axhline(overall_rate, color='black', linestyle='--')
    plt.title(f'Churn Rate by {v}')
    plt.ylabel('Churn Rate')
    plt.ylim(0, 0.20)
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1))
    plt.show()
    
#as we can see in the graphics, all of them are flat, meaning no of this columns affects directly 
#to the churn rate
#===========================================================================================================================
#Business question 1
#What percentage of customers have churned overall? And what is the most common reasons?

#Overall churn rate
churn_counts = df['Churn Status'].value_counts()

plt.pie(churn_counts, labels=churn_counts.index, autopct='%1.1f%%',
        colors=['#71D3FF','#E8E8E8'], startangle=90)
plt.title('Overall Customer Churn Rate')
plt.show()
#As we can see in the first graph only 12,2% of the customers left, this is important because this are the
#people we are gonna work on in the proyect

#Commons reasons to churn
reason_counts = df['Churn Reason'].value_counts()

sns.barplot(x=reason_counts.values, y=reason_counts.index, color='#71D3FF')
plt.title('Reasons Given by Churned Customers')
plt.xlabel('Number of Customers')
plt.ylabel('Churn Reason')
plt.show()
#This chart shows the reasons churned customers gave for leaving. All four reasons sit at a very similar level, 
#telling us there isn't one dominant cause behind customer churn. 
#That said, Service Issues is worth prioritizing — unlike Relocation or Better Offers Elsewhere, 
#which are largely outside the bank's control, service quality is something the bank can directly improve, 
#making it the most actionable lever available.

#Business question 2
#Does account balance relate to churn?
sns.boxplot(data=df, x='Churn Status', y='Balance', hue='Churn Flag',
            palette=['#71D3FF','#E8E8E8'], legend=False,
            flierprops={'markersize': 2})
plt.title('Account Balance: Churned vs Retained Customers')
plt.xlabel('Customer Status')
plt.ylabel('Balance ($)')
plt.show()

#In this graph we can see: the boxes represent the balance that most of the customer of each group are in,
#the middle line inside the boxes represent the average ammount of money that each group have in their accounts
#the lines outside represent people that are out of 'normal group' for each one
#and the dark dots in the top part of the churned box is represented by variable outliners explained bellow

#Variable 1 takes the persons that were churned, and are inside the 25% of the group still
V1 = df['Balance'][df['Churn Flag']==1].quantile(0.25)
#Variable 2 takes the persons that were churned, and are inside the 75% of the group still
V2 = df['Balance'][df['Churn Flag']==1].quantile(0.75)
df['Balance'][df['Churn Flag']==1].describe() #double checking if it's correct

upper_limit = V2 + 1.5*(V2 - V1) #gives us the value of the upper line in the churned graph

outliners = df[(df['Churn Flag']==1) & (df['Balance'] > upper_limit)]
print("Number of outliners customers:", len(outliners))

outliners
#Variable outliners represent the churned people that have a balance abpve of what is expected
#(the dark dots in the graph) and we will use it later

outliners[['CustomerId','Balance','NumOfProducts','NumComplaints','Credit Score','Churn Reason']].sort_values('Balance', ascending=False).head(10)

outliners.to_excel('outliners customers.xlsx', index=False)
#Here is an excel document with all the data about this outliners customers

#Business question 3
#How does churn rate change as the number of complaints increases?
#Is there a relationship between the account balance and churn rate?

#Churn rate rises as complaints increase
complaint_churn = df.groupby('NumComplaints')['Churn Flag'].mean()
df['NumComplaints'].min()
df['NumComplaints'].max()

plt.plot(complaint_churn.index, complaint_churn.values, marker='o', color='#71D3FF', linewidth=2)
plt.title('Churn Rate by Number of Complaints')
plt.xlabel('Number of Complaints')
plt.ylabel('Churn Rate (%)')
plt.xticks(range(0,11))
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1))
plt.show()
#As we can see in the graph, the churn rate does increase exponentially as the complains increase

#Does balance also move with complaints, or is this a separate effect?
sns.histplot(data=df, x='NumComplaints',  y='Balance', hue='Churn Status', bins=15,
             palette=['#71D3FF','#E8E8E8'], stat='percent', common_norm=False,
             multiple='dodge', shrink=0.85, edgecolor='white', linewidth=0.5)
plt.title('Account Balance vs Number of Complaints', fontsize=13, pad=12)
plt.xlabel('Number of Complaints')
plt.ylabel('Balance ($)')
plt.show()

#Here we can see that customers with more balance, have a more number of complains before they leave

counts = outliners['NumComplaints'].value_counts().sort_index()

labels = [f'{n}' for n in counts.index]
plt.pie(counts, autopct='%1.1f%%', colors=['#35C5FF', '#71D3FF', '#AFE4FF','#E8E8E8'], startangle=90)
plt.title('Outliners by Number of Complaints (7-10)')
plt.legend(labels, title='Complaints', loc='upper left', bbox_to_anchor=(-0.35, 0.55))
plt.show()

outliners[['Balance', 'NumComplaints']].sort_values('Balance', ascending=False).head(10)
#As we can see, all of the outliners customers have a high rate numer of complins, wich tells us that the
#number of complains affects more that the balance in the churn rate

#Business question 4
#Does the number of products a customer holds affect their churn risk? 
product_churn = df.groupby('NumOfProducts')['Churn Flag'].mean()

plt.bar(product_churn.index, product_churn.values, color='#71D3FF')
plt.title('Churn Rate by Number of Products Held')
plt.xlabel('Number of Products')
plt.ylabel('Churn Rate')
plt.xticks(product_churn.index)
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1))
plt.show()

outliners[['Balance', 'NumOfProducts']].sort_values('Balance', ascending=False).head(10)

product_status = pd.crosstab(df['NumOfProducts'], df['Churn Status'], normalize='index') * 100

product_status.plot(kind='bar', stacked=True, color=['#71D3FF', '#E8E8E8'],
                     figsize=(9,6), width=0.6)

plt.title('Churn Rate by Number of Products Held')
plt.xlabel('Number of Products')
plt.ylabel('Percent of Customers (%)')
plt.xticks(rotation=0)
plt.legend(title='Status')

for bar_group in plt.gca().containers:
    plt.gca().bar_label(bar_group, fmt='%.0f%%', label_type='center', color='black', weight='bold')

plt.show()

#Here also the outliners have the less number of products, wich is also an indicator that even in the balance
#is not that high, the number of products really affects the churn rate 

#Business question 5 
#How is credit score distributed differently between churned and retained customers?
sns.histplot(data=df, x='Credit Score', hue='Churn Status', bins=15,
             palette=['#71D3FF','#E8E8E8'], stat='percent', common_norm=False,
             multiple='dodge', shrink=0.85, edgecolor='white', linewidth=0.5)
plt.title('Credit Score Distribution: Churned vs Retained', fontsize=13, pad=12)
plt.xlabel('Credit Score')
plt.ylabel('Percent of Customers (%)')
plt.legend(title='Customer Status', labels=['Churned', 'Non Churned'])
plt.gca().yaxis.set_major_formatter(PercentFormatter())
plt.show()


#Split credit scores into equal-population groups, enough bins for a detailed trend line
outliners_binned = outliners
outliners_binned['Credit Score Bin'] = pd.qcut(outliners_binned['Credit Score'], q=15, duplicates='drop')

#Average balance and midpoint credit score for each bin
bin_summary = outliners_binned.groupby('Credit Score Bin', observed=True).agg(
    avg_balance=('Balance', 'mean'),
    avg_credit_score=('Credit Score', 'mean')
).reset_index()

plt.plot(bin_summary['avg_credit_score'], bin_summary['avg_balance'],
         marker='o', color='#71D3FF', linewidth=2, markersize=6, markerfacecolor='#1F86D9')

plt.title('Account Balance vs Credit Score (outliners customers)')
plt.xlabel('Credit Score')
plt.ylabel('Balance ($)')
plt.show()

#Here we can see that the outliners group usually have less credit score

#Business question 6
#Closer question: What would a "typical high-risk churn profile" look like? 
#Which combination of product count and complaint level will help me to identify him?
df['Balance Bin'] = pd.cut(df['Balance'], bins=[0,50000,100000,150000,200000,250000],
                            labels=['$0-50K','$50-100K','$100-150K','$150-200K','$200-250K'])
df['Credit Score Bin'] = pd.cut(df['Credit Score'], bins=[300,410,520,630,740,850],
                                 labels=['300-410','410-520','520-630','630-740','740-850'])

variables = {
    'Number of Products': 'NumOfProducts',
    'Number of Complaints': 'NumComplaints',
    'Balance': 'Balance Bin',
    'Credit Score': 'Credit Score Bin'
}

for title, col in variables.items():
    matrix = pd.crosstab(df['Churn Status'], df[col], normalize='index')

    plt.figure(figsize=(10,3))
    sns.heatmap(matrix, annot=True, fmt='.0%', cmap='Blues')
    plt.title(f'{title} Distribution by Churn Status')
    plt.xlabel(title)
    plt.ylabel('Churn Status')
    plt.show()

#As conclusion we can say that the most common reason people leave the bank is because of the balance in their accounts,
#But the combine of the other variables (Complains, Number Of Products and credit score), is also really important
#and can make a person leave the bank even if the balance is not that low
#=======================================================================================================
extreme_risk = df[(df['NumOfProducts']==1) & (df['NumComplaints']>=8) &
                   (df['Balance'] < df['Balance'].median()) &
                   (df['Credit Score'] < df['Credit Score'].median()) &
                   (df['Churn Flag']==0)]

print(len(extreme_risk), "customers —",
      f"{len(extreme_risk)/len(df):.1%} of the customer base are in extreme risk of leaving the bank")

extreme_risk.info()

extreme_risk.to_excel('customers in danger to leave.xlsx', index=False)

#According to everything explained, here is an excel document with the customer that fit the 
#situation of the people who will potencially left the bank so we can make a desicion on how make them stay
