#-*- coding: utf-8 -*-
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pickle
from datetime import datetime, timedelta
import base64
import os

class res_config_settings(models.TransientModel):
	_inherit = 'res.config.settings'

	@api.onchange('secrete')
	def lets_authenticate(self):
		path = os.getcwd()
		token = str(path) + '/token.pkl'
		if os.path.exists(token):
			raise ValidationError(_('Authentication already done!'))
		elif self.secrete:
			path = str(path) + '/client_secrete.json'
			file = open('client_secrete.json','wb')
			content = base64.decodebytes(self.secrete)
			file.write(content)
			file.close()
			scopes = ['https://www.googleapis.com/auth/calendar']
			flow = InstalledAppFlow.from_client_secrets_file(path, scopes=scopes)
			credentials = flow.run_console()
			pickle.dump(credentials, open("token.pkl", "wb"))
		else:
			pass

	secrete = fields.Binary('Secrete token', help="Upload your Json token file here.")	
		


class gCal(models.Model):
	_inherit = 'calendar.event'

	@api.model
	def create(self, vals):
		res = super(gCal, self).create(vals)
		path = os.getcwd()
		token = str(path) + '/token.pkl'
		summary = vals.get('name','')
		description = vals.get('description','')
		location = vals.get('location','')
		if vals.get('allday'):
			start = vals.get('start_date')
			st_dt = start.split("-")
			yr = st_dt[0]
			mnth = st_dt[1][1] if st_dt[1][0]=='0' else st_dt[1]
			dt = st_dt[2]
			start_time = yr + '-' + mnth + '-' + dt + 'T00:00:00'
			end_time = yr + '-' + mnth + '-' + dt + 'T23:59:59'
		else:
			start_time = vals.get('start_datetime')
			hours = vals.get('duration')
			st = start_time.split(" ")
			st_dt = st[0].split("-")
			st_tm = st[1].split(":")
			yr = int(st_dt[0])
			mnth = int(st_dt[1][1]) if st_dt[1][0]=='0' else int(st_dt[1])
			dt = int(st_dt[2])
			t1 = int(st_tm[0])
			t2 = int(st_tm[1])
			t3 = int(st_tm[2])
			start_time = datetime(yr, mnth, dt, t1, t2, t3)
			end_time = start_time + timedelta(hours=hours)
			start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
			end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")

		timezone = vals.get('event_tz','Asia/Kolkata')
		credentials = pickle.load(open(token, "rb"))
		service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
		result = service.calendarList().list().execute() #need to find solution on this 2 lines
		calendar_id = result['items'][0]['id']			 #everytime get all events and then calendar id
		event = {
			"summary": summary,
			"location": location,
			"description": description,
			"start": {
				"dateTime": start_time,
				"timeZone": timezone,
			},
			"end": {
				"dateTime": end_time,
				"timeZone": timezone,
			},
			"reminders": {
				"useDefault": False,
				"overrides": [
					{"method": "email", "minutes": 24 * 60},
					{"method": "popup", "minutes": 10},
				],
			},
		}
		service.events().insert(calendarId=calendar_id, body=event).execute()
		return res