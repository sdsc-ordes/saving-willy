from huggingface_hub import HfApi
import json
import tempfile
import os

#huggingface_hub

submission = {'latitude': '3.5', 'longitude': '44', 'author_email':
    'super@whale.org', 'date': '2024-10-25', 'time': '12:07:04.487612',
    'predicted_class': 'bottlenose_dolphin', 'class_overriden': None,
    'image_filename': '000a8f2d5c316a.webp', 'image_md5':
    'd41d8cd98f00b204e9800998ecf8427e'}

imgname = submission['image_filename']

api = HfApi()


# generate a tempdirectory to store the image 
#tempdir = tempfile.TemporaryDirectory()
# write a tempfile

# write submission to a tempfile in json format with the name of the image, giving the filename and path as a string

f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
jstr = json.dumps(submission)
f.write(jstr)
f.close()



#with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
#    jstr = json.dumps(submission)
#    f.write(jstr)
#    #print(f.path)

path_in_repo= f"metadata/{submission['author_email']}/{submission['image_md5']}.json"
print(f"fname: {f.name} | path: {path_in_repo}")
rv = api.upload_file(
    path_or_fileobj=f.name,
    path_in_repo=path_in_repo,
    repo_id="Saving-Willy/Happywhale-kaggle",
    repo_type="dataset",
)
print(rv)



    