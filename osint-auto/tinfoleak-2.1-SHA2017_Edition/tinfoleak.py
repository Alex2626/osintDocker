#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License:
# This work is licensed under a Creative Commons Attribution Share-Alike v4.0 License.
# https://creativecommons.org/licenses/by-sa/4.0/

"""
Tinfoleak - Get intelligenge from Twitter 
	:author: 	Vicente Aguilera Diaz
	:version: 	2.1 SHA2017 Edition

	License:
	This work is licensed under a Creative Commons Attribution Share-Alike v4.0 License.
	https://creativecommons.org/licenses/by-sa/4.0/

"""

# Classes
#	Configuration
#	User
#	Sources
#	Social_Networks
#	Geolocation
#	Search_GeoTweets
#	Hashtags
#	Mentions
#	User_Tweets
#	User_Images
# 	User_Conversations
#	Parameters
# 	Followers
# 	Friends
#	Favorites


import argparse
import tweepy
import sys
import ConfigParser
import datetime
import errno
import os
import urllib2
from PIL import Image, ExifTags, ImageCms
import exifread
import struct
import time
from datetime import date, timedelta
import pyexiv2
from collections import OrderedDict
from operator import itemgetter
from OpenSSL import SSL
from jinja2 import Template, Environment, FileSystemLoader
from urlparse import urlparse
import re
import csv
import json
import oauth2 as oauth
import operator

reload(sys)  
sys.setdefaultencoding('utf8')

# ----------------------------------------------------------------------
def credits(parameters):
	"""Show program credits"""

	print "  _______ _        __      _            _    "
 	print " |__   __(_)      / _|    | |          | |   "
 	print "    | |   _ _ __ | |_ ___ | | ___  __ _| | __"
 	print "    | |  | | '_ \|  _/ _ \| |/ _ \/ _` | |/ /"
 	print "    | |  | | | | | || (_) | |  __/ (_| |   < "
 	print "    |_|  |_|_| |_|_| \___/|_|\___|\__,_|_|\_\\"
   
 	print
	print "\t" + parameters.program_name + " " + parameters.program_version + " - \"Get intelligence from Twitter\""
	print "\t" + parameters.program_author_name + ". " + parameters.program_author_twitter
	print "\t" + parameters.program_author_companyname
	print "\t" + parameters.program_date
	print 

 
# ==========================================================================
class Configuration():
	"""Configuration information"""

	# ----------------------------------------------------------------------
	def __init__(self):
		try:
			# Read tinfoleak configuration file ("tinfoleak.conf")
			config = ConfigParser.RawConfigParser()
			config.read('tinfoleak.conf')
			self.color = config.get('colors', 'INFO')
			self.color_hdr = config.get('colors', 'HEADER')
			self.color_fun = config.get('colors', 'FUNCTION')

			CONSUMER_KEY = config.get('Twitter OAuth', 'CONSUMER_KEY')
			CONSUMER_SECRET = config.get('Twitter OAuth', 'CONSUMER_SECRET')
			ACCESS_TOKEN = config.get('Twitter OAuth', 'ACCESS_TOKEN')
			ACCESS_TOKEN_SECRET = config.get('Twitter OAuth', 'ACCESS_TOKEN_SECRET') 
			
			# User authentication
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		
			# Tweepy (a Python library for accessing the Twitter API)
			self.api = tweepy.API(auth)

			consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
			access_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_TOKEN_SECRET)

			# Twitter API
			self.client = oauth.Client(consumer, access_token)


		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class User:
	"""Information about a Twitter user"""

	screen_name = ""
	name = ""
	id = ""
	created_at = ""
	followers_count = ""
	statuses_count = ""
	location = ""
	geo_enabled = ""
	description = ""
	expanded_description = ""
	url = ""
	expanded_url = ""
	profile_image_url = ""
	profile_banner_url = ""
	tweets_average = ""
	meta = ""
	
	# ----------------------------------------------------------------------
	def set_user_information(self, api):
		try:
			self.screen_name = api.screen_name
			self.name = api.name
			self.id = api.id
			self.created_at = api.created_at
			self.followers_count = api.followers_count
			self.friends_count = api.friends_count
			self.statuses_count = api.statuses_count
			self.location = api.location
			self.geo_enabled = api.geo_enabled
			self.time_zone = api.time_zone

			td = datetime.datetime.today() - self.created_at
			if td.days > 0:
				self.tweets_average = round(float(self.statuses_count / (td.days * 1.0)),2) 
			else:
				self.tweets_average = self.statuses_count

			self.url = api.url
			 
			if len(api.entities) > 1:
				if api.entities['url']['urls']:
					self.expanded_url = api.entities['url']['urls'][0]['expanded_url']
				else:
					self.expanded_url = ""
			else:
				self.expanded_url = ""
				
			try:
				self.description = api.description 
				if api.entities['description']['urls']:
					tmp_expanded_description = api.description
					url = api.entities['description']['urls'][0]['url']
					expanded_url = api.entities['description']['urls'][0]['expanded_url']
					self.expanded_description = tmp_expanded_description.replace(url, expanded_url)
				else:
					self.expanded_description= ""
			except:
				self.expanded_description= ""		
			
			self.profile_image_url = str(api.profile_image_url).replace("_normal","")
			
			try:
				if api.profile_banner_url:
					self.profile_banner_url = str(api.profile_banner_url).replace("_normal","")
				else:
					self.profile_banner_url = ""
			except:
				self.profile_banner_url = ""
			
			self.favourites_count = str(api.favourites_count)
			self.verified = str(api.verified)
			self.listed_count = str(api.listed_count)
			self.lang = str(api.lang)

		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Sources:
	"""Get tools used to publish tweets"""

	# source = [source1, source2, ... ]
	# sources_firstdate = {source1: first_date1, source2: first_date2, ... ]
	# sources_lastdate = {source1: last_date1, source2: last_date2, ... ]
	# sources_count = {source1: tweets_number1, source2: tweets_number2, ... ]
	# sources_lasttweet = {source1: tweet_id1, source2: tweet_id2, ...}
	sources = []
	sources_firstdate = {}
	sources_lastdate = {}
	sources_count = {}
	sources_total_count = 0
	sources_percent = {}
	sources_firsttweet = {}
	sources_lasttweet = {}
	
	# ----------------------------------------------------------------------
	def set_sources_information(self, tweet):
		try:
			add = 1
			for index, item in enumerate(self.sources):
				if tweet.source == item[0]:
					add = 0
					self.sources_count[tweet.source] += 1
					self.sources_total_count += 1
					if tweet.created_at < self.sources_firstdate[tweet.source]:
						self.sources_firstdate[tweet.source] = tweet.created_at
					if tweet.created_at > self.sources_lastdate[tweet.source]:
						self.sources_lastdate[tweet.source] = tweet.created_at
					self.sources_firsttweet[tweet.source] = tweet.id
			
			if add:
				self.sources.append([tweet.source])
				self.sources_count[tweet.source] = 1
				self.sources_firstdate[tweet.source] = tweet.created_at
				self.sources_lastdate[tweet.source] = tweet.created_at
				self.sources_total_count += 1
				self.sources_lasttweet[tweet.source] = tweet.id

		except Exception, e:
			show_error(e)
			sys.exit(1)

	# ----------------------------------------------------------------------
	def set_global_information(self):
		try:

			for s in self.sources:
				self.sources_percent[s[0]] = round((self.sources_count[s[0]] * 100.0) / self.sources_total_count, 1) 

		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Followers:
	"""Get followers for the specified user"""
	
	# ----------------------------------------------------------------------
	def get_followers(self, username, api, limit):
		try:

			followers_file = username + "_followers.txt"

			username_directory = os.path.dirname(os.path.abspath(__file__)) + "/" + username
			if not os.path.isdir(username_directory):
				os.mkdir(username_directory)

			pics_directory = username_directory + "/followers-" + datetime.datetime.now().strftime('%Y%m%d')
			if not os.path.isdir(pics_directory):
				os.mkdir(pics_directory)

			csvFile = open(pics_directory + "/" + followers_file, "wb")
			csvWriter = csv.writer(csvFile)
			csvWriter.writerow(["", "TINFOLEAK Report"])
			csvWriter.writerow(["", "Vicente Aguilera Díaz"])
			csvWriter.writerow(["", "@VAguileraDiaz"])
			csvWriter.writerow(["", "www.isecauditors.com"])
			csvWriter.writerow([""])
			csvWriter.writerow(["", ">>> Date:", datetime.datetime.now().strftime('%Y-%m-%d')])
			csvWriter.writerow(["", ">>> Time:", datetime.datetime.now().strftime('%H:%M')])
			csvWriter.writerow(["", ">>> Analyzed user:", username])
			csvWriter.writerow(["", ">>> Information:", "Followers"])
			csvWriter.writerow([""])
			csvWriter.writerow(["#", "ID", "USERNAME", "SCREEN NAME", "DESCRIPTION", "PROFILE IMAGE URL", "PROFILE BANNER URL", "CREATED AT", "LOCATION", "TIME_ZONE", "GEO ENABLED", "FOLLOWERS COUNT", "FRIENDS COUNT", "STATUSES COUNT", "LISTED COUNT", "FAVOURITES COUNT", "USER VERIFIED", "USER LANG"])

			analyzed_user = 0
			for userid in tweepy.Cursor(api.followers_ids, screen_name=username).items():
				try:
					if int(analyzed_user) < int(limit):
						user = api.get_user(userid)
						analyzed_user += 1
						csvWriter.writerow([analyzed_user, user.id, user.name.encode('utf-8'), user.screen_name, user.description.encode('utf-8'), user.profile_image_url, user.profile_background_image_url, user.created_at, user.location, user.time_zone, user.geo_enabled, user.followers_count, user.friends_count, user.statuses_count, user.listed_count, user.favourites_count, user.verified, user.lang])
						csvFile.flush()
						sys.stdout.write("\r\t\t" + str(analyzed_user) +"/" + str(limit) + " users analyzed")
						sys.stdout.flush()

						try:
							img = urllib2.urlopen(user.profile_image_url.replace("_normal.", ".")).read()
							filename = str(user.id) + ".jpg" 
							image = pics_directory + "/" +filename
							if not os.path.exists(image):
								f = open(image, 'wb')
								f.write(img)
								f.close()
										
						except Exception, e:
							pass
					else:
						break

				except Exception, e:
					rate_limit = show_error(e)
					if rate_limit:
						print "\t\tWaiting..."
						time.sleep(60)
						continue


			print "\n\n\t\tOutput file: " + pics_directory + "/" + followers_file 

			csvFile.close()

		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Friends:
	"""Get friends for the specified user"""
	
	# ----------------------------------------------------------------------
	def get_friends(self, username, api, limit):
		try:
			friends_file = username + "_friends.txt"

			username_directory = os.path.dirname(os.path.abspath(__file__)) + "/" + username
			if not os.path.isdir(username_directory):
				os.mkdir(username_directory)

			pics_directory = username_directory + "/friends-" + datetime.datetime.now().strftime('%Y%m%d')
			if not os.path.isdir(pics_directory):
				os.mkdir(pics_directory)

			csvFile = open(pics_directory + "/" + friends_file, "wb")
			csvWriter = csv.writer(csvFile)
			csvWriter.writerow(["", "TINFOLEAK Report"])
			csvWriter.writerow(["", "Vicente Aguilera Díaz"])
			csvWriter.writerow(["", "@VAguileraDiaz"])
			csvWriter.writerow(["", "www.isecauditors.com"])
			csvWriter.writerow([""])
			csvWriter.writerow(["", ">>> Date:", datetime.datetime.now().strftime('%Y-%m-%d')])
			csvWriter.writerow(["", ">>> Time:", datetime.datetime.now().strftime('%H:%M')])
			csvWriter.writerow(["", ">>> Analyzed user:", username])
			csvWriter.writerow(["", ">>> Information:", "Friends"])
			csvWriter.writerow([""])
			csvWriter.writerow(["#", "ID", "USERNAME", "SCREEN NAME", "DESCRIPTION", "PROFILE IMAGE URL", "PROFILE BANNER URL", "CREATED AT", "LOCATION", "TIME_ZONE", "GEO ENABLED", "FOLLOWERS COUNT", "FRIENDS COUNT", "STATUSES COUNT", "LISTED COUNT", "FAVOURITES COUNT", "USER VERIFIED", "USER LANG"])

			analyzed_user = 0
			for userid in tweepy.Cursor(api.friends_ids, screen_name=username).items():				
				try:
					if int(analyzed_user) < int(limit):
						user = api.get_user(userid)
						analyzed_user += 1
						csvWriter.writerow([analyzed_user, user.id, user.name.encode('utf-8'), user.screen_name, user.description.encode('utf-8'), user.profile_image_url, user.profile_background_image_url, user.created_at, user.location, user.time_zone, user.geo_enabled, user.followers_count, user.friends_count, user.statuses_count, user.listed_count, user.favourites_count, user.verified, user.lang])
						csvFile.flush()
						sys.stdout.write("\r\t\t" + str(analyzed_user) +"/" + str(limit) + " users analyzed")
						sys.stdout.flush()

						try:
							img = urllib2.urlopen(user.profile_image_url.replace("_normal.", ".")).read()
							filename = str(user.id) + ".jpg" 
							image = pics_directory + "/" +filename
							if not os.path.exists(image):
								f = open(image, 'wb')
								f.write(img)
								f.close()
										
						except Exception, e:
							pass
					else:
						break

				except Exception, e:
					rate_limit = show_error(e)
					if rate_limit:
						print "\t\tWaiting..."
						time.sleep(60)
						continue

			print "\n\n\t\tOutput file: " + pics_directory + "/" + friends_file 

			csvFile.close()


		except Exception, e:
			show_error(e)
			sys.exit(1)



