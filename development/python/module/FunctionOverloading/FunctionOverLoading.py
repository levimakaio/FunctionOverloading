from types import MethodType
from re    import sub

OLF_ConversionTable = {}
OLF_ConversionTable['bool']   = ['c_bool']

OLF_ConversionTable['int']      = [ 'c_byte',       #| char                                   | int
                                    'c_ubyte',      #| unsigned char                          | int
                                    'c_short',      #| short                                  | int
                                    'c_ushort',     #| unsigned short                         | int
                                    'c_int',        #| int                                    | int
                                    'c_uint',       #| unsigned int                           | int
                                    'c_long',       #| long                                   | int
                                    'c_ulong',      #| unsigned long                          | int
                                    'c_longlong',   #| __int64 or long long                   | int
                                    'c_ulonglong',  #| unsigned __int64 or unsigned long long | int
                                    'c_size_t',     #| size_t                                 | int
                                    'c_ssize_t',    #| ssize_t or Py_ssize_t                  | int
                                    'c_time_t',     #| time_t                                 | int

                                    'float',
                                    'c_float',
                                    'c_double',
                                    'c_longdouble'
                                    ]

OLF_ConversionTable['float']    = [ 'c_float',      #| float                                  | float
                                    'c_double',     #| double                                 | float
                                    'c_longdouble'] #| long double                            | float

OLF_ConversionTable['str']      = ['c_wchar_p']

def signitureConversionMatch(key, signiture, table = OLF_ConversionTable):
	# key       :tuple of argument types used to call a function
	# signature :tuple of argument types used to uniquely define a function

	#This function will use the OLF_converisontable to see if the key and
	#signature match if the key is allowed to be cast in accordance with the
	#conversion table

	#check that key and signature have matching lengths,
	#return false if they do not
	if not len(key) == len(signiture): return False

	#check each argument of the signature for conversion matches with the key.
	#If any of the keys can not be converted return False
	for index, arg in enumerate(signiture):

		#check for an exact match
		if key[index] == arg: continue

		# return false if there are no defined conversion for key[index]
		if key[index] not in table: return False

		# return false there is no valid conversion
		if arg not in table[key[index]]: return False

	# return true if all key arguments can be converted
	return True

def createKey(argTypeList, **kwArgs):
	return tuple(argTypeList)

def createKey1(OLF_functionToken):
	return tuple(OLF_functionToken.argTypeList)

class OLF_Token_typ():

	def __init__(self, fn, keyFunction = createKey1):

		#set function to create unique function signatures.
		#keyFunction() must return a hashable object
		self.keyFunction  = keyFunction

		#set info for the function
		if fn is not None:
			self.name         = fn.__name__
			self.ptr          = fn
			self.argTypeList  = [value[1].__name__ for value in fn.__annotations__.items()] #I need to check for return values, this could cause me problems
			self.argNameList  = [value[0]          for value in fn.__annotations__.items()] #I need to check for return values, this could cause me problems
			#self.returnType   = 
			self.numVars      = len(self.argNameList)
			self.signiture    = self.createKey()

	def createKey(self):
		return self.keyFunction(self)

class OLF_Function_typ():

	def __init__(self, name):
		self.name            = name
		self.funcDict        = {}
		self.keyFunction     = createKey
		self.conversionTable = OLF_ConversionTable

	def addFunction(self, fn, keyFunction = createKey1):

		#create a token
		token = OLF_Token_typ(fn)

		#check that this key has not been used
		if token.signiture in self.funcDict:
			input(f'"{token.signiture}" already exists in overloaded function "{self.name}"')
			return

		#add token to the dictionary using its unique signiture as the key
		self.funcDict[token.signiture] = token

	def __call__(self, instance, *args, **kwargs):

		argTypesList = [type(arg).__name__ for arg in args]

		if instance is None:
			#get the key based on the args of the fucntion call
			key = self.keyFunction(argTypesList, prefix = self.name)
		else:
			instanceTypeName = sub('_typ', '',type(instance).__name__)
			key = self.keyFunction( [instanceTypeName] + argTypesList, prefix = self.name)

		key = self.signitueResolution(key)
		if key is None: return

		if instance is None:
			return self.funcDict[key].ptr(*args, **kwargs)
		else:
			return self.funcDict[key].ptr(instance, *args, **kwargs)

	def signitueResolution(self, key):

		#return key if exact match if found
		if key in self.funcDict: return key

		# return signature if the key can be converted to a match
		# NOTE: we are returning the first match found, if may not be the best match available
		for signature in self.funcDict:
			if signitureConversionMatch(key, signature, self.conversionTable): return signature

		#if key doesn't exist in funcDict and cant be converted issue a warning and return none
		print(''.center(50,'*'))
		print(f'\t"{key}"\n')
		print(f'Is not in overloaded function "{self.name}".  The defined keys are:')
		print()
		print(self.man(printString=False))
		print()
		print('defined conversion:')
		for key, value in self.conversionTable.items():
			print(f'{key.rjust(25)}: {value}')


		input()

		return None

	def man(self, space = 0., printString=True):
		#return a list of valid keys
		returnString = ''
		for key in self.funcDict:
			returnString += f'{"".center(space)}{key} {self.funcDict[key].argNameList}\n'

		if printString:
			print(returnString)

		return returnString


	def __get__(self, instance, owner):
		#this fucntion is required to get the instance of the base class to pass through
		return MethodType(self, instance) if instance else self

class OLF_Dict_typ():

	def __init__(self):
		self.funcDict = {}

	def addFunction(self, fn):

		#create a new entry if this is the first time this
		#function name has been added to this dictionary
		if fn.__name__ not in self.funcDict:
			self.funcDict[fn.__name__] = OLF_Function_typ(fn.__name__)

		#add function to class 
		self.funcDict[fn.__name__].addFunction(fn)

		return;

	def __str__(self):

		returnString = ''
		for func_key in self.funcDict:
			returnString+=func_key
			returnString+='\n'
			returnString+=self.funcDict[func_key].man(space = 5, printString=False)
			returnString+='\n'

		if returnString == '':
			returnString = 'No mehtods'

		return returnString

	def show(self):
		print(self.__str__())
		#print out a list of all functions with their oveload keys
#		for func_key in self.funcDict:
#			print(func_key)
#			self.funcDict[func_key].man(space = 5)
#			print()
#			for tag, details in self.funcDict[func_key].funcDict.items():
#				print(details.ptr.__annotations__)
#				print(f'\t{tag}', details.argNameList)


	def bind(self, instance):
		#bind all functions to a python class
		for method in self.funcDict:
			setattr(instance, method, self.funcDict[method])
