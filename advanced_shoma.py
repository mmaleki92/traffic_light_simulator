import requests
import json
import argparse
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint

# Configuration
BASE_URL = "http://127.0.0.1:8000"
console = Console()

class TrafficControlClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def api_request(self, method, endpoint, data=None):
        """Make an API request and handle errors"""
        url = f"{self.base_url}/{endpoint}"
        try:
            if method.lower() == "get":
                response = requests.get(url, timeout=5)
            elif method.lower() == "post":
                response = requests.post(url, json=data, timeout=5)
            else:
                console.print(f"[bold red]Invalid method: {method}")
                return None
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]API Error: {e}")
            return None
    
    # Health check
    def health_check(self):
        """Check server health status"""
        return self.api_request("get", "health")
    
    # Lane counter operations
    def get_lane_counters(self):
        """Get current lane counters"""
        return self.api_request("get", "lane-counters")
    
    def update_lane_counters(self, counters):
        """Update lane counters"""
        return self.api_request("post", "lane-counters", counters)
    
    # Traffic light operations
    def get_traffic_lights(self):
        """Get all traffic lights"""
        return self.api_request("get", "traffic-lights")
    
    def update_traffic_light(self, light_id, red=False, yellow=False, green=False):
        """Update a traffic light"""
        light_status = {
            "id": light_id,
            "red": red,
            "yellow": yellow,
            "green": green
        }
        return self.api_request("post", "traffic-lights", light_status)
    
    # Traffic patterns
    def get_traffic_patterns(self):
        """Get all available traffic patterns"""
        return self.api_request("get", "traffic-patterns")
    
    def create_traffic_pattern(self, name, description, lights):
        """Create a new traffic pattern"""
        pattern = {
            "name": name,
            "description": description,
            "lights": lights
        }
        return self.api_request("post", "traffic-patterns", pattern)
    
    def apply_pattern(self, pattern_name):
        """Apply a traffic pattern"""
        return self.api_request("post", f"apply-pattern/{pattern_name}")
    
    # Safety and accidents
    def check_accident(self):
        """Check if there's a potential accident"""
        return self.api_request("get", "check-accident")
    
    def log_accident(self, message, is_accident=True):
        """Log an accident"""
        accident = {
            "message": message,
            "is_accident": is_accident
        }
        return self.api_request("post", "log-accident", accident)
    
    def get_accident_logs(self):
        """Get all accident logs"""
        return self.api_request("get", "log-accident")
    
    # Statistics
    def get_statistics(self):
        """Get traffic statistics"""
        return self.api_request("get", "statistics")
    
    # System management
    def reset_system(self):
        """Reset the system"""
        return self.api_request("post", "reset")

# Display functions for rich output
def display_lane_counters(counters):
    """Display lane counters in a nice table"""
    if not counters:
        console.print("[bold red]Failed to get lane counters")
        return

    table = Table(title="Lane Counters")
    table.add_column("Lane", style="cyan")
    table.add_column("Count", style="green")
    
    for lane, count in counters.items():
        table.add_row(lane.capitalize(), str(count))
    
    console.print(table)

def display_traffic_lights(lights):
    """Display traffic lights in a nice table"""
    if not lights:
        console.print("[bold red]Failed to get traffic lights")
        return

    table = Table(title="Traffic Lights")
    table.add_column("ID", style="cyan")
    table.add_column("Direction", style="cyan")
    table.add_column("Position", style="cyan")
    table.add_column("Red", style="red")
    table.add_column("Yellow", style="yellow")
    table.add_column("Green", style="green")
    
    for light in lights:
        table.add_row(
            str(light['id']),
            light['direction'],
            f"({light['pos'][0]}, {light['pos'][1]})",
            "●" if light['red'] else "○",
            "●" if light['yellow'] else "○",
            "●" if light['green'] else "○"
        )
    
    console.print(table)

def display_traffic_patterns(patterns):
    """Display traffic patterns"""
    if not patterns:
        console.print("[bold red]Failed to get traffic patterns")
        return

    for name, pattern in patterns.items():
        panel = Panel(
            f"[cyan]Description:[/cyan] {pattern['description']}\n\n"
            f"[cyan]Lights:[/cyan] {len(pattern['lights'])} configured",
            title=f"[bold]Pattern: {name}[/bold]",
            border_style="green"
        )
        console.print(panel)

