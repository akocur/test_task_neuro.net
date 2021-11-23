
class NeuroVoiceLibrary:
    def say(self, name, val=None):
        pass

    def listen(self, entities):
        return NeuroNluRecognitionResult()


class NeuroNluRecognitionResult():
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def entity(self, name):
        pass
    
    def has_entities(self):
        pass


def hangup_action():
    pass

def bridge_action():
    pass