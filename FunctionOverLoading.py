from types import MethodType
from re    import sub

def createKey(argTypeList, **kwArgs):
	return tuple(argTypeList)


def createKey1(OLF_functionToken):
	return tuple(OLF_functionToken.argTypeList)


class OLF_Token_typ():

	def __init__(self, fn, keyFunction = createKey1):

		#set function to create unique function signitures.
		#keyFunction() must return a hashable object
		self.keyFunction  = keyFunction

		#set info for the function
		if fn is not None:
			self.name         = fn.__name__
			self.ptr          = fn
			self.argTypeList  = [value[1].__name__ for value in fn.__annotations__.items()] #I need to chack for return values, this could cause me problems
			self.argNameList  = [value[0]          for value in fn.__annotations__.items()] #I need to chack for return values, this could cause me problems
			#self.returnType   = 
			self.numVars      = len(self.argNameList)
			self.signiture    = self.createKey()

	def createKey(self):
		return self.keyFunction(self)

class OLF_Function_typ():

	def __init__(self, name):
		self.name         = name
		self.funcDict     = {}
		self.keyFunction  = createKey

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

		if key in self.funcDict:
			if instance is None:
				return self.funcDict[key].ptr(*args, **kwargs)
			else:
				return self.funcDict[key].ptr(instance, *args, **kwargs)

		#if key doens't exist in funcDict return warning
		print(f'\t"{key}"\n')
		print(f'Is not in overloaded function "{self.name}".  The defined keys are:')
		print()
		self.man()

	def man(self, space = 0., printString=True):
		#return a list of valid keys
		returnString = ''
		for key in self.funcDict:
			returnString += f'{"".center(space)}{key} {self.funcDict[key].argNameList}\n'

		if printString:
			print(returnString)

		return returnString


	def __get__(self, instance, owner):
		#this fucntion is required to get the instance of the base calss to pass through
		return MethodType(self, instance) if instance else self

class OLF_Dict_typ():

	def __init__(self):
		self.funcDict = {}

	def addFunction(self, fn):

		#create a new entrly if this is the first time this
		#funciton name has been added to this dictionary
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
