# Trumid Financial Takehome

Initial thoughts with the take home were to establish an initial quick answer process through a form of exploratory data analysis using a Jupyter Notebook to conduct a quick review of code. This Notebook was an attempt to quickly find ways of answering the first two questions listed on the take-home. Quick and easy identification of stations that are running either full or empty, or then the best possible way of evaluating whether or not a bike is lost or stolen.

### Repo Index
#### Bike Anlaysis - Quick throw together of Terraform Code to deploy two cloud functions capable of analyzing dictionaries to report on station fill, and bike theft
#### Creds - Folder to hold users BigQuery Service Account creds.
#### Data - Demo data to be used in the trumid_bike_analysis.ipynb.
#### Docs - Quick store of the two citi-bike tables to hold local area for column definitions and data-types.
#### trumid_bike_analysis.ipynb - Quick and dirty show the functions written in Bike Analysis function as intended.
#### trumid_eda.ipynb - EDA and code showing SQL work to satisfy first two questions on take home.
#### venv.sh - Quck shell script to stand up local virtual environemnt to run the current code.


## Requirements
Setting up your local environment will require work to establsh the proper python environemnt, and then also ensuring you have working creds to establish a connection to BigQuery

### Python 
The user in order to run this code has either one of two options to mimic the proper environemnt. They can either use the included requiremnets.txt in order to ensure the proper python packages are installed, or they can use the included shell script to create a virtual environment to use. This process can be seen by the execution of the following command.
```bash
source venv.sh
```

From there if within VSCode please follow the [following instructions][3] to ensure your Python Interpreter is set to use the newly created venv.  

### GCP Setup for Local Runs
Execution of the following Jupyter Notebook requires the user to extract a service account from gcp and save it down to the creds folder. The following link should give the user an idea of how to extract a key from Google Cloud IAM. [Working Link][1]

This file will need to be saved in the following location, and as the following file name for quick and easy plugin. There is a pre-existing file within this repo called the local-creds that contians an example of what the dictionary should look like.
`creds/personal_creds.json`


## EDA Notebook
For the EDA Notebook my objective with it from the outset was to isolate all of the data aggregation, munging, and labeling of the data to BigQuery. The size of the dataset is 7Gb which I would say is moderately large, and then the data resides in BigQuery. Might as well use BigQuery waht it was built for to do very quick analysis on large datasets. Python will then be used when necessary to perform either minor alterations to summarized datasets, or display results visually.

### Detection of Station Fill
#### Assumptions
- Will be able to use the `station_id` column in both the `citibike_stations` and `citibike_trips` tables to match back more information to enrich that data.
- Some records will exist here which show mass amounts of bikes moving between stations without a trip log exisiting. Think like start and end station with no trip duration or anything.
- Trip logs are inserted into the table without require an endtime. Was curious that there were not entries like this in the trips table, but that sugests that the trips tbale here truly just logs complete trips only. Not incomplete trips.


#### Thoughts
Pushed as much code here to a query to be executed in BigQuery to perform a series of unions, and window calculations right off the bat. I will say personally that the syntax to perform both these types of transformations is not only easier to read in SQL, but also easier to implement. Again, the stated goal here with data processing remains true here to push as much of it up to BigQuery as possible in order to take advantage of its processing capabilities.

What didn't work on this initial run through here was the ability to bound the upper and lower bounds of the station according to the requirements of this take-hoe. Initially I tried to 'over-solve' the problem and massage the data so that in instances where the upper or lower bounds were violated no more bikes could be added to the stations. I attempted this by thinking I could loop over the returned dataframe in Python, and then manually adjust the current element being looped over. It would be kept within the bounds, set to the upper bound if the cumulative violates the upper bound, or set to the lower bound if the cumulative violates the lower bound. Thus keeping the cumulative sum bounded for the duration of trip records.

Wasn't able to do this, and then quickly revisited the original SQL code to find a way of just identifying when one of the bounds has been violated. Decided to just then quickly use a Query within the WHERE clause of the tracker CTE to filter for the earliest date where one of the bounds is violated. Then filter back on this. This query should work to identify, if given a station id, the datetime when a station has either reached fill or empty.  


#### Next Steps/ Optimizations
EDA here took about one hour so I decided to try and build out a short terraform repository here. Please note that this is just extra work that will most likely not work if used to try and construct it within GCP. This is all kind of a design exercise in order to take the identification of full/ empty stations to the next level.

My assumption here is that we can create a cloud function triggered by inserts occurring against a table live tracking the current status of fill at given stations. This table will have data inserted against it from some type of streaming service inserting a new record each time it arrives. Each time a latest record occurs then a re-calculation will occur against a stored `inventory_count` column. Depending on the record containing either a 1, or -1 the `inventory_count` column will be updated accordingly.

The latest record will be sent to the cloud function at this point in time as either a dictionary or series, both should work here, where the record will be reviewed by `analyze_station_inv()` function. Depending on the value either being at the upper or lower bound, or within the bound a next steps of notification and recording will occur.

Data will be inserted into a `station_fill_monitoring` tables for further analysis at a later point in time. Further, making an assumption here, that Citi uses Microsoft Teams a general message will be sent out to general channel to update Citibike Station Workers that stations are in need of attention of refilling, or emptying.


#### Testing Next Steps
Wrote simple unit tests here at this location to show that the code beahves as expected for message generation.  
`bike_analysis/source/cloud_functions/station_inventory/test_inventory_notification.py`

#### Final Thoughts
This process could be further enhanced by having further access to the CitiBike project for the purpose of exploring other datasets to further understand stations, and how bike movement is handled by the CitBike team. Without having access to something like the overall movement of bikes outside of trips it is nearly impossible to build a solution for monitoring station fill. It would be nice to have what those records are to further enrich the dataset so we could track when bikes at stations are moved without a trip being involved.

