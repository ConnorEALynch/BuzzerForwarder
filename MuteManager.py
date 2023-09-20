from collections import namedtuple

import pendulum


#class Mutmanager()
# manages the variables and operatins related to muting the buzzer. this includes parsing inputs, generating responses and converting from timezones. If it cares about muting it handles it
class MuteManger():

	__now = None									# universal now to avoid repeat calls
	__timeZone = None								# client Timezone
	__formatDict = None								# contains a dictionary of parse formats and function pointers
	conversionFormat = "h:mm A YYYY-MM-D"			# format for conversion
	__displayFormat = "h:mm A [on] MMM D YYYY"		# format for dsiplaying in messages

	def __init__(self, secret):
		self.__timeZone = pendulum.timezone('America/Toronto')
		self.__now = pendulum.now(tz='UTC')
		self.tenantList = self.__generate_tenant_list(secret)
		self.callList = self.__generate_call_list()

	#  def manage_request(self,request):
	# 	PARAMS: self, request
	#   	self: refrence to instance for attribute assignment
	# 		request: the web request conatining all the varaibles associated with the REST call
	#	RETRUN: returns a confirmation or error string depending on the operation and its success
	#
	def manage_request(self,request):
		self.number = request.values["From"]			#number of the sent message
		self.message = request.values["Body"]			#contents of the message

		#these vars will be used for more dynamic timezones in a future update. right now its local time
		self.state = request.values["FromState"]		#sender state/province
		self.country = request.values["FromCountry"]	#sender country

		#remove a mute or add a new one
		if self.message.lower() == "unmute":
			return self.__unmute()
		else:
			#dict of parse formats and function pointers
			self.__formatDict = {'h A' : self.__parse_time,'h:mm A' : self.__parse_time,'ddd': self.__parse_weekday, 'dddd': self.__parse_weekday , 'MM D' : self.__parse_date, 'MMM D' : self.__parse_date, 'M/D': self.__parse_date,'h:mm A M/D' : self.__parse_exact,'h:mm A M D' : self.__parse_exact}

		#consider moving update mute here for less repeated code
			return self.__parse_message()

	#  def __unmute(self):
	# 	PARAMS: self, request
	#   	self: refrence to instance for attribute assignment
	#	RETRUN: a message saying the mute was removed
	#
	def __unmute(self):
		#if number exists in the tenant list return the items mute. make the list a single item
		[previousMute] = [x.mute for x in self.tenantList if x.number == self.number]
		message = "No mute is currently active"
		#if another mute is not null say it was removed
		if previousMute != None:
			message = "Your mute set to end at %s has been removed"%(previousMute.in_tz(self.__timeZone).format(self.__displayFormat))

		#update the numbers mute value in the object
		self.__update_mute(None)
		return message

	# 	def __parse_message(self):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#	RETRUN: returns a confirmation or error message
	#
	def __parse_message(self):
		parsedVals = None
		result = None
		#iterate through the list and try to parse against all the formats. call the associated function on success
		for format, func in self.__formatDict.items():
			try:
				parsedVals = pendulum.from_format(self.message, format, tz= self.__timeZone).in_timezone('UTC')
				result = func(parsedVals)
				break
			#needed to catch all the failed parses. handled properly just below
			except ValueError:
				pass

		if parsedVals == None:
			return """Invalid Command:
unmute - removes mute
8:33 AM - next 8:33 AM
9/7 - Sept 7 at current time
Saturday - next Sat at current time
8:00 AM 9/7 - exact time and day"""
		#update the mute value and return the formated string
		self.__update_mute(result)
		return "The buzzer will be mute until %s"%(result.in_tz(self.__timeZone).format(self.__displayFormat))

	# 	def __parse_time(self, values):
	# 	PARAMS: self, values
	#   	self: refrence to instance for attribute assignment
	#		values: the datetime object with values stored in it
	#	RETRUN: returns a confirmation or error message
	#
	def __parse_time(self, values):
		result = None
		parsedTime = values.time()
		#if the parsed time is less than now set the alarm at this time tomorrow
		if parsedTime < self.__now.time():
			tmw = pendulum.tomorrow()
			result = values.set(day= tmw.day, month= tmw.day, year= tmw.year)
		else:
		#otherwise set it for today
			today = pendulum.today()
			result = values.set(day= today.day, month= today.day, year= today.year)

		return result.in_tz('UTC')

	# 	def __parse_date(self, values):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#		values: the datetime object with values stored in it
	#	RETRUN: returns a confirmation or error message
	#
	def __parse_date(self, values):
		result = None
		parsedThisYear = values.set(year= self.__now.year)
		#if the parsed date is less than now set the alarm at this date next year
		if parsedThisYear.date() < pendulum.today().date():
			parsedNextYear = parsedThisYear.set(year= parsedThisYear.add(years= 1).year)
			result = parsedNextYear
		else:
			result = parsedThisYear
		#sets alarm to current time. use axact parse for precision
		result = result.set(hour=self.__now.hour, minute=self.__now.minute)
		return result.in_tz('UTC')

	# 	def __parse_weekday(self, values):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#		values: the datetime object with values stored in it
	#	RETRUN: returns a confirmation or error message
	#
	def __parse_weekday(self, values):
		#get the next weekday specified and set the alarm for that day with current time
		return self.__now.next(values.day_of_week).set(hour=self.__now.hour, minute=self.__now.minute).in_tz('UTC')

	# 	def __parse_exact(self, values):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#		values: the datetime object with values stored in it
	#	RETRUN: returns a confirmation or error message
	#
	def __parse_exact(self, values):
		result = None
		#if the parsed atetime is less than now set it for the next coming year
		parsedThisYear = values.set(year= self.__now.year)
		if parsedThisYear < self.__now:
			result = parsedThisYear.set(year= parsedThisYear.add(years= 1).year)
		else:
			result = parsedThisYear
		return result.in_tz('UTC')

	# 	def __generate_tenant_list(self, secret):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#		secret: needed for locally assigning the number and mute values
	#	RETRUN: returns a list of tenant objects holding the number and active mute of the user
	#	
	def __generate_tenant_list(self, secret):
		tenantList = list()
		numbers = secret.values["NUMBERS"].split(",")
		mute = secret.values["MUTE"].split(",")
		Tenant = namedtuple('tenant',['number', 'mute'])
		#enumerate through numbers appending tenant objects contianing parsed datetimes
		for i, item in enumerate(numbers):
			if mute[i] == "None":
				tenantList.append(Tenant(numbers[i], None))	
			else:
				formatedMute = pendulum.from_format(mute[i], self.conversionFormat, tz= self.__timeZone)
				tenantList.append(Tenant(numbers[i], formatedMute))	
		return tenantList

	# 	def __generate_call_list(self):
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#	RETRUN: returns a confirmation or error message
	#	
	def __generate_call_list(self):
		callList = list()
		bothMute = True
		#check if each user has a mute that is active append those without to the call list
		for tenant in self.tenantList:
			if tenant.mute == None or tenant.mute < self.__now :
				callList.append(tenant.number)
				bothMute = False
		#determines if both are mute for easier use
		self.bothMute = bothMute
		return callList

	# 	def __update_mute(self, newMute:
	# 	PARAMS: self
	#   	self: refrence to instance for attribute assignment
	#		newMute: a datetime or none with the new mute value 
	#	
	def __update_mute(self, newMute):
		for count, tenant in enumerate(self.tenantList):
			if tenant.number == self.number:
				self.tenantList[count] = tenant._replace(mute= newMute)
		#update call list for both muted later in endpoint
		self.__generate_call_list()

	def both_mute(self):
		result = True
		for tenant in self.tenantList:
			if tenant.mute == None or self.__now < tenant.mute:
				result = False

		return result
