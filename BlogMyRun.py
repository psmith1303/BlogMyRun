#!/usr/bin/env python3
#
#
#

from smashrun import Smashrun

# use urn:ietf:wg:oauth:2.0:oob for applications that aren't a web app
client = Smashrun(client_id='my_client_id',
                  redirect_uri='urn:ietf:wg:oauth:2.0:auto')
auth_url = client.get_auth_url()
code = input("Go to '%s' and authorize this application. Paste the provided code here:" % auth_url[0])
client.fetch_token(code=code)