def display_accident_logs(logs):
    """Display accident logs in a nice table"""
    if not logs:
        console.print("[yellow]No accident logs found")
        return

    table = Table(title="Accident Logs")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Status", style="cyan")
    table.add_column("Message", style="white")
    
    for log in logs:
        status = "[red]ACCIDENT" if log.get('is_accident', True) else "[green]CLEAR"
        table.add_row(
            log.get('timestamp', 'Unknown'),
            status,
            log.get('message', 'No message')
        )
    
    console.print(table)

def display_statistics(stats):
    """Display statistics in a nice panel"""
    if not stats:
        console.print("[bold red]Failed to get statistics")
        return
    
    panel = Panel(
        f"[cyan]Total Cars:[/cyan] {stats['total_cars']}\n\n"
        f"[cyan]Cars per Lane:[/cyan]\n"
        f"  Top: {stats['cars_per_lane']['top']}\n"
        f"  Bottom: {stats['cars_per_lane']['bottom']}\n"
        f"  Left: {stats['cars_per_lane']['left']}\n"
        f"  Right: {stats['cars_per_lane']['right']}\n\n"
        f"[cyan]Accidents:[/cyan] {stats['accidents']}\n\n"
        f"[cyan]Timestamp:[/cyan] {stats['timestamp']}",
        title="[bold]Traffic Statistics[/bold]",
        border_style="green"
    )
    console.print(panel)

