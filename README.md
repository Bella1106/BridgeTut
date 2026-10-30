# BridgeTut

BridgeTut is a desktop **Contract Bridge tutoring application** developed as a CSC3003 capstone project at the University of Cape Town. It combines core Bridge game logic with guided bidding and play tutorials in a PySide6 interface.

The project was developed collaboratively by **Isabella Swartz, Nxedile Macu and Alonso Cupido**. This public portfolio copy preserves the original collaborative Git history while removing course assignment documents from the repository history.

## What the application does

BridgeTut supports the main stages and rules needed for guided Contract Bridge practice, including:

- card, hand, deck and player modelling
- bidding, passes, auction completion, doubles and redoubles
- contract, declarer and opening-leader determination
- card-play validation and trick resolution
- vulnerability and scoring logic
- guided bidding and guided play lessons
- parsing of text-based tutorial lesson scripts
- saved-game history and replay support
- a desktop GUI built with PySide6
- automated unit, integration and regression tests with pytest

## My contributions

My work focused primarily on the bidding, declarer and tutorial flows, together with their validation and GUI integration. The preserved commit history shows these contributions over the course of the project.

Key areas I worked on include:

- implementing bid representation, ranking, validation and recording
- pass handling and auction-completion rules
- double and redouble logic
- declarer and opening-leader logic
- dealer rotation and deal-flow fixes
- play-validation logic and integration
- guided bidding for tutorial mode
- parsing single and multi-lesson Bid + Play tutorial files
- guided tutorial play and lesson-state integration
- integrating guided bidding and play into the GUI
- regression and integration testing for the tutorial flow
- final tutorial routing and game-history handling

## Tech stack

**Python · PySide6 · pytest · Object-Oriented Programming · Git**

## Project structure

```text
BridgeTut/
├── bidding/        # bid representation and auction logic
├── card_model/     # cards, hands, decks and players
├── contract/       # contract model and contract determination
├── game_history/   # saved-game records and history management
├── game_logic/     # dealing, scoring, tutorials, validation and trick logic
├── gui/            # PySide6 application interface
├── bbo/            # sample hand-record data used by parser functionality
├── tests/          # unit, integration and regression tests
└── README.md
```

## Run locally

Use a recent Python 3 version.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m gui.main
```

## Run the tests

```bash
python -m pytest
```

The test suite covers the core card model, bidding and contract logic, dealing, declarer logic, scoring, play validation, tutorial parsing and play, persistence, and GUI behaviour.

## Collaboration and history

This was a three-person capstone project, so the repository intentionally preserves the original authorship, branches, merge history and commit messages. That history provides a more accurate view of how the application evolved and which parts were developed by each contributor than a single final upload would.

## Portfolio note

This repository is a portfolio-safe copy of the original student project. University assignment PDF/DOCX files have been removed from the complete Git history. The application source code and collaborative development history have otherwise been retained, apart from a small publication cleanup to improve setup documentation and correct an inconsistent tutorial test fixture.
