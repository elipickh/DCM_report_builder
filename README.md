# DCM report builder
## Create and download DoubleClick Campaign Manager (DCM) reports in Python

This Python code automatically initializes your access to DCM's API and then provdes easy access to pre-configued reports or to create and run new reports.

# A. Pre-reqs. (this should only be done the first time running the API)

1. 
  1. Go to https://console.developers.google.com/start/api?id=dfareporting&credential=client_key (using your DCM login) <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;and click <font color='green'>Continue</font> to create a project:

  <img src="https://preview.ibb.co/iDytKR/01.png" width="300" align="left"/>
  <br><br><br><br><br><br><br><br><br>

  2. You should see the message: _The API is enabled_. <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Click on <font color='green'>Go to credentials</font>

  3. Set the following settings (i.e., <font color='red'>Other UI</font> and <font color='red'>User data</font>):

  <img src="https://preview.ibb.co/jkNLzR/02.png" width="300" align="left"/>
  &nbsp;&nbsp;&nbsp;&nbsp;<br><br><br><br><br><br><br><br><br><br><br><br><br><br>

  4. Click <font color='green'>What credentials do I need?</font>, then enter something for the client name (e.g., <font color='red'>dcm_api</font>):

  <img src="https://preview.ibb.co/jYDhDm/03.png" width="300" align="left"/>
  <br><br><br><br><br><br><br><br><br><br><br>

  5. Click <font color='green'>Create client ID</font>. Under *'product name shown to user'* enter something (e.g., <font color='red'>dcm_api</font>):

  <img src="https://preview.ibb.co/gM5vYm/04.png" width="300" align="left"/>
  <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

  6. Click <font color='green'>Continue</font> then <font color='green'>Download</font> to get the json file containing the API credentials. Click <font color='green'>Done</font>.

2. Place the json file in the *working directory* (i.e., where you are/will be running this notebook from).

## B. Get your Samsung DCM profile ID. 
#### Can be found in DCM by clicking the round user icon (top right) -- the profile ID is the 7-digit number next to your user name.

## C. Use the following screen as a reference for the available fields in a (STANDARD) report:

<img src="http://preview.ibb.co/fkabkc/Screen_Shot_2018_02_04_at_15_46_46.png" width="500" align="left"/>
