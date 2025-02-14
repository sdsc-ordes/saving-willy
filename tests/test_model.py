import os
from huggingface_hub import HfApi
import cv2
import pandas as pd
import numpy as np

from transformers import pipeline
from transformers import AutoModelForImageClassification
import time

'''
how to use this script:
1. get data from the kaggle competition, including images and the train.csv file
edit the "folder" variable, assuming the following layout

ceteans/
├── images
│   ├── 00021adfb725ed.jpg
│   ├── 000562241d384d.jpg
│   ├── ...
└── train.csv

2. inspect the df_results dataframe to see how the model is performing
'''

# setup for the ML model on huggingface (our wrapper)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
rev = 'main'

# load the model
cetacean_classifier = AutoModelForImageClassification.from_pretrained(
    "Saving-Willy/cetacean-classifier", 
    revision=rev,
    trust_remote_code=True)

# get ready to load images
from pathlib import Path
folder = os.getcwd()
base = Path(f'{folder}/data_model_test/').expanduser()
df = pd.read_csv(base / 'train.csv')
img_pth = base / 'images'
img_files = list(img_pth.glob('*.jpg'))

i_max = None # put a limit on the number of images to classify in this test (or None)

# for each file in the folder folder/images, 1/ load image, 2/ classify, 3/ compare against the relevant row in df
# also keep track of the time it takes to classify each image

classifications = []

for i, img_file in enumerate(img_files):
    # lets check we can get the right target.
    img_id = img_file.name # includes .jpg
    target = df.loc[df['image'] == img_id, 'species'].item()
    #print(img_id, target)

    start_time = time.time()
    image = cv2.imread(str(img_file))
    load_time = time.time() - start_time

    start_time = time.time()
    out = cetacean_classifier(image) # get top 3 matches
    classify_time = time.time() - start_time

    whale_prediction1 = out['predictions'][0]

    # comparison
    ok = whale_prediction1 == target
    any = target in [x for x in out['predictions']]
    row = [img_id, target, whale_prediction1, ok, any, load_time, classify_time] + list(out['predictions'])

    print(i, row)

    classifications.append(row)

    if i_max is not None and i >= i_max:
        break


df_results = pd.DataFrame(classifications, columns=['img_id', 'label', 'first_prediction', 'ok', 'any', 'load_time', 'classify_time'] + [f'pred_{i}' for i in range(3)])
df_results.to_csv(base / "results.csv")
# print out a few summary stats
# mean time to load and classify (formatted 3dp), +- std dev (formatted to 2dp), 
print(f"Mean load time: {df_results['load_time'].mean():.3f} +- {df_results['load_time'].std():.2f} s")
print(f"Mean classify time: {df_results['classify_time'].mean():.3f} +- {df_results['classify_time'].std():.2f} s")

# accuracy: count of ok / count of any
print(f"Accuracy: correct with top prediction: {df_results['ok'].sum()} | any of top 3 correct: {df_results['any'].sum():.3f} (of total {df_results.shape[0]})")

# diversity: is the model just predicting one class for everything it sees?
print("Which classes are predicted?")
print(df_results.pred_0.value_counts())

