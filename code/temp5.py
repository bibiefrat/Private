


class Animal(object):
    def __init__(self):
        self.age = 0
        self.hunger = 10
        self.fun = 0
        self._item = {}
    def grow(self):
        self.age += 1
    def eat(self):
        if self.hunger > 0:
            self.hunger -= 1
    def play(self):
        self.fun += 1
    def go_to_toilet(self):
        self.hunger += 1
    def sleep(self):
        self.fun -= 1
        
class Dog(Animal):
    def __init__(self):
        Animal.__init__(self)
    def bark(self):
        print 'Waff Waff'
    def wag_tail(self):
        self.fun += 2
        print 'Wagging'
        
        
class AgingDog(Dog):
    def grow(self):
        self.age += 10

an = Animal()   
aging_dog = AgingDog()     
print aging_dog.__class__

print AgingDog.__bases__

print aging_dog.__dict__