# ==========================================================================
class Social_Networks:
	"""Identify social networks identities for a user"""
	
	#: social networks used by a Twitter user:
	#: {'twitteruser': [[Instagram_user, Instagram_profile], 
	#:					[Foursquare_user, Foursquare_profile], 
	#:					[Facebook_user, Facebook_profile],
	#:					[LinkedIn_user, LinkedIn_profile],
	#:					[Runkeeper_user, Runkeeper_profile],
	#:					[Flickr_user, Flickr_profile],
	#:					[Vine_user, Vine_profile],
	#:					[Periscope_user, Periscope_profile],
	#:					[Kindle_user, Kindle_profile],
	#:					[Youtube_user, Youtube_profile],
	#:					[Google+_user, Google+_profile],
	#:					[Frontback_user, Frontback_profile]
	#:					]} 
	user_sn = {}
	see_again = 1

	# ----------------------------------------------------------------------
	def get_socialnetwork_userinfo(self, status, socialnetwork):
		try:
			#: username used in the social network
			username = "Unknown"
			#: link to the user profile in the social network
			link = ""
			#: user picture in the social network
			pic = "" 
			#: real user name 
			name = ""
			#: additional info
			info = ""
			#: html page
			html = ""

			medias = status.entities['urls']
			for m in medias:
				url = m['expanded_url']	

				try:
					response = urllib2.urlopen(url)  
					html = response.read()
				except Exception as e:	
					pass
				if socialnetwork.lower().find("instagram") >= 0:
					#: Instagram
					#: ----------------------------------------------
					
					urls = re.search('<meta property="og:title" content="Instagram post by (.*) •', html)

					if urls:
						name = urls.group(1)

					urls = re.search('viewer_has_liked":(.*)"profile_pic_url": "(.*)", "username": "(.*)", "followed_by_viewer"', html)

					if urls:
						pic = urls.group(2)
						username = urls.group(3)

					if username:					
						link = "https://instagram.com/" + username
						# Stop after the first result
						break	
				else:
					if socialnetwork.lower().find("foursquare") >= 0:
						#: Foursquare
						#: ----------------------------------------------
						urls = re.search('https://www.swarmapp.com/(.*)/checkin/', html)
						if urls:
							username = urls.group(1)
							link = "https://foursquare.com/" + username 
						else:
							urls = re.search('canonicalPath":"..(\w*)","canonicalUrl"', html)
							if urls:
								username = urls.group(1)
								link = "https://foursquare.com/" + username
						tmp = re.search('<div class="venue push"><h1><strong>(.*)</strong> at ', html)
						if tmp:
							name = tmp.group(1).decode('utf-8')

						tmp = re.search('<div id="mapContainer"><img src="(.*)" alt="(.*)" class="avatar mainUser"width="86"', html)
						if tmp:
							pic = tmp.group(1).decode('unicode-escape')
							pic = re.sub('\d{2,}x\d{2,}', '1024x1024', pic)

						if username:					
							# Stop after the first result
							break	
					else:
						if socialnetwork.lower().find("facebook") >= 0:
							#: Facebook	
							#: ----------------------------------------------
							if status.source.lower().find("facebook") >= 0:
							# Identify Faceboook acount from Facebook page
								if not html:
									# Identify Faceboook acount from 404 not found facebook page
									try:
										response = urllib2.urlopen(url) 
										html = response.read()
									except Exception as e:	
										pass
									urls = re.search(';id=(.*)">', html)
									if urls:
										try:
											response = urllib2.urlopen("https://facebook.com/profile.php?id=" + urls.group(1)) 
											html = response.read()
										except Exception as e:	
											pass
										urls = re.search('0; URL=/(.*)\/\?_fb_noscript=1', html)
										if urls:
											username = urls.group(1)									
											link = "https://facebook.com/" + username
											try:
												response = urllib2.urlopen(link)  
												html = response.read()
											except Exception as e:	
												pass
											tmp = re.search('<img class="profilePic img" alt="(.*)" src="(.*)" /></a></div></div><div class="_58gk">', html)
											if tmp:
												pic = tmp.group(2).replace("&amp;", "&")
											tmp = re.search('<span itemprop="name">(.*)</span><span class="_5rqt">', html)
											if tmp:
												info = tmp.group(1).decode('utf-8')
								else:
									urls = re.search('autocomplete="off" name="next" value="https://www.facebook.com/(.*)/posts/[0-9]*"', html)
									if urls:
										if str(urls.group(1)).find("profile.php") < 0:
											username = urls.group(1)
											link = "https://facebook.com/" + username
									else:
										try:
											response = urllib2.urlopen("http://longurl.org/expand?url="+url) 
											html2 = response.read()
											urls = re.search('<a href="https://www.facebook.com/(.*)/posts/[0-9]*">https://', html2)
										except Exception as e:
											pass
										if urls:
											username = urls.group(1)
											link = "https://facebook.com/" + username
											try:
												response = urllib2.urlopen(link)  
												html = response.read()
											except Exception as e:	
												pass
											tmp = re.search('<img class="profilePic img" alt="(.*)" src="(.*)" /></a></div></div><div class="_58gk">', html)
											if tmp:
												pic = tmp.group(2).replace("&amp;", "&")
											tmp = re.search('<span itemprop="name">(.*)</span><span class="_5rqt">', html)
											if tmp:
												info = tmp.group(1).decode('utf-8')

							else:
								if self.see_again == 0:
									username = ""
								if (self.user_sn[status.user.screen_name][1][0] and self.user_sn[status.user.screen_name][1][0].find("Unknown") < 0 and self.see_again > 0):
									# Identify Faceboook acount from Fourquare page
									self.see_again = 0
									username = ""
									try:
										response = urllib2.urlopen("https://foursquare.com/"+self.user_sn[status.user.screen_name][1][0])  
										html = response.read()
									except Exception as e:
										pass
									urls = re.search('<ul class="social"><li><a href="http://www.facebook.com/profile.php\?id=(.*)" rel="nofollow" target="_blank" class="fbLink"', html)
									if urls:
										username = urls.group(1)
										link = "http://www.facebook.com/profile.php?id=" + username
										try:
											response = urllib2.urlopen(link)  
											html = response.read()
										except Exception as e:	
											pass
										tmp = re.search('<img class="profilePic img" alt="(.*)" src="(.*)" /></div></div><meta itemprop="image"', html)
										if tmp:
											pic = tmp.group(2).replace("&amp;", "&")
										tmp = re.search('autocomplete="off" name="next" value="https://www.facebook.com/(.*)" /></form>', html)
										if tmp:
											username = tmp.group(1)
											link = "https://facebook.com/" + username
										tmp = re.search('<span id="fb-timeline-cover-name">(.*)</span></a><span class="_1xim">', html)
										if tmp:
											name = tmp.group(1)
										try:
											response = urllib2.urlopen(link)  
											html = response.read()
										except Exception as e:	
											pass
										tmp = re.search('<img class="profilePic img" alt="(.*)" src="(.*)" /></a></div></div><div class="_58gk">', html)
										if tmp:
											pic = tmp.group(2).replace("&amp;", "&")
										tmp = re.search('<span itemprop="name">(.*)</span><span class="_5rqt">', html)
										if tmp:
											info = tmp.group(1).decode('utf-8')
							if username:					
								# Stop after the first result
								break				
						else:
							if socialnetwork.lower().find("linkedin") >= 0:
								#: LinkedIn
								#: ----------------------------------------------
								if not html:
									try:
										req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
										html = urllib2.urlopen(req).read()
										
										tmp = re.search('linkedin.com/in/(.*)"/><link rel="stylesheet"', html)
										if tmp:
											username = tmp.group(1).decode('utf-8')
											link = "https://www.linkedin.com/in/" + username

										tmp = re.search('<meta property="og:image" content="(.*)"/>', html)
										if tmp:
											pic = tmp.group(1).decode('utf-8')

										tmp = re.search('<title>(.*) \| LinkedIn</title>', html)
										if tmp:
											name = tmp.group(1).decode('utf-8')
									except Exception as e:	
										pass

								if username:					
									# Stop after the first result
									break	

							else:
								if socialnetwork.lower().find("runkeeper") >= 0:
									# Runkeeper 
									#: ----------------------------------------------
									urls = re.search('"https://runkeeper.com/user/(.*)/activity/', html)
									if urls:
										username = urls.group(1)
										link = "https://runkeeper.com/user/" + username
										try:
											response = urllib2.urlopen(link)  
											html = response.read()
										except Exception as e:	
											pass
										tmp = re.search('https://graph.facebook.com(.*)" title', html)
										if tmp:
											pic = "https://graph.facebook.com" + tmp.group(1)
										tmp = re.search('<h1 id="userStatementHead"><b>(.*) is using Runkeeper</b>', html)
										if tmp:
											name = tmp.group(1).decode('utf-8')
										tmp = re.search('<meta name="description" content="(.*)"/>', html)
										if tmp:
											info = tmp.group(1)[tmp.group(1).find("joined"):].decode('utf-8')
									if username:					
										# Stop after the first result
										break				
								else:
									if socialnetwork.lower().find("flickr") >= 0:
										# Flickr
										#: ----------------------------------------------
										urls = re.search('"og:url" content="https://www.flickr.com/photos/(.*)/[0-9]*/"', html)
										if urls:
												username = urls.group(1)
												link = "https://www.flickr.com/" + username

										tmp = re.search('"image": "(.*).jpg?', html)
										if tmp:
											pic = tmp.group(1).decode('unicode-escape') + ".jpg"

										tmp = html.find('"name": ')
										if tmp:
											html = html[tmp+5:]
											tmp = html.find('"name": ')
											if tmp:
												html = html[tmp+5:]
											tmp = re.search('"name": "(.*)",', html)
											if tmp:
												name = tmp.group(1).decode('utf-8') 									
										if username:					
											# Stop after the first result
											break				
									else:
										if socialnetwork.lower().find("vine") >= 0:
											# Vine
											#: ----------------------------------------------
											urls = re.search('"name": "(.*)",', html)
											if urls:
													username = urls.group(1)
											urls = re.search('"url": "https://vine.co/u/(.*)"', html)
											if urls:
													link = "https://vine.co/u/" + urls.group(1)
											if username:					
												# Stop after the first result
												break	
										else:
											if socialnetwork.lower().find("periscope") >= 0:
												# Periscope 
												#: ----------------------------------------------
												#urls = re.search('pscp://user/(.*)&quot;,&quot;inAppUrl', html)
												urls = re.search('pscp://user/(.*)&quot;,&quot;deepLinkFollowUrl', html)
												if urls:
														username = urls.group(1)
														link = "https://www.periscope.tv/" + username

												tmp = re.search('avatarUrl&quot;:&quot;(.*)&quot;}}},&quot;usernames', html)
												if tmp:
														pic = tmp.group(1)

												if username:					
													# Stop after the first result
													break	
											else:
												if socialnetwork.lower().find("kindle") >= 0:
													# Kindle 
													#: ----------------------------------------------
													urls = re.search('customerId":"(.*)","howLongAgo', html)
													if urls:
														tmp = urls.group(1)	
														try:
															url = "https://kindle.amazon.com/profile/redirect/" + tmp
															response = urllib2.urlopen(str(url)) 
															html = response.read()
														except Exception as e:
															pass
														urls = re.search('"/profile/(.*)"', html)
														if urls:
															tmp = re.search('(.*)/[0-9]*', urls.group(1))
															if tmp:
																username = tmp.group(1)
																link = "https://kindle.amazon.com/profile/" + urls.group(1)
																try:
																	response = urllib2.urlopen(link) 
																	html = response.read()
																except Exception as e:
																	pass
																urls = re.search('<img alt="(.*)" class="profilePhoto" src="(.*).jpg" />', html)
																if urls:
																	name = urls.group(1).decode('utf-8')
																	pic = urls.group(2).decode('utf-8')
																tmp = re.search('<span id="numFollowers(.*)">(.*)</span></a>', html)
																if tmp:
																	info = "Followers: " + tmp.group(2)
																tmp = re.search('<span id="numFollowing(.*)">(.*)</span></a>', html)
																if tmp:
																	info += " Following: " + tmp.group(2)
													if username:					
														# Stop after the first result
														break													
												else:
													if socialnetwork.lower().find("youtube") >= 0:
														# Youtube 
														#: ----------------------------------------------
														urls = re.search('/channel/(.*)" class', html)
														if urls:
															tmp = urls.group(1)	
															try:
																url = "http://www.youtube.com/channel/" + tmp
																response = urllib2.urlopen(str(url)) 
																html = response.read()
															except Exception as e:
																pass
															urls = re.search('href="http://www.youtube.com/user/(.*)"', html)
															if urls:
																username = urls.group(1)
																link = "http://www.youtube.com/user/" + username
															else:
																urls = re.search('<meta property="og:title" content="(.*)">', html)
																if urls:
																	username = urls.group(1)
																	link = "http://www.youtube.com/user/" + username
															try:
																url = "http://www.youtube.com/user/" + username
																response = urllib2.urlopen(url) 
																html = response.read()
															except Exception as e:
																pass
															tmp = re.search(' <img class="appbar-nav-avatar" src="(.*)" title="(.*)" alt="', html)
															if urls:
																pic = tmp.group(1)
																name = tmp.group(2).decode('utf-8')
															tmp = re.search('<meta name="keywords" content="(.*)">', html)
															if urls:
																info = tmp.group(1).decode('utf-8').replace("&quot;", "")
														else:
															# Identify Youtube acount from Google+ page
															urls = re.search('<link itemprop="url" href="http://www.youtube.com/user/(.*)">', html)
															if urls:
																username = urls.group(1)	
																link = "http://www.youtube.com/user/" + username									
														if username:					
															# Stop after the first result
															break	
													else:
														if socialnetwork.lower().find("google") >= 0:
															# Google+ 
															#: ----------------------------------------------
															urls = re.search('"url" href="https://plus.google.com/(.*)">', html)
															if urls:
																tmp = urls.group(1)
																username = tmp
																link = "https://plus.google.com/" + username	
																try:
																	url = "https://plus.google.com/" + tmp
																	response = urllib2.urlopen(url) 
																	html = response.read()
																except Exception as e:
																	pass
																urls = re.search('href="https://plus.google.com/(.*)"><meta itemprop="name" content=', html)
																if urls:
																	username = urls.group(1)
																	link = "https://plus.google.com/" + username
																tmp = re.search('<meta itemprop="image" content="(.*)"><meta itemprop="url"', html)											
																if tmp:
																	pic = "https:" + tmp.group(1)
																tmp = re.search('<meta property="og:title" content="(.*): Google\+"><meta name="twitter:title"', html)											
																if tmp:
																	name = tmp.group(1).decode('utf-8')
																tmp = re.search('<meta itemprop="description" content="(.*)"><meta itemprop="image" content="', html)
																if tmp:
																	info = tmp.group(1).decode('utf-8')
															if username:					
																# Stop after the first result
																break	
														else:
															if socialnetwork.lower().find("frontback") >= 0:
																# Frontback 
																#: ----------------------------------------------
																urls = re.search('<h1 class="post-info-username"><a class="no-ui" href="http://www.frontback.me/(.*)">(.*)</a></h1>', html)
																if urls:
																	username = urls.group(1)
																	link = "http://www.frontback.me/" + username
																try:
																	response = urllib2.urlopen(link) 
																	html = response.read()
																except Exception as e:
																	pass
																tmp = re.search('data-image-url="(.*)"></span></header><div class="pp-usercard"><h2>(.*)</h2><strong>(.*)</strong><p>(.*)</p><span class="pp-location"><i></i>(.*)</span><a class="button button-label-big button-green" data-deeplink=', html)
																if tmp:
																	pic = tmp.group(1)
																	name = tmp.group(3)
																	info = tmp.group(5)																	

			return username, link, pic, name, info

		except Exception, e:
			show_error(e)
			sys.exit(1)

	# Other social networks
	# WhoSay, Beme, http://get.shyp.com/rt/2hrm3z7, vimeo.com (la9deanon), fancy (aplusk)

	# ----------------------------------------------------------------------
	def set_social_networks(self, status):
		try:
			# Twitter user
			owner = status.user.screen_name
			status.user.screen_name = status.user.screen_name.lower()
			if not hasattr(status, 'retweeted_status'):
				# The user is the original source of this tweet
				if status.source.lower().find("instagram") >= 0 and (self.user_sn[status.user.screen_name][0][0] == "" or self.user_sn[status.user.screen_name][0][0] == "Unknown"): 
					# Instagram user. 
					username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "instagram")
					self.user_sn[status.user.screen_name][0][0] = username
					self.user_sn[status.user.screen_name][0][1] = link
					self.user_sn[status.user.screen_name][0][2] = pic
					self.user_sn[status.user.screen_name][0][3] = name
					self.user_sn[status.user.screen_name][0][4] = info
				else:
					if status.source.lower().find("foursquare") >= 0 and (self.user_sn[status.user.screen_name][1][0] == "" or self.user_sn[status.user.screen_name][1][0] == "Unknown"):
						# Foursquare user
						username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "foursquare")						
						self.user_sn[status.user.screen_name][1][0] = username
						self.user_sn[status.user.screen_name][1][1] = link
						self.user_sn[status.user.screen_name][1][2] = pic
						self.user_sn[status.user.screen_name][1][3] = name
						self.user_sn[status.user.screen_name][1][4] = info
					if status.source.lower().find("facebook") >= 0  and (self.user_sn[status.user.screen_name][2][0] == "" or self.user_sn[status.user.screen_name][2][0] == "Unknown"):
						# Facebook user
						username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "facebook")							
						self.user_sn[status.user.screen_name][2][0] = username
						self.user_sn[status.user.screen_name][2][1] = link
						self.user_sn[status.user.screen_name][2][2] = pic
						self.user_sn[status.user.screen_name][2][3] = name
						self.user_sn[status.user.screen_name][2][4] = info
					else:
						if status.source.lower().find("linkedin") >= 0 and (self.user_sn[status.user.screen_name][3][0] == "" or self.user_sn[status.user.screen_name][3][0] == "Unknown"):
							# LinkedIn user
							username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "linkedin")					
							self.user_sn[status.user.screen_name][3][0] = username
							self.user_sn[status.user.screen_name][3][1] = link
							self.user_sn[status.user.screen_name][3][2] = pic
							self.user_sn[status.user.screen_name][3][3] = name
							self.user_sn[status.user.screen_name][3][4] = info
						else:
							if status.source.lower().find("runkeeper") >= 0 and (self.user_sn[status.user.screen_name][4][0] == "" or self.user_sn[status.user.screen_name][4][0] == "Unknown"):
								# Runkeeper user
								username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "runkeeper")						
								self.user_sn[status.user.screen_name][4][0] = username
								self.user_sn[status.user.screen_name][4][1] = link
								self.user_sn[status.user.screen_name][4][2] = pic
								self.user_sn[status.user.screen_name][4][3] = name
								self.user_sn[status.user.screen_name][4][4] = info
							else:
								if status.source.lower().find("flickr") >= 0 and (self.user_sn[status.user.screen_name][5][0] == "" or self.user_sn[status.user.screen_name][5][0] == "Unknown"):
									# Flickr user
									username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "flickr")
									self.user_sn[status.user.screen_name][5][0] = username
									self.user_sn[status.user.screen_name][5][1] = link
									self.user_sn[status.user.screen_name][5][2] = pic
									self.user_sn[status.user.screen_name][5][3] = name
									self.user_sn[status.user.screen_name][5][4] = info
								else:
									if status.source.lower().find("vine") >= 0 and (self.user_sn[status.user.screen_name][6][0] == "" or self.user_sn[status.user.screen_name][6][0] == "Unknown"):
										# Vine user
										username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "vine")
										self.user_sn[status.user.screen_name][6][0] = username
										self.user_sn[status.user.screen_name][6][1] = link
										self.user_sn[status.user.screen_name][6][2] = pic
										self.user_sn[status.user.screen_name][6][3] = name
										self.user_sn[status.user.screen_name][6][4] = info
									else:
										if status.source.lower().find("periscope") >= 0 and (self.user_sn[status.user.screen_name][7][0] == "" or self.user_sn[status.user.screen_name][7][0] == "Unknown"):
											# Periscope user
											username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "periscope")											
											self.user_sn[status.user.screen_name][7][0] = username
											self.user_sn[status.user.screen_name][7][1] = link
											self.user_sn[status.user.screen_name][7][2] = pic
											self.user_sn[status.user.screen_name][7][3] = name
											self.user_sn[status.user.screen_name][7][4] = info
										else:
											if status.source.lower().find("kindle") >= 0 and (self.user_sn[status.user.screen_name][8][0] == "" or self.user_sn[status.user.screen_name][8][0] == "Unknown"):
												# Kindle user
												username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "kindle")
												self.user_sn[status.user.screen_name][8][0] = username
												self.user_sn[status.user.screen_name][8][1] = link
												self.user_sn[status.user.screen_name][8][2] = pic
												self.user_sn[status.user.screen_name][8][3] = name
												self.user_sn[status.user.screen_name][8][4] = info
											else:
												if status.source.lower().find("google") >= 0 and status.text.lower().find("a @youtube") >= 0 and (self.user_sn[status.user.screen_name][10][0] == "" or self.user_sn[status.user.screen_name][10][0] == "Unknown"):
													# Google+ user
													username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "google")							
													self.user_sn[status.user.screen_name][10][0] = username
													self.user_sn[status.user.screen_name][10][1] = link												
													self.user_sn[status.user.screen_name][10][2] = pic
													self.user_sn[status.user.screen_name][10][3] = name
													self.user_sn[status.user.screen_name][10][4] = info
												
												if ((status.source.lower().find("youtube") >= 0 and status.text.lower().find("a @youtube") >= 0) or (status.source.lower().find("google") >= 0 and status.text.lower().find("a @youtube") >= 0)) and (self.user_sn[status.user.screen_name][9][0] == "" or self.user_sn[status.user.screen_name][9][0] == "Unknown"):
													# Youtube user
													username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "youtube")
													self.user_sn[status.user.screen_name][9][0] = username
													self.user_sn[status.user.screen_name][9][1] = link												
													self.user_sn[status.user.screen_name][9][2] = pic
													self.user_sn[status.user.screen_name][9][3] = name
													self.user_sn[status.user.screen_name][9][4] = info
												else:
													if status.source.lower().find("frontback") >= 0 and (self.user_sn[status.user.screen_name][11][0] == "" or self.user_sn[status.user.screen_name][11][0] == "Unknown"):
														# Frontback user
														username, link, pic, name, info = self.get_socialnetwork_userinfo(status, "frontback")
														self.user_sn[status.user.screen_name][11][0] = username
														self.user_sn[status.user.screen_name][11][1] = link																							
														self.user_sn[status.user.screen_name][11][2] = pic
														self.user_sn[status.user.screen_name][11][3] = name
														self.user_sn[status.user.screen_name][11][4] = info

		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Geolocation:
	"""Get geolocation info included in tweets"""

	toplocations = {}
	toplocationsstartdate = {}
	toplocatonsenddate = {}
	geoimg = 0 # tweets with images and geolocation (parameter: -p 0)
	toplocations = {} # store the user most visited locations 
	toplocationsdatetime = {} # store date and time of the user most visited locations
	toplocationsstartdate = {} # store initial date of the user most visited locations
	toplocationsenddate = {} # store final date of the user most visited locations
	toplocationsstarttime = {} # store initial time of the user most visited locations
	toplocationsdays = {} # store week day of the user most visited locations
	toplocationsendtime = {} # store final time of the user most visited locations
	toplocationsdaysmo = {} # store week day of the user most visited locations
	toplocationsdaystu = {} # store week day of the user most visited locations
	toplocationsdayswe = {} # store week day of the user most visited locations
	toplocationsdaysth = {} # store week day of the user most visited locations
	toplocationsdaysfr = {} # store week day of the user most visited locations
	toplocationsdayssa = {} # store week day of the user most visited locations
	toplocationsdayssu = {} # store week day of the user most visited locations
	geo_info = []
	toplocations_tweets = {}
	toplocations_tweets_route = {}
		
	visited_locations = []
	visited_locations_startdate = []
	visited_locations_enddate = []
	visited_locations_starttime = []
	visited_locations_endtime = []
	visited_locations_days = []
	
	kml_info = []
	media_info = {}
	toploc = []
	
	# ----------------------------------------------------------------------
	def set_geolocation_information(self, tweet):
		try:
			
			add = 0
			splace = ""
			sgeo = ""
			in_reply_to_screen_name = ""
			source_app = ""
			lat = ""
			lon = ""

			if tweet.place:
				splace = tweet.place.name.encode('utf-8')
				add = 1
			if tweet.geo:
				reply = tweet.in_reply_to_screen_name
				if reply:
					in_reply_to_screen_name = reply	

				source_app = tweet.source
				sgeo = tweet.geo['coordinates']
				add = 1
				lat = str(sgeo[0])[:str(sgeo[0]).find(".")+4]
				lon = str(sgeo[1])[:str(sgeo[1]).find(".")+4]	
				location_coord = "[" + lat + ", " + lon + "]"
				for i in range (1, 20-len(location_coord)):
					location_coord += " "
				location = location_coord + "\t" + splace

				if location in self.toplocations.keys():
					self.toplocations[location] += 1
					if tweet.created_at < self.toplocationsstartdate[location]:
						self.toplocationsstartdate[location] = tweet.created_at 
					if tweet.created_at > self.toplocationsenddate[location]:
						self.toplocationsenddate[location] = tweet.created_at
					if tweet.created_at.time() < self.toplocationsstarttime[location]:
						self.toplocationsstarttime[location] = tweet.created_at.time() 
					if tweet.created_at.time() > self.toplocationsendtime[location]:
						self.toplocationsendtime[location] = tweet.created_at.time() 
				else:
					self.toplocations[location] = 1
					self.toplocationsstartdate[location] = tweet.created_at 
					self.toplocationsenddate[location] = tweet.created_at 
					self.toplocationsstarttime[location] = tweet.created_at.time()
					self.toplocationsendtime[location] = tweet.created_at.time()
					self.toplocationsdaysmo[location] = 0
					self.toplocationsdaystu[location] = 0
					self.toplocationsdayswe[location] = 0
					self.toplocationsdaysth[location] = 0
					self.toplocationsdaysfr[location] = 0
					self.toplocationsdayssa[location] = 0
					self.toplocationsdayssu[location] = 0
				if tweet.created_at.weekday() == 0: # Monday
						self.toplocationsdaysmo[location] += 1
				elif tweet.created_at.weekday() == 1:   # Tuesday
						self.toplocationsdaystu[location] += 1
				elif tweet.created_at.weekday() == 2: # Wednesday
						self.toplocationsdayswe[location] += 1
				elif tweet.created_at.weekday() == 3: # Thursday
						self.toplocationsdaysth[location] += 1
				elif tweet.created_at.weekday() == 4: # Friday
						self.toplocationsdaysfr[location] += 1
				elif tweet.created_at.weekday() == 5: # Saturday
						self.toplocationsdayssa[location] += 1
				elif tweet.created_at.weekday() == 6: # Sunday
						self.toplocationsdayssu[location] += 1					
															
			place = splace.decode('utf-8')
			if splace in self.toplocations_tweets:
				self.toplocations_tweets[place] += 1	
			else:
				self.toplocations_tweets[place] = 1
			
			sinfo = ""
			media_url = ""
			keywords_instagram = []

			if tweet.entities.has_key('media') :
				medias = tweet.entities['media']
				for m in medias :
					media_url = m['media_url']

			else:
				if tweet.entities['urls']:
					media = str(tweet.entities['urls'][0]['expanded_url'])
					if media.find("instagram") > 0:
						# Instagram
						try:
							response = urllib2.urlopen(str(media))  
							html = response.read()
							media_url = get_url_media_from_instagram(html)
							#tagged_users, owner = get_tagged_users_from_instagram(html)
							#keywords_instagram = get_hashtags_from_instagram(html)
							if media_url.find(".mp4") > 0:
								media_type = "Video"
						except Exception as e:
							pass
					else:
						media_url = ""

			if add:
				place = splace.decode('utf-8')
				sinfo = media_url + splace.decode('utf-8') + " " + str(sgeo).decode('utf-8')
				self.geo_info.append([media_url, place, str(sgeo).decode('utf-8'), str(tweet.created_at.strftime('%m/%d/%Y')), str(tweet.created_at.time()), str(tweet.id), source_app])
				
				if len(self.visited_locations)>0 and place in self.visited_locations[len(self.visited_locations)-1][0]: 
					self.visited_locations[len(self.visited_locations)-1][1] = tweet.created_at 
					self.visited_locations[len(self.visited_locations)-1][2] = tweet.created_at.time() 
					delta = self.visited_locations[len(self.visited_locations)-1][3] - tweet.created_at 
					self.visited_locations[len(self.visited_locations)-1][5] = delta.days+1 
					self.visited_locations[len(self.visited_locations)-1][6] = self.toplocations_tweets[place]
					
				else:
					# [place, date (since), time (since), date (until), time (until), days, tweets] 
					coord = lat + ", " + lon
					self.visited_locations.append([place, tweet.created_at,  tweet.created_at.time(), tweet.created_at, tweet.created_at.time(), 1, 1, coord])
					
			else:
				sinfo = ""		
			
		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_geofile_information(self, tweet, user):
		try:
			tweet_geo = 0
			place = ""
			geo = ""
			
			# Get place from tweet
			if tweet.place:
				place = tweet.place.name.encode('utf-8')
			
			# Get coordinates from tweet
			if tweet.geo:
				geo = tweet.geo['coordinates']
				tweet_geo = 1
			
			media_url = []
			# Get media content from tweet
			if tweet.entities.has_key('media') :
				medias = tweet.entities['media']
				for m in medias :
					media_url.append(m['media_url'])
						
			photo = ""
			if tweet_geo:
				# Tweet with coordinates
				content = "<table width=\"100%\"><tr><td width=\"48\"><img src=\""+user.profile_image_url.encode('utf-8') +"\"></td><td bgcolor=\"#cde4f3\"><b>" + user.name.encode('utf-8') + "</b> @" + user.screen_name.encode('utf-8') + "<br>" + tweet.text.encode('utf-8') + "</td></tr></table>"
				
				for media in media_url:
					photo = " [Media] "
					content += "<table width=\"100%\"><tr><td><img src=\"" + str(media) + "\"></td></tr></table>"
								
				date = tweet.created_at.strftime('%m/%d/%Y')
				time = tweet.created_at.time()
				self.kml_info.append([geo, content, photo, place, date, time])
					
		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def generates_geofile(self, geofile, parameters):
		kml_file_content = ""
		kml_file_header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://earth.google.com/kml/2.2\">\n<Folder>\n"
		kml_file_body = ""
		kml_file_foot = "</Folder>\n</kml>"
		header = ""
		content = ""

		try:
			f = open(geofile, "w")
			
			header = "<table bgcolor=\"#000000\" width=\"100%\"><tr><td><font color=\"white\"><b>" + parameters.program_name + " " + parameters.program_version + "</b></font><td align=\"right\"><font color=\"white\">" + parameters.program_author_twitter + "</font></td></tr></table>"
					
			for info in self.kml_info:
				#INFO: [coordinates, content, photo, place, date, time]
				coord = str(info[0])
				lat = coord[1:coord.find(",")]
				lon = coord[coord.find(",")+2:coord.find("]")]
				
				cdata = ""
				cdata = "\t\t<![CDATA[" + header + str(info[1]) + "]]>\n"
				snippet = ""
				
				# Place + [Photo]
				snippet = info[3] + " " + str(info[2])
				kml_file_body += "\t<Placemark>\n"

				# Date + Time
				kml_file_body += "\t\t<name>" + str(info[4]) + " - " + str(info[5]) + "</name>\n"
				kml_file_body += "\t\t<Snippet>" + snippet + "</Snippet>\n"
				kml_file_body += "\t\t<description>\n" + cdata + "\t\t</description>\n"				
				kml_file_body += "\t\t<Point>\n"
				kml_file_body += "\t\t\t<coordinates>" + lon + "," + lat + "</coordinates>\n"
				kml_file_body += "\t\t</Point>\n"
				kml_file_body += "\t</Placemark>\n"

			kml_file_content = kml_file_header + kml_file_body + kml_file_foot
			f.write(kml_file_content)
			f.close()			

		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_global_information(self, top):
		try:

			sort_loc = OrderedDict(sorted(self.toplocations.items(), key=itemgetter(1), reverse=True))
			sort_top = sort_loc.items()[0:int(top)]

			for place, value in sort_top:
				startdate = self.toplocationsstartdate[place]
				enddate = self.toplocationsenddate[place]
				starttime = self.toplocationsstarttime[place]
				endtime = self.toplocationsendtime[place]
				
				favorite = 1
				
				mo = self.toplocationsdaysmo[place]
				tu = self.toplocationsdaystu[place]
				we = self.toplocationsdayswe[place]
				th = self.toplocationsdaysth[place]
				fr = self.toplocationsdaysfr[place]
				sa = self.toplocationsdayssa[place]
				su = self.toplocationsdayssu[place]
				
				week = [mo, tu, we, th, fr, sa, su]
				week_sort = sorted(week, reverse = True)
				maxday = week_sort [0]
										
				if week_sort[0] > 0 and week_sort[1] == 0:
					favorite = 0
				else:
					while week_sort[0] == maxday:
						del week_sort[0]
					if len(week_sort) > 0:
						if week_sort[0] == 0:
							favorite = 0
				
				day = []
				fav = 0
				mo_day = "Mo"
				tu_day = "Tu"
				we_day = "We"
				th_day = "Th"
				fr_day = "Fr"
				sa_day = "Sa"
				su_day = "Su" 
				
				if mo == 0:
						mo_day = ""
				else:
						if mo == maxday and favorite:
							fav = "1"
							day.append("Mo")
				if tu == 0:
						tu_day = ""
				else:
						if tu == maxday and favorite:
							fav = "2"							
							day.append("Tu")
				if we == 0:
						we_day = ""
				else:
						if we == maxday and favorite:
							fav = "3"
							day.append("We")
				if th == 0:
						th_day = ""
				else:
						if th == maxday and favorite:
							fav = "4"
							day.append("Th")
				if fr == 0:
						fr_day = ""
				else:
						if fr == maxday and favorite:
							fav = "5"
							day.append("Fr")
				if sa == 0:
						sa_day = ""
				else:
						if sa == maxday and favorite:
							fav = "6"
							day.append("Sa")
				if su == 0:
						su_day = ""
				else:
						if su == maxday and favorite:
							fav = "7"
							day.append("Su")
				
				coordinates = place[1:place.find("]")]
				location = place[20:len(place)]
				
				self.toploc.append([str(value), str(startdate.strftime('%m/%d/%Y')), str(enddate.strftime('%m/%d/%Y')), str(starttime), str(endtime), mo_day, tu_day, we_day, th_day, fr_day, sa_day, su_day, coordinates, location, fav, day])
															
		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Search_GeoTweets:
	"""Get tweets based in geolocation info"""
	toplocations = {}
	toplocationsstartdate = {}
	toplocatonsenddate = {}
	geoimg = 0 # tweets with images and geolocation (parameter: -p 0)
	adv_geo_info = []
	
	kml_info = []
	adv_media_info = {}
	toploc = []

	user_sn = {} # social networks used by this Twitter user:{'twitteruser': [[Image], [Instagram User, Image], [Foursquare user, Image], [Facebook user, Image]] }. Example: { 'jlopez', ['julian.lopez', 'julianl', 'ad23', 'http://www.facebook.com/profile.php?id=343844'] }
	user_taggeds = {} #  { 'user': ['by', 'media_url', 'tweet', 'author_image', 'date', 'time'] }
	user_keywords = {} # { 'user': 'keywords' }
	
	adv_media_count = 0 # total images	
	

	# ----------------------------------------------------------------------
	def set_geolocation_information(self, api, find, latlonkm, tweets, sdate, edate, stime, etime, hashtag, mentions, social_networks, parameters, user_images):
		# Search with coordinates
		try:
			splace = ""
			sgeo = ""
			media = 0

			tweets_count = int(tweets)		
			searched_tweets = []
			last_id = -1
			tweets_found = 0

			l = find.split()
			find = l

			for status in tweepy.Cursor(api.search,
				q="",
				geocode=latlonkm,
				#count=200,
				since=sdate,
				until=edate,
				result_type='recent').items():

				add = 1
				retweeted = 0

				# Media
				if status.entities.has_key('media') :
					media = 1
				else:
					media = 0
				
				# Retweeted
				screen_name = ""
				profile_image_url = ""
				created_at = status.created_at
				if hasattr (status, 'retweeted_status'): 
					profile_image_url = status.retweeted_status.author.profile_image_url_https.replace("_normal.", ".")
					screen_name = status.retweeted_status.author.screen_name
					created_at = status.retweeted_status.created_at
					retweeted = 1
				else: 
					profile_image_url = status.user.profile_image_url_https.replace("_normal.", ".")
					screen_name = status.user.screen_name

				for f in find:
					operator = ""
					string = ""
					to_search = re.search('\[(.*)\](.*)', f)
					if to_search:
						operator = str(to_search.group(1)).lower()
						string = str(to_search.group(2)).lower()


					if ((operator and string) or ( (operator == "+r") or (operator == "-r") or (operator == "-m") or (operator == "+m") )):
						# operator: [+]contain [-]not_contain [+r]retweeted [-r]not_retweeted [+m]contain_media [-m]not_contain_media

						if operator == "-":
							# Not contain this word
							if string in status.text.lower():
								add = 0
						elif operator == "+":
							# Contain this word
							if string not in status.text.lower() and add:
								add = 0
						elif operator == "-r":
							# Not retweeted
							if retweeted:
								add = 0
						elif operator == "+r":
							# Retweeted
							if not retweeted:
								add = 0
						elif operator == "-m":
							# Not contain media
							if media:
								add = 0
						elif operator == "+m":
							# Contain media
							if not media:
								add = 0

					else:
						add = 0

				if add:
					
					if str(status.created_at.time()) <= etime and str(status.created_at.time()) >= stime: #and str(status.created_at.strftime('%Y-%m-%d')) <= edate and str(status.created_at.strftime('%Y-%m-%d')) >= sdate:

						if parameters.output_hashtag:
							hashtag.set_hashtags_information(status)
						if parameters.output_mention:
							mentions.set_mentions_information(status)
						if parameters.output_media:
							user_images.set_images_information(status)

						profile_image_url = status.user.profile_image_url_https.replace("_normal.", ".")
						self.user_sn[status.user.screen_name] = [[profile_image_url],'','','']
						coord = ""
						try:
							coord = str(status.geo['coordinates'])
						except:
							coord = ""
							
						if not status.source:
							status.source = ""
																					
						media_url = ""
						media_type = ""
						videos = []
						keywords_instagram = []
			
						
						
						if status.entities.has_key('media') :
							medias = status.entities['media']
							for m in medias :
								media_url = m['media_url']
								if str(media_url).find("video_thumb") >= 0:
									for content in status.extended_entities['media'][0]['video_info']['variants']:
										if str(content['url']).find(".mp4") >= 0:
											videos.append([str(content['url']), content['bitrate']])

									sort_vid = OrderedDict(sorted(videos, key=itemgetter(1), reverse=True))
									vid_top = sort_vid.items()[0:1]

									media_type = "Video" 
									media_url = str(vid_top[0][0])

								if media_url.find("/media/") >= 0:
									media_type = "Image"

						
						else:
							if status.entities['urls']:
								media = str(status.entities['urls'][0]['expanded_url'])							
								if media.find("instagram") > 0:
									# Instagram
									try:
										response = urllib2.urlopen(str(media))  
										html = response.read()
										
										media_url = get_url_media_from_instagram(html)
										tagged_users, owner, profile_image = get_tagged_users_from_instagram(html)
										keywords_instagram = get_hashtags_from_instagram(html)
										
										self.user_sn[status.user.screen_name][1] = [owner, profile_image]
										for u in tagged_users:
											if u in self.user_taggeds: 
												pass
											else:
												self.user_taggeds[u]=[str(status.author.screen_name), str(media_url), status.id, profile_image_url, str(status.created_at.strftime('%m/%d/%Y')), str(status.created_at.time()), coord]
										if media_url.find(".mp4") > 0:
											media_type = "Video"
										else:
											media_type = "Image"
									except Exception as e:
										pass
						
								else:
									if media.find("swarmapp") > 0:
										# Foursquare
										media_url, owner, profile_image = get_url_media_from_foursquare(media)
										user_facebook = ""
										user_private_facebook = ""
										url_facebook = ""

										self.user_sn[status.user.screen_name][2] = [owner, profile_image] 
										
										if media_url:
											url_facebook, user_facebook, profile_image = get_url_facebook_from_foursquare("https://foursquare.com/"+owner)
											self.user_sn[status.user.screen_name][3] = [user_facebook, profile_image] 

									else:
										media_url = ""

						
						url = ""
						owner = status.user.screen_name

						if media_url and not media_type:
							# GIF
							media_type = "Image"
						
						profile_image_url = status.user.profile_image_url_https.replace("_normal.", ".")
						self.adv_geo_info.append([coord, status.user.screen_name, media_url, str(status.created_at.strftime('%m/%d/%Y')), str(status.created_at.time()), status.id, url, str(status.source), media_type, screen_name, profile_image_url, str(created_at.strftime('%m/%d/%Y')), str(created_at.time()), status.user.profile_image_url_https.replace("_normal.", ".")])
						tweets_found += 1
						
						keywords_list = []
						# Get keywords from twitter
						if status.entities.has_key('hashtags'):
							for h in status.entities['hashtags']:
								keywords_list.append(h['text'].lower())

						
						# List merge without dupe
						keywords_list = list(set(keywords_list + keywords_instagram))					

						keywords_tmp = ""
						if self.user_keywords:
							if self.user_keywords.has_key(status.user.screen_name):
								keywords_tmp = self.user_keywords[status.user.screen_name]
								# List merge without dupe
								keywords_list = list(set(keywords_list + keywords_tmp))					
								
						self.user_keywords[status.user.screen_name] = keywords_list
						
				sys.stdout.write("\r\t\t" + str(int(tweets) - tweets_count + 1) + " tweets analyzed")
				sys.stdout.flush()										
								
				tweets_count -= 1

				if tweets_count == 0:
					break

			sys.stdout.write("\n\t\t" + str(tweets_found) + " tweets found")

		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_search_information(self, api, find, latlonkm, tweets, sdate, edate, stime, etime, hashtag, mentions, social_networks, parameters, user_images):
		# Search without coordinates
		try:
			splace = ""
			sgeo = ""
			media = 0
			tweets_found = 0

			tweets_count = int(tweets)		
			searched_tweets = []
			last_id = -1

			l = find.split()
			find = l

			with_words = ""
			without_words = ""

			search = "-thisisaimpossiblewordinatweet and -thisisnotpossibleinatweet"

			for f in find:
				operator = ""
				string = ""
				to_search = re.search('\[(.*)\](.*)', f)
				if to_search:
					operator = str(to_search.group(1)).lower()
					string = str(to_search.group(2)).lower()

				if ((operator and string) or ( (operator == "+r") or (operator == "-r") or (operator == "-m") or (operator == "+m") )):
					# operator: [+]contain [-]not_contain [+r]retweeted [-r]not_retweeted [+m]contain_media [-m]not_contain_media

					if operator == "-":
						# Not contain this word
						without_words += " and -" + string
					elif operator == "+":
						# Contain this word
						with_words += " and " + string


			for status in tweepy.Cursor(api.search,
				q=search + with_words + without_words,
				#geocode=latlonkm,
				#count=100,
				since=sdate,
				until=edate,
				result_type='recent').items():


				add = 1
				retweeted = 0
				media = 0

				screen_name = ""
				profile_image_url = ""
				created_at = status.created_at

				if hasattr (status, 'retweeted_status'): 
					retweeted = 1
					if status.retweeted_status.entities.has_key('media'):
						media = 1
	
				else: 
					retweeted = 0
					if status.entities.has_key('media'):
						media = 1
										
				for f in find:
					operator = ""
					string = ""
					to_search = re.search('\[(.*)\](.*)', f)
					if to_search:
						operator = str(to_search.group(1)).lower()
						string = str(to_search.group(2)).lower()


					if ((operator and string) or ( (operator == "+r") or (operator == "-r") or (operator == "-m") or (operator == "+m") )):
						# operator: [+]contain [-]not_contain [+r]retweeted [-r]not_retweeted [+m]contain_media [-m]not_contain_media

						if operator == "-r":
							# Not retweeted
							if retweeted:
								add = 0
						elif operator == "+r":
							# Retweeted
							if not retweeted:
								add = 0
						elif operator == "-m":
							# Not contain media
							if media:
								add = 0
						elif operator == "+m":
							# Contain media
							if not media:
								add = 0

					else:
						add = 0

				if add:
										
					if str(status.created_at.time()) <= etime and str(status.created_at.time()) >= stime: #and str(status.created_at.strftime('%Y-%m-%d')) <= edate and str(status.created_at.strftime('%Y-%m-%d')) >= sdate:

						if parameters.output_hashtag:
							hashtag.set_hashtags_information(status)
						if parameters.output_mention:
							mentions.set_mentions_information(status)
						if parameters.output_media:
							user_images.set_images_information(status)

						profile_image_url = status.user.profile_image_url_https.replace("_normal.", ".")
						self.user_sn[status.user.screen_name] = [[profile_image_url],'','','']
						coord = ""
						try:
							coord = str(status.geo['coordinates'])
						except:
							coord = ""
							
						if not status.source:
							status.source = ""
																					
						media_url = ""
						media_type = ""
						videos = []
						keywords_instagram = []
						extended_entities = ""

						if media:
							if retweeted:
								medias = status.retweeted_status.entities['media']
								if str(media_url).find("video_thumb") >= 0:
									extended_entities = status.retweeted_status.extended_entities['media'][0]['video_info']['variants']
							else:
								medias = status.entities['media']
								if str(media_url).find("video_thumb") >= 0:
									extended_entities = status.extended_entities['media'][0]['video_info']['variants']

							for m in medias :
								media_url = m['media_url']
								if str(media_url).find("video_thumb") >= 0:
									if extended_entities:
										for content in extended_entities: #status.extended_entities['media'][0]['video_info']['variants']:
											if str(content['url']).find(".mp4") >= 0:
												videos.append([str(content['url']), content['bitrate']])
									
										sort_vid = OrderedDict(sorted(videos, key=itemgetter(1), reverse=True))
										vid_top = sort_vid.items()[0:1]
										media_type = "Video" 
										media_url = str(vid_top[0][0])
									
								if media_url.find("/media/") >= 0:
									media_type = "Image"

						else:
							media = ""
							if retweeted:
								if status.retweeted_status.entities['urls']:
									media = str(status.retweeted_status.entities['urls'][0]['expanded_url'])							

							else:
								if status.entities['urls']:
									media = str(status.entities['urls'][0]['expanded_url'])							


							if media.find("instagram") > 0:
								# Instagram
								try:
										
									response = urllib2.urlopen(str(media))  
									html = response.read()
									media_url = get_url_media_from_instagram(html)
									tagged_users, owner, profile_image = get_tagged_users_from_instagram(html)
									keywords_instagram = get_hashtags_from_instagram(html)


									self.user_sn[status.user.screen_name][1] = [owner, profile_image]
									for u in tagged_users:
										if u in self.user_taggeds: 
											pass
										else:
											self.user_taggeds[u]=[str(status.author.screen_name), str(media_url), status.id, profile_image_url, str(status.created_at.strftime('%m/%d/%Y')), str(status.created_at.time()), coord]

									if media_url.find(".mp4") > 0:
										media_type = "Video"
									else:
										media_type = "Image"

								except Exception as e:
									pass
							else:
								if media.find("swarmapp") > 0:
									# Foursquare
									media_url, owner, profile_image = get_url_media_from_foursquare(media)
									user_facebook = ""
									user_private_facebook = ""
									url_facebook = ""

									self.user_sn[status.user.screen_name][2] = [owner, profile_image] 
										
									if media_url:
										url_facebook, user_facebook, profile_image = get_url_facebook_from_foursquare("https://foursquare.com/"+owner)
										self.user_sn[status.user.screen_name][3] = [user_facebook, profile_image] 

								else:
									media_url = ""

						
						url = ""
						owner = status.user.screen_name


						if media_url and not media_type:
							# GIF
							media_type = "Image"
						

						profile_image_url = status.user.profile_image_url_https.replace("_normal.", ".")
						self.adv_geo_info.append([coord, status.user.screen_name, media_url, str(status.created_at.strftime('%m/%d/%Y')), str(status.created_at.time()), status.id, url, str(status.source), media_type, screen_name, profile_image_url, str(created_at.strftime('%m/%d/%Y')), str(created_at.time()), status.user.profile_image_url_https.replace("_normal.", "."), status.text])
						tweets_found += 1
						
						keywords_list = []
						# Get keywords from twitter
						if status.entities.has_key('hashtags'):
							for h in status.entities['hashtags']:
								keywords_list.append(h['text'].lower())

						
						# List merge without dupe
						keywords_list = list(set(keywords_list + keywords_instagram))					

						keywords_tmp = ""
						if self.user_keywords:
							if self.user_keywords.has_key(status.user.screen_name):
								keywords_tmp = self.user_keywords[status.user.screen_name]
								# List merge without dupe
								keywords_list = list(set(keywords_list + keywords_tmp))					
								
						self.user_keywords[status.user.screen_name] = keywords_list
						
				sys.stdout.write("\r\t\t" + str(int(tweets) - tweets_count + 1) + " tweets analyzed")
				sys.stdout.flush()										
								
				tweets_count -= 1

				if tweets_count == 0:
					break

			sys.stdout.write("\n\t\t" + str(tweets_found) + " tweets found")

		except Exception, e:
			show_error(e)
			sys.exit(1)



