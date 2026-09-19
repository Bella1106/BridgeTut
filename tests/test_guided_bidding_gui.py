from pathlib import Path

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from bidding.bid import Bid, Denomination
from bidding.bidding_system import SpecialCall
from card_model.player import Position
from game_logic.guided_bidding import (
    GuidedBiddingLesson,
    GuidedBiddingState,
)
from game_logic.tutorial_parser import (
    parse_bid_and_play_lessons,
)
from gui.bidding_page import BiddingPage


def get_game_one():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    lessons = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )

    return lessons[0]


def make_page():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    data = get_game_one()

    guided_lesson = GuidedBiddingLesson(
        dealer=data.dealer,
        script=data.auction,
        user_seat=Position.SOUTH,
    )

    state = GuidedBiddingState(
        guided_lesson
    )

    page = BiddingPage(
        guided_bidding_state=state,
        tutorial_lesson_data=data,
    )

    return page, state, data


def test_guided_page_uses_sponsor_dealer():
    page, state, data = make_page()

    assert page.dealer == data.dealer


def test_guided_page_uses_sponsor_vulnerability():
    page, state, data = make_page()

    assert page.vulnerability == data.vulnerability


def test_guided_page_uses_same_bidding_system():
    page, state, data = make_page()

    assert page.bidding_system is state.bidding_system


def test_guided_page_stops_for_south_turn():
    page, state, data = make_page()

    assert state.current_player == Position.SOUTH
    assert state.is_user_turn()


def test_wrong_south_bid_does_not_advance():
    page, state, data = make_page()

    calls_before = state.calls_made

    wrong_bid = Bid(
        7,
        Denomination.NO_TRUMP,
    )

    page.on_bid_clicked(wrong_bid)

    assert state.calls_made == calls_before
    assert state.current_player == Position.SOUTH


def test_correct_south_bid_advances_lesson():
    page, state, data = make_page()

    expected = state.expected_call

    assert isinstance(expected, Bid)

    calls_before = list(state.calls_made)

    page.on_bid_clicked(expected)

    assert len(state.calls_made) > len(calls_before)

def test_completed_guided_auction_emits_handoff():
    page, state, data = make_page()

    received = []

    page.guided_auction_finished.connect(
        lambda lesson_data: received.append(lesson_data)
    )

    while not state.is_complete():
        if state.is_user_turn():
            expected = state.expected_call

            if expected is None:
                page.on_pass_clicked()

            elif expected == SpecialCall.DOUBLE:
                page.on_double_clicked()

            elif expected == SpecialCall.REDOUBLE:
                page.on_redouble_clicked()

            else:
                page.on_bid_clicked(expected)

    assert state.is_complete()
    assert page.auction_completed
    assert received == [data]

def test_mode_one_handoff_reaches_play_page():
    data = get_game_one()

    window = MainWindow()

    window.start_bid_and_play_lesson(
        data
    )

    state = (
        window.bidding_page
        .guided_bidding_state
    )

    while not state.is_complete():

        if state.is_user_turn():

            expected = state.expected_call

            if expected is None:
                window.bidding_page.on_pass_clicked()

            elif expected == SpecialCall.DOUBLE:
                window.bidding_page.on_double_clicked()

            elif expected == SpecialCall.REDOUBLE:
                window.bidding_page.on_redouble_clicked()

            else:
                window.bidding_page.on_bid_clicked(
                    expected
                )

    assert window.play_data is not None

    assert (
        window.play_data["lesson_state"]
        is not None
    )

    assert (
        window.play_data["declarer"]
        == Position.SOUTH
    )

    assert (
        window.play_data["lesson_state"]
        .lesson.opening_leader
        == Position.WEST
    )