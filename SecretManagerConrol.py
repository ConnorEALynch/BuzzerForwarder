import json

import boto3
from botocore.exceptions import ClientError

#CLASS:class SecretManagerControl:
# Made to simplify reading and writting to a preexisting secret in the AWS secret manager. On instantiation it establishes a client connection to the manager of the specified secret. Afterwards it reads the current secret and thier values into the program to be changed and overwritten using the overwriteSecretValues() method. May be expanded in the future to create new secrets

class SecretManagerControl:
	#  __init__(self, SecretARN, version = None)
	# PARAMS: self, SecretARN, version = None
	#   self: refrence to instance for attribute assignment
	# 	SecretARN: The unique ID that that the client needs to connect to the secretsmanager
	# 	version = None: The version of secrets to pull. defaults to none
	#
	def __init__(self, SecretARN, version = None):
		self.SecretARN = SecretARN 
		self.secrets_client = boto3.client("secretsmanager", region_name='us-east-1')
		self.kwargs = {'SecretId': self.SecretARN}
		if version is not None:
			self.kwargs['VersionStage'] = version
		self.__read_secret_values()

	#	DEPRICATED
	#  def custom_decoder(self, responseDict)
	# 	PARAMS: self, responseDict
	#   self: refrence to instance for attribute assignment
	# 	responseDict: the response dictionary returned from the secret manager
	#	RETRUN: a recordclass that is formated to be added to the SecretManagerControl object
	#
	def custom_decoder(self, responseDict):
		meh = responseDict.keys()
		bleh = responseDict.values()
		#return MutableNamedTuple('X', meh)(*bleh)
		return list('X', responseDict.keys())(*responseDict.values())
		#return recordclass('X', responseDict.keys())(*responseDict.values())
		
		
	# def __read_secret_values(self)
	# PARAMS: self
	#   self: refrence to instance for attribute assignment
	#
	def __read_secret_values(self):

		self.rawResponse = self.secrets_client.get_secret_value(**self.kwargs)
		self.values = json.loads(self.rawResponse["SecretString"])


		
	# def __overwrite_secret_values(self)
	# PARAMS: self
	#   self: refrence to instance for attribute assignment
	#
	def __overwrite_secret_values(self):
		result = False
	
		if self.values != None:
			self.kwargs['SecretString'] = json.dumps(self.values)
			if self.secrets_client.update_secret(**self.kwargs) != None:
				result = True
		return result

	# def update_mute(self, muteManager)
	# PARAMS: self
	#   self: refrence to instance for attribute assignment
	#	muteManger: object holding the updated information
	def update_mute(self, muteManager):
		muteList = list()
		for tenant in muteManager.tenantList:
			if tenant.mute != None:
				#muteManager Logic bleeds over into this class functionality. will correct in future update
				muteList.append(tenant.mute.format(muteManager.conversionFormat))
			else:
				muteList.append(str(None))
		#transforms the tenant objects into comma deliminated strings for storage
		newValues = ",".join(muteList)
		#check if anythings cahnged to avoid unnecessary writes
		if newValues != self.values["MUTE"]:
			self.values["MUTE"] = newValues
			self.__overwrite_secret_values()



		
