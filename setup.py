"""
Quick Setup Helper
Checks configuration and provides setup instructions
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

console = Console()

def check_setup():
    """Check if system is properly configured"""
    
    console.print("\n[bold cyan]🔧 AI Krishi Sahayak - Setup Check[/bold cyan]\n")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[red]❌ .env file not found[/red]")
        console.print("   Creating from template...")
        import shutil
        shutil.copy(".env.example", ".env")
        console.print("[green]✅ .env file created[/green]\n")
    
    # Load environment
    load_dotenv()
    
    # Check GitHub token
    github_token = os.getenv("GITHUB_TOKEN", "")
    
    if not github_token or github_token == "your_github_token_here":
        console.print("[yellow]⚠️  GitHub Token not configured[/yellow]\n")
        
        setup_panel = Panel(
            "[bold]To use this system, you need a GitHub Token:[/bold]\n\n"
            "[cyan]Step 1:[/cyan] Visit https://github.com/settings/tokens\n"
            "[cyan]Step 2:[/cyan] Click 'Generate new token (classic)'\n"
            "[cyan]Step 3:[/cyan] Enable the [yellow]'Models'[/yellow] permission\n"
            "[cyan]Step 4:[/cyan] Copy the generated token\n\n"
            "[bold yellow]Would you like to add it now?[/bold yellow]",
            title="🔑 GitHub Token Required",
            border_style="yellow"
        )
        console.print(setup_panel)
        
        response = Prompt.ask(
            "\n[cyan]Do you have a GitHub token ready?[/cyan]",
            choices=["yes", "no", "skip"],
            default="no"
        )
        
        if response == "yes":
            token = Prompt.ask("[cyan]Enter your GitHub token[/cyan]", password=True)
            
            # Update .env file
            with open(".env", "r") as f:
                content = f.read()
            
            content = content.replace(
                "GITHUB_TOKEN=your_github_token_here",
                f"GITHUB_TOKEN={token}"
            )
            
            with open(".env", "w") as f:
                f.write(content)
            
            console.print("\n[green]✅ Token saved to .env file![/green]")
            console.print("\n[bold cyan]Starting the system...[/bold cyan]\n")
            
            # Import and run CLI
            from cli import main
            main()
            
        elif response == "skip":
            console.print("\n[yellow]⚠️  Skipping for now. Add token to .env file manually.[/yellow]")
            console.print("\nEdit the .env file and replace:")
            console.print("[dim]GITHUB_TOKEN=your_github_token_here[/dim]")
            console.print("with your actual token.\n")
        else:
            console.print("\n[blue]ℹ️  No problem! Here's how to get one:[/blue]")
            console.print("\n1. Go to: [cyan]https://github.com/settings/tokens[/cyan]")
            console.print("2. Click: [yellow]Generate new token (classic)[/yellow]")
            console.print("3. Name it: [yellow]AI Krishi Sahayak[/yellow]")
            console.print("4. Enable: [yellow]Models[/yellow] permission")
            console.print("5. Click: [yellow]Generate token[/yellow]")
            console.print("6. Copy the token and run this script again!\n")
            
    else:
        console.print("[green]✅ GitHub Token configured[/green]")
        console.print("\n[bold cyan]Starting the system...[/bold cyan]\n")
        
        # Import and run CLI
        from cli import main
        main()

if __name__ == "__main__":
    check_setup()
