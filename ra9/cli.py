"""
RA9 Command Line Interface.

This module provides the main CLI interface for RA9.
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.config import get_config, Config
from .core.logger import setup_logging, get_logger
from .core.engine import run_ra9_cognitive_engine
from .core.cli_workflow_engine import run_cli_workflow
from .memory.memory_manager import get_memory_manager, retrieve_memory_snippets


console = Console()
logger = get_logger("ra9.cli")


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), 
              default="INFO", help="Set log level")
@click.option("--config-file", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, debug: bool, log_level: str, config_file: Optional[str]):
    """RA9 - Ultra-Deep Cognitive Engine CLI."""
    
    # Setup logging
    setup_logging(log_level=log_level, enable_json=debug)
    
    # Load config
    config = get_config()
    if config_file:
        # TODO: Implement config file loading
        pass
    
    if debug:
        config.debug = True
        config.dev_mode = True
    
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["debug"] = debug


@cli.command()
@click.option("--query", "-q", required=True, help="Query to process")
@click.option("--mode", "-m", type=click.Choice(["concise", "detailed", "creative", "analytical"]), 
              default="concise", help="Processing mode")
@click.option("--iterations", "-i", type=int, default=1, help="Number of iterations")
@click.option("--memory", is_flag=True, help="Enable memory storage")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", 
              help="Output format")
@click.pass_context
def process(ctx, query: str, mode: str, iterations: int, memory: bool, output_format: str):
    """Process a single query."""
    
    config = ctx.obj["config"]
    logger = get_logger("ra9.cli.process")
    
    if not config.is_configured():
        console.print("[red]Error: No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY.[/red]")
        sys.exit(1)
    
    # Create job payload
    job_payload = {
        "jobId": str(uuid.uuid4()),
        "text": query,
        "mode": mode,
        "loopDepth": iterations,
        "allowMemoryWrite": memory,
        "userId": "cli_user"
    }
    
    try:
        if output_format == "json":
            # Use JSON output mode
            result = run_cli_workflow(job_payload)
            print(json.dumps(result, indent=2))
        else:
            # Use interactive mode
            console.print(Panel(f"[bold blue]Processing Query:[/bold blue] {query}"))
            console.print(f"[dim]Mode: {mode}, Iterations: {iterations}, Memory: {memory}[/dim]")
            
            result = run_cli_workflow(job_payload)
            
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                sys.exit(1)
            
            if "final_answer" in result:
                console.print(Panel(f"[bold green]Result:[/bold green]\n{result['final_answer']}"))
            else:
                console.print("[yellow]No result generated[/yellow]")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode."""
    
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]Error: No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY.[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]RA9 Ultra-Deep Cognitive Engine[/bold blue]\n"
        "[dim]Interactive Mode - Type 'exit' to quit[/dim]",
        border_style="blue"
    ))
    
    while True:
        try:
            query = click.prompt("\n[bold]Query[/bold]", type=str)
            
            if query.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not query.strip():
                continue
            
            # Process query
            job_payload = {
                "jobId": str(uuid.uuid4()),
                "text": query,
                "mode": "concise",
                "loopDepth": 1,
                "allowMemoryWrite": True,
                "userId": "interactive_user"
            }
            
            result = run_cli_workflow(job_payload)
            
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
            elif "final_answer" in result:
                console.print(f"\n[green]{result['final_answer']}[/green]")
            else:
                console.print("[yellow]No result generated[/yellow]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.pass_context
def config_info(ctx):
    """Show configuration information."""
    
    config = ctx.obj["config"]
    
    info = {
        "API Keys": {
            "Gemini": "✓" if config.gemini_api_key else "✗",
            "OpenAI": "✓" if config.openai_api_key else "✗",
        },
        "Memory": {
            "Enabled": config.memory_enabled,
            "Path": str(config.memory_path),
            "Max Entries": config.max_memory_entries,
        },
        "Agents": {
            "Max Iterations": config.max_iterations,
            "Default Mode": config.default_mode,
            "Reflection Enabled": config.enable_reflection,
        },
        "Logging": {
            "Level": config.log_level,
            "File": str(config.log_file) if config.log_file else "None",
        }
    }
    
    console.print(Panel.fit(
        Text.assemble(
            ("RA9 Configuration\n\n", "bold blue"),
            *[f"{section}:\n" + "\n".join(f"  {k}: {v}" for k, v in data.items()) + "\n" 
              for section, data in info.items()]
        ),
        title="Configuration",
        border_style="green"
    ))


@cli.command()
@click.option("--port", "-p", type=int, default=8000, help="Port to run server on")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to")
@click.pass_context
def server(ctx, port: int, host: str):
    """Start the web server."""
    
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]Error: No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY.[/red]")
        sys.exit(1)
    
    try:
        import uvicorn
        from .server import app
        
        console.print(f"[green]Starting RA9 server on {host}:{port}[/green]")
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except ImportError:
        console.print("[red]Error: FastAPI and Uvicorn not installed. Install with: pip install fastapi uvicorn[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        sys.exit(1)


@cli.group()
@click.pass_context
def memory(ctx):
    """Memory management commands."""
    pass


@memory.command("search")
@click.option("--query", "query", required=True)
@click.option("--k", type=int, default=6)
def memory_search(query: str, k: int):
    hits = retrieve_memory_snippets(query, k=k)
    console.print(Panel("\n".join(hits) or "No hits", title="Memory Search"))


@memory.command("write")
@click.option("--text", required=True)
@click.option("--type", "mtype", default="episodic")
@click.option("--tags", multiple=True)
def memory_write(text: str, mtype: str, tags: tuple[str, ...]):
    mm = get_memory_manager()
    mem_id = mm.write_memory(mtype, text, tags=list(tags), importance=0.6, consent=True)
    console.print(f"[green]Wrote memory:[/green] {mem_id}")


@memory.command("delete")
@click.option("--id", "mem_id", required=True)
def memory_delete(mem_id: str):
    mm = get_memory_manager()
    c = mm.conn.cursor()
    c.execute("DELETE FROM embeddings WHERE memory_id=?", (mem_id,))
    c.execute("DELETE FROM memory_items WHERE id=?", (mem_id,))
    mm.conn.commit()
    console.print(f"[yellow]Deleted:[/yellow] {mem_id}")


@memory.command("rebuild-index")
def memory_rebuild_index():
    mm = get_memory_manager()
    n = mm.rebuild_index()
    console.print(f"[green]Rebuilt FAISS with {n} vectors")


@memory.command("consolidate")
def memory_consolidate():
    from .memory.jobs import consolidate_once
    n = consolidate_once()
    console.print(f"[green]Created {n} semantic facts")


@memory.command("prune")
def memory_prune():
    from .memory.jobs import prune_once
    n = prune_once()
    console.print(f"[yellow]Pruned {n} episodic items")


@memory.group("wm")
def memory_wm():
    """Working memory subcommands."""
    pass


@memory_wm.command("get")
@click.option("--user", "user_id", required=True)
@click.option("--cap", type=int, default=7)
def memory_wm_get(user_id: str, cap: int):
    mm = get_memory_manager()
    console.print("\n".join(mm.wm_get(user_id, cap=cap)) or "<empty>")


@memory_wm.command("add")
@click.option("--user", "user_id", required=True)
@click.option("--entry", "entries", multiple=True)
@click.option("--cap", type=int, default=7)
def memory_wm_add(user_id: str, entries: tuple[str, ...], cap: int):
    mm = get_memory_manager()
    mm.wm_add_entries(user_id, list(entries), cap=cap)
    console.print("[green]OK")


@memory_wm.command("clear")
@click.option("--user", "user_id", required=True)
def memory_wm_clear(user_id: str):
    mm = get_memory_manager()
    n = mm.wm_clear(user_id)
    console.print(f"[yellow]Cleared {n} entries")


@memory.command("export")
@click.option("--session-id", "session_id", default=None)
def memory_export(session_id: Optional[str]):
    mm = get_memory_manager()
    if session_id:
        events = mm.get_session_events(session_id)
    else:
        events = mm.get_tail(k=100)
    print(json.dumps(events, indent=2))


@memory.command("stats")
def memory_stats():
    # Basic counters from audit_log
    mm = get_memory_manager()
    c = mm.conn.cursor()
    totals = {
        "writes": c.execute("SELECT COUNT(*) FROM audit_log WHERE action='write_memory'").fetchone()[0],
        "semantic": c.execute("SELECT COUNT(*) FROM semantic_facts").fetchone()[0],
        "events": c.execute("SELECT COUNT(*) FROM episodic_events").fetchone()[0],
    }
    console.print(Panel(json.dumps(totals, indent=2), title="Memory Stats"))


@memory.command("maintain")
def memory_maintain():
    from .memory.jobs import scheduled_maintenance
    summary = scheduled_maintenance()
    console.print(Panel(json.dumps(summary, indent=2), title="Maintenance Summary"))


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
