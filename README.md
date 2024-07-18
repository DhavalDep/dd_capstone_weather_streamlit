# 📊 UK Weather Application

This is a streamlit application that is used to see the current weather and forecasted weather for certain cities in the UK.

It uses a python code (https://github.com/DhavalDep/WeatherPyFile) to collect data from an API about the weather and store this in two SQL tables, which is run hourly on a CRON job.
This data is then used by the streamlit app to create a nice dashboard where a user can see: The current temperature, the current condition,
the forecasted temperature for the day, and also the accuracy of yesterdays forecast, for a UK city of the users choice. This is all presented,
tidily to the user by an easy to read/use interface.


### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
