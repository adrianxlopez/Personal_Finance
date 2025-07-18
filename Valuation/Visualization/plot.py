import matplotlib.pyplot as plt


def plot(df, metric):
    if not df.empty or not df == None:
        print("Plotting...")
    years = df["year"][:]
    values = df[metric][:]
    plt.figure(figsize=(8, 5))
    plt.plot(years, values, marker='o')
    plt.title(f"{metric} Trend Over Time")
    plt.xticks(df['year'], rotation= 45)
    plt.xlabel("Year")
    plt.ylabel(f"{metric} (MM)")
    plt.grid(True)
    plt.show()