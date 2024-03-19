import sys, os

currentPath = os.path.dirname(os.path.abspath(__file__))

from FunctionOverloading import OLF_Dict_typ

class testClass():
	methods = OLF_Dict_typ()

	def __init__(self):
		self.var = 1

test = testClass()
#print(dir(test))




@testClass.methods.addFunction
def add(self:testClass, a:int,b:int):
	return self.var+a+b

@testClass.methods.addFunction
def add(self, a:int,b:int,c:int):
	return a+b+c


testClass.methods.bind(testClass)

print(test.add(1,2))

test.add(1,2)



#print(add(1,2))