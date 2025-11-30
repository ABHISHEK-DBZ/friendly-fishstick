"""
Simple CLI Interface for AI Krishi Sahayak
Provides interactive command-line interface for farmers/testers
"""
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from main import KrishiSahayakCoordinator
from config import Config

console = Console()


class KrishiSahayakCLI:
    """Command-line interface for the agricultural assistant."""
    
    def __init__(self):
        self.coordinator = KrishiSahayakCoordinator()
        self.current_user = None
    
    def show_banner(self):
        """Display welcome banner."""
        banner = """
[bold green]🌱 AI KRISHI SAHAYAK 🌱[/bold green]
[cyan]Intelligent Agricultural Assistant Agent[/cyan]

Empowering Farmers with AI-Powered Crop Health Management
        """
        console.print(Panel(banner, border_style="green"))
    
    def main_menu(self):
        """Display main menu options."""
        console.print("\n[bold]Main Menu:[/bold]")
        console.print("1. 🆕 New User Registration")
        console.print("2. 👤 Login as Existing User")
        console.print("3. 📸 Diagnose Plant Disease")
        console.print("4. 📜 View Diagnosis History")
        console.print("5. 📅 View Follow-Up Schedule")
        console.print("6. ℹ️  About the System")
        console.print("7. 🚪 Exit")
        console.print()
    
    def register_user(self):
        """Register a new user."""
        console.print("\n[bold cyan]📝 New User Registration[/bold cyan]\n")
        
        user_id = Prompt.ask("Enter User ID (e.g., farmer001)")
        name = Prompt.ask("Enter your name")
        location = Prompt.ask("Enter your location (city/village)")
        phone = Prompt.ask("Enter phone number (optional)", default="")
        
        success = self.coordinator.create_user(user_id, name, location, phone)
        
        if success:
            console.print(f"\n✅ [green]User registered successfully![/green]")
            console.print(f"Welcome, {name}! Your User ID is: [bold]{user_id}[/bold]")
            self.current_user = user_id
        else:
            console.print("\n❌ [red]Registration failed. Please try again.[/red]")
    
    def login_user(self):
        """Login as existing user."""
        console.print("\n[bold cyan]🔐 User Login[/bold cyan]\n")
        user_id = Prompt.ask("Enter your User ID")
        
        # Simple check - in production, verify against database
        self.current_user = user_id
        console.print(f"\n✅ [green]Logged in as: {user_id}[/green]")
    
    async def diagnose_plant(self):
        """Diagnose plant disease."""
        if not self.current_user:
            console.print("\n⚠️  [yellow]Please login or register first![/yellow]")
            return
        
        console.print("\n[bold cyan]📸 Plant Disease Diagnosis[/bold cyan]\n")
        
        # Get image path
        image_path = Prompt.ask(
            "Enter path to plant image",
            default=str(Config.UPLOADS_DIR / "sample_leaf.jpg")
        )
        
        if not Path(image_path).exists():
            console.print(f"\n❌ [red]Image not found: {image_path}[/red]")
            console.print("Please provide a valid image path.")
            return
        
        location = Prompt.ask("Enter your location (for weather data)", default="Pune")
        context = Prompt.ask(
            "Any additional information? (e.g., 'spots appeared yesterday')",
            default=""
        )
        
        console.print("\n🔄 [yellow]Processing... This may take a moment...[/yellow]\n")
        
        try:
            # Run diagnosis
            result = await self.coordinator.diagnose_plant(
                image_path=image_path,
                user_id=self.current_user,
                location=location,
                additional_context=context
            )
            
            # Display results
            console.print("\n" + "="*60)
            console.print("[bold green]📊 DIAGNOSIS RESULTS[/bold green]")
            console.print("="*60 + "\n")
            
            # Show action plan
            action_plan = result.get("action_plan", "No action plan generated")
            console.print(action_plan)
            
            console.print("\n" + "="*60 + "\n")
            
            # Ask if they want to save
            save = Confirm.ask("Save this diagnosis to your history?", default=True)
            if save:
                console.print("✅ [green]Diagnosis saved![/green]")
            
        except Exception as e:
            console.print(f"\n❌ [red]Error during diagnosis: {e}[/red]")
            console.print("Please check your API keys in .env file.")
    
    def view_history(self):
        """View user's diagnosis history."""
        if not self.current_user:
            console.print("\n⚠️  [yellow]Please login or register first![/yellow]")
            return
        
        console.print("\n[bold cyan]📜 Your Diagnosis History[/bold cyan]\n")
        
        history = self.coordinator.get_user_history(self.current_user, limit=10)
        
        if not history:
            console.print("No diagnosis history found.")
            return
        
        # Create table
        table = Table(title="Past Diagnoses")
        table.add_column("Session", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("Plant", style="green")
        table.add_column("Disease", style="yellow")
        table.add_column("Confidence", style="blue")
        
        for record in history:
            table.add_row(
                str(record['session_id']),
                record['date'],
                record['plant_type'],
                record['disease_detected'],
                f"{record['confidence']:.1f}%"
            )
        
        console.print(table)
    
    def view_follow_ups(self):
        """View pending follow-ups."""
        if not self.current_user:
            console.print("\n⚠️  [yellow]Please login or register first![/yellow]")
            return
        
        console.print("\n[bold cyan]📅 Your Follow-Up Schedule[/bold cyan]\n")
        
        follow_ups = self.coordinator.get_follow_ups(self.current_user)
        
        if not follow_ups:
            console.print("No pending follow-ups.")
            return
        
        # Create table
        table = Table(title="Pending Follow-Ups")
        table.add_column("ID", style="cyan")
        table.add_column("Scheduled Date", style="magenta")
        table.add_column("Disease", style="yellow")
        table.add_column("Notes", style="green")
        
        for fu in follow_ups:
            table.add_row(
                str(fu['follow_up_id']),
                fu['scheduled_date'],
                fu['disease'],
                fu.get('notes', 'Check treatment progress')
            )
        
        console.print(table)
    
    def show_about(self):
        """Show information about the system."""
        about = """
[bold]AI Krishi Sahayak - Intelligent Agricultural Assistant[/bold]

[cyan]What is it?[/cyan]
A multi-agent AI system that helps farmers diagnose plant diseases,
get treatment recommendations, and manage their crops more effectively.

[cyan]How does it work?[/cyan]
1. Vision Agent: Analyzes your plant images using GPT-4o
2. Research Agent: Fetches treatment options and weather data
3. Advisory Agent: Creates simple, actionable plans
4. Memory Agent: Tracks your farm history and schedules follow-ups

[cyan]Features:[/cyan]
✅ Instant disease detection from photos
✅ Treatment recommendations (organic + chemical)
✅ Weather-based timing advice
✅ Safety guidelines
✅ Cost estimates
✅ Automated follow-ups

[cyan]Built with:[/cyan]
• Microsoft Agent Framework
• GPT-4o (Vision + Text)
• GitHub Models API
• OpenWeatherMap API

[cyan]Contact & Support:[/cyan]
GitHub: github.com/[your-username]/ai-krishi-sahayak
Track: Agents for Good - GitHub Models Hackathon

[green]Empowering Farmers with AI 🌾[/green]
        """
        console.print(Panel(about, border_style="cyan"))
    
    async def run(self):
        """Main CLI loop."""
        self.show_banner()
        
        while True:
            self.main_menu()
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                self.register_user()
            elif choice == "2":
                self.login_user()
            elif choice == "3":
                await self.diagnose_plant()
            elif choice == "4":
                self.view_history()
            elif choice == "5":
                self.view_follow_ups()
            elif choice == "6":
                self.show_about()
            elif choice == "7":
                console.print("\n[bold green]Thank you for using AI Krishi Sahayak! 🌱[/bold green]")
                console.print("Stay healthy, grow better crops! 🌾\n")
                break
            
            if choice != "7":
                Prompt.ask("\nPress Enter to continue...")
                console.clear()


async def main():
    """Entry point for CLI."""
    cli = KrishiSahayakCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
