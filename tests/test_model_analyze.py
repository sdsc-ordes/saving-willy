import os
import pandas as pd

from pathlib import Path
folder = os.getcwd()
base = Path(f'{folder}/data_model_test/').expanduser()
df_results = pd.read_csv(base / 'results.csv')
print(df_results.head())
# calculate accuracy per species 
df_species = df_results.groupby("label").agg(correct_predictions=pd.NamedAgg(column="ok", aggfunc="sum"),
                                        correct_top3=pd.NamedAgg(column="any", aggfunc="sum"),
                                        total_count=pd.NamedAgg(column="ok", aggfunc="count")).reset_index()
print(df_species)

def summary_stats_species(df, total):
    df["perc_correct"] = df["correct_predictions"] / df["total_count"]
    df["perc_correct_top3"] = df["correct_top3"] / df["total_count"]
    df.sort_values("perc_correct", ascending=False, inplace=True)
    for i, row in df.iterrows():
        print(f"{row['label']}: Accuracy on top prediction: {row['perc_correct']:.3f} | Accuracy on top 3 prediction: {row['perc_correct_top3']:.3f}")
    

def summary_stats_global(df):
    # print out a few summary stats
    # mean time to load and classify (formatted 3dp), +- std dev (formatted to 2dp), 
    print(f"Mean load time: {df['load_time'].mean():.3f} +- {df['load_time'].std():.2f} s")
    print(f"Mean classify time: {df['classify_time'].mean():.3f} +- {df['classify_time'].std():.2f} s")

    # diversity: is the model just predicting one class for everything it sees?
    print("Which classes are predicted?")
    print(df.pred_0.value_counts())

    # accuracy: count of ok / count of any
    print(f"Accuracy: correct with top prediction: {df['ok'].sum()} | any of top 3 correct: {df['any'].sum():.3f} (of total {df.shape[0]})")
    total = df.shape[0]
    return total 


total = summary_stats_global(df_results)
summary_stats_species(df_species, total)