# ==========================================================================
class Hashtags:
	"""Get hashtags included in tweets"""
	# hashtag = [hashtag1, hashtag2, ... ]
	# hashtags_firstdate = {hashtag1: first_date1, hashtag2: first_date2, ... ]
	# hashtags_lastdate = {hashtag1: last_date1, hashtag2: last_date2, ... ]
	# hashtags_count = {hashtag1: tweets_number1, hashtag2: tweets_number2, ... ]
	hashtags = []
	hashtags_owner = {}
	hashtags_firstdate = {}
	hashtags_lastdate = {}
	hashtags_count = {}
	hashtags_tweet = []
	hashtags_rt = {}
	hashtags_fv = {}
	hashtags_results1 = 0
	hashtags_results2 = 0
	hashtags_results3 = 0	
	hashtags_top = {}
	hashtags_list = []
	hashtags_users = {}
	
	# ----------------------------------------------------------------------
	def set_hashtags_information(self, tweet):
		try:
							
			tmp = ""

			try:
				fav_count = tweet.retweeted_status.favorite_count
			except Exception, e:
				fav_count = tweet.favorite_count			

			self.hashtags_list = []			

			for i in tweet.entities['hashtags']:

				if i['text']:
					tmp = tmp + "#" + i['text'] + " "
					self.hashtags_list.append(i['text'])

				if i['text'].upper() in (name.upper() for name in self.hashtags_rt):
					self.hashtags_rt[i['text'].upper()] += tweet.retweet_count						
				else:
					self.hashtags_rt[i['text'].upper()] = tweet.retweet_count
				
				if i['text'].upper() in (name.upper() for name in self.hashtags_fv):
					self.hashtags_fv[i['text'].upper()] += fav_count						
				else:
					self.hashtags_fv[i['text'].upper()] = fav_count

			screen_name = ""
			if len(tmp):
				if hasattr (tweet, 'retweeted_status'): 
					screen_name = tweet.retweeted_status.author.screen_name
					profile_image_url = tweet.retweeted_status.author.profile_image_url.replace("_normal.", ".")
					#profile_image_url = tweet.retweeted_status.author.profile_image_url
					location = tweet.retweeted_status.author.location
				else:
					screen_name = tweet.user.screen_name
					profile_image_url = tweet.user.profile_image_url.replace("_normal.", ".")
					#profile_image_url = tweet.user.profile_image_url
					location = tweet.user.location

				self.hashtags_tweet.append([str(tweet.created_at.strftime('%m/%d/%Y')), str(tweet.created_at.time()), str(tweet.retweet_count), str(fav_count), tmp, str(tweet.id), screen_name, profile_image_url, location])
				self.hashtags_results1 += 1
			
			try:
				# Hashtags tweeted by a user 
				if len (self.hashtags_users[screen_name]):
					self.hashtags_users[screen_name].extend(self.hashtags_list)
				else:
					self.hashtags_users[screen_name] = self.hashtags_list
			except Exception, e:
				self.hashtags_users[screen_name] = self.hashtags_list

			for h in tweet.entities['hashtags']:
				orig = h['text']
				upper = h['text'].upper()
				
				if upper in (name.upper() for name in self.hashtags):
					self.hashtags_count[upper] += 1
					if tweet.created_at < self.hashtags_firstdate[upper]:
						self.hashtags_firstdate[upper] = tweet.created_at
					if tweet.created_at > self.hashtags_lastdate[upper]:
						self.hashtags_lastdate[upper] = tweet.created_at
						
				else:
					self.hashtags.append(orig)
					self.hashtags_count[upper] = 1
					self.hashtags_firstdate[upper] = tweet.created_at
					self.hashtags_lastdate[upper] = tweet.created_at
					self.hashtags_results2 += 1
					self.hashtags_owner[upper] = screen_name

		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_global_information(self):
		try:

			for h in self.hashtags:				
				self.hashtags_top[h] = self.hashtags_count[h.upper()]

			sort_has = OrderedDict(sorted(self.hashtags_top.items(), key=itemgetter(1), reverse=True))
			self.hashtags_top = sort_has.items()[0:10]
			self.hashtags_results3 = len (self.hashtags_top)
											
		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Mentions:
	""" Get mentions included in tweets """
	# mention = [mention1, mention2, ... ]
	# mentions_count = {mention1: tweets_number1, mention2: tweets_number2, ... ]
	# mentions_firstdate = {mention1: first_date1, mention2: first_date2, ... ]
	# mentions_lastdate = {mention1: last_date1, mention2: last_date2, ... ]
	mentions = []
	mentions_firstdate = {}
	mentions_lastdate = {}
	mentions_name = {}
	mentions_count = {}
	mentions_tweet = []
	mentions_rt = {}
	mentions_fv = {}
	mentions_results3 = 0
	mentions_top = {}
	mentions_list = []
	mentions_users = {}
	mentions_profileimg = {}
	
	# ----------------------------------------------------------------------
	def set_mentions_information(self, tweet):
		try:

			tmp = ""

			try:
				fav_count = tweet.retweeted_status.favorite_count
			except Exception, e:
				fav_count = tweet.favorite_count			

			self.mentions_list = []			

			for i in tweet.entities['user_mentions']:
				if i['screen_name'].encode('utf-8'):
					tmp = tmp + "@" + i['screen_name'].encode('utf-8') + " "
					self.mentions_list.append(i['screen_name'])

				if i['screen_name'].encode('utf-8').upper() in (name.upper() for name in self.mentions_rt):
					self.mentions_rt[i['screen_name'].encode('utf-8').upper()] += tweet.retweet_count						
				else:
					self.mentions_rt[i['screen_name'].encode('utf-8').upper()] = tweet.retweet_count
				
				if i['screen_name'].encode('utf-8').upper() in (name.upper() for name in self.mentions_fv):
					self.mentions_fv[i['screen_name'].encode('utf-8').upper()] += fav_count						
				else:
					self.mentions_fv[i['screen_name'].encode('utf-8').upper()] = fav_count
				
			screen_name = ""
			if len(tmp):
				if hasattr (tweet, 'retweeted_status'): 
					screen_name = tweet.retweeted_status.author.screen_name.encode('utf-8')
					profile_image_url = tweet.retweeted_status.author.profile_image_url.replace("_normal.", ".")
					#profile_image_url = tweet.retweeted_status.author.profile_image_url
					location = tweet.retweeted_status.author.location.encode('utf-8')
				else:
					screen_name = tweet.user.screen_name.encode('utf-8')
					profile_image_url = tweet.user.profile_image_url.replace("_normal.", ".")
					#profile_image_url = tweet.user.profile_image_url
					location = tweet.user.location.encode('utf-8')

				self.mentions_tweet.append([str(tweet.created_at.strftime('%m/%d/%Y')), str(tweet.created_at.time()), str(tweet.retweet_count), str(fav_count), tmp, str(tweet.id), screen_name, profile_image_url, location])
			
			try:
				# Mentions tweeted by a user 
				if len (self.mentions_users[screen_name]):
					self.mentions_users[screen_name].extend(self.mentions_list)
				else:
					self.mentions_users[screen_name] = self.mentions_list
			except Exception, e:
				self.mentions_users[screen_name] = self.mentions_list

			
			for m in tweet.entities['user_mentions']:
				orig = m['screen_name'].encode('utf-8')
				upper = m['screen_name'].encode('utf-8').upper()
				if upper in (name.upper() for name in self.mentions):
					self.mentions_count[upper] += 1
					if tweet.created_at < self.mentions_firstdate[upper]:
						self.mentions_firstdate[upper] = tweet.created_at
					if tweet.created_at > self.mentions_lastdate[upper]:
						self.mentions_lastdate[upper] = tweet.created_at
						
				else:
					self.mentions.append(orig)
					self.mentions_count[upper] = 1
					self.mentions_firstdate[upper] = tweet.created_at
					self.mentions_lastdate[upper] = tweet.created_at
					self.mentions_name[upper] = str(m['name'].encode('utf-8'))
				
		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_global_information(self):
		try:

			for h in self.mentions:				
				self.mentions_top[h] = self.mentions_count[h.upper()]

			sort_has = OrderedDict(sorted(self.mentions_top.items(), key=itemgetter(1), reverse=True))
			self.mentions_top = sort_has.items()[0:10]
			self.mentions_results3 = len (self.mentions_top)
											
		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class User_Tweets:
	""" Handle user tweets """
	
	find_text = [] # Search text in tweets
	tweets_find = [] # [[text, date, time, ID, screen_name, profile_image_url, location, name], ...]
	

	# ----------------------------------------------------------------------
	def set_find_information(self, text, tweet):
		try:
			# Identify a tweet with all user criteria
			add = 1
			
			retweeted = 0
			media = 0

			media_url = ""
			media_type = ""
			videos = []


			if tweet.entities.has_key('media') :
				media = 1
						
				if tweet.entities.has_key('media') :
					medias = tweet.entities['media']
					for m in medias :
						media_url = m['media_url']
						if str(media_url).find("video_thumb") >= 0:
							for content in tweet.extended_entities['media'][0]['video_info']['variants']:
								if str(content['url']).find(".mp4") >= 0:
									videos.append([str(content['url']), content['bitrate']])

							sort_vid = OrderedDict(sorted(videos, key=itemgetter(1), reverse=True))
							vid_top = sort_vid.items()[0:1]

							media_type = "Video" 
							media_url = str(vid_top[0][0])

						if media_url.find("/media/") >= 0:
							media_type = "Image"

				else:
					if tweet.entities['urls']:
						media = str(tweet.entities['urls'][0]['expanded_url'])							
						if media.find("instagram") > 0:
							# Instagram
							try:
								response = urllib2.urlopen(str(media))  
								html = response.read()
								media_url = get_url_media_from_instagram(html)
								if media_url.find(".mp4") > 0:
									media_type = "Video"
								else:
									media_type = "Image"
							except Exception as e:
								pass
						else:
							if media.find("swarmapp") > 0:
								# Foursquare
								media_url, owner, profile_image = get_url_media_from_foursquare(media)
								if media_url.find(".mp4") > 0:
									media_type = "Video"
								else:
									media_type = "Image"

							else:
								media_url = ""


			if hasattr (tweet, 'retweeted_status'): 
				screen_name = tweet.retweeted_status.author.screen_name
				profile_image_url = tweet.retweeted_status.author.profile_image_url.replace("_normal.", ".")
				#profile_image_url = tweet.retweeted_status.author.profile_image_url
				location = tweet.retweeted_status.author.location
				name = tweet.retweeted_status.author.name
				retweeted = 1	
			else:
				screen_name = tweet.user.screen_name
				profile_image_url = tweet.user.profile_image_url.replace("_normal.", ".")
				#profile_image_url = tweet.user.profile_image_url
				location = tweet.user.location
				name = tweet.user.name

			for f in text:
				operator = ""
				string = ""
				to_search = re.search('\[(.*)\](.*)', f)
				if to_search:
					operator = str(to_search.group(1)).lower()
					string = str(to_search.group(2)).lower()


				if ((operator and string) or ( (operator == "+r") or (operator == "-r") or (operator == "-m") or (operator == "+m") )):
					# operator: [+]contain [-]not_contain [+r]retweeted [-r]not_retweeted [+m]contain_media [-m]not_contain_media

					if operator == "-":
						# Not contain this word
						if string in tweet.text.lower():
							add = 0
					elif operator == "+":
						# Contain this word
						if string not in tweet.text.lower() and add:
							add = 0
					elif operator == "-r":
						# Not retweeted
						if retweeted:
							add = 0
					elif operator == "+r":
						# Retweeted
						if not retweeted:
							add = 0
					elif operator == "-m":
						# Not contain media
						if media:
							add = 0
					elif operator == "+m":
						# Contain media
						if not media:
							add = 0

				else:
					add = 0
			
			if add:
				self.tweets_find.append([tweet.text, tweet.created_at.strftime('%m/%d/%Y'), tweet.created_at.time(), tweet.id, screen_name, profile_image_url, location, name, media_url, media_type])

			
		except Exception, e:
			show_error(e)
			sys.exit(1)


