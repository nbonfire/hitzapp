hitzapp
=======

This is a TrueSkill-based ladder for the New England NHL Hitz 2002 Players League. 

It is currently set up for deployment on heroku at hitzapp.heroku.com for testing, but it is not live.

Known Issues:
-------------

The "team" ui in the flask-admin GameRuleView leaves a lot to be desired. I want to make it so it will get or create the Team with the players specified. Currently I have trouble with https://github.com/flask-admin/flask-admin/issues/909 since we use two teams. Or I just don't know what I'm doing, which is very likely.