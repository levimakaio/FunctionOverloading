import ctypes

def OLF__del__(self):
	print(f'delete "{type(self).__name__}" pointer at address {ctypes.addressof(self)}')
	#check if a pointer to a "delete" funciton exists
	if callable(getattr(self, 'delete', None)):
		self.methods.funcDict['delete'](None, ctypes.cast(ctypes.pointer(self), ctypes.POINTER(type(self).__mro__[2]) ))
	else:
		input(f'Warning: No destructor define in {type(self)}')

def OLF__new__(cls, *args):

	#check if a pointer to a create funciton exists
	if callable(getattr(cls, 'create', None)):
		ptr = cls.create(None, *args)
	else:
		ptr = None

	#if the ptr is not NULL:
	#cast the class as this type which will add a destructor to deallocate the memory after this instance goes out of scope in python.
	#Note: if this class goes out of scope but there is still a pointer to this address that address will now point to garbage
	#TODO: create accounting for when a pointer should get deleted. this seems complicated so will punt on this for now
	if ptr is not None:
		return ctypes.cast(ptr, ctypes.POINTER(cls)).contents

	#return an empty instance if the pointer is NULL 
	return super(cls.__mro__[1], cls).__new__(cls.__mro__[2])

def OLF__init__(self, *args):
	pass
#	#check if a pointer to a create funciton exists
#	if callable(getattr(self, 'create', None)):
#		self.ptr = self.create(*args)
#	else:
#		self.ptr = None

#	self.ptr = 4

#	print('__init__')


def OLF__pass__(self,*args):
	pass

class OLF_classModifier():
	pass

OLF_classModifier.__new__     = OLF__new__
OLF_classModifier.__init__    = OLF__pass__
OLF_classModifier.__del__     = OLF__del__