# ==========================================================================
class Words_Tweets:
	""" Handle words in tweets """
	
	top_words = {} # Most used words
	ordered_words = {}
	top_dates = {} 
	total_occurrences = 0
	

	# ----------------------------------------------------------------------
	def set_words_information(self, top, tweet):
		try:
			# Identify words in a tweet

			english_words = ['a', 'about', 'above', 'across', 'after', 'afterwards']
			english_words += ['again', 'against', 'all', 'almost', 'alone', 'along']
			english_words += ['already', 'also', 'although', 'always', 'am', 'among']
			english_words += ['amongst', 'amoungst', 'amount', 'an', 'and', 'another']
			english_words += ['any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere']
			english_words += ['are', 'around', 'as', 'at', 'back', 'be', 'became']
			english_words += ['because', 'become', 'becomes', 'becoming', 'been']
			english_words += ['before', 'beforehand', 'behind', 'being', 'below']
			english_words += ['beside', 'besides', 'between', 'beyond', 'bill', 'both']
			english_words += ['bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant']
			english_words += ['co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de']
			english_words += ['describe', 'detail', 'did', 'do', 'done', 'down', 'due']
			english_words += ['during', 'each', 'eg', 'eight', 'either', 'eleven', 'else']
			english_words += ['elsewhere', 'empty', 'enough', 'etc', 'even', 'ever']
			english_words += ['every', 'everyone', 'everything', 'everywhere', 'except']
			english_words += ['few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first']
			english_words += ['five', 'for', 'former', 'formerly', 'forty', 'found']
			english_words += ['four', 'from', 'front', 'full', 'further', 'get', 'give']
			english_words += ['go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her']
			english_words += ['here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers']
			english_words += ['herself', 'him', 'himself', 'his', 'how', 'however']
			english_words += ['hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed']
			english_words += ['interest', 'into', 'is', 'it', 'its', 'itself', 'keep']
			english_words += ['last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made']
			english_words += ['many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine']
			english_words += ['more', 'moreover', 'most', 'mostly', 'move', 'much']
			english_words += ['must', 'my', 'myself', 'name', 'namely', 'neither', 'never']
			english_words += ['nevertheless', 'next', 'nine', 'no', 'nobody', 'none']
			english_words += ['noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of']
			english_words += ['off', 'often', 'on','once', 'one', 'only', 'onto', 'or']
			english_words += ['other', 'others', 'otherwise', 'our', 'ours', 'ourselves']
			english_words += ['out', 'over', 'own', 'part', 'per', 'perhaps', 'please']
			english_words += ['put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed']
			english_words += ['seeming', 'seems', 'serious', 'several', 'she', 'should']
			english_words += ['show', 'side', 'since', 'sincere', 'six', 'sixty', 'so']
			english_words += ['some', 'somehow', 'someone', 'something', 'sometime']
			english_words += ['sometimes', 'somewhere', 'still', 'such', 'system', 'take']
			english_words += ['ten', 'than', 'that', 'the', 'their', 'them', 'themselves']
			english_words += ['then', 'thence', 'there', 'thereafter', 'thereby']
			english_words += ['therefore', 'therein', 'thereupon', 'these', 'they']
			english_words += ['thick', 'thin', 'third', 'this', 'those', 'though', 'three']
			english_words += ['three', 'through', 'throughout', 'thru', 'thus', 'to']
			english_words += ['together', 'too', 'top', 'toward', 'towards', 'twelve']
			english_words += ['twenty', 'two', 'un', 'under', 'until', 'up', 'upon']
			english_words += ['us', 'very', 'via', 'was', 'we', 'well', 'were', 'what']
			english_words += ['whatever', 'when', 'whence', 'whenever', 'where']
			english_words += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
			english_words += ['wherever', 'whether', 'which', 'while', 'whither', 'who']
			english_words += ['whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with']
			english_words += ['within', 'without', 'would', 'yet', 'you', 'your']
			english_words += ['yours', 'yourself', 'yourselves']


			spanish_words = ['a', 'acuerdo', 'adelante', 'ademas', 'además', 'adrede', 'ahi', 'ahí', 'ahora', 'al', 'alli', 'allí', 'alrededor', 'antano', 'antaño', 'ante', 'antes', 'apenas', 'aproximadamente', 'aquel', 'aquél', 'aquella', 'aquélla', 'aquellas', 'aquéllas', 'aquello', 'aquellos', 'aquéllos', 'aqui', 'aquí', 'arriba', 'abajo', 'asi', 'así', 'aun', 'aún', 'aunque', 'b', 'bajo', 'bastante', 'bien', 'breve', 'c', 'casi', 'cerca', 'claro', 'como', 'cómo', 'con', 'conmigo', 'contigo', 'contra', 'cual', 'cuál', 'cuales', 'cuáles', 'cuando', 'cuándo', 'cuanta', 'cuánta', 'cuantas', 'cuántas', 'cuanto', 'cuánto', 'cuantos', 'cuántos', 'd', 'de', 'debajo', 'del', 'delante', 'demasiado', 'dentro', 'deprisa', 'desde', 'despacio', 'despues', 'después', 'detras', 'detrás', 'dia', 'día', 'dias', 'días', 'donde', 'dónde', 'dos', 'durante', 'e', 'el', 'él', 'ella', 'ellas', 'ellos', 'en', 'encima', 'enfrente', 'enseguida', 'entre', 'es', 'esa', 'ésa', 'esas', 'ésas', 'ese', 'ése', 'eso', 'esos', 'ésos', 'esta', 'está', 'ésta', 'estado', 'estados', 'estan', 'están', 'estar', 'estas', 'éstas', 'este', 'éste', 'esto', 'estos', 'éstos', 'ex', 'excepto', 'f', 'final', 'fue', 'fuera', 'fueron', 'g', 'general', 'gran', 'h', 'ha', 'habia', 'había', 'habla', 'hablan', 'hace', 'hacia', 'han', 'hasta', 'hay', 'horas', 'hoy', 'i', 'incluso', 'informo', 'informó', 'j', 'junto', 'k', 'l', 'la', 'lado', 'las', 'le', 'lejos', 'lo', 'los', 'luego', 'm', 'mal', 'mas', 'más', 'mayor', 'me', 'medio', 'mejor', 'menos', 'menudo', 'mi', 'mí', 'mia', 'mía', 'mias', 'mías', 'mientras', 'mio', 'mío', 'mios', 'míos', 'mis', 'mismo', 'mucho', 'muy', 'n', 'nada', 'nadie', 'ninguna', 'no', 'nos', 'nosotras', 'nosotros', 'nuestra', 'nuestras', 'nuestro', 'nuestros', 'nueva', 'nuevo', 'nunca', 'o', 'os', 'otra', 'otros', 'p', 'pais', 'paìs', 'para', 'parte', 'pasado', 'peor', 'pero', 'poco', 'por', 'porque', 'pronto', 'proximo', 'próximo', 'puede', 'q', 'qeu', 'que', 'qué', 'quien', 'quién', 'quienes', 'quiénes', 'quiza', 'quizá', 'quizas', 'quizás', 'r', 'raras', 'repente', 's', 'salvo', 'se', 'sé', 'segun', 'según', 'ser', 'sera', 'será', 'si', 'sí', 'sido', 'siempre', 'sin', 'sobre', 'solamente', 'solo', 'sólo', 'son', 'soyos', 'su', 'supuesto', 'sus', 'suya', 'suyas', 'suyo', 't', 'tal', 'tambien', 'también', 'tampoco', 'tarde', 'te', 'temprano', 'ti', 'tiene', 'todavia', 'todavía', 'todo', 'todos', 'tras', 'tu', 'tú', 'tus', 'tuya', 'tuyas', 'tuyo', 'tuyos', 'u', 'un', 'una', 'unas', 'uno', 'unos', 'usted', 'ustedes', 'v', 'veces', 'vez', 'vosotras', 'vosotros', 'vuestra', 'vuestras', 'vuestro', 'vuestros', 'w', 'x', 'y', 'ya', 'yo', 'z']
			
			symbols = ['!', '"', '·', '$', '%', '&', '/', '(', ')', '=', '?', '¿', '^', '*', ',', '.', '-', ';', ':', '_', '[', ']', '@', '#', '~', '¡']

			empty_words = english_words + spanish_words + symbols

			words = tweet.text.split()
			words = [w for w in words if w.lower() not in empty_words]
			words = [w for w in words if w[0] not in ['@', '#']]

			for word in words:
				freq = words.count(word)

				if self.top_words.has_key(word):
					freq = self.top_words[word] + freq
					datefrom = self.top_dates[word][0]
					dateto = self.top_dates[word][1]

					if tweet.created_at < datefrom:
						datefrom = tweet.created_at
					if tweet.created_at > dateto:
						dateto = tweet.created_at

					self.top_words[word] = freq
					self.top_dates[word] = [datefrom, dateto]

				else:
					# First occurrence
					self.top_words[word] = freq
					self.top_dates[word] = [tweet.created_at, tweet.created_at]
			
		except Exception, e:
			show_error(e)
			sys.exit(1)


