# Project Name

tete-a-tete

## Description

A tête-à-tête, from the French "head to head," refers to a private conversation between two people.  This is an app that allows you to easily keep track of your 1:1s, including managing agendas, keeping track of to-do items, and establishing metrics over time based on employee sentiment.  Future information will be added as we get fully integrated with identity providers and scheduling tools.

## Local Development

To build locally, clone the repo and run "docker-compose --profile frontend up -d --build" at the top level.  This will build containers for the react app, the django app, and a postgres DB mounted to a volume so it persists data across restarts.  If you omit the "--profile frontend" you'll only get the django app and the db; you can the run "npm start" in the ui folder and edit your .js files live.