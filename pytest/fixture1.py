from __future__ import print_function
import pytest

@pytest.fixture()
def cheese_db(request):
    print('\n[setup] cheese_db, connect to db')
    # code to connect to your db 
    a_dictionary_for_now = {'Brie': 'No.', 'Camenbert': 'Ah! We have Camenbert, yessir.'}
    def fin():
        print('\n[teardown] cheese_db finalizer, disconnect from db')
    request.addfinalizer(fin)
    return a_dictionary_for_now
 
def test_cheese_database(cheese_db):
    print('in test_cheese_database()')
    for variety in cheese_db.keys():
        print('%s : %s' % (variety, cheese_db[variety]))
 
def test_brie(cheese_db):
    print('in test_brie()')
    assert cheese_db['Brie'] == 'No.' 
 
def test_camenbert(cheese_db):
    print('in test_camenbert()')
    assert cheese_db['Camenbert'] != 'No.' 