#==========================================================================
class Favorites:
	""" Handle favorite tweets """
	
	favorites_tweets = []
	
	# ----------------------------------------------------------------------
	def set_favorites_information(self, api, username, total_favs):
		try:

			favorites_count = 0
			page = 1
			end = 0
			while not end:
				try:

					favorites = api.favorites(id=username, page=page)
					if favorites:
						for tweet in favorites:
							favorites_count += 1
							if favorites_count > total_favs:
								end = 1
							else:
								sys.stdout.write("\r\t\t" + str(favorites_count) + "/" + str(total_favs) + " tweets analyzed")
								sys.stdout.flush()
								tweet_date = tweet.created_at.strftime('%m/%d/%Y')
								tweet_time = tweet.created_at.time()
								media_url=""

								if tweet.entities.has_key('media') :
									medias = tweet.entities['media']
									for m in medias :
										media_url = m['media_url']

								profile_image_url = tweet.user.profile_image_url_https.replace("_normal.", ".")
								self.favorites_tweets.append([tweet.id, tweet_date, tweet_time, tweet.user.screen_name, profile_image_url, tweet.user.name, media_url, tweet.text])
					page += 1

				except Exception, e:
					rate_limit = show_error(e)
					if rate_limit:
						print "\t\tWaiting..."
						time.sleep(60)
						continue
				
		except Exception, e:
			show_error(e)
			sys.exit(1)



