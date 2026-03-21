#!/usr/bin/env python3
"""
GPU Job Scheduler
==================
Practice Project 3: Condition Variables, Priority Queues, Topological Sort, Graceful Shutdown

Run: python main.py
"""

from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold red]GPU Job Scheduler[/bold red]\n"
        "Practice Project 3: Condition, heapq, Topological Sort, Shutdown",
        border_style="red"
    ))
    console.print()

    try:
        from app import run
        run()
    except NotImplementedError as e:
        console.print(f"[yellow]Warning: Not yet implemented:[/yellow] {e}")
    except TypeError as e:
        if "NoneType" in str(e):
            console.print(f"[yellow]Warning: A function returned None.[/yellow]")
            console.print(f"[dim]Error: {e}[/dim]")
        else:
            raise

if __name__ == "__main__":
    main()
