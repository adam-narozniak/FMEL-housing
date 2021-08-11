# fmel_housing
## Install requirements
`pip install -r  requirements.txt`
## Run webscrapping version
Edit ./resources/credentials_config.json and ./resources/email_credentials_config.json, then run<br>
`python3 main_webscrapping.py --mode voice --date "16/08"`<br>
Mode can be: voice or email.
Voice mode plays a short audio announcing the possibility of a free place.
Email mode sends an email (sender and recipient is the same mail) with a link to the page to make a reservation.
You can choose date from: 16/08, 01/09, 16/09 or 01/10.