# ==========================================================================
class User_Conversations:
	""" Show conversations between two users """
	
	conversations = {} # {'tweet1_id1': '[[tweet1], [tweet2], ..., [tweet_n]], 'tweet2_id2': '[[tweet1], [tweet2], ..., [tweet_n]], ...}
	processed_tweets = []



	# ----------------------------------------------------------------------
	def make_tweet_to_append(self, tweet, position):
		try:
			tweet_to_append = []

			user_screen_name = tweet.user.screen_name
			user_profile_image_url = tweet.user.profile_image_url
			user_location = tweet.user.location
			user_name = tweet.user.name
			tweet_date = tweet.created_at.strftime('%m/%d/%Y')
			tweet_time = tweet.created_at.time()
			tweet_datetime = tweet.created_at.strftime('%Y/%m/%d') + "-" + str(tweet_time)

			tweet_to_append = [tweet.id, tweet.text, tweet_date, tweet_time, user_screen_name, user_profile_image_url, user_location, user_name, position, tweet_datetime, "", tweet.in_reply_to_status_id]

			return tweet_to_append

		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_tweets_conversations(self, parameters, tweet):
		try:
			
			add_tweet_conversation = 1
			conversation_id = 0
								
			while add_tweet_conversation > 0:
				if tweet.id not in self.processed_tweets:
					self.processed_tweets.append(tweet.id)

					if tweet.in_reply_to_status_id:
						# Reply
						try:

							if conversation_id == 0:
								conversation_id = tweet.in_reply_to_status_id

							tweet_in_reply = parameters.api.get_status(tweet.in_reply_to_status_id)

							tweet_to_append_in_reply = self.make_tweet_to_append(tweet_in_reply, "")
							tweet_to_append_reply = self.make_tweet_to_append(tweet, "")

							conversation_to_append = tweet_to_append_in_reply
							conversation = self.conversations.get(conversation_id)

							if conversation:

								for conv in conversation:
									if conv[0] == tweet_to_append_in_reply[0]:
										# Already exist
										break
									else:
										self.conversations[conversation_id].append(conversation_to_append)
										break
							else:
								self.conversations[conversation_id] = [conversation_to_append]
							
							conversation_to_append = tweet_to_append_reply
							self.conversations[conversation_id].append(conversation_to_append)


							search_user_screen_name = tweet.user.screen_name
							search_tweet_id = tweet.id
							search_since = tweet.created_at.strftime('%Y-%m-%d')
							tmp = tweet.created_at + datetime.timedelta(days=1)
							search_until = tmp.strftime('%Y-%m-%d')

							# Find others replies
							for status in tweepy.Cursor(parameters.api.search,
								q="@" + search_user_screen_name,
								since_id=search_tweet_id,
								count=100,
								since=search_since,
								until=search_until,
								result_type='recent').items():			

								if status.in_reply_to_status_id == search_tweet_id:
									tweet_to_append = self.make_tweet_to_append(status, "")
									self.conversations[conversation_id].append(tweet_to_append)

							tweet = tweet_in_reply

						except Exception, e:
							show_error(e)
							add_tweet_conversation = 0

					else:
						add_tweet_conversation = 0
				else:
					add_tweet_conversation = 0

		except Exception, e:
			show_error(e)
			sys.exit(1)



# ==========================================================================
class User_Images:
	""" Handle user images and metadata information """
	metadata = 0
	
	profile_image_url = ""
	profile_banner_url = ""
	screen_name = ""
	
	pic = [] 
	pics_directory = ""
	pics_result = 0
	username = ""
	images = ""
	meta = ""
	meta_description = {}
	meta_copyright = {}
	meta_date = {}
	meta_make = {}
	meta_model = {}
	meta_software = {}
	meta_distance = {}
	meta_size = {}
	meta_platform = {}
	meta_iccdate = {}
	meta_GPSLatitude = {}
	meta_coordinates = {}
	meta_thumb = {}
	meta_profile_image = []
	meta_profile_banner = []
	
	platforms = {
		"APPL" : "Apple Computer Inc.", 
		"MSFT" : "Microsoft Corporation", 
		"SGI " : "Silicon Graphics Inc.", 
		"SUNW" : "Sun Microsystems Inc.", 
		"TGNT" : "Taligent Inc.",
		}
		
	# ----------------------------------------------------------------------
	def set_images_information(self, tweet):
		try:
			media_url = ""
			image = ""
			media_type = "Image" 
			in_reply_to_screen_name = ""

			reply = tweet.in_reply_to_screen_name
			if reply:
				in_reply_to_screen_name = reply	

	
			if tweet.entities.has_key('media') :
				medias = tweet.entities['media']
				for m in medias :
					media_url = m['media_url']
					if str(media_url).find("video") >= 0:
						media_type = "Video" 
						videos = []
						for content in tweet.extended_entities['media'][0]['video_info']['variants']:
							if str(content['url']).find(".mp4") >= 0:
								videos.append([str(content['url']), content['bitrate']])

						sort_vid = OrderedDict(sorted(videos, key=itemgetter(1), reverse=True))
						vid_top = sort_vid.items()[0:1]
						media_url = str(vid_top[0][0])

					else:
						if self.images == "d" or self.meta:
							if not os.path.isdir(self.username):
								os.mkdir(self.username)
							img = urllib2.urlopen(media_url).read()
							filename = media_url.split('/')[-1]
							self.pics_directory = os.path.dirname(os.path.abspath(__file__)) + "/" + self.username
							image = self.pics_directory + "/" +filename
							if not os.path.exists(self.username+"/"+filename):
								f = open(self.username+"/"+filename, 'wb')
								f.write(img)
								f.close()			

			else:
				if tweet.entities['urls']:
					media = str(tweet.entities['urls'][0]['expanded_url'])
					if media.find("instagram") > 0:
						# Instagram
						try:
							response = urllib2.urlopen(str(media))  
							html = response.read()
							media_url = get_url_media_from_instagram(html)
							if media_url.find(".mp4") > 0:
								media_type = "Video"
						except Exception as e:
							pass
					else:
						media_url = ""


			if media_url:
				screen_name = ""
				profile_image_url_orig = ""
				created_at = tweet.created_at
				screen_name = tweet.user.screen_name
				screen_name_orig = ""
				profile_image_url = tweet.user.profile_image_url_https.replace("_normal.", ".")
				if hasattr (tweet, 'retweeted_status'): 
					source_app = str(tweet.retweeted_status.source)
					source_likes = str(tweet.retweeted_status.favorite_count)
					source_rt = str(tweet.retweeted_status.retweet_count)
					profile_image_url_orig = tweet.retweeted_status.author.profile_image_url_https.replace("_normal.", ".")
					screen_name_orig = tweet.retweeted_status.author.screen_name
					created_at = tweet.retweeted_status.created_at
				else:
					source_app = tweet.source
					source_likes = str(tweet.favorite_count)
					source_rt = str(tweet.retweet_count)			
				
				self.pic.append([media_url, image, str(tweet.created_at.strftime('%m/%d/%Y')), str(tweet.created_at.time()), str(tweet.id), screen_name_orig, profile_image_url_orig, str(created_at.strftime('%m/%d/%Y')), str(created_at.time()), media_type, screen_name, profile_image_url, source_app, source_rt, source_likes, in_reply_to_screen_name])
			
		except Exception, e:
			show_error(e)
			sys.exit(1)


	# ----------------------------------------------------------------------
	def set_metadata_information(self, tweet):
		try:
		
			for p in self.pic:
				path = p[1]
				self.meta_description[p[0]] = ""
				self.meta_copyright[p[0]] = ""
				self.meta_date[p[0]] = ""
				self.meta_make[p[0]] = ""
				self.meta_model[p[0]] = ""
				self.meta_software[p[0]] = ""
				self.meta_distance[p[0]] = ""
				self.meta_platform[p[0]] = ""
				self.meta_iccdate[p[0]] = ""
				self.meta_coordinates[p[0]] = ""
				self.meta_thumb[p[0]] = ""
				
				fileName, fileExtension = os.path.splitext(path)								
					
				if os.path.exists(path):
					img = Image.open(path)
					if fileExtension in (".jpg", ".jpeg"):			
						if img._getexif():
							metadata = 1
							exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
							self.meta_description[p[0]] = unicode(exif['ImageDescription'])
							self.meta_copyright[p[0]] = unicode(exif['Copyright'])
							self.meta_date[p[0]] = unicode(exif['ImageDescription'])
							self.meta_make[p[0]] = unicode(exif['Make'])
							self.meta_model[p[0]] = unicode(exif['Model'])
							self.meta_software[p[0]] = unicode(exif['Software'])
							self.meta_distance[p[0]] = unicode(exif['SubjectDistance'][0]/float(exif['SubjectDistance'][1])) + " meters"
											
					self.meta_size[p[0]] = str(img.size[0]) + "x" + str(img.size[1]) + " px"
					if 'icc_profile' in img.info:
						icc_profile = img.info.get("icc_profile")
						if icc_profile:
							platform = icc_profile[40:44]
							metadata = 1
							if platform in ('APPL', 'MSFT', 'SGI ', 'SUNW', 'TGNT'):
								self.meta_platform[p[0]] = self.platforms[platform]
							datetime = struct.unpack('>hhhhhh',icc_profile[24:36])
							tmp_tuple = (0, 0, 0)
							final_tuple = datetime + tmp_tuple
							self.meta_iccdate[p[0]] = unicode(time.strftime('%Y/%m/%d %H:%M:%S', final_tuple))
					
					# Checkf for GPS information
					try:
						latitude = metadata.__getitem__("Exif.GPSInfo.GPSLatitude")
						latitudeRef = metadata.__getitem__("Exif.GPSInfo.GPSLatitudeRef")
						longitude = metadata.__getitem__("Exif.GPSInfo.GPSLongitude")
						longitudeRef = metadata.__getitem__("Exif.GPSInfo.GPSLongitudeRef")

						latitude = str(latitude).split("=")[1][1:-1].split(" ");
						latitude = map(lambda f: str(float(Fraction(f))), latitude)
						latitude = latitude[0] + u"\u00b0" + latitude[1] + "'" + latitude[2] + '"' + " " + str(latitudeRef).split("=")[1][1:-1]

						longitude = str(longitude).split("=")[1][1:-1].split(" ");
						longitude = map(lambda f: str(float(Fraction(f))), longitude)
						longitude = longitude[0] + u"\u00b0" + longitude[1] + "'" + longitude[2] + '"' + " " + str(longitudeRef).split("=")[1][1:-1]

						latitude_value = dms_to_decimal(*metadata.__getitem__("Exif.GPSInfo.GPSLatitude").value + [metadata.__getitem__("Exif.GPSInfo.GPSLatitudeRef").value]);
						longitude_value = dms_to_decimal(*metadata.__getitem__("Exif.GPSInfo.GPSLongitude").value + [metadata.__getitem__("Exif.GPSInfo.GPSLongitudeRef").value]);

						self.meta_coordinates[p[0]] = str(latitude_value) + ", " + str(longitude_value)
					except Exception, e:
						# No GPS information
						pass
				
		except Exception, e:
			show_error(e)
			sys.exit(1)

			
	# ----------------------------------------------------------------------			
	def get_metadata(self, filename, save, username):
		try:
			metadata = 0
			platforms = {
				"APPL" : "Apple Computer Inc.", 
				"MSFT" : "Microsoft Corporation", 
				"SGI " : "Silicon Graphics Inc.", 
				"SUNW" : "Sun Microsystems Inc.", 
				"TGNT" : "Taligent Inc.",
			}

			self.profile_image_url = filename

			if save:
				save_image(filename, username)
	
			pics_directory = os.path.dirname(os.path.abspath(__file__)) + "/" + username
	
			filename = filename.split('/')[-1]
			path = pics_directory + "/" + filename
			fileName, fileExtension = os.path.splitext(path)					
			
			if os.path.exists(path):	

				img = Image.open(path)
				if fileExtension in (".jpg", ".jpeg"):			
					if img._getexif():
						metadata = 1
						exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
						self.meta_profile_image.append(unicode(exif['ImageDescription']))
						self.meta_profile_image.append(unicode(exif['Copyright']))
						self.meta_profile_image.append(unicode(exif['DateTimeOriginal']))
						self.meta_profile_image.append(unicode(exif['Make']))
						self.meta_profile_image.append(unicode(exif['Model']))
						self.meta_profile_image.append(unicode(exif['Software']))
						self.meta_profile_image.append(unicode(exif['SubjectDistance'][0]/float(exif['SubjectDistance'][1])) + " meters")
						
					else:	
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
						self.meta_profile_image.append("")
																								
				if 'icc_profile' in img.info:
					icc_profile = img.info.get("icc_profile")
					if icc_profile:
						platform = icc_profile[40:44]
						metadata = 1
						if platform in ('APPL', 'MSFT', 'SGI ', 'SUNW', 'TGNT'):
							self.meta_profile_image.append(platforms[platform])
								
						datetime = struct.unpack('>hhhhhh',icc_profile[24:36])
						tmp_tuple = (0, 0, 0)
						final_tuple = datetime + tmp_tuple
						self.meta_profile_image.append(time.strftime('%Y/%m/%d %H:%M:%S', final_tuple))

					
				try:
					latitude = metadata.__getitem__("Exif.GPSInfo.GPSLatitude")
					latitudeRef = metadata.__getitem__("Exif.GPSInfo.GPSLatitudeRef")
					longitude = metadata.__getitem__("Exif.GPSInfo.GPSLongitude")
					longitudeRef = metadata.__getitem__("Exif.GPSInfo.GPSLongitudeRef")
	
					latitude = str(latitude).split("=")[1][1:-1].split(" ");
					latitude = map(lambda f: str(float(Fraction(f))), latitude)
					latitude = latitude[0] + u"\u00b0" + latitude[1] + "'" + latitude[2] + '"' + " " + str(latitudeRef).split("=")[1][1:-1]
	
					longitude = str(longitude).split("=")[1][1:-1].split(" ");
					longitude = map(lambda f: str(float(Fraction(f))), longitude)
					longitude = longitude[0] + u"\u00b0" + longitude[1] + "'" + longitude[2] + '"' + " " + str(longitudeRef).split("=")[1][1:-1]
	
					latitude_value = dms_to_decimal(*metadata.__getitem__("Exif.GPSInfo.GPSLatitude").value + [metadata.__getitem__("Exif.GPSInfo.GPSLatitudeRef").value]);
					longitude_value = dms_to_decimal(*metadata.__getitem__("Exif.GPSInfo.GPSLongitude").value + [metadata.__getitem__("Exif.GPSInfo.GPSLongitudeRef").value]);
	
				except Exception, e:
					pass
		
		except Exception, e:
			show_error(e)
			sys.exit(1)

# ==========================================================================
class Parameters:
	"""Global program parameters"""
	# ----------------------------------------------------------------------
	def __init__(self, **kwargs):
		try:
			config = Configuration()
			self.api = config.api
			self.client = config.client
			self.info_color = config.color
			self.header_color = config.color_hdr
			self.function_color = config.color_fun
			self.screen_name= kwargs.get("username")
			self.tweets = kwargs.get("tweets")
			self.sdate = kwargs.get("sdate")
			self.edate = kwargs.get("edate")
			self.sdate = kwargs.get("stime")
			self.edate = kwargs.get("etime")
			self.elapsedtime = kwargs.get("elapsedtime")
			self.friend = kwargs.get("friend")
			self.geo = kwargs.get("geo")
			self.top = kwargs.get("top")
			self.find = kwargs.get("find")
			self.search = kwargs.get("latlonkm")
			self.output = kwargs.get("output")
			self.favorites = kwargs.get("favorites")
			self.username = ""

			self.menu_apps = 0
			self.menu_social = 0
			self.menu_hashtags = 0
			self.menu_mentions = 0
			self.menu_tweets = 0
			self.menu_metadata = 0
			self.menu_media = 0
			self.menu_geolocation = 0
			self.menu_search = 0

			self.output_source = 0
			self.output_followers = 0
			self.output_social = 0
			self.output_hashtag = 0
			self.output_mention = 0
			self.output_tweet = 0
			self.output_metadata = 0
			self.output_media = 0
			self.output_geolocation = 0
			self.output_search = 0
			self.output_conversation = 0
			self.output_favorites = 0
			self.output_words = 0


			self.program_name ="Tinfoleak"
			self.program_version = "v2.1 [SHA2017 Edition]"
			self.program_date = "08/07/2017"
			self.program_author_name = "Vicente Aguilera Diaz"
			self.program_author_twitter = "@VAguileraDiaz"
			self.program_author_companyname = "Internet Security Auditors"
			self.html_output_directory = "Output_Reports"

		except Exception, e:
			show_error(e)
			sys.exit(1)



