from company_evaluation.libraries import NeuroVoiceLibrary


nv = NeuroVoiceLibrary()


class BaseLogic:
    def __init__(self):
        self.action = None
        self.entities = []

    def get_answer(self):
        with nv.listen(entities=self.entities) as r:
            answer = {
                entity: r.entity(entity) for entity in self.entities
                if r.entity(entity) is not None
            }
            answer['null'] = not r.has_entities()
            return answer

    def run(self):
        stop = self.action()
        while not stop:
            stop = self.action()


class HelloLogic(BaseLogic):
    def __init__(self):
        self.action = self.hello
        self.entities = ['confirm', 'wrong_time', 'repeat']

    def set_action(self, answer):
        if answer.get('null', False):
            if self.action == self.hello_null:                
                self.action = HangupLogic().hangup_null
            else:
                self.action = self.hello_null
        elif answer.get('confirm', False):
            self.action = MainLogic().recommend_main
        elif not answer.get('confirm', True) or answer.get('wrong_time', False):
            self.action = HangupLogic().hangup_wrong_time
        elif answer.get('repeat', False):
            self.action = self.hello_repeat
        else:
            self.action = MainLogic().recommend_main

    def hello(self):        
        nv.say(name='hello')
        answer = self.get_answer()
        self.set_action(answer)
        return False
            
    def hello_repeat(self):
        nv.say(name='hello_repeat')
        answer = self.get_answer()
        self.set_action(answer)
        return False

    def hello_null(self):
        nv.say(name='hello_null')
        answer = self.get_answer()
        self.set_action(answer)
        return False


class MainLogic(BaseLogic):
    def __init__(self):
        self.action = [self.recommend_main]
        self.entities = [
            'recommendation_score',
            'recommendation',
            'repeat',
            'wrong_time',
            'question',
        ]

    def set_action(self, answer):                
        if answer.get('null', False):        
            if self.action == self.recommend_null:
                self.action = HangupLogic().hangup_null
            else:
                self.action = self.recommend_null
        elif answer.get('recommendation_score', 10) in range(9):
            self.action = HangupLogic.hangup_negative
        elif answer.get('recommendation_score', 0) in range(9, 11):
            self.action = HangupLogic.hangup_positive
        elif answer.get('recommendation') == 'negative':
            self.action = self.recommend_score_negative
        elif answer.get('recommendation') == 'neutral':
            self.action = self.recommend_score_neutral
        elif answer.get('recommendation') == 'positive':
            self.action = self.recommend_score_positive
        elif answer.get('repeat', False):
            self.action = self.recommend_repeat
        elif answer.get('recommendation') == 'dont_know':
            self.action = self.recommend_repeat_2
        elif answer.get('wrong_time', False):
            self.action = HangupLogic.hangup_wrong_time
        elif answer.get('question', False):
            self.action = ForwardLogic.forward
        else:  # default
            if self.action == self.recommend_default:
                self.action.pop()
                self.action = HangupLogic().hangup_null
            else:
                self.action = self.recommend_default

    def recommend_main(self):
        nv.say(name='recommend_main')
        answer = self.get_answer()
        self.set_action(answer)
        return False
        
    def recommend_repeat(self):
        nv.say(name='recommend_repeat')
        answer = self.get_answer()
        self.set_action(answer)
        return False

    def recommend_repeat_2(self):
        nv.say(name='recommend_repeat_2')
        answer = self.get_answer()
        self.set_action(answer)
        return False

    def recommend_score_negative(self):
        nv.say(name='recommend_score_negative')
        answer = self.get_answer()
        self.set_action(answer)
        return False
    
    def recommend_score_neutral(self):
        nv.say(name='recommend_score_neutral')
        answer = self.get_answer()
        self.set_action(answer)
        return False
    
    def recommend_score_positive(self):
        nv.say(name='recommend_score_positive')
        answer = self.get_answer()
        self.set_action(answer)
        return False
    
    def recommend_null(self):
        nv.say(name='recommend_null')
        answer = self.get_answer()
        self.set_action(answer)
        return False

    def recommend_default(self):
        nv.say(name='recommend_default')
        answer = self.get_answer()
        self.set_action(answer)
        return False


class HangupLogic(BaseLogic):
    def __init__(self):
        self.state = [self.hangup_positive]

    def hangup_positive(self):
        nv.say(name='hangup_positive')
        return True

    def hangup_negative(self):
        nv.say(name='hangup_negative')
        return True

    def hangup_wrong_time(self):
        nv.say(name='hangup_wrong_time')
        return True

    def hangup_null(self):
        nv.say(name='hangup_null')
        return True


class ForwardLogic(BaseLogic):
    def __init__(self):
        self.state = [self.forward]

    def forward(self):
        nv.say(name='forward')
        return True
