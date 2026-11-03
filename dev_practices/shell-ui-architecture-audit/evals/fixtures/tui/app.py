"""Textual shell for the ops console."""
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, ListView, ListItem, Label, Static


class OpsConsole(App):
    CSS = """
    #nav { width: 24; background: #1e1b4b; color: #ffffff; }
    #body { padding: 1 2; }
    """
    BINDINGS = [Binding("q", "quit", "Quit"), Binding("d", "toggle_dark", "Dark")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield ListView(ListItem(Label("Deploys")), ListItem(Label("Alerts")), id="nav")
            yield Static("select a view", id="body")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.query_one("#body", Static).update(f"{event.item.children[0].renderable}")


if __name__ == "__main__":
    OpsConsole().run()
