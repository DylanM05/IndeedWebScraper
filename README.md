IndeedScraper.py

This will scrape Indeed.com for jobs. It will take keywords, a location, radius in KMs, and number of pages per query it will look at.

It will combine keywords1 and keywords2 in order to make descriptive queries with each different word combo.

It will then click on each job listing on each page, and copy all of the information from it.
Including:
Job Title
Company Name
Rating out of 5
Location
Posting Description
URL of job posting

Then save it to an excel file for later use.


ListingOrganizer.py

This will take an excel file, (designed to take the output from IndeedScraper) and organize it and clean it up

It uses Google maps API in order to find the distance between a location I put in, and the locations on the job postings.
It also checks whether the job is remote or hybrid.

It then sorts all of the jobs by distance from the location I put in, (I put my home town)

But before that it puts everything that is remote or hybrid at the very top regardless of their location.

It also checks if there are duplicate listings, excluding the link as chances are, if there are multiple listings, they will have seperate links

It also creates columns for Distance to Peterborough, and a true or false marker whether it's remote or hybrid.