# ----------------------------------------------------------------------
def is_valid(tweet, args):
	"""Verify if a tweet meets all requirements"""
	try:
		valid = 1
		
		date = str(tweet.created_at.strftime('%Y-%m-%d'))

		if date < args.sdate or date > args.edate:
			valid = 0
		time = str(tweet.created_at.strftime('%H:%M:%S'))
		if time< args.stime or time> args.etime:
			valid = 0
		
		return valid
		
	except Exception, e:
		show_error(e)
		sys.exit(1)


# ----------------------------------------------------------------------
def get_video_url(url):
	"""Get video URL from a tweet media URL"""
	try:
		video_url = ""
		
		response = urllib2.urlopen(str(url))  
		html = response.read()
		if html.find(".mp4") >= 0:
			begin = html.index('video-src="')
			end = html.index('.mp4"')
			video_url = html[begin+11:end+4]
		
		return video_url
		
	except Exception, e:
		show_error(e)
		sys.exit(1)

# ----------------------------------------------------------------------
def getKey(item):
	return item[9]

# ----------------------------------------------------------------------
def generates_HTML_file(parameters, user, source, social, hashtag, mention, geolocation, user_images, user_tweets, search, user_conversations, favorites,top_words):
	"""Generates a HTML output file"""
	try:
		tinfoleak_dir = os.path.dirname(os.path.abspath(__file__))
		jinja2_env = Environment(loader=FileSystemLoader(tinfoleak_dir), autoescape=True, trim_blocks=True)
		
		desc = user.description
		if user.expanded_description:
			desc = user.expanded_description

		url = user.url
		if user.expanded_url and len(user.expanded_url) < 50:
			url = user.expanded_url		

		all_conv = {}
		conversations_number = 0
		conversations_users = {}
		conversations_messages = {}


		for tid, conv in user_conversations.conversations.items():
			# Order conversations by datetime
			tmp = sorted(conv, key=getKey)
			user_conversations.conversations[tid] = tmp

			# Remove duplicates
			tmplist = []
			res = []
			index = 0
			for n in tmp:
				if n[0] not in tmplist:
					tmplist.append(n[0])
					res.append(n)
				index += 1

			user_conversations.conversations[tid] = res

			# Make some updates
			index = 0
			for n in res:
				if res[index][11]:
					# In reply ID
					res[index][10] = "replied"
				else:
					# First tweet of this conversation
					res[index][10] = "tweeted"

				if index > 0:
						
					size = len(res)
					while size >= 0:
						if n[11] == res[size-1][0]:
							# If tweet.in_reply_to_status_id == tweet.id => change chat position
							if res[size-1][8] == "left":
								res[index][8] = "right"
							else:
								res[index][8] = "left"

						size -= 1

				else:
					res[index][8] = "left"
				index += 1

			user_conversations.conversations[tid] = res
			
			try:
				for r in res:
					all_conv[res[0][0]].append(r)
			except Exception, e:
				all_conv[res[0][0]] = res

		user_conversations.conversations = all_conv


		for tid, conv in user_conversations.conversations.items():
			conversations_number += 1

			# Order conversations by datetime
			tmp = sorted(conv, key=getKey)
			user_conversations.conversations[tid] = tmp

			# Remove duplicates
			tmplist = []
			res = []
			index = 0
			users = []
			for n in tmp:

				if n[0] not in tmplist:
					tmplist.append(n[0])
					res.append(n)

				value = [n[4], n[7]] 
				if value not in users:					
					users.append(value)

				index += 1

			conversations_users[tid] = users 
			conversations_messages[tid] = len(conv)
			user_conversations.conversations[tid] = res

		template_values = {
			'program': parameters.program_name, 
			'version': parameters.program_version,
			'author_name': parameters.program_author_name,
			'author_twitter': parameters.program_author_twitter,
			'author_company': parameters.program_author_companyname,
			'profile_image': user.profile_image_url.replace("_normal.", "."),
			'screen_name': user.screen_name,
			'user_name': user.name, 
			'twitter_id': user.id,
			'date': user.created_at.strftime('%m/%d/%Y'), 
			'followers': '{:,}'.format(user.followers_count),
			'friends': '{:,}'.format(user.friends_count),
			'geo': user.geo_enabled,
			'tweets': '{:,}'.format(user.statuses_count),
			'location': user.location,
			'timezone': user.time_zone,
			'description': desc, 
			'url': url,
			'tweets_average': user.tweets_average,
			'favourites_count': user.favourites_count,
			'verified': user.verified,
			'listed_count': user.listed_count,
			'lang': user.lang,
			'user_color': "DDDDDD",
			'argv': str(sys.argv),
			'os_name': os.name,
			'os_platform': sys.platform,
			
			# source
			'output_source': parameters.output_source,
			'source': source.sources,
			'sources_count': source.sources_count,
			'sources_percent': source.sources_percent,
			'sources_firstdate': source.sources_firstdate,
			'sources_lastdate': source.sources_lastdate,
			'sources_results': len(source.sources),
			'sources_firsttweet': source.sources_firsttweet,
			'sources_lasttweet': source.sources_lasttweet,

			# social
			'output_social': parameters.output_social,
			'menu_social': parameters.menu_social,
			'social_tweet': social.user_sn,
			'social_results': len(social.user_sn),
			
			# hashtag
			'output_hashtag': parameters.output_hashtag,
			'hashtags_tweet': hashtag.hashtags_tweet,
			'hashtags_results1': hashtag.hashtags_results1,
			'hashtags_results2': hashtag.hashtags_results2,
			'hashtags_results3': hashtag.hashtags_results3,
			'hashtags_firstdate': hashtag.hashtags_firstdate,
			'hashtags_lastdate': hashtag.hashtags_lastdate,
			'hashtag': hashtag.hashtags,
			'hashtags_rt': hashtag.hashtags_rt,
			'hashtags_fv': hashtag.hashtags_fv,
			'hashtags_count': hashtag.hashtags_count,
			'hashtags_top': hashtag.hashtags_top,
			'hashtags_owner': hashtag.hashtags_owner,
			'hashtags_users': hashtag.hashtags_users,

			# mention
			'output_mention': parameters.output_mention,
			'mentions_tweet': mention.mentions_tweet,
			'mentions_results1': len(mention.mentions_tweet),
			'mentions_results2': len(mention.mentions_count),
			'mentions_results3': mention.mentions_results3,
			'mentions_firstdate': mention.mentions_firstdate,
			'mentions_lastdate': mention.mentions_lastdate,
			'mentions_name': mention.mentions_name,
			'mention': mention.mentions,
			'mentions_rt': mention.mentions_rt,
			'mentions_fv': mention.mentions_fv,
			'mentions_count': mention.mentions_count,
			'mentions_top': mention.mentions_top,
			'mentions_users': mention.mentions_users,
			'mentions_profileimg': mention.mentions_profileimg,
			
			# find text 
			'output_tweet': parameters.output_tweet,
			'find': user_tweets.find_text,
			'tweet_find': user_tweets.tweets_find,
			'find_count': len(user_tweets.tweets_find),

			# media
			'output_media': parameters.output_media,
			'media': user_images.pic,
			'media_directory': user_images.pics_directory,
			'media_count': len(user_images.pic),
			
			#meta
			'output_metadata': parameters.output_metadata,
			'meta_size': user_images.meta_size,
			'meta_description': user_images.meta_description,
			'meta_copyright': user_images.meta_copyright,
			'meta_date': user_images.meta_date,
			'meta_make': user_images.meta_make,
			'meta_model': user_images.meta_model,
			'meta_software': user_images.meta_software,
			'meta_distance': user_images.meta_distance,
			'meta_platform': user_images.meta_platform,
			'meta_iccdate': user_images.meta_iccdate,
			'meta_coordinates': user_images.meta_coordinates,
			'meta_thumb': user_images.meta_thumb,
			'meta_profile_image': user_images.meta_profile_image,
			'meta_profile_banner': user_images.meta_profile_banner,
			'meta_profile_image_url': user_images.profile_image_url,
			'meta_profile_banner_url': user_images.profile_banner_url,
			
			# geolocation
			'output_geolocation': parameters.output_geolocation,
			'geo_info': geolocation.geo_info,
			'geo_count': len(geolocation.geo_info),
			'geo_media': geolocation.media_info,			
			'geo_info_count': len(geolocation.geo_info),
			'geo_visited_locations': geolocation.visited_locations,
			'geo_visited_locations_count': len(geolocation.visited_locations),	
			'geo_toplocations_tweets': geolocation.toplocations_tweets,	
			'geo_toplocations': geolocation.toploc,
			'geo_toplocations_count': len(geolocation.toploc),

			# advanced search
			'output_search': parameters.output_search,
			'output_search_nocoord': parameters.search,
			'adv_geo_info': search.adv_geo_info,
			'adv_geo_count': len(search.adv_geo_info),
			'adv_geo_media': search.adv_media_info,
			'adv_media_count': search.adv_media_count,
			'user_sn': search.user_sn,
			'user_sn_count': len(search.user_sn),
			'user_taggeds': search.user_taggeds,
			'user_taggeds_count': len(search.user_taggeds),
			'user_keywords': search.user_keywords,

			# conversations
			'output_conversation': parameters.output_conversation,
			'conversations': user_conversations.conversations.items(),
			'conversations_number': conversations_number,
			'conversations_users': conversations_users,
			'conversations_messages': conversations_messages,

			# favorites
			'output_favorites': parameters.output_favorites,
			'favourites_tweets': favorites.favorites_tweets,
			'fav_count': len(favorites.favorites_tweets),

			# top words
			'output_words': parameters.output_words,
			'top_words': top_words.ordered_words,
			'top_dates': top_words.top_dates,
			'total_occurrences': top_words.total_occurrences,
			'words_count': len(top_words.ordered_words)

	
		}
		
		html_content = jinja2_env.get_template('ReportTemplate/tinfoleak-theme.html').render(template_values)

		if not os.path.exists(parameters.html_output_directory) :
			os.makedirs(parameters.html_output_directory)

		f = open(parameters.html_output_directory + "/" + parameters.output, "w")
		f.write(html_content.encode('utf-8'))
		f.close()
		
	except Exception, e:
		show_error(e)
		sys.exit(1)



# ----------------------------------------------------------------------
def save_image(url, username):
	try:
		if not os.path.isdir(username):
			os.mkdir(username)
		
		img = urllib2.urlopen(url).read()
		filename = url.split('/')[-1]
		pics_directory = os.path.dirname(os.path.abspath(__file__)) + "/" + username
		image = pics_directory + "/" +filename
		if not os.path.exists(username+"/"+filename):
			f = open(username+"/"+filename, 'wb')
			f.write(img)
			f.close()
					
	except Exception, e:
		show_error(e)
		sys.exit(1)


# ----------------------------------------------------------------------
def get_information(args, parameters):
	"""Get information about a Twitter user"""
	try:

		source = Sources()
		hashtag = Hashtags()
		mentions = Mentions()
		user_images = User_Images()
		geolocation = Geolocation()
		user = User()
		search = Search_GeoTweets()	
		user_tweets = User_Tweets()
		user_conversations = User_Conversations()
		social_networks = Social_Networks()
		followers = Followers()
		friends = Friends()
		favorites = Favorites()
		top_words = Words_Tweets()
		user.meta = args.meta	

		#: [username, link, picture, name, info] 
		social_networks.user_sn[args.username] = \
			[["", "", "", "", ""], # Instagram 
			 ["", "", "", "", ""], # Foursquare
			 ["", "", "", "", ""], # Facebook
			 ["", "", "", "", ""], # LinkedIn
			 ["", "", "", "", ""], # Runkeeper
			 ["", "", "", "", ""], # Flickr
			 ["", "", "", "", ""], # Vine
			 ["", "", "", "", ""], # Periscope
			 ["", "", "", "", ""], # Kindle
			 ["", "", "", "", ""], # Youtube
			 ["", "", "", "", ""], # Google+
			 ["", "", "", "", ""]] # Frontback
		
		if not args.username and not args.latlonkm:
			print "\tYou need to specify an USERNAME (-u, --user) or a LATLONKM (--search).\n\tExecute './tinfoleak.py -h' to see the available options."
		else:
			if args.latlonkm:
				print "\n\t\tExecuting operations..."
				api = parameters.api.get_user("tinfoleak")
				user.set_user_information(api)
			
				if parameters.search != "*":
					# Search with coordinates
					search.set_geolocation_information(parameters.api, parameters.find, parameters.search, args.tweets_number, parameters.sdate, parameters.edate, parameters.stime, parameters.etime, hashtag, mentions, social_networks, parameters, user_images)
				else:
					# Search without coordinates
					search.set_search_information(parameters.api, parameters.find, parameters.search, args.tweets_number, parameters.sdate, parameters.edate, parameters.stime, parameters.etime, hashtag, mentions, social_networks, parameters, user_images)

				print "\n\t\tOK"
					
			else:								
				print "\tLooking info for @"  + args.username + ":\n"
				
				if not args.information and not args.file and not args.number and not args.d and not args.sources and not args.hashtags and not args.mentions and not args.text and not args.meta and not args.conv and not args.socialnetworks and not args.followers_number and not args.friends_number and not args.words_number and not args.likes_number: 
					print "\tYou need to specify an operation. Execute './tinfoleak.py -h' to see the available operations."
				else:
					print "\n\t\tGetting account information..."
					api = parameters.api.get_user(args.username)
					user.set_user_information(api)
					print "\t\tOK"

					if args.sources or args.hashtags or args.mentions or args.d or args.file or args.number or args.text or args.meta or args.conv or args.socialnetworks or args.words_number:
						page = 1
						tweets_count = 0	
						print "\n\t\tExecuting operations..."

						while True:
							timeline = parameters.api.user_timeline(screen_name=args.username, include_rts=True, count=args.tweets_number, page=page)
						
							if timeline:
								for tweet in timeline:
									tweets_count += 1
									if is_valid(tweet, args):
										if args.sources:
											# Get information about the sources applications used to publish tweets
											source.set_sources_information(tweet)
										if args.hashtags:
											# Get hashtags included in tweets
											hashtag.set_hashtags_information(tweet)
										if args.mentions:
											# Get mentions included in tweets
											mentions.set_mentions_information(tweet)
										if args.d:
											# Get images included in tweets
											user_images.username = args.username
											user_images.images = args.d
											user_images.meta = args.meta
											user_images.set_images_information(tweet)
										if args.socialnetworks:
											parameters.menu_social = 1
											# Identify social networks identities
											social_networks.set_social_networks(tweet)
										if args.meta:
											# Get metadata information from user images
											user_images.set_metadata_information(tweet)
										if args.file or args.number:
											# Get geolocation information from user tweets
											geolocation.set_geolocation_information(tweet)
											geolocation.set_geofile_information(tweet, user)
										if args.text:
											# Search text in tweets
											l = args.text.split()
											user_tweets.find_text = l
											user_tweets.set_find_information(l, tweet)
										if args.conv:
											# Get conversations between two users
											user_conversations.set_tweets_conversations(parameters, tweet)
										if args.words_number:
											top_words.set_words_information(args.words_number, tweet)

														
									sys.stdout.write("\r\t\t" + str(tweets_count) + " tweets analyzed")
									sys.stdout.flush()										
									if tweets_count >= int(args.tweets_number):
										break
							else:
								break
							page += 1
							if tweets_count >= int(args.tweets_number):
								print
								break

						if args.meta: 
							user_images.profile_image_url = user.profile_image_url
							user_images.profile_banner_url = user.profile_banner_url
							user_images.screen_name = user.screen_name
														
							tmp_profile_image_url = user.profile_image_url
							if user.profile_image_url.find("_normal") < 0:
								tmp_profile_image_url = user.profile_image_url.replace(".jpg", "_400x400.jpg")
							else:
								tmp_profile_image_url = user.profile_image_url.replace("_normal.", ".")

							user_images.get_metadata(tmp_profile_image_url, 1, user.screen_name)

						if args.file:
							# Show geolocation information from user tweets
							geolocation.generates_geofile(args.file, parameters)
					
						print "\r\t\tOK"												

			if args.sources:
				# Get global information about the sources applications used to publish tweets
				source.set_global_information()

			if args.hashtags or args.latlonkm:
				# Get global information about hashtags included in tweets
				hashtag.set_global_information()

			if args.mentions or args.latlonkm:
				# Get global ifnromatino about mentions included in tweets
				mentions.set_global_information()			

			if args.number:
				# Get global ifnromatino about mentions included in tweets
				geolocation.set_global_information(args.number)			

			if args.followers_number:
				# Get followers for the specified user
				print "\n\t\tGetting followers..."
				followers.get_followers(args.username, parameters.api, parameters.output_followers)

			if args.friends_number:
				# Get friends for the specified user
				print "\n\t\tGetting friends..."
				friends.get_friends(args.username, parameters.api, parameters.output_friends)

			if args.likes_number:
				# Get favorites tweets
				print "\n\t\tGetting favorites..."
				if user.favourites_count: 
					favorites.set_favorites_information(parameters.api, args.username, int(args.likes_number))
				else:
					print "The user has not marked favorite tweets"
				print "\n\r\t\tOK"

			if args.words_number:
				
				#print top_words.top_words
				
				wordlist = sorted(top_words.top_words.items(), key=operator.itemgetter(1))
				wordlist.reverse()

				max = int(args.words_number)
				if max > len(wordlist) - 1:
					max = len(wordlist) - 1

				top_words.ordered_words = wordlist[0:max]

				for n in top_words.ordered_words:
					top_words.total_occurrences += n[1]
			

			if args.latlonkm or args.information or args.file or args.number or args.d or args.sources or args.hashtags or args.mentions or args.text or args.meta or args.conv or args.socialnetworks or args.likes_number:
				print "\n\t\tGenerating report..."
				generates_HTML_file(parameters, user, source, social_networks, hashtag, mentions, geolocation, user_images, user_tweets, search, user_conversations, favorites, top_words)
				if os.name == "nt":
					html_dir = os.path.dirname(os.path.abspath(__file__)) + "\\" + parameters.html_output_directory + "\\" + str(parameters.output)
				else:
					html_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + parameters.html_output_directory + "/" + str(parameters.output)
				print "\t\tOK"
				print "\n\n\tYour HTML report: " + html_dir 
				
	
	except Exception as e:
		show_error(e)
		sys.exit(1)


# ----------------------------------------------------------------------
def show_error(error):
	""" Show error message """
	try:
		rate_limit = 0
		print "\n\n\t\tOops! Something went wrong:"

		if str(error).find("Name or service not known") >= 0:
			print "\t\tDo you have Internet connection?"
		else:
			if str(error).find("Could not authenticate you") >= 0:
				print "\t\tYou need to assign value to OAuth tokens. Please, read the README.txt file for more information."
			else:	
				print "\t\t" + str(sys.exc_info()[1][0][0]['message'])		
				if "Rate limit exceeded" in str(sys.exc_info()[1][0][0]['message']):
					rate_limit = 1
		print 

		return rate_limit
		
	except Exception, e:
		print "\t\t" + str(error) + "\n"
		sys.exit(1)


# ----------------------------------------------------------------------
def get_string_with_padding(string, lon):
	""" Return a string with the specified length """

	try:
		padding = " " * lon
		if len(string) < lon:
			string_tmp = string + padding[0:len(padding)-len(string)]
			string = string_tmp[0:len(padding)]
		else:
			string_tmp = string
			string = string_tmp[0:len(padding)]

		return string
		
	except Exception as e:
		show_error(e)
		sys.exit(1)
	

# ----------------------------------------------------------------------
def get_url_media_from_instagram(html):
	""" Return a URL with the instagram photo or video """

	try:
		url_instagram = ""

		urls = re.search('og:video:secure_url" content="(.*)"', html)
		if urls:
			url_instagram = urls.group(1)
		else:
			urls = re.search('og:image" content="(.*)"', html)
			if urls:
				url_instagram = urls.group(1)
		
		return url_instagram
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_tagged_users_from_instagram(html):
	""" Return the tagged users in the instagram image """

	try:
		tagged_users = []
		owner = ""
		profile_image = ""
		
		urls = re.findall('"user": {"username": "(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"}', html)  
		for users in urls:
			tagged_users.append(users[23:len(users)-2])
		
		urls = re.search('viewer_has_liked":(.*)"profile_pic_url": "(.*)", "username": "(.*)", "followed_by_viewer"', html)

		if urls:
			profile_image = urls.group(2)
			owner = urls.group(3)

		return tagged_users, owner, profile_image
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_hashtags_from_instagram(html):
	""" Return the hashtags in the instagram message """

	try:
		hashtags = []
			
		hash = re.findall('<meta content="(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" property="instapp:hashtags"', html)  
		for h in hash:
			hashtags.append(h[15:len(h)-29] .lower())
						
		return hashtags
		
	except Exception as e:
		pass
		

# ----------------------------------------------------------------------
def get_url_media_from_foursquare(url):
	""" Return a URL with the foursquare photo or video """

	try:
		url_foursquare = ""
		owner = ""
		profile_image = ""

		try:
			response = urllib2.urlopen(str(url))  
			html = response.read()
		except Exception as e:
			return url_foursquare, owner, profile_image		

		urls = re.search('<div id="mapContainer"><img src="(.*).jpg" alt="', html) 
		if urls:
			profile_image = urls.group(1) + ".jpg"
		
		urls = re.search('","canonicalUrl":"https:(.*),"venue":{"name":"', html)

		if urls:
			urls = re.search('foursquare.com(.*)/checkin', str(urls.group(1)))
			if urls:
				owner = urls.group(1)[2:len(urls.group(1))-1]
				urls = re.search('"canonicalPath":(.*)checkin', str(urls.group(1)))
				if urls:	

					last_position = 0
					try:
						while True:
							last_position = urls.group(1).index('"', last_position+1)
					except ValueError: 
						owner = urls.group(1)[last_position+3:len(urls.group(1))-2]

				#url_foursquare = "https://foursquare.com/"+owner
				url_foursquare = ""

		return url_foursquare, owner, profile_image
		
	except Exception as e:
		pass



# ----------------------------------------------------------------------
def get_url_facebook_from_foursquare(url):
	""" Return a URL with the facebook url from a foursquare user """

	try:
		url_facebook = ""
		user_facebook = ""
		profile_image = ""
		
		try:
			response = urllib2.urlopen(str(url))  
			html = response.read()
		except Exception as e:
			return url_facebook, user_facebook, profile_image 
		urls = re.search('<a href="http://www.facebook.com/(.*)" rel="nofollow" target="_blank" class="fbLink iconLink"', html) 
		if urls:
			url_facebook = urls.group(1)

			url = "https://www.facebook.com/" + url_facebook

			request_headers = {
				'User-agent': 'Mozilla/5.0',
				'Cookie': 'c_user=100010863996105; xs=64%3AeKa4GH5PF-pZpw%3A2%3A1474823721',
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
				}

			try:
				request = urllib2.Request(url, headers=request_headers)
				html = urllib2.urlopen(request.read())
				urls = re.search('content="0; URL=/(.*)?_fb_noscript=1"', html)
				if urls:
					user_facebook = str(urls.group(1))	
			except Exception as e:
				pass

		return url_facebook, user_facebook, profile_image 
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_user_from_facebook_url(url):
	""" Return a URL with the facebook url from a foursquare user """

	try:
		user_facebook = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('autocomplete="off" name="next" value="https://www.facebook.com/(.*)/posts/[0-9]*"', html)
		if urls:
			if str(urls.group(1)).find("profile.php") < 0:
				user_facebook = urls.group(1)
		else:
			try:
				response = urllib2.urlopen("http://longurl.org/expand?url="+url) 
				html = response.read()
				urls = re.search('<a href="https://www.facebook.com/(.*)/posts/[0-9]*">https://', html)
				if urls:
					user_facebook = urls.group(1)
			except Exception as e:
				pass
				
		return user_facebook 
		
	except Exception as e:
		pass



# ----------------------------------------------------------------------
def get_user_from_flickr_url(url):
	""" Return the username of a flickr user """

	try:
		user_flickr = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('"og:url" content="https://www.flickr.com/photos/(.*)/[0-9]*/"', html)
		if urls:
				user_flickr = urls.group(1)
				
		return user_flickr
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_user_from_runkeeper_url(url):
	""" Return the username of a Runkeeper user """

	try:
		user_runkeeper = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('"https://runkeeper.com/user/(.*)/activity/', html)
		if urls:
				user_flickr = urls.group(1)
				
		return user_flickr
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_user_from_vine_url(url):
	""" Return the username of a Vine user """

	try:
		user = ""
		html = ""
		
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('"name": "(.*)",', html)
		if urls:
			tmp = urls.group(1)
			id = re.search('"url": "https://vine.co/u/(.*)"', html)
			if id:
				user = id.group(1)
				user = id.group(1) + "/" + str(tmp)
		
		return user
		
	except Exception as e:
		pass

# ----------------------------------------------------------------------
def get_user_from_periscope_url(url):
	""" Return the username of a Periscope user """

	try:
		user_periscope = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('pscp://user/(.*)&quot;,&quot;inAppUrl', html)
		if urls:
				user_periscope = urls.group(1)
		
		return user_periscope
		
	except Exception as e:
		pass

# ----------------------------------------------------------------------
def get_user_from_kindle_url(url):
	""" Return the username of a Kindle user """

	try:
		user_kindle = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('customerId":"(.*)","howLongAgo', html)
		if urls:
			tmp = urls.group(1)	
			try:
				url = "https://kindle.amazon.com/profile/redirect/" + tmp
				response = urllib2.urlopen(str(url)) 
				html = response.read()
			except Exception as e:
				pass

			urls = re.search('"/profile/(.*)"', html)
			if urls:
					user_kindle = urls.group(1)
				
		return user_kindle
		
	except Exception as e:
		pass

# ----------------------------------------------------------------------
def get_user_from_youtube_url(url):
	""" Return the username of a Youtube user """

	try:
		user = ""
		html = ""

		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('/channel/(.*)" class', html)
		if urls:
			tmp = urls.group(1)	
			try:
				url = "http://www.youtube.com/channel/" + tmp
				response = urllib2.urlopen(str(url)) 
				html = response.read()
			except Exception as e:
				pass

			urls = re.search('href="http://www.youtube.com/user/(.*)"', html)
			if urls:
				user = tmp + "/" + urls.group(1)
			else:
				urls = re.search('<meta property="og:title" content="(.*)">', html)
				if urls:
						user = tmp + "/" + urls.group(1)
				
		return user
		
	except Exception as e:
		pass

# ----------------------------------------------------------------------
def get_user_from_googleplus_url(url):
	""" Return the username of a Google+ user """

	try:
		user = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('"https://plus.google.com/(.*)">', html)
		if urls:
			tmp = urls.group(1)	
			try:
				url = "https://plus.google.com/" + tmp
				response = urllib2.urlopen(str(url)) 
				html = response.read()
			except Exception as e:
				pass

			urls = re.search('<meta itemprop="url" content="https://plus.google.com/(.*)"><link rel="alternate" href="android-app:', html)
			if urls:
					user = tmp + "/" + urls.group(1)
 
		return user
		
	except Exception as e:
		pass

# ----------------------------------------------------------------------
def get_user_from_frontback_url(url):
	""" Return the username of a Frontback user """

	try:
		user = ""
		html = ""
		try:
			response = urllib2.urlopen(str(url)) 
			html = response.read()
		except Exception as e:
			pass
		
		urls = re.search('post-info-username"><a class="no-ui" href="http://www.frontback.me/(.*)">(.*)</a></h1><h2 class="post-info-caption', html)
		if urls:
				user = urls.group(1)
				
		return user
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def get_url_media_from_youtube(url):
	""" Return a URL with the foursquare photo or video """

	try:
		url_youtube = ""
		
		try:
			response = urllib2.urlopen(str(url))  
			html = response.read()
		except Exception as e:
			return url_youtube
		
		urls = re.findall('data-expanded-url="http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)  

		if urls:
			url_youtube = urls[0][19:]
			
		return url_youtube
		
	except Exception as e:
		pass


# ----------------------------------------------------------------------
def main():
	""" Main function"""
	try:
		parameters = Parameters() 
		credits(parameters)

		parser = argparse.ArgumentParser(
			version='Tinfoleak v2.0',
			description='Tinfoleak')
		parser.add_argument('-t', '--tweets', dest='tweets_number', default=200, help='analyze TWEETS_NUMBER tweets (default: 200)')
		parser.add_argument('-i', '--info', action='store_true', dest='information', help='get general information about the user')
		parser.add_argument('-s', '--sources', action='store_true', dest='sources', help='get the client applications used to publish every tweet')
		parser.add_argument('-f', '--followers', default=0, dest='followers_number', help='get the last FOLLOWERS_NUMBER followers for the user')
		parser.add_argument('-r', '--friends', default=0, dest='friends_number', help='get the last FRIENDS_NUMBER friends for the user')
		parser.add_argument('-w', '--words', default=0, dest='words_number', help='get the top WORDS_NUMBER most used words')
		parser.add_argument('--conv', action='store_true', dest='conv', help='get user conversations')
		parser.add_argument('--sdate', dest='sdate', help='filter the results with SDATE as start date (format: yyyy-mm-dd)')
		parser.add_argument('--edate', dest='edate', help='filter the results with EDATE as end date (format: yyyy-mm-dd)')
		parser.add_argument('--stime', default='00:00:00', dest='stime', help='filter the results with STIME as start time (format: HH:MM:SS)')
		parser.add_argument('--etime', default='23:59:59', dest='etime', help='filter the results with ETIME as end time (format: HH:MM:SS)')
		parser.add_argument('--hashtags', action='store_true', dest='hashtags', help='get information about hashtags')
		parser.add_argument('--mentions', action='store_true', dest='mentions', help='get information about user mentions')
		parser.add_argument('--likes', default=0, dest='likes_number', help='get information about the last LIKES_NUMBER favorites tweets')
		parser.add_argument('--meta', action='store_true', dest='meta', help='get metadata information from user images')
		parser.add_argument('--media', dest='d', const='*', help='[no value]: show user images and videos, [D]: download user images to \"username\" directory', type=str, nargs='?')
		parser.add_argument('--social', action='store_true', dest='socialnetworks', default='', help='identify user identities in social networks')
		parser.add_argument('--geo', dest='file', default='', help='get geolocation information and generates an output FILE (KML format)')
		parser.add_argument('--top', dest='number', default='', help='get top NUMBER locations visited by the user')
		parser.add_argument('--find', dest='text', default='', help='search tweets based on filters. [+]word : include "word", [-]word : not include "word", [+r] : retweeted, [-r] : not retweeted, [+m] : multimedia, [-m] : not multimedia')
		parser.add_argument('--search', dest='latlonkm', const='*', nargs='?', help='search tweets in global timeline or filtering by LATitude, LONgitude, and KMs (distance)')
		parser.add_argument('-o', '--output', dest='output', default='', help='generates a OUTPUT file (HTML format)')
		parser.add_argument('-u', '--user', dest="username", default='', help='Twitter user name')
			
		args = parser.parse_args()

		if args.sdate:
			parameters.sdate = args.sdate
		else:			
			today = date.today()
			if args.latlonkm:
				parameters.sdate = date.fromordinal(today.toordinal()-14).strftime('%Y-%m-%d')
			else:
				parameters.sdate = date.fromordinal(today.toordinal()-365).strftime('%Y-%m-%d')				
			args.sdate = parameters.sdate
		
		if args.edate:
			parameters.edate = args.edate
		else:
			tmp = datetime.datetime.now() + datetime.timedelta(days=1)
			parameters.edate = tmp.strftime('%Y-%m-%d')
			args.edate = parameters.edate
			
		if args.stime:
			parameters.stime = args.stime
		else:
			parameters.stime = "00:00:00"
		
		if args.etime:
			parameters.etime= args.etime
		else:
			parameters.etime = "23:59:59"

		if args.file:
			parameters.geo = args.file
		else:
			parameters.geo = ""

		if args.number:
			parameters.top = args.number
			parameters.output_geolocation = 1
		else:
			parameters.top = ""

		if args.text:
			parameters.find = args.text
			parameters.output_tweet = 1
		else:
			parameters.find = ""

		if args.output:
			parameters.output= args.output
		else:
			parameters.output = "tinfoleak.html"
		
		if args.latlonkm:
			parameters.search= args.latlonkm
			parameters.output_search = 1
		else:
			parameters.search = ""

		if args.meta:
			parameters.output_metadata = 1

		if args.socialnetworks:
			parameters.output_social = 1

		if args.hashtags:
			parameters.output_hashtag = 1

		if args.mentions:
			parameters.output_mention = 1

		if args.likes_number:
			parameters.output_favorites = 1

		if args.d:
			parameters.output_media = 1

		if args.sources:
			parameters.output_source = 1

		if args.followers_number:
			parameters.output_followers = args.followers_number

		if args.friends_number:
			parameters.output_friends = args.friends_number

		if args.words_number:
			parameters.output_words = args.words_number

		if args.conv:
			parameters.output_conversation = 1

		if args.username:
			parameters.username= args.username
		
		# Get the current time
		sdatetime = datetime.datetime.now()
		
		# Obtain the information requested
		get_information(args, parameters)

		# Show the elapsed time
		tdelta = datetime.datetime.now() - sdatetime 
		hours, remainder = divmod(tdelta.seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		print "\n\n\tElapsed time: %02d:%02d:%02d" % (hours, minutes, seconds)
		print "\nSee you soon!\n"
		
		parameters.elapsedtime = (hours, minutes, seconds)
		
	except Exception, e:
		show_error(e)
		sys.exit(1)
				
				
if __name__ == '__main__':
	main()
