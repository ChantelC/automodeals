# -*- coding: utf-8 -*-

'''This is automated code to add and commit the updated all_cars.csv file to GitHub'''

import subprocess as cmd
from datetime import datetime
import os
import pandas as pd

def uploadRepository(newsz, **kwargs):

	if 'dailynm' in kwargs.keys():
		dailynm = kwargs['dailynm']
	else:
		dailynm = None

	try:
		cmd.run("git add data/all_cars.csv", check=True, shell=True)
		cont = 1
	except:
		print('Adding crashed!')
		# Save to error log
		crash_df = pd.DataFrame({'timestamp':[str(datetime.now().strftime("%Y-%m-%d %H%M%S"))], 'message':['Git add crash']})
		if os.path.isfile('errors/git_error_log.csv'):
			crash_df.to_csv('errors/git_error_log.csv', mode='a', index=False, header=False)
		else:
			crash_df.to_csv('errors/git_error_log.csv', index=False)			
		cont = 0
		
	if dailynm:
		try:
			cmd.run(f"git add {dailynm}", check=True, shell=True)
		except:
			print("Couldn't add backup daily csv via git. Add manually.")
			# Save to error log
			crash_df = pd.DataFrame({'timestamp':[str(datetime.now().strftime("%Y-%m-%d %H%M%S"))], 'message':["Couldn't add backup daily csv via git. Add manually."]})
			if os.path.isfile('errors/git_error_log.csv'):
				crash_df.to_csv('errors/git_error_log.csv', mode='a', index=False, header=False)
			else:
				crash_df.to_csv('errors/git_error_log.csv', index=False)

	message = f'{str(datetime.now().strftime("%Y-%m-%d %H%M%S"))} - There are now {newsz} cars in all_cars.csv'
	print(message)

	if cont == 1:
		try:
			cmd.check_call(['git'] + ['commit', '-m', f'{message}'])
			cont = 1
		except:
			print('Committing crashed!')
			# Save to error log
			crash_df = pd.DataFrame({'timestamp':[str(datetime.now().strftime("%Y-%m-%d %H%M%S"))], 'message':["Git commit crash"]})
			if os.path.isfile('errors/git_error_log.csv'):
				crash_df.to_csv('errors/git_error_log.csv', mode='a', index=False, header=False)
			else:
				crash_df.to_csv('errors/git_error_log.csv', index=False)
			cont = 0

	if cont == 1:
		try:
			cmd.run("git pull project master", check=True, shell=True)
			cont = 1
		except:
			print('Pulling crashed!')
			# Save to error log
			crash_df = pd.DataFrame({'timestamp':[str(datetime.now().strftime("%Y-%m-%d %H%M%S"))], 'message':["Git pull crash"]})
			if os.path.isfile('errors/git_error_log.csv'):
				crash_df.to_csv('errors/git_error_log.csv', mode='a', index=False, header=False)
			else:
				crash_df.to_csv('errors/git_error_log.csv', index=False)
			cont = 0

	if cont == 1:
		try:
			cmd.run("git push project master", check=True, shell=True)
			cont = 1
		except:
			print('Pushing crashed!')
			# Save to error log
			crash_df = pd.DataFrame({'timestamp':[str(datetime.now().strftime("%Y-%m-%d %H%M%S"))], 'message':["Git push crash"]})
			if os.path.isfile('errors/git_error_log.csv'):
				crash_df.to_csv('errors/git_error_log.csv', mode='a', index=False, header=False)
			else:
				crash_df.to_csv('errors/git_error_log.csv', index=False)
			cont = 0

	if cont == 1:
		print()
		print(message)