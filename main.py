from time import perf_counter

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine import Match
from storage import Leaderboard, QuestionBank

console = Console()


def hand_over(player):
    console.clear()
    console.print(
        f"\n[bold magenta]Hand over to {escape(player)}![/bold magenta]"
    )
    input(f"{player}, press Enter when ready...")

def ask(player, question, round_number):
    console.clear()
    console.print(
        Panel(
            f"[bold cyan]Round {round_number}[/bold cyan]\n\n"
            f"{question.text}",
            title="QUIZ GAME"
        )
    )
    for letter, option in zip("ABCD", question.options):
        console.print(f"{letter}: {option}")
    start_time = perf_counter()
    user_answer = input(f"\n{player}, your choice: ").strip().upper()
    elapsed = perf_counter() - start_time
    return user_answer, elapsed

def show_round_results(match, results, question):
    console.clear()
    console.print(
        Panel(
            f"[bold cyan]Round {match.rounds} Results[/bold cyan]\n\n"
            f"{question.text}",
            title="QUIZ GAME"
        )
    )
    for player in match.players:
        result = results[player]
        _, elapsed = match.answer_of(player)

        if result.status == "correct":
            console.print(
                f"{escape(player)}: [bold green]{result.status}[/bold green] | "
                f"Score: +{result.score} | "
                f"Time: {elapsed:.2f}s"
            )
        elif result.status == "too_late":
            console.print(
                f"{escape(player)}: [bold yellow]{result.status}[/bold yellow] | "
                f"Score: +{result.score} | "
                f"Time: {elapsed:.2f}s"
            )
        elif result.status == "incorrect":
            console.print(
                f"{escape(player)}: [bold red]{result.status}[/bold red] | "
                f"Score: +{result.score} | "
                f"Time: {elapsed:.2f}s"
            )
    for player in match.players:
        console.print(
            f"{escape(player)}: Total Score: {match.score_of(player)}"
        )

    input("\nPress Enter to continue...")


def show_final_results(match):
    console.clear()
    console.print(
        Panel(
            "[bold cyan]Final Results[/bold cyan]",
            title="QUIZ GAME"
        )
    )
    for player in match.players:
        console.print(
            f"{escape(player)}: Total Score: {match.score_of(player)}"
        )
    winner = match.winner()
    if winner is None:
        console.print(
            Panel(
                "[bold yellow]It's a Draw![/bold yellow]"
            )
        )
    else:
        console.print(
            Panel(
                f"[bold green]Winner: {escape(winner)}[/bold green]"
            )
        )


def player_name(number, other_name=None):
    while True:
        name = input(f"Enter name for Player {number}: ").strip()
        if not name:
            console.print("Enter a non-empty name.")
        elif name == other_name:
            console.print("Choose a different name for each player.")
        else:
            return name


def main():
    questions = QuestionBank()
    console.print("[bold cyan]Welcome to the Quiz Game![/bold cyan]\n")
    name1 = player_name(1)
    name2 = player_name(2, name1)
    match = Match([name1, name2], questions.pick(5))

    while not match.is_over():
        question = match.start_round()
        for player in match.players:
            hand_over(player)
            choice, elapsed = ask(player, question, match.rounds)
            match.submit(player, choice, elapsed)
        show_round_results(match, match.results_round(), question)
    show_final_results(match)

    leaderboard = Leaderboard()
    leaderboard.record(
        match.winner(), name1, name2, match.score_of(name1), match.score_of(name2)
    )
    table = Table(title="LEADERBOARD")
    table.add_column("Player", style="cyan")
    table.add_column("Total Score", justify="right")
    table.add_column("Wins", justify="right")
    table.add_column("Draws", justify="right")
    for player, totals in leaderboard.top():
        table.add_row(
            Text(player), str(totals["score"]), str(totals["wins"]), str(totals["draws"])
        )
    console.print(table)


if __name__ == "__main__":
    main()
