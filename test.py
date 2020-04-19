import pandas as pd
df = pd.DataFrame([1,2, 3, 4], columns=['one'])
d = df['one'].rolling(window=2).mean()
print(d)

