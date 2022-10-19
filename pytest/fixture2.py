from __future__ import print_function
import pytest

@pytest.fixture()
def my_fixture(request):
    print('\n-----------------')
    print('fixturename : %s' % request.fixturename)
    print('scope       : %s' % request.scope)
    print('function    : %s' % request.function.__name__)
    print('cls         : %s' % request.cls)
    print('module      : %s' % request.module.__name__)
    print('fspath      : %s' % request.fspath)
    print('-----------------')
 
    if request.function.__name__ == 'test_three':
        request.applymarker(pytest.mark.xfail)
 
def test_one(my_fixture):
    print('test_one():')
 
class TestClass():
    def test_two(self, my_fixture):
        print('test_two()')
 
def test_three(my_fixture):
    print('test_three()')
    assert False
    
@pytest.fixture( params=[1,2,3] )
def test_data(request):
    return request.param
 
def test_not_2(test_data):
    print('test_data: %s' % test_data)
    assert test_data != 2
    
    
    