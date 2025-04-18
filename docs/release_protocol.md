# Release Protocol

We use 2 spaces on hugging face: one for the development of the interface and the main space for showcasing the most recent stable release. The main branch is protected and deploys to the main space when a PR is accepted.

We wish to enforce strict commits from the dev branch to the main branch when a PR is made to create a new release.

Dev to Main PR Checklist:

1. Open a PR from dev branch to main branch
2. Commit: in `dataset/download` change the `dataset_id` to point to the main dataset : `Saving-Willy/main_dataset`
3. Commit: in the ReadMe, to avoid merge conflict, change the header to this  : 

```
---
title: Saving Willy
emoji: 🐋
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.39.0
python_version: "3.10"
app_file: src/main.py
pinned: false
license: apache-2.0
short_description: 'SDSC Hackathon - Project 10. '
---
```

4. Ask for Review
5. Merge and make a new release of the code 