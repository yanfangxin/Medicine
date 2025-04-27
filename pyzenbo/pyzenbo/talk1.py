import pandas as pd
import random
qa_data = pd.read_excel("D:\\pyzenbo\\pyzenbo\\test.xlsx")
#print(qa_data)
lenth = len(qa_data)
c = 0
a = input("請輸入:")
for i in range(lenth):
  if a == qa_data.iloc[i][0]:
    for j in range(5):
      if not pd.isna(qa_data.iloc[i][j]):
        c = c+1  
    print(qa_data.iloc[i][random.randint(1,c)])