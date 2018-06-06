#!/usr/bin/python
# Adapted from Google's Python API module 

import os, time

from googleapiclient import discovery
import httplib2
from oauth2client import client
from oauth2client import file as oauthFile
from oauth2client import tools
from io import StringIO
from IPython.display import Markdown, display
import pandas as pd
import numpy as np


API_NAME = 'dfareporting'
API_VERSION = 'v3.0'
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
              'https://www.googleapis.com/auth/dfatrafficking',
              'https://www.googleapis.com/auth/ddmconversions']

# Filename used for the credential store.
CREDENTIAL_STORE_FILE = API_NAME + '.dat'



def load_application_default_credentials():
  """Atempts to load application default credentials.
  Returns:
    A credential object initialized with application default credentials or None
    if none were found.
  """
  try:
    credentials = client.GoogleCredentials.get_application_default()
    return credentials.create_scoped(API_SCOPES)
  except client.ApplicationDefaultCredentialsError:
    # No application default credentials, continue to try other options.
    pass


def load_user_credentials(client_secrets, storage, flags):
  """Attempts to load user credentials from the provided client secrets file.
  Args:
    client_secrets: path to the file containing client secrets.
    storage: the data store to use for caching credential information.
    flags: command-line flags.
  Returns:
    A credential object initialized with user account credentials.
  """
  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets,
      scope=API_SCOPES,
      message=tools.message_if_missing(client_secrets))

  # Retrieve credentials from storage.
  # If the credentials don't exist or are invalid run through the installed
  # client flow. The storage object will ensure that if successful the good
  # credentials will get written back to file.
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)

  return credentials


def setup(flags):
  """Handles authentication and loading of the API.
  Args:
    flags: command-line flags obtained by calling ''get_arguments()''.
  Returns:
    An initialized service object.
  """
  # Load application default credentials if they're available.
  credentials = load_application_default_credentials()

  # Otherwise, load credentials from the provided client secrets file.
  if credentials is None:
    # Name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret, which are found
    # on the Credentials tab on the Google Developers Console.
    try: 
      client_secrets = os.path.join(os.path.dirname(__file__),'client_secrets.json') 
      storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
      credentials = load_user_credentials(client_secrets, storage, flags)
    except: 
      try:
        client_secrets = os.path.join(os.path.dirname(__file__),'client_id.json') 
        storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
        credentials = load_user_credentials(client_secrets, storage, flags)
      except:
        try:
          client_secrets = os.path.join(os.path.dirname(__file__),'client_secret.json') 
          storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
          credentials = load_user_credentials(client_secrets, storage, flags)  
        except:
          print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'The "client_id.json" file is not in the working directory. \nRefer to the guide and make sure it is placed in the working folder, then try again.')        

  if credentials is not None:

    # Authorize HTTP object with the prepared credentials.
    http = credentials.authorize(http=httplib2.Http())

    # Construct and return a service object via the discovery service.
    return discovery.build(API_NAME, API_VERSION, http=http)


def download_report(profile_id, report_id):
  flags = {'auth_host_name': 'localhost', 'noauth_local_webserver': False, 'auth_host_port': [8080, 8090], 'logging_level': 'ERROR', 'profile_id': profile_id, 'report_id': report_id}
  service = setup(flags)
  ##service = dfareporting_utils.setup(flags)
  try:
      # Construct a get request for the specified report.
      request = service.reports().run(profileId=profile_id, reportId=report_id)
      # Execute request and print response.
      result = request.execute()

  # Pause so request can be processed
      time.sleep(5)
      start_time = time.time()
      while True:
          try:
              # Construct a get request for the specified profile.
              request = service.files().list(profileId=profile_id)
              response = request.execute()
          except client.AccessTokenRefreshError:
              print ('The credentials have been revoked or expired, please re-run the application to re-authorize')        
          
          def recent_report(current_report_id):
              out1 = []
              for this in response['items']:
                if this['reportId'] == current_report_id:
                  out1.append(this)  
              run_times = [x['lastModifiedTime'] for x in out1]
              return out1[next((index for (index, d) in enumerate(out1) if d["lastModifiedTime"] == max(run_times)), None)]
        
          if 'REPORT_AVAILABLE' in recent_report(report_id)['status']:
            break
          else:
            if recent_report(report_id)['status'] != 'PROCESSING':
              print('ERROR: Processing failed. Try again.')
              break
            else:
              print('\r', recent_report(report_id)['status'], '; time elapsed: ', int(time.time() - start_time), ' seconds', end='')    
          time.sleep(2)

      flags['fileId']=recent_report(report_id)['id']
      try:
          # Construct the request.
          request = service.files().get_media(reportId=report_id, fileId=flags['fileId'])
          # Execute request and save the file contents
          report_obj = request.execute().decode("utf-8")
      except client.AccessTokenRefreshError:
          print ('The credentials have been revoked or expired, please re-run the application to re-authorize')
      
      report_string = ''.join(report_obj.partition('Report Fields')[1:])
      # skipping footer to remove 'Grand Totals' row
      report_df = pd.read_csv(StringIO(report_string), skiprows=1, skipfooter=1, engine='python')
      report_df.columns = report_df.columns.str.lower().str.replace(' ', '_')
      if 'total_conversions' in report_df:
          report_df['total_conversions'] = report_df.total_conversions.astype(int)

      report_meta_string = ''.join(report_obj.partition('Report Fields')[:1])
      report_meta_df = pd.read_csv(StringIO(report_meta_string), engine='python')

      return report_df, report_meta_df

  except client.AccessTokenRefreshError:
      print ('The credentials have been revoked or expired, please re-run the application to re-authorize')
  except discovery.HttpError:
      print('Report id incorrect or unavailable. Check front-end DCM')

