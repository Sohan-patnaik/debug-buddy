import typer
from routes.debug import router as debug_router

app = typer.Typer(help="Debug Buddy — AI-powered CLI debugger")
app.add_typer(debug_router, name="debug-buddy")

if __name__ == "__main__":
    app()