In addition to this it would be nice to know how Citibikes manages there data ingress. My assumption here is some type of messaging, but it would allow for a better understand of what could be used to trigger the cloud function to review the latest data entry.


### Evaluation of Lost/ Stolen Bikes
#### Assumptions
- This should move pretty quickly as we should just be able to look at where startime is not null and endtime is null. Bikes that are lost or stolen should just have indefinite trips.
- Given that the above is not the case I went from there to establish and idea of how we can back in to the idea of what is classified as a lost or stolen bike. Reviewing the Citibike Information Page on [Ridership Limits][2] there are two types of users and they are 'Customer' and 'Subscriber'. Given the limitations I have assigned any ride for a 'Customer' exceeding 1.5 hours (5400 seconds), and any ride by a 'Subscriber' exceeding 2 hours (7200 seconds) as lost/ stolen.

#### Thoughts
First go here was again to push all data processing and aggregation for the pre-stated reasons to GCP. Initially I was hoping that the trip table would make this super easy by having incomplete trip. Where one of either the `stoptime` or `end_station_id/end_station_name` columns would be NULL indicating an incomplete trip. This is not the case for this table though and it appears only complete trips are logged. This means that there really isn't a way to identify lost/ stolen bikes that are CURRENTLY lost/ stolen, but it is possible to identify bikes that have at one point or time been lost or stolen.

Identification of lost/ stolen bikes was then achieved by checking the aforementioned CitiBike [Ridership Limits][2] site. Establishment of buckets incremented by half hours were then applied using a CASE statement against a partition of usertype. The partition was chosen given there are different limitations on extra changes applied to ride length by usertype. The initial return shown below at least gives us the idea that our theory of seconds applied to usertype for labeling certain rides as lost/ stolen should work. 

With the below we are looking from the overall set of data that 93.9% of Customer trips resulted in no lost or stolen bikes, and then that 99.61% of Subscriber trips resulted in no lost or stolen bikes.


|    | usertype   |   trip_buckets |   bucket_count |   group_total | lost_stolen_flag   |   p_of_user |
|---:|:-----------|---------------:|---------------:|--------------:|:-------------------|------------:|
|  0 | Customer   |           1800 |        4806519 |       6191149 | False              |       77.64 |
|  1 | Customer   |           3600 |        1006746 |       6191149 | False              |       16.26 |
|  2 | Customer   |           5400 |         178543 |       6191149 | True               |        2.88 |
|  3 | Customer   |           7200 |          74047 |       6191149 | True               |        1.2  |
|  4 | Customer   |           9000 |          38608 |       6191149 | True               |        0.62 |
|  5 | Customer   |           9001 |          86686 |       6191149 | True               |        1.4  |
|  6 | Subscriber |           1800 |       44407631 |      46917572 | False              |       94.65 |
|  7 | Subscriber |           3600 |        2328967 |      46917572 | False              |        4.96 |
|  8 | Subscriber |           5400 |          81295 |      46917572 | False              |        0.17 |
|  9 | Subscriber |           7200 |          26113 |      46917572 | True               |        0.06 |
| 10 | Subscriber |           9000 |          13640 |      46917572 | True               |        0.03 |
| 11 | Subscriber |           9001 |          59926 |      46917572 | True               |        0.13 |



#### Next Steps
EDA here took about one hour so I decided to try and build out a short terraform repository here. Please note that this is just extra work that will most likely not work if used to try and construct it within GCP. This is all kind of a design exercise in order to take the identification of lost/stolen bikes to the next level.

Objective here was to create a cloud function that would be triggered by an event occurring. This event could either be an entry into a table, or the arrival of a particular set of data in PubSub message. This event could then send a data package to the function in the form of a dict to be analyzed and reviewed. The `analyze_bike_status()` function would then take this information and review it. If a bound is violated according to the CustomerType then a message will be generated for insertion into a table collection all theft data. Additionally there could be a message posted to a Microsoft teams channel indicating that this particular bike has experienced, or is experiencing a lost/ stolen event.


#### Testing Next Steps
Wrote simple unit tests here at this location to show that the code beahves as expected for message generation.  
`bike_analysis/source/cloud_functions/bike_theft/test_theft_analysis.py`

#### Final Thoughts
While this work does give us an idea of how to identify bikes that have at some point have been lost/ stolen it doesn't allow for real time understanding of a lost or stolen bike. This data though could be used to potentially determine which stations might be more likely to have bikes lost/stolen from them by backing into stations that have high rates of excessive trip times. Further if this data is enriched with either customer ID's or payment information then a potential 'no-loan' list could be established to have a form of loss prevention pushed into the Citibike Management System.

Live monitoring could be enabled as well if there was a set of incomplete trips somewhere. In a sense whatever the process is that is monitoring or counting the time of the trip reaches one of our thresholds then a notification could be sent, or data logged to a table concerning the bikes trip status.

## Finalish Considerrations
Future work should be done on two fronts here for the suggested system running in GCP.
    1. Build out architecture diagram concerning the movement of data within GCP for the system
    2. Apply understanding of daily historical data loads to cost predictions for running the bike_analysis process within GCP
    3. Stand up local Docker Image to test the terraform code. Just thinking about the idea of it.


[//]: # (Links)
[1]:https://www.progress.com/tutorials/jdbc/a-complete-guide-for-google-bigquery-authentication
[2]:https://help.citibikenyc.com/hc/en-us/articles/360032024912-How-long-can-I-keep-a-bike-out
[3]:https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters