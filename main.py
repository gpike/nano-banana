import typer
import requests
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from nano_sdk import NanoBananaSDK

app = typer.Typer()
console = Console()

@app.command()
def create(
    subject: str = typer.Option(..., help="Path to the person/pet photo"),
    text: str = typer.Option(..., help="Text to add (e.g., 'Justin 2025')"),
    bg: str = typer.Option(None, help="Path to background image (optional, for style inspiration)"),
    clothes: str = typer.Option("Santa suit", help="Description of clothing"),
    output: str = typer.Option("final_banana.jpg", help="Output filename"),
    template: str = typer.Option("christmas_round", help="Design template: christmas_round, holiday_card, festive_scene")
):
    """
    🍌 Nano Banana CLI: Create personalized designs with AI.

    Templates:
    - christmas_round: Round design with Christmas lights border (like AI Studio example)
    - holiday_card: Traditional holiday card layout
    - festive_scene: Full festive Christmas scene
    """

    if bg and not os.path.exists(bg):
        console.print(f"[bold red]Error:[/bold red] Background not found at {bg}")
        return
    if not os.path.exists(subject):
        console.print(f"[bold red]Error:[/bold red] Subject not found at {subject}")
        return

    try:
        sdk = NanoBananaSDK()
    except ValueError as e:
        console.print(f"[bold red]Config Error:[/bold red] {e}")
        return

    with Progress(
        SpinnerColumn("dots", style="yellow"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        # 1. Generate Image with Text Integrated
        task1 = progress.add_task("[yellow]Peeling the banana (AI Processing with Text)...", total=None)
        try:
            final_path = sdk.create_design(bg, subject, text, clothes, template)
            progress.remove_task(task1)
        except Exception as e:
            console.print(f"[bold red]AI Failed:[/bold red] {e}")
            return

        # 2. Rename if output filename is different
        if final_path != output:
            try:
                os.rename(final_path, output)
                final_path = output
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Could not rename to {output}, kept as {final_path}")
                pass

    console.print(f"\n[bold green]✨ Ready![/bold green] Saved to: [underline]{final_path}[/underline]")
    if os.name == 'posix': os.system(f"open {final_path}")
    if os.name == 'nt': os.system(f"start {final_path}")

if __name__ == "__main__":
    app()
