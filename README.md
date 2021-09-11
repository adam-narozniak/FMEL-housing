# FMEL HOUSING BOT
#Prerequisites
## Install Chrome driver
The works using google Chrome. Make sure that you have it installed. Additionally, you will have to install a driver 
that enable __selenium__ (one of the libraries used in the program) to communicate with Chrome. I'll show you what do
you have to do in the next few steps:
* Check the Chrome version. = Open Chrome. Click the three dots in the right top corner, 
  then Help and About Google Chrome.
* Open this page https://sites.google.com/a/chromium.org/chromedriver/downloads and download ChromeDriver 
  corresponding to your Chrome version.
* Place downloaded file in /usr/local/bin if you are using Mac/Linux or if you are on the Windows create a directory in
\Program Files called WebDriver\bin. Then add this path to PATH. <br>
  ```setx /m path "%path%;<copy_your_path_with_Webdriver\bin_here>"```
## Install requirements
`pip install -r  requirements.txt`
# Run
Put your credentials (login and password) in:
* ./resources/credentials_config.json for a __FMEL account__
* ./resources/email_credentials_config.json for an __email account__

Change directory (in command line) to the one containing python sciprts.
<br>Run: <br>
`python3 main_webscrapping.py --mode voice --date "16/08" --refresh_rate 5 --full_automation`<br>
See parameters explanation below.
###Mode
It can be: voice, email or mix (voice + email).

* voice mode - plays a short audio announcing the possibility of a free place (when the page changes).
* email mode - sends an email (sender and recipient is the same mail) with a link to the page to make a reservation.<br>
**_NOTE:_** only gmail email address is supported now.<br>
### Date
Format __dd/mm__ is required.
###Refresh rate
The program refreshed the page after every x seconds. Default is 2.5 s (in case you don't specify the parameter).
### Full automation
The program puts newly appearing offer to the basket.<br>

## How does FMEL booking process work
When an offer appears then you have to click __SELECT__. Then you have to click __BOOK NOW__ button. 
If you do that the offer will be in your basket for 30 minutes and no one else will see it. At the same time it 
does not mean you have to take the offer. If you do not take any action for 30 minutes you loose the offer.

**_NOTE:_** The program enables you to search for one date, if you wish to check many dates you have to run program 
many times with different date parameters.