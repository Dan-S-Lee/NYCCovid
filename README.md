# NYC COVID Dashboard
Dashboard website that displays New York City's cumulative COVID-19 Reports broken down by Zip Code Tabulated Areas (ZCTA).
http://www.danleedata.com/

## Usage
The map on the homepage has pop-up functionality, where more data is displayed when the red circles are clicked. 

![alt text](https://dan-s-lee.github.io/NYCCovid/docs/images/PopupDemo.png "Pop-up function demo")

The statistics page features real-time regressions on the total number of COVID cases against various demographics including race, median income, and poverty rate. Certain correlations are not statistically signficant but were still kept for illustrative purposes.

## Built with
* Python - Packages such as folium, dash, pandas, sqlite3, lxml allowed for easy, concise code for data collection and visualization
* Bootstrap - Free open-source CSS framework focused on responsive, mobile-first web development
* Python Anywhere - Online IDE and web hosting service that is used to display the HTML files generated from the program

### Data Sources

[US 2010 Census](https://data.census.gov/)

[NYC Department of Health](https://www1.nyc.gov/site/doh/covid/covid-19-data.page#download)
