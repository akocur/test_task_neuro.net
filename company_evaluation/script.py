from company_evaluation.logic import (
    Dialog,
    ForwardLogic,
    HangupLogic,
    HelloLogic,
    MainLogic,
)


def main():
    """Entry point."""
    hangup_logic = HangupLogic()
    forward_logic = ForwardLogic()
    main_logic = MainLogic(hangup_logic, forward_logic)
    hello_logic = HelloLogic(main_logic, hangup_logic)

    dialog = Dialog(hello_logic.hello)
    dialog.run()

    next_action = dialog.callback
    if next_action is not None:
        next_action()


if __name__ == '__main__':
    main()
