# Job Listing Scraper

## What is this?

This is a web scraper! It scrapes job listings from the websites of various companies and puts them into a database. This database is used by the frontend hosted at https://technljobboard.vercel.app/.
You find the source code for the frontend [here](https://github.com/techNL-dev/Job-Listing-Frontend).

## Todo

- [x] Fix description scraping
- [x] Add the rest of the websites
- [x] Set up selenium web scraping
- [x] Automate the scraping once a day
- [x] Make listings persist correctly
- - [x] Delete only listings that weren't found when scraping
- - [x] Add only listings that are not already in the database
- - [x] Upload deleted listings to a second collection
- [x] Sync collections to spreadsheets
- - [x] Sync changes from spreadsheets
- [x] Add error handling
