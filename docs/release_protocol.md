# Release Protocol

We use 2 spaces on hugging face: one for the development of the interface and the main space for showcasing the most recent stable release. The main branch is protected and deploys to the main space when a PR is accepted.

We wish to enforce strict commits from the dev branch to the main branch when a PR is made to create a new release.

Dev to Main PR Checklist:

1. Open a PR from dev branch to main branch
2. Commit: change the dataset to point the dataset to the main dataset
3. Commit: change the naming in ReadME to avoid merge conflict 
4. Ask for Review
5. Merge and make a new release of the code 