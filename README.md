
# Trading App

An application that aims to load trades from an excel file, query additional trading information from Yahoo Financial API and calculate some values like: P&L, market values, 
net price profiles, etc.
## Tech Stack

**Client:** TailwindCSS

**Server:** Django Rest Framework

**Database:** Postgres

**Deployment:** Docker


## Installation

Clone the repository locally.

Using the terminal in the root folder of the project run:

```bash
  docker-compose up -d --build
```

This will:
- deploy backend docker container running on port 8000
- deploy Postgres database
- run migrations for database
- deploy the frontend running on port 8080

After deploy is complete, visist http://localhost:8080/index.html for accessing the web application.

*Optional: when uploading the excel, you can use the one under input_files/trades multiple data.xlsx

