"""
Demo Script - AI Krishi Sahayak System Architecture
Shows the system structure without needing API keys
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def show_architecture():
    """Display the multi-agent architecture"""
    
    console.print("\n[bold cyan]🌾 AI KRISHI SAHAYAK - MULTI-AGENT SYSTEM[/bold cyan]")
    console.print("[dim]Agricultural AI Assistant using Microsoft Agent Framework[/dim]\n")
    
    # System Overview
    overview = Panel(
        "[bold yellow]Agents for Good - GitHub Models Hackathon[/bold yellow]\n\n"
        "A multi-agent AI system that helps farmers identify and treat plant diseases.\n"
        "Uses GPT-4o for vision analysis and generates farmer-friendly action plans.\n\n"
        "[cyan]Framework:[/cyan] Microsoft Agent Framework (Preview)\n"
        "[cyan]Model:[/cyan] GPT-4o via GitHub Models\n"
        "[cyan]Architecture:[/cyan] Sequential Multi-Agent Workflow",
        title="🎯 Project Overview",
        border_style="green"
    )
    console.print(overview)
    
    # Agents Table
    table = Table(title="\n🤖 Agent Architecture", box=box.ROUNDED)
    table.add_column("Agent", style="cyan", justify="left")
    table.add_column("Role", style="yellow")
    table.add_column("Technology", style="green")
    
    table.add_row(
        "1️⃣  Vision Agent",
        "Analyzes plant images\nIdentifies diseases",
        "GPT-4o Vision\nImage Processing"
    )
    table.add_row(
        "2️⃣  Research Agent",
        "Finds treatment info\nGets weather data",
        "Web Scraping\nOpenWeatherMap API"
    )
    table.add_row(
        "3️⃣  Advisory Agent",
        "Creates action plans\nFarmer-friendly language",
        "GPT-4o\nStructured Output"
    )
    table.add_row(
        "4️⃣  Memory Agent",
        "Stores diagnosis history\nTracks follow-ups",
        "SQLite Database\nPersistent Storage"
    )
    
    console.print(table)
    
    # Workflow
    workflow = Panel(
        "[bold]Step 1:[/bold] Farmer uploads plant image 📸\n"
        "         ⬇️\n"
        "[bold]Step 2:[/bold] Vision Agent analyzes image using GPT-4o 🔍\n"
        "         ⬇️\n"
        "[bold]Step 3:[/bold] Research Agent finds treatment + weather 📚\n"
        "         ⬇️\n"
        "[bold]Step 4:[/bold] Advisory Agent creates action plan 📋\n"
        "         ⬇️\n"
        "[bold]Step 5:[/bold] Memory Agent saves diagnosis 💾\n"
        "         ⬇️\n"
        "[bold green]Result:[/bold green] Farmer receives complete treatment guide! ✅",
        title="🔄 Workflow",
        border_style="yellow"
    )
    console.print("\n")
    console.print(workflow)
    
    # Features
    features = Table.grid(padding=(0, 2))
    features.add_column(style="cyan", justify="left")
    features.add_column(style="white")
    
    features.add_row("✅", "[bold]Multi-Language Support[/bold] - English & Hindi")
    features.add_row("✅", "[bold]Weather Integration[/bold] - Location-based recommendations")
    features.add_row("✅", "[bold]Persistent Memory[/bold] - Track diagnosis history")
    features.add_row("✅", "[bold]Farmer-Friendly[/bold] - Simple language with emojis")
    features.add_row("✅", "[bold]Follow-up System[/bold] - Scheduled progress checks")
    
    console.print("\n")
    console.print(Panel(features, title="✨ Key Features", border_style="blue"))
    
    # Tech Stack
    tech = Table.grid(padding=(0, 2))
    tech.add_column(style="yellow", justify="left")
    tech.add_column(style="white")
    
    tech.add_row("🔧", "Microsoft Agent Framework (Python)")
    tech.add_row("🤖", "GPT-4o via GitHub Models")
    tech.add_row("🗄️", "SQLite for data persistence")
    tech.add_row("🌐", "OpenWeatherMap API")
    tech.add_row("🎨", "Rich for beautiful CLI")
    tech.add_row("📦", "Pillow for image processing")
    
    console.print("\n")
    console.print(Panel(tech, title="🛠️ Technology Stack", border_style="magenta"))
    
    # Setup Instructions
    setup = Panel(
        "[bold cyan]1. Get GitHub Token:[/bold cyan]\n"
        "   Visit: https://github.com/settings/tokens\n"
        "   Enable: [yellow]Models[/yellow] permission\n\n"
        "[bold cyan]2. Configure .env:[/bold cyan]\n"
        "   Edit [yellow].env[/yellow] file\n"
        "   Add: [yellow]GITHUB_TOKEN=your_token_here[/yellow]\n\n"
        "[bold cyan]3. Run the System:[/bold cyan]\n"
        "   [yellow]python cli.py[/yellow]\n\n"
        "[bold cyan]4. Upload an Image:[/bold cyan]\n"
        "   Choose option [yellow]2[/yellow] - Diagnose Plant Disease\n"
        "   Provide image path or URL",
        title="🚀 Quick Start",
        border_style="green"
    )
    console.print("\n")
    console.print(setup)
    
    # Sample Output
    sample = Panel(
        "[bold red]🦠 Disease Detected:[/bold red] Tomato Late Blight\n\n"
        "[bold yellow]🌡️ Weather Alert:[/bold yellow] High humidity (78%) - favorable for spread\n\n"
        "[bold green]💚 Treatment Plan:[/bold green]\n"
        "1. Remove affected leaves immediately\n"
        "2. Apply copper-based fungicide\n"
        "3. Improve air circulation\n"
        "4. Avoid overhead watering\n\n"
        "[bold cyan]📅 Follow-up:[/bold cyan] Check again in 3 days",
        title="📋 Sample Output",
        border_style="red"
    )
    console.print("\n")
    console.print(sample)
    
    # Project Structure
    console.print("\n[bold cyan]📁 Project Structure:[/bold cyan]\n")
    console.print("├── [yellow]agents/[/yellow]")
    console.print("│   ├── vision_agent.py       # GPT-4o image analysis")
    console.print("│   ├── research_agent.py     # Treatment research")
    console.print("│   ├── advisory_agent.py     # Action plan creation")
    console.print("│   └── memory_agent.py       # History tracking")
    console.print("├── [yellow]config.py[/yellow]               # Configuration & disease DB")
    console.print("├── [yellow]main.py[/yellow]                 # Workflow coordinator")
    console.print("├── [yellow]cli.py[/yellow]                  # Interactive interface")
    console.print("└── [yellow]requirements.txt[/yellow]        # Dependencies")
    
    # Footer
    console.print("\n")
    console.print(Panel(
        "[bold green]✅ System Ready![/bold green]\n\n"
        "All dependencies installed successfully.\n"
        "Add your GITHUB_TOKEN to [yellow].env[/yellow] and run [cyan]python cli.py[/cyan] to start!",
        border_style="green",
        box=box.DOUBLE
    ))

if __name__ == "__main__":
    show_architecture()
