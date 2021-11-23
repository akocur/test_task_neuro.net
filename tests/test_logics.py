from company_evaluation.logics import HelloLogic
from company_evaluation.logics import nv
from company_evaluation.libraries import NeuroNluRecognitionResult




def fake_say(name):
    return name

def fake_listen():
    nr = NeuroNluRecognitionResult()
    nr.has_entities
    return 

def fake_entity(name):
    pass

def fake_has_entities():
    pass

nv.say = fake_say
nv.listen = fake_listen

# nr = NeuroNluRecognitionResult()
# nr.entity = fake_entity
# nr.has_entities = fake_has_entities

"""
Проверить:
1. Нужное ли вызывается приглашение
2. Правильность перехода
"""

def test_hello():
    hello_logic = HelloLogic()
    assert hello_logic.action.pop() == hello_logic.hello
    # hello_logic.hello()
    # hello_logic.say() == nv.say()
    # hello_logic.answer = None
    
    # assert hello_logic.state == hello_logic.hello_null

    # assert hello_logic.state == 
