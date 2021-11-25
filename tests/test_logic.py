from company_evaluation.logic import (
    Dialog,
    ForwardLogic,
    HangupLogic,
    HelloLogic,
    MainLogic,
    nv,
)


def fake_say(name, val=None):
    """Fake say for nv object."""
    return name


class FakeNeuroNluRecognitionResult(object):
    """Fake NeuroNluRecognitionResult."""

    def __init__(self, entities):
        self.entities = entities

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def entity(self, name):  # noqa: D102
        return self.entities.get(name, None)

    def has_entities(self):  # noqa: D102
        return bool(self.entities)


def fake_listen(recognition_entities):
    """Fake listen for nv.listen."""
    def listen(*args, **kwargs):  # noqa: WPS430
        return FakeNeuroNluRecognitionResult(entities=recognition_entities)
    return listen


nv.say = fake_say

NULL = {}  # noqa: WPS407
DEFAULT = {'dont_recognition': True}  # noqa: WPS407
BUSY = {'wrong_time': True}  # noqa: WPS407
REPEAT = {'repeat': True}  # noqa: WPS407


def correct_transition_was_made(dialog, start_action, cases):
    """Test all transitions for start_action."""
    for recognition_entities, action in cases:
        dialog.current_action = start_action
        nv.listen = fake_listen(recognition_entities)
        dialog.next_step()
        assert dialog.current_action == action
    return True


def test_dialog():
    """Test Dialog class."""
    hangup_logic = HangupLogic()
    forward_logic = ForwardLogic()
    main_logic = MainLogic(hangup_logic, forward_logic)
    hello_logic = HelloLogic(main_logic, hangup_logic)

    dialog = Dialog(hello_logic.hello)
    assert dialog.current_action == hello_logic.hello


def test_hello_logic():
    """Test HelloLogic class."""
    hangup_logic = HangupLogic()
    forward_logic = ForwardLogic()
    main_logic = MainLogic(hangup_logic, forward_logic)
    hello_logic = HelloLogic(main_logic, hangup_logic)

    common_cases = {
        'null': (NULL, hello_logic.hello_null),
        'default': (DEFAULT, main_logic.recommend_main),
        'yes': ({'confirm': True}, main_logic.recommend_main),
        'no': ({'confirm': False}, hangup_logic.hangup_wrong_time),
        'busy': (BUSY, hangup_logic.hangup_wrong_time),
        'repeat': (REPEAT, hello_logic.hello_repeat),
    }

    dialog = Dialog(hello_logic.hello)

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        hello_logic.hello,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        hello_logic.hello_repeat,
        cases.values(),
    )

    cases = common_cases.copy()
    cases['null'] = (NULL, hangup_logic.hangup_null)
    assert correct_transition_was_made(
        dialog,
        hello_logic.hello_null,
        cases.values(),
    )


def test_main_logic():  # noqa: WPS218
    """Test MainLogic class."""
    hangup_logic = HangupLogic()
    forward_logic = ForwardLogic()
    main_logic = MainLogic(hangup_logic, forward_logic)

    common_cases = {
        'null': (NULL, main_logic.recommend_null),
        'default': (DEFAULT, main_logic.recommend_default),
        0: ({'recommendation_score': 0}, hangup_logic.hangup_negative),
        1: ({'recommendation_score': 1}, hangup_logic.hangup_negative),
        2: ({'recommendation_score': 2}, hangup_logic.hangup_negative),
        3: ({'recommendation_score': 3}, hangup_logic.hangup_negative),
        4: ({'recommendation_score': 4}, hangup_logic.hangup_negative),
        5: ({'recommendation_score': 5}, hangup_logic.hangup_negative),
        6: ({'recommendation_score': 6}, hangup_logic.hangup_negative),
        7: ({'recommendation_score': 7}, hangup_logic.hangup_negative),
        8: ({'recommendation_score': 8}, hangup_logic.hangup_negative),
        9: ({'recommendation_score': 9}, hangup_logic.hangup_positive),
        10: ({'recommendation_score': 10}, hangup_logic.hangup_positive),
        11: ({'recommendation_score': 11}, hangup_logic.hangup_positive),
        'no': (
            {'recommendation': 'negative'},
            main_logic.recommend_score_negative,
        ),
        'maybe': (
            {'recommendation': 'neutral'}, main_logic.recommend_score_neutral,
        ),
        'yes': (
            {'recommendation': 'positive'},
            main_logic.recommend_score_positive,
        ),
        'dont_know': (
            {'recommendation': 'dont_know'}, main_logic.recommend_repeat_2,
        ),
        'repeat': (REPEAT, main_logic.recommend_repeat),
        'busy': (BUSY, hangup_logic.hangup_wrong_time),
        'question': ({'question': True}, forward_logic.forward),
    }

    dialog = Dialog(main_logic.recommend_main)

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_main,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_repeat,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_repeat_2,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_score_negative,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_score_neutral,
        cases.values(),
    )

    cases = common_cases.copy()
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_score_positive,
        cases.values(),
    )

    cases = common_cases.copy()
    cases['null'] = (NULL, hangup_logic.hangup_null)
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_null,
        cases.values(),
    )

    cases = common_cases.copy()
    cases['default'] = (DEFAULT, hangup_logic.hangup_null)
    assert correct_transition_was_made(
        dialog,
        main_logic.recommend_default,
        cases.values(),
    )


def test_hangup_logic():
    """Test HangupLogic class."""
    hangup_logic = HangupLogic()

    dialog = Dialog(hangup_logic.hangup_positive)
    dialog.next_step()
    assert dialog.current_action is None

    dialog.current_action = hangup_logic.hangup_negative
    dialog.next_step()
    assert dialog.current_action is None

    dialog.current_action = hangup_logic.hangup_wrong_time
    dialog.next_step()
    assert dialog.current_action is None

    dialog.current_action = hangup_logic.hangup_null
    dialog.next_step()
    assert dialog.current_action is None


def test_forward_logic():
    """Test ForwardLogic class."""
    forward_logic = ForwardLogic()
    dialog = Dialog(forward_logic.forward)
    dialog.next_step()
    assert dialog.current_action is None