def create_report():

  try:
    profile_id_dcmapi
  except NameError:
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'You must enter your DCM profile ID.')
    return

  try:
    report_name_dcmapi
  except NameError: 
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'You must name your report')
    return

  try:
    report_type_dcmapi
  except NameError:
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'You must choose your report_type')
    return
  ''' 
  try:
    relative_date_range_dcmapi
  except NameError:
    relative_date_range_dcmapi = ''

  try:
    start_date_dcmapi
  except NameError:
    start_date_dcmapi = ''

  try:
    end_date_dcmapi
  except NameError:
    end_date_dcmapi = ''  
  '''
  if all(v for v in [relative_date_range_dcmapi, start_date_dcmapi, end_date_dcmapi]):
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'You have entered both a relative_date_range and start/end dates. Only one of these can be used')
    return
  elif relative_date_range_dcmapi:
    if relative_date_range_dcmapi.upper() in ['LAST_24_MONTHS', 'LAST_30_DAYS', 'LAST_365_DAYS', 'LAST_7_DAYS', 'LAST_90_DAYS', 'MONTH_TO_DATE', 'PREVIOUS_MONTH', 'PREVIOUS_QUARTER', 'PREVIOUS_WEEK', 'PREVIOUS_YEAR', 'QUARTER_TO_DATE', 'TODAY', 'WEEK_TO_DATE', 'YEAR_TO_DATE', 'YESTERDAY']:
      dates = {"relativeDateRange": relative_date_range_dcmapi.upper()}
    else:
      print('You have entered a relative date range that is not supported. Check your entry and try again. Otherwise, leave this value blank and set start/end dates.')
      return
  elif start_date_dcmapi and end_date_dcmapi:
    from datetime import date, timedelta, datetime
    import dateutil.parser as parser
    start_date1 = str(date(parser.parse(start_date_dcmapi).year, parser.parse(start_date_dcmapi).month, parser.parse(start_date_dcmapi).day))
    end_date1 = str(date(parser.parse(end_date_dcmapi).year, parser.parse(end_date_dcmapi).month, parser.parse(end_date_dcmapi).day))
    if start_date1 > end_date1:
      print('Your start date is after your end date. Please adjust your dates.')
    else:
      dates = {"startDate": start_date1, "endDate": end_date1}
  else:
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'Define either a relative_date_range or start/end dates')
    return
  
  try:
    dimensions_list = [{'name':x} for x in list(set(dimensions_dcmapi))]
  except NameError:
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'Choose at least one dimension to report on')
    return

  try:
    metrics_dcmapi
  except NameError:
    print('\x1b[1;31m'+'ERROR: '+'\x1b[0m'+ 'Choose at least one metric to report on')
    return
   
  ccc = ['dfa:'+v.split('_dimfilter')[0] for v in [s for s in globals() if '_dimfilter' in s and s.endswith('_dcmapi')]]
  ddd = [v for v in [s for s in globals() if '_dimfilter' in s and s.endswith('_dcmapi')]]
  
  dimensions_filter = []
  if ccc and ddd: 
    for i in range(len(ccc)):
        my_dict = {}
        if globals()[ddd[i]]:
            for j in range(len(globals()[ddd[i]])):
                my_dict['dimensionName'] =  ccc[i]
                my_dict['value'] = globals()[ddd[i]][j]
                dimensions_filter.append(dict(my_dict)) 

  eee = ['dfa:'+v.split('_actfilter')[0] for v in [s for s in globals() if '_actfilter' in s and s.endswith('_dcmapi')]]
  eee = list(set([i.replace('Id', '') for i in eee]))
  fff = [v for v in [s for s in globals() if '_actfilter' in s and s.endswith('_dcmapi')]]
  activities_filter = []
  if eee and fff:
    for i in range(len(eee)):
        my_dict2 = {}
        if globals()[fff[i]]:
            for j in range(len(globals()[fff[i]])): 
                my_dict2['dimensionName'] =  eee[i]
                my_dict2['id'] = globals()[fff[i]][j]
                activities_filter.append(dict(my_dict2)) 

  if eee and [v for v in [s for s in globals() if '_dimfilter' in s and 'activitiy' in s and s.endswith('_dcmapi')]]:
    print('ERROR: You entered activity fields both to filter dimensions and as columns. Only one can be used at a time.')
    return

  if all(v is not None for v in [profile_id_dcmapi,report_name_dcmapi,report_type_dcmapi,dates,dimensions_dcmapi,metrics_dcmapi]):

    flags = {'auth_host_name': 'localhost', 'noauth_local_webserver': False, 'auth_host_port': [8080, 8090], 'logging_level': 'ERROR', 'profile_id': profile_id_dcmapi}
    service = dcm_tools.setup(flags)
    try:
        # Create a new report resource to insert
        report = {
            'name': report_name_dcmapi,
            'type': report_type_dcmapi,
            'criteria': {
                'dateRange': dates,
                'dimensions': dimensions_list,
                'metricNames': metrics_dcmapi}}

        if dimensions_filter:
          report['criteria']['dimensionFilters'] = dimensions_filter

        if activities_filter:
          report['criteria']['activities'] = {}
          report['criteria']['activities']['filters'] = activities_filter

        try:
         report['criteria']['activities']['metricNames'] = list(set(metrics_activities_dcmapi))
        except NameError:
          pass
        
        # Construct the request.
        request = service.reports().insert(profileId=profile_id_dcmapi, body=report)
        # Execute request and print response.
        response = request.execute()
        new_report_id = response['id']
        print ('Created %s report with ID %s, time range %s, and name "%s".'
               % (response['type'], response['id'], dates, response['name']))
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the '
               'application to re-authorize')
        return

    try:
      # Construct a get request for the specified report.
      request = service.reports().run(profileId=profile_id_dcmapi, reportId=new_report_id)
      # Execute request and print response.
      result = request.execute()
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the application to re-authorize')
        return

    def recent_report(current_report_id):
      out1 = []
      for this in response['items']:
        if this['reportId'] == current_report_id:
          out1.append(this)  
      run_times = [x['lastModifiedTime'] for x in out1]
      return out1[next((index for (index, d) in enumerate(out1) if d["lastModifiedTime"] == max(run_times)), None)]

    # Pause so request can be processed
    time.sleep(5)
    start_time = time.time()
    while True:
        try:
            # Construct a get request for the specified profile.
            request = service.files().list(profileId=profile_id_dcmapi)
            response = request.execute()
            recent_report(new_report_id)['fileName'] = report_name_dcmapi
        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the application to re-authorize')
        if report_name_dcmapi not in recent_report(new_report_id)['fileName']:
            print("Report name incorrect. Check front-end DCM")
            break
        else:
            if 'REPORT_AVAILABLE' in recent_report(new_report_id)['status']:
                break
            else:
              if recent_report(new_report_id)['status'] != 'PROCESSING':
                print('ERROR: Processing failed. Try again.')
                break
              else:
                print('\r', recent_report(new_report_id)['status'], '; time elapsed: ', int(time.time() - start_time), ' seconds', end='')
        time.sleep(2)
    print('Report has been processed successfully')
    print('Downloading report...')
    flags['fileId']=recent_report(new_report_id)['id']
    try:
        # Construct the request.
        request = service.files().get_media(reportId=recent_report(new_report_id)['reportId'], fileId=flags['fileId'])
        # Execute request and save the file contents
        report_obj = request.execute().decode("utf-8")
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the application to re-authorize')
    print('Converting report to a pandas df...')
    report_string = ''.join(report_obj.partition('Report Fields')[1:])
    # skipping footer to remove 'Grand Totals' row
    report_df = pd.read_csv(StringIO(report_string), skiprows=1, skipfooter=1, engine='python')
    report_df.columns = report_df.columns.str.lower().str.replace(' ', '_')
    if 'total_conversions' in report_df:
        report_df['total_conversions'] = report_df.total_conversions.astype(int)

    report_meta_string = ''.join(report_obj.partition('Report Fields')[:1])
    report_meta_df = pd.read_csv(StringIO(report_meta_string), engine='python')    
    
    ''' TODO:
    if dimensions_filter:
      report_meta_df.loc['dimensions_filter',report_meta_df.columns[0]]= str(dimensions_filter)

    report_meta_df.loc['dimensions',report_meta_df.columns[0]] = str(dimensions_dcmapi)

    report_meta_df.loc['metrics',report_meta_df.columns[0]] = str(metrics_dcmapi)

    if activities_filter:
      report_meta_df.loc['activities_filter',report_meta_df.columns[0]] = str(activities_filter)

    if metrics_activities_dcmapi:
      report_meta_df.loc['metrics_activities',report_meta_df.columns[0]] = str(metrics_activities_dcmapi)
    '''

    print('\nReport imported successfully')
    return report_df, report_meta_df

def printmd(string):
    display(Markdown(string))


def dcm_api_init(dcm_profile_id):  
  from argparse import Namespace
  flags = Namespace(auth_host_name= 'localhost', noauth_local_webserver= False, auth_host_port= [8080, 8090], logging_level= 'ERROR', profile_id = dcm_profile_id)
  service = setup(flags)
  if service is not None:    
    #printmd('**API access: Success**')
    print('\x1b[1;31m'+'API access: '+'\x1b[0m'+ 'Success')




