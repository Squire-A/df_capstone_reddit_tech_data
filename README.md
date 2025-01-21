# ![Digital Futures Academy](https://github.com/digital-futures-academy/DataScienceMasterResources/blob/main/Resources/datascience-notebook-header.png?raw=true)

# Anthony Squire - Capstone Project

## Project Requirements
1. Choose a website, API or RSS feed. It must be something that updates frequently
2. Create a script or process that obtains the data. (This script will eventually be run periodically)
   1. Consider efficiency -> Don't scrape all data every time, just the new data
3. Put the data into a table or series of tables in the SQL sandbox (DF pagila database) or preferred location
4. Create a visualisation that demonstrates an aspect of the data

## Expected Outputs
1. Project plan
2. Data flow diagram
3. Demo of script and visualisation
4. Presentation of process and product

## Proposed Project
- Utilise the reddit API to get the top 10 hot posts in the r/technology subreddit every few hours
- Store the post data in a posts table
  - id
  - title 
  - url 
  - datetime published
  - score
- Store the top 200 comments data in a comments table
  -  id
  -  post id
  -  body
  -  score
  -  datetime published
- Create and deploy a streamlit app showcasing my analysis and visualisations:
  - Generate word cloud of the most common words seen in post titles each day and in the comments of each post
  - Perform sentiment analysis of the comments and display this some way
  - Identify any trending subjects for each day

## Data Flow Diagrams

### Overall Process

```mermaid
graph TD
    A((Source: Reddit API - /r/technology))
    B[Data Collection Script]
    C[(PostgreSQL Database Tables - Posts and Comments)]
    D[Data Enrichment and Analysis]
    E[Generate Visualisations]
    F@{ shape: stadium, label: "Display Visualisations in Streamlit App"}

    A -->|Fetch Post/Comment Data| B
    B -->|Insert/Update Records| C
    C -->|Provide Post/Comment Data| D
    D --> E
    E --> F
```


### Data Collection Script

```mermaid
graph TD
    A@{shape: circle, label: "Start Script"}
    B@{shape: tri, label: "Fetch hot /r/technology Posts from Reddit API"}
    C@{shape: diamond, label: "Check Posts Table" }
    D@{shape: subproc, label: "Insert Post into Posts Table"}
    E@{shape: subproc, label: "Update Post in Posts Table"}
    F@{shape: diamond, label: "Check Comments Table" }
    G@{shape: subproc, label: "Insert Comment into Comments Table"}
    H@{shape: subproc, label: "Update Comment in Comments Table"}
    I@{shape: hex, label: "Rank and Delete Comments where Rank > 200"}
    J@{shape: subproc, label: "Commit Changes to Database"}
    K@{shape: dbl-circ, label: "End Script"}

    A --> B
    B --> |"Extract Post Details"| C
    C --> |"New Post"| D
    C --> |"Existing Post"| E
    B --> |"Extract top 200 comments"| F
    F --> |"New Comment"| G
    F --> |"Existing Comment"| H
    G --> I
    H --> I
    D --> J
    E --> J
    I --> J
    J --> K
```