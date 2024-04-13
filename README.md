# developer-metrics

User adds a github handle or list (or csv) of github handles. It will receive per user the following metrics:
- When they started coding in Starknet projets (first commit) and their progress over time. 
- Gold star: Monthly Active Developers (However MAD is multi-causal and a lagging indicator so you need leading indicators which you have more direct control over.)
- Classify the developer as a always been inactive, previously active but no longer, low-level active, and highly involved. 
- If provided a list of github handles, it will also provide a list of the most active developers in the project. And the aggregate metrics for all the idnvidiuals.

## Process

* Create a gradio app where the user can input the github handles in a variable separated by commas. Also give the option to upload a csv file with the github handles in a single column, no need to name the column (mention this to the user). then this will be read by the main.py file.
* in the backend there will a csv file (data/source/all_networks_developer_classification.csv) with the github handles and all their commits to projects in the Starknet ecosystem. the columns are: developer,month_year,network,total_commits,dev_classification (in other words we have the number of commits per developer per network per month).  main.py will read this file and match the github handles with the ones in the config.yaml file and create a subset of the csv file with only the commits of the github handles in the config.yaml file.
* It will then plot in gradio (make it as aesthetic as possible) the commits per month for each developer in the subset of the csv file. The plot will have the x-axis as the month and the y-axis as the number of commits and each developer will be there. Make the plot start wuen we get the first ever commit by any of the users inputed by the user. it will also create a table in gradio with a classification of the developers as "always been inactive" (when the developer has never commited to the starknet repos), "previously active but no longer" (when the developer has been active before but has not been active in the last 3 months), "low-level active" (when the developer has been active in the last 3 months but with a total number of commits less than 20 summed), and "highly involved" (when the developer has more than 20 commits summed in the last three months). Order the developers in the table by the their classifition starting with the highly involved.



# Welcome to AnimeMetrics

Hello there! We built **AnimeMetrics** for a simple reason: to help you understand who's building the Starknet universe, how they're doing it, and the vibrant community behind the scenes.

## What We Offer

### Get to Know the Builders
- **First Steps & Journeys**: See when a developer first dipped their toes into Starknet projects and follow their path since then.
- **Who’s Who**: We categorize contributors to help you understand their engagement level at a glance:
  - **The Quiet Ones**: Some prefer to watch from afar.
  - **The Cameo**: Once active, now less so.
  - **The Contributors**: They pop in and out, making their mark.
  - **The Pillars**: The heart and soul of projects, always there.

### Insights That Matter
- **Spotlight Metric**: Our focus on Monthly Active Developers (MAD) gives you a glimpse of the project's heartbeat. But we go beyond, offering insights that help you see the full picture, today and tomorrow.

### Bigger Picture
- Give us one, ten, or a hundred GitHub handles, and we'll show you:
  - The movers and shakers.
  - Overall vibes of the community, combining all the bits and pieces.

## Dive In

Starting is as simple as entering a GitHub handle (or a bunch of them). We'll take it from there, weaving through data to bring you insights wrapped in simplicity.

## Why We Do It

In a tech world that can often feel complex and distant, we aim to bring it down to earth. **AnimeMetrics** is here to decode the buzz of activity into stories of people, passion, and the progress they make together. Let's celebrate the community shaping Starknet, one commit at a time.