def display_dashboard(client):
    """Display a live dashboard"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    
    layout["left"].split_column(
        Layout(name="counters"),
        Layout(name="lights")
    )
    
    layout["right"].split_column(
        Layout(name="statistics"),
        Layout(name="safety")
    )
    
    with Live(layout, refresh_per_second=1, screen=True) as live:
        try:
            while True:
                # Update header
                health = client.health_check()
                layout["header"].update(
                    Panel(
                        f"[bold white]Server Status:[/bold white] {'[green]Online' if health else '[red]Offline'}\n"
                        f"[bold white]Current Time:[/bold white] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        title="[bold]Traffic Control Dashboard[/bold]",
                        border_style="blue"
                    )
                )
                
                # Update lane counters
                counters = client.get_lane_counters()
                if counters:
                    table = Table(title="Lane Counters")
                    table.add_column("Lane", style="cyan")
                    table.add_column("Count", style="green")
                    
                    for lane, count in counters.items():
                        table.add_row(lane.capitalize(), str(count))
                    
                    layout["counters"].update(table)
                
                # Update traffic lights
                lights = client.get_traffic_lights()
                if lights:
                    table = Table(title="Traffic Lights")
                    table.add_column("ID", style="cyan", width=4)
                    table.add_column("Direction", style="cyan", width=8)
                    table.add_column("Red", style="red", width=5)
                    table.add_column("Yellow", style="yellow", width=5)
                    table.add_column("Green", style="green", width=5)
                    
                    for light in lights:
                        table.add_row(
                            str(light['id']),
                            light['direction'],
                            "●" if light['red'] else "○",
                            "●" if light['yellow'] else "○",
                            "●" if light['green'] else "○"
                        )
                    
                    layout["lights"].update(table)
                
                # Update statistics
                stats = client.get_statistics()
                if stats:
                    layout["statistics"].update(
                        Panel(
                            f"[cyan]Total Cars:[/cyan] {stats['total_cars']}\n\n"
                            f"[cyan]Cars per Lane:[/cyan]\n"
                            f"  Top: {stats['cars_per_lane']['top']}\n"
                            f"  Bottom: {stats['cars_per_lane']['bottom']}\n"
                            f"  Left: {stats['cars_per_lane']['left']}\n"
                            f"  Right: {stats['cars_per_lane']['right']}\n\n"
                            f"[cyan]Accidents:[/cyan] {stats['accidents']}",
                            title="[bold]Traffic Statistics[/bold]",
                            border_style="green"
                        )
                    )
                
                # Update safety status
                accident_status = client.check_accident()
                if accident_status:
                    status = "[bold red]WARNING! Potential accident detected!" if accident_status.get('is_accident', False) else "[bold green]No accidents detected"
                    message = accident_status.get('message', '')
                    
                    layout["safety"].update(
                        Panel(
                            f"{status}\n\n{message}",
                            title="[bold]Safety Status[/bold]",
                            border_style="red" if accident_status.get('is_accident', False) else "green"
                        )
                    )
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            return

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description='Traffic Control Client')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health check
    subparsers.add_parser('health', help='Check server health')
    
    # Lane counters
    subparsers.add_parser('get-lanes', help='Get lane counters')
    
    update_lane_parser = subparsers.add_parser('update-lane', help='Update a lane counter')
    update_lane_parser.add_argument('lane', choices=['top', 'bottom', 'left', 'right'], help='Lane to update')
    update_lane_parser.add_argument('count', type=int, help='New count value')
    
    # Traffic lights
    subparsers.add_parser('get-lights', help='Get traffic lights')
    
    update_light_parser = subparsers.add_parser('update-light', help='Update a traffic light')
    update_light_parser.add_argument('id', type=int, help='Light ID')
    update_light_parser.add_argument('--red', action='store_true', help='Turn red light on')
    update_light_parser.add_argument('--yellow', action='store_true', help='Turn yellow light on')
    update_light_parser.add_argument('--green', action='store_true', help='Turn green light on')
    
    # Traffic patterns
    subparsers.add_parser('get-patterns', help='Get traffic patterns')
    
    apply_pattern_parser = subparsers.add_parser('apply-pattern', help='Apply a traffic pattern')
    apply_pattern_parser.add_argument('name', help='Pattern name to apply')
    
    # Accidents and safety
    subparsers.add_parser('check-accident', help='Check for potential accidents')
    subparsers.add_parser('accident-logs', help='Get accident logs')
    
    log_accident_parser = subparsers.add_parser('log-accident', help='Log an accident')
    log_accident_parser.add_argument('message', help='Accident message')
    log_accident_parser.add_argument('--false-alarm', action='store_true', help='Mark as a false alarm')
    
    # Statistics
    subparsers.add_parser('stats', help='Get traffic statistics')
    
    # System management
    subparsers.add_parser('reset', help='Reset the system')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show live traffic dashboard')
    
    # Parse arguments
    args = parser.parse_args()
    client = TrafficControlClient()
    
    # Execute command
    if args.command == 'health':
        health = client.health_check()
        if health:
            console.print(f"[green]Server is healthy. Version: {health.get('version', 'unknown')}")
            console.print(f"Timestamp: {health.get('timestamp', 'unknown')}")
        else:
            console.print("[red]Server is not responding")
    
    elif args.command == 'get-lanes':
        counters = client.get_lane_counters()
        display_lane_counters(counters)
    
    elif args.command == 'update-lane':
        current = client.get_lane_counters()
        if current:
            current[args.lane] = args.count
            result = client.update_lane_counters(current)
            if result:
                console.print(f"[green]Lane {args.lane} updated to {args.count}")
                display_lane_counters(result)
    
    elif args.command == 'get-lights':
        lights = client.get_traffic_lights()
        display_traffic_lights(lights)
    
    elif args.command == 'update-light':
        result = client.update_traffic_light(args.id, args.red, args.yellow, args.green)
        if result:
            console.print(f"[green]Light {args.id} updated successfully")
            display_traffic_lights(result)
    
    elif args.command == 'get-patterns':
        patterns = client.get_traffic_patterns()
        display_traffic_patterns(patterns)
    
    elif args.command == 'apply-pattern':
        result = client.apply_pattern(args.name)
        if result:
            console.print(f"[green]Pattern '{args.name}' applied successfully")
            display_traffic_lights(result.get('traffic_lights', []))
    
    elif args.command == 'check-accident':
        status = client.check_accident()
        if status:
            if status.get('is_accident', False):
                console.print(f"[bold red]WARNING! {status.get('message', 'Potential accident detected!')}")
            else:
                console.print(f"[bold green]No accidents detected")
    
    elif args.command == 'accident-logs':
        logs = client.get_accident_logs()
        display_accident_logs(logs)
    
    elif args.command == 'log-accident':
        result = client.log_accident(args.message, not args.false_alarm)
        if result:
            console.print(f"[green]Accident logged successfully")
    
    elif args.command == 'stats':
        stats = client.get_statistics()
        display_statistics(stats)
    
    elif args.command == 'reset':
        result = client.reset_system()
        if result:
            console.print(f"[green]System reset successfully")
    
    elif args.command == 'dashboard':
        console.print("[bold green]Starting dashboard. Press CTRL+C to exit.")
        display_dashboard(client)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()