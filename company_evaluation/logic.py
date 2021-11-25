from enum import Enum

from company_evaluation.library import (
    NeuroVoiceLibrary,
    bridge_action,
    hangup_action,
)

nv = NeuroVoiceLibrary()

DEFAULT = 'default'


class Dialog(object):
    """Dialog."""

    def __init__(self, start_action):
        self.current_action = start_action
        self.end_action = start_action
        self.callback = None

    def next_step(self):
        """Control the flow of the dialog."""
        self.end_action = self.current_action
        next_action, callback = self.current_action()
        self.current_action = next_action
        self.callback = callback

    def run(self):
        """Run dialog."""
        while self.current_action is not None:
            self.next_step()


class BaseLogic(object):
    """Logic base class."""

    entities = []

    def __init__(self):
        self.transitions = {}

    @property
    def answer(self):
        """Return answer based on entities."""
        with nv.listen(entities=self.entities) as result:  # noqa: WPS110
            if not result.has_entities():
                return 'null'
            for entity in self.entities:
                value = result.entity(entity)  # noqa: WPS110
                if value is not None:
                    return f'{entity}={value}'
            return DEFAULT

    def next_action(self, answer, current_action):
        """Return next action based on answer and current action."""
        transition = self.transitions.get(answer, {})
        if transition.get(current_action, None) is None:
            return transition.get(DEFAULT, None)
        return transition.get(current_action, None)


class HangupLogic(BaseLogic):
    """Implement hangup_logic unit."""

    answers = None

    def __init__(self):
        self.transitions = {
            None: {
                DEFAULT: None,
            },
        }

    @property
    def answer(self):
        """Map entities with HangupLogic.answers."""
        return None  # noqa: WPS324

    def hangup_positive(self):
        """Run actions for hangup_positive handler.

        Return next handler and callback function.
        """
        nv.say(name='hangup_positive')
        return (
            self.next_action(self.answer, self.hangup_positive),
            hangup_action,
        )

    def hangup_negative(self):
        """Run actions for hangup_negative handler.

        Return next handler and callback function.
        """
        nv.say(name='hangup_negative')
        return (
            self.next_action(self.answer, self.hangup_negative),
            hangup_action,
        )

    def hangup_wrong_time(self):
        """Run actions for hangup_wrong_time handler.

        Return next handler and callback function.
        """
        nv.say(name='hangup_wrong_time')
        return (
            self.next_action(self.answer, self.hangup_wrong_time),
            hangup_action,
        )

    def hangup_null(self):
        """Run actions for hangup_null handler.

        Return next handler and callback function.
        """
        nv.say(name='hangup_null')
        return (
            self.next_action(self.answer, self.hangup_null),
            hangup_action,
        )


class ForwardLogic(BaseLogic):
    """Implement forward_logic unit."""

    answers = None

    def __init__(self):
        self.transitions = {
            None: {
                DEFAULT: None,
            },
        }

    @property
    def answer(self):
        """Map entities with ForwardLogic.answers."""
        return None  # noqa: WPS324

    def forward(self):
        """Run actions for forward handler and return next handler."""
        nv.say(name='forward')
        return (
            self.next_action(self.answer, self.forward),
            bridge_action,
        )


