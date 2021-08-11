import json

import boto3
from botocore.exceptions import ClientError
from recordclass import asdict, recordclass

#CLASS:class SecretManagerControl:
# Made to simplify reading and writting to a preexisting secret in the AWS secret manager. On instantiation it establishes a client connection to the manager of the specified secret. Afterwards it reads the current variables and thier values into the program to be changed and overwritten using the overwriteSecretValues() method. May be expanded in the future to create new secrets

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
		self.__readSecretValues()


	#  def customDecoder(self, responseDict)
	# PARAMS: self, SecretARN, version = None
	#   self: refrence to instance for attribute assignment
	# 	responseDict: the response dictionary returned from the secret manager
	#RETRUN: a recordclass that is formated to be added to the SecretManagerControl object
	#
	def customDecoder(self, responseDict):
		return recordclass('X', responseDict.keys())(*responseDict.values())
		
		
	#  def __readSecretValues(self)
	# PARAMS: self, SecretARN, version = None
	#   self: refrence to instance for attribute assignment
	#
	def __readSecretValues(self):
		try:
			self.rawResponse = self.secrets_client.get_secret_value(**self.kwargs)
			self.values = json.loads(self.rawResponse["SecretString"], object_hook=self.customDecoder)
		#print outputs to log in AWS lambda
		except ClientError as err:
			print(err)
		except json.JSONDecodeError as err :
			print(err)
		except Exception as catchAll:
			print(catchAll)

		
	# def overwriteSecretValues(self)
	# PARAMS: self, SecretARN, version = None
	#   self: refrence to instance for attribute assignment
	#
	def overwriteSecretValues(self):
		result = False
		try:
			if self.values != None:
				self.kwargs['SecretString'] = json.dumps(asdict(self.values))
				if self.secrets_client.update_secret(**self.kwargs) != None:
					result = True
		#print outputs to log in AWS lambda
		except ClientError as err:
			print(err)
		except json.JSONDecodeError as err :
			print(err)
		except Exception as catchAll:
			print(catchAll)
		return result


		
