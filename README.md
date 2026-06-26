Running this app: 
python -m fastapi dev main.py

Testing: 
pytest --cov=.


Notes: 

I added a github action to only be able to merge on 80% test coverage, I couldn't get this working consistently in the time frame and didn't want to shoe horn in AI code without learning how to properly do this. I've left the code in but I removed the ruleset from Github so I could merge. Tests are stil at 80% + on local. 