class MainLogic(BaseLogic):  # noqa: WPS214
    """Implement hello_logic unit."""

    entities = [
        'recommendation_score',
        'recommendation',
        'repeat',
        'wrong_time',
        'question',
    ]
    answers = Enum(
        value='answers',
        names=(
            'null default range_from_0_to_8 range_from_9_to_10 no maybe yes '
            'repeat dont_know busy question'
        ),
    )

    def __init__(self, hangup_logic, forward_logic):
        self.transitions = {
            MainLogic.answers.null: {
                DEFAULT: self.recommend_null,
                self.recommend_null: hangup_logic.hangup_null,
            },
            MainLogic.answers.default: {
                DEFAULT: self.recommend_default,
                self.recommend_default: hangup_logic.hangup_null,
            },
            MainLogic.answers.range_from_0_to_8: {
                DEFAULT: hangup_logic.hangup_negative,
            },
            MainLogic.answers.range_from_9_to_10: {
                DEFAULT: hangup_logic.hangup_positive,
            },
            MainLogic.answers.no: {
                DEFAULT: self.recommend_score_negative,
            },
            MainLogic.answers.maybe: {
                DEFAULT: self.recommend_score_neutral,
            },
            MainLogic.answers.yes: {
                DEFAULT: self.recommend_score_positive,
            },
            MainLogic.answers.repeat: {
                DEFAULT: self.recommend_repeat,
            },
            MainLogic.answers.dont_know: {
                DEFAULT: self.recommend_repeat_2,
            },
            MainLogic.answers.busy: {
                DEFAULT: hangup_logic.hangup_wrong_time,
            },
            MainLogic.answers.question: {
                DEFAULT: forward_logic.forward,
            },
        }

    @property
    def answer(self):
        """Map entities with MainLogic.answers."""
        answer = super().answer
        if answer.startswith('recommendation_score='):
            _, value = super().answer.split('=')  # noqa: WPS110
            answer = 'recommendation_score[9..]'
            if int(value) in range(0, 9):
                answer = 'recommendation_score[0..8]'

        return {
            'null': MainLogic.answers.null,
            DEFAULT: MainLogic.answers.default,
            'recommendation_score[0..8]': MainLogic.answers.range_from_0_to_8,
            'recommendation_score[9..]': MainLogic.answers.range_from_9_to_10,
            'recommendation=negative': MainLogic.answers.no,
            'recommendation=neutral': MainLogic.answers.maybe,
            'recommendation=positive': MainLogic.answers.yes,
            'repeat=True': MainLogic.answers.repeat,
            'recommendation=dont_know': MainLogic.answers.dont_know,
            'wrong_time=True': MainLogic.answers.busy,
            'question=True': MainLogic.answers.question,
        }.get(answer, MainLogic.answers.default)

    def recommend_main(self):
        """Run actions for recommend_main handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_main')
        return self.next_action(self.answer, self.recommend_main), None

    def recommend_repeat(self):
        """Run actions for recommend_repeat handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_repeat')
        return self.next_action(self.answer, self.recommend_repeat), None

    def recommend_repeat_2(self):  # noqa: WPS114
        """Run actions for recommend_repeat_2 handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_repeat_2')
        return self.next_action(self.answer, self.recommend_repeat_2), None

    def recommend_score_negative(self):
        """Run actions for recommend_score_negative handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_score_negative')
        return (
            self.next_action(self.answer, self.recommend_score_negative),
            None,
        )

    def recommend_score_neutral(self):
        """Run actions for recommend_score_neutral handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_score_neutral')
        return (
            self.next_action(self.answer, self.recommend_score_neutral),
            None,
        )

    def recommend_score_positive(self):
        """Run actions for recommend_score_positive handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_score_positive')
        return (
            self.next_action(self.answer, self.recommend_score_positive),
            None,
        )

    def recommend_null(self):
        """Run actions for recommend_null handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_null')
        return self.next_action(self.answer, self.recommend_null), None

    def recommend_default(self):
        """Run actions for recommend_default handler.

        Return next handler and callback function.
        """
        nv.say(name='recommend_default')
        return self.next_action(self.answer, self.recommend_default), None


class HelloLogic(BaseLogic):
    """Implement hello_logic unit."""

    entities = ['confirm', 'wrong_time', 'repeat']
    answers = Enum(
        value='answers',
        names='null default yes no busy repeat',
    )

    def __init__(self, main_logic, hangup_logic):
        self.transitions = {
            HelloLogic.answers.null: {
                DEFAULT: self.hello_null,
                self.hello_null: hangup_logic.hangup_null,
            },
            HelloLogic.answers.default: {
                DEFAULT: main_logic.recommend_main,
            },
            HelloLogic.answers.yes: {
                DEFAULT: main_logic.recommend_main,
            },
            HelloLogic.answers.no: {
                DEFAULT: hangup_logic.hangup_wrong_time,
            },
            HelloLogic.answers.busy: {
                DEFAULT: hangup_logic.hangup_wrong_time,
            },
            HelloLogic.answers.repeat: {
                DEFAULT: self.hello_repeat,
            },
        }

    @property
    def answer(self):
        """Map entities with HelloLogic.answers."""
        return {
            'null': HelloLogic.answers.null,
            DEFAULT: HelloLogic.answers.default,
            'confirm=True': HelloLogic.answers.yes,
            'confirm=False': HelloLogic.answers.no,
            'wrong_time=True': HelloLogic.answers.busy,
            'repeat=True': HelloLogic.answers.repeat,
        }.get(super().answer, HelloLogic.answers.default)

    def hello(self):
        """Run actions for hello handler.

        Return next handler and callback function.
        """
        nv.say(name='hello')
        return self.next_action(self.answer, self.hello), None

    def hello_repeat(self):
        """Run actions for hello_repeat handler.

        Return next handler and callback function.
        """
        nv.say(name='hello_repeat')
        return self.next_action(self.answer, self.hello_repeat), None

    def hello_null(self):
        """Run actions for hello_null handler.

        Return next handler and callback function.
        """
        nv.say(name='hello_null')
        return self.next_action(self.answer, self.hello_null), None
