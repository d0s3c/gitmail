import time
import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box

console = Console()

def get_centered_input(prompt_text):
    console.print(Align.center(f"\n[bold green]?[/bold green] {prompt_text}"))
    return console.input(f"{' ' * (console.width // 2 - 2)}[bold cyan]>[/bold cyan] ").strip()

def print_banner():
    banner_text = """
                                       
                                       
 ▄▄▄▄ ▄▄ ▄▄▄▄▄▄ ▄▄   ▄▄  ▄▄▄  ▄▄ ▄▄    
██ ▄▄ ██   ██   ██▀▄▀██ ██▀██ ██ ██    
  ▀███▀ ██   ██   ██   ██ ██▀██ ██ ██▄▄▄ 
                                        
                                                       
    ::: EMAIL RECONNAISSANCE TOOL :::
    """
    panel = Panel(
        Text(banner_text, justify="center", style="bold cyan"),
        border_style="blue",
        padding=(1, 2),
        title="[bold white]v2.0[/bold white]",
        subtitle="[dim]Github Intelligence Gatherer[/dim]",
        width=70
    )
    console.print(Align.center(panel))

def fetch_commits(username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    params = {'per_page': 20} 
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 404:
            return None, "err_not_found"
        elif response.status_code == 403:
            return None, "err_rate_limit"
        elif response.status_code != 200:
            return None, f"err_{response.status_code}"
        return response.json(), "success"
    except Exception as e:
        return None, str(e)

def extract_emails(commits):
    results = {}
    
    for item in commits:
        commit = item.get('commit', {})
        author = commit.get('author', {})
        name = author.get('name', 'Unknown')
        email = author.get('email', '')
        
        if email and "noreply.github.com" not in email:
            if email not in results:
                results[email] = {'name': name, 'count': 1}
            else:
                results[email]['count'] += 1
                
    return results

def main():
    console.clear()
    print_banner()
    
    console.print(Align.center("[italic dim]Press Ctrl+C to exit at any time.[/italic dim]\n"))

    username = get_centered_input("Enter target [bold cyan]GitHub Username[/bold cyan]")
    
    if not username:
        console.print(Align.center("[bold red]Username is required![/bold red]"))
        return

    repository = get_centered_input(f"Enter [bold cyan]Repository[/bold cyan] for [bold white]{username}[/bold white]")
    
    if not repository:
        console.print(Align.center("[bold red]Repository is required![/bold red]"))
        return
    
    console.print()
    
    with console.status(f"[bold yellow]Scanning commit history...[/bold yellow]", spinner="dots2", spinner_style="bold cyan") as status:
        time.sleep(1) 
        commits, code = fetch_commits(username, repository)
        
        if code == "success":
            time.sleep(0.5)
            data = extract_emails(commits)
        else:
            data = None

    if code != "success":
        error_panel = Panel(
            Text(f"Scan Failed: {code}\n\n• Check spelling of user/repo\n• API Rate limit might be exceeded", justify="center"),
            title="[bold red]ERROR[/bold red]",
            style="red",
            width=60
        )
        console.print(Align.center(error_panel))
    
    elif not data:
        console.print(Align.center(Panel("[yellow]No public emails found in the recent commit history.[/yellow]", title="Result", border_style="yellow", width=60)))
        
    else:
        table = Table(title=f"Extracted Data: {username}/{repository}", box=box.ROUNDED, show_lines=True)
        
        table.add_column("Author Name", style="cyan", justify="center")
        table.add_column("Email Address", style="bold green", justify="center")
        table.add_column("Freq", justify="center", style="magenta")

        for email, info in data.items():
            table.add_row(info['name'], email, str(info['count']))

        console.print(Align.center(table))
        console.print(Align.center(f"\n[bold green]✔ Scan complete.[/bold green] Found {len(data)} unique address(es)."))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(Align.center("\n[bold red]Aborted by user.[/bold red]"))
        sys.exit()
