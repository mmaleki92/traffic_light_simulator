import requests
import time
import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal text
init()

# URL of the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

class TrafficControlSystem:
    def __init__(self):
        self.config_file = "traffic_config.json"
        self.load_config()
        
    def load_config(self):
        """Load configuration from file or use defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    print(f"{Fore.GREEN}Configuration loaded from {self.config_file}{Style.RESET_ALL}")
            else:
                self.config = {
                    "server_url": BASE_URL,
                    "refresh_rate": 2,
                    "auto_mode": False,
                    "patterns": {
                        "normal": [
                            {"id": 0, "red": False, "yellow": False, "green": True},
                            {"id": 1, "red": False, "yellow": False, "green": True},
                            {"id": 2, "red": True, "yellow": False, "green": False},
                            {"id": 3, "red": True, "yellow": False, "green": False}
                        ],
                        "north_south_priority": [
                            {"id": 0, "red": False, "yellow": False, "green": True},
                            {"id": 1, "red": False, "yellow": False, "green": True},
                            {"id": 2, "red": True, "yellow": False, "green": False},
                            {"id": 3, "red": True, "yellow": False, "green": False}
                        ],
                        "east_west_priority": [
                            {"id": 0, "red": True, "yellow": False, "green": False},
                            {"id": 1, "red": True, "yellow": False, "green": False},
                            {"id": 2, "red": False, "yellow": False, "green": True},
                            {"id": 3, "red": False, "yellow": False, "green": True}
                        ],
                        "all_red": [
                            {"id": 0, "red": True, "yellow": False, "green": False},
                            {"id": 1, "red": True, "yellow": False, "green": False},
                            {"id": 2, "red": True, "yellow": False, "green": False},
                            {"id": 3, "red": True, "yellow": False, "green": False}
                        ]
                    }
                }
        except Exception as e:
            print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")
            self.config = {"server_url": BASE_URL, "refresh_rate": 2, "auto_mode": False}

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"{Fore.GREEN}Configuration saved to {self.config_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error saving configuration: {e}{Style.RESET_ALL}")

    def api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Make an API request with proper error handling"""
        url = f"{self.config['server_url']}/{endpoint}"
        try:
            if method.lower() == "get":
                response = requests.get(url, timeout=5)
            elif method.lower() == "post":
                response = requests.post(url, json=data, timeout=5)
            else:
                print(f"{Fore.RED}Invalid method: {method}{Style.RESET_ALL}")
                return None
                
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}Connection error: Could not connect to {url}{Style.RESET_ALL}")
            return None
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}Timeout error: Server at {url} took too long to respond{Style.RESET_ALL}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}HTTP error: {e}{Style.RESET_ALL}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Request error: {e}{Style.RESET_ALL}")
            return None
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error decoding JSON response from server{Style.RESET_ALL}")
            return None

    def get_accident_status(self) -> None:
        """Get and display the current accident status"""
        accident_info = self.api_request("get", "check-accident")
        if accident_info:
            status = "YES - ALERT!" if accident_info["is_accident"] else "No"
            color = Fore.RED if accident_info["is_accident"] else Fore.GREEN
            print(f"Accident status: {color}{status}{Style.RESET_ALL}")
            if "message" in accident_info and accident_info["message"]:
                print(f"Accident message: {color}{accident_info['message']}{Style.RESET_ALL}")

    def get_lane_counters(self) -> Optional[Dict[str, int]]:
        """Get the current lane counters"""
        counters = self.api_request("get", "lane-counters")
        if counters:
            print(f"{Fore.CYAN}Lane Counters:{Style.RESET_ALL}")
            print(f"  Top: {counters['top']}")
            print(f"  Bottom: {counters['bottom']}")
            print(f"  Left: {counters['left']}")
            print(f"  Right: {counters['right']}")
            print(f"  Total: {sum(counters.values())}")
        return counters

    def update_lane_counters(self) -> None:
        """Update lane counters with user input"""
        counters = self.get_lane_counters() or {"top": 0, "bottom": 0, "left": 0, "right": 0}
        
        try:
            print("\nEnter new values (press Enter to keep current):")
            top = input(f"  Top lane count [{counters['top']}]: ")
            bottom = input(f"  Bottom lane count [{counters['bottom']}]: ")
            left = input(f"  Left lane count [{counters['left']}]: ")
            right = input(f"  Right lane count [{counters['right']}]: ")
            
            new_counters = {
                "top": int(top) if top.strip() else counters['top'],
                "bottom": int(bottom) if bottom.strip() else counters['bottom'],
                "left": int(left) if left.strip() else counters['left'],
                "right": int(right) if right.strip() else counters['right']
            }
            
            result = self.api_request("post", "lane-counters", new_counters)
            if result:
                print(f"{Fore.GREEN}Lane counters updated successfully{Style.RESET_ALL}")
                self.get_lane_counters()
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter numeric values.{Style.RESET_ALL}")

    def get_traffic_lights(self) -> Optional[List[Dict[str, Any]]]:
        """Get and display current traffic light status"""
        lights = self.api_request("get", "traffic-lights")
        if lights:
            self.display_traffic_lights(lights)
        return lights

    def display_traffic_lights(self, lights: List[Dict[str, Any]]) -> None:
        """Format and display traffic light information"""
        print(f"\n{Fore.CYAN}Traffic Lights:{Style.RESET_ALL}")
        print(f"  {'ID':<4} {'Direction':<10} {'Position':<15} {'Status'}")
        print(f"  {'-'*40}")
        for light in lights:
            status = ""
            if light['red']:
                status += f"{Fore.RED}■{Style.RESET_ALL} "
            else:
                status += "□ "
                
            if light['yellow']:
                status += f"{Fore.YELLOW}■{Style.RESET_ALL} "
            else:
                status += "□ "
                
            if light['green']:
                status += f"{Fore.GREEN}■{Style.RESET_ALL}"
            else:
                status += "□"
                
            position = f"({light['pos'][0]}, {light['pos'][1]})"
            print(f"  {light['id']:<4} {light['direction']:<10} {position:<15} {status}")

    def update_traffic_light(self) -> None:
        """Update the status of a traffic light"""
        lights = self.get_traffic_lights()
        if not lights:
            return
        
        try:
            print("\nEnter traffic light information:")
            light_id = input("  Light ID to update: ")
            
            # Validate ID
            light_id = int(light_id)
            valid_id = any(light['id'] == light_id for light in lights)
            if not valid_id:
                print(f"{Fore.RED}Invalid light ID{Style.RESET_ALL}")
                return
                
            print("\nEnter light status (y/n):")
            red = input("  Red light on? (y/n): ").lower().startswith('y')
            yellow = input("  Yellow light on? (y/n): ").lower().startswith('y')
            green = input("  Green light on? (y/n): ").lower().startswith('y')
            
            result = self.api_request("post", "traffic-lights", {
                "id": light_id,
                "red": red,
                "yellow": yellow,
                "green": green
            })
            
            if result:
                print(f"{Fore.GREEN}Traffic light {light_id} updated successfully{Style.RESET_ALL}")
                self.display_traffic_lights(result)
                
        except ValueError:
            print(f"{Fore.RED}Invalid input. Light ID must be a number.{Style.RESET_ALL}")

    def log_accident(self) -> None:
        """Get accident logs"""
        response = self.api_request("get", "log-accident")
        if response:
            print(f"\n{Fore.CYAN}Accident Logs:{Style.RESET_ALL}")
            for entry in response:
                timestamp = entry.get('timestamp', 'Unknown')
                message = entry.get('message', 'No message')
                is_accident = entry.get('is_accident', False)
                
                status = f"{Fore.RED}ACCIDENT{Style.RESET_ALL}" if is_accident else f"{Fore.GREEN}CLEAR{Style.RESET_ALL}"
                print(f"  [{timestamp}] {status}: {message}")

    def apply_traffic_pattern(self, pattern_name: str) -> None:
        """Apply a predefined traffic pattern"""
        if pattern_name not in self.config.get('patterns', {}):
            print(f"{Fore.RED}Pattern '{pattern_name}' not found{Style.RESET_ALL}")
            return
            
        pattern = self.config['patterns'][pattern_name]
        print(f"{Fore.YELLOW}Applying traffic pattern: {pattern_name}{Style.RESET_ALL}")
        
        for light_config in pattern:
            result = self.api_request("post", "traffic-lights", light_config)
            if not result:
                print(f"{Fore.RED}Failed to update light {light_config['id']}{Style.RESET_ALL}")
                return
        
        # Verify the changes
        self.get_traffic_lights()

    def auto_control_traffic(self) -> None:
        """Automatically control traffic based on lane counters"""
        print(f"{Fore.YELLOW}Starting automatic traffic control...{Style.RESET_ALL}")
        print("(Press Ctrl+C to stop)")
        
        try:
            self.config["auto_mode"] = True
            self.save_config()
            
            while True:
                counters = self.api_request("get", "lane-counters")
                if not counters:
                    print(f"{Fore.RED}Could not get lane counters. Retrying...{Style.RESET_ALL}")
                    time.sleep(2)
                    continue
                
                # Simple algorithm to decide which pattern to use
                ns_traffic = counters['top'] + counters['bottom']
                ew_traffic = counters['left'] + counters['right']
                
                if ns_traffic > ew_traffic * 2:
                    self.apply_traffic_pattern("north_south_priority")
                elif ew_traffic > ns_traffic * 2:
                    self.apply_traffic_pattern("east_west_priority")
                else:
                    # Alternate between patterns
                    timestamp = int(time.time())
                    if (timestamp // 30) % 2 == 0:  # Switch every 30 seconds
                        self.apply_traffic_pattern("north_south_priority")
                    else:
                        self.apply_traffic_pattern("east_west_priority")
                
                # Check for accidents
                self.get_accident_status()
                
                # Wait before the next check
                time.sleep(self.config["refresh_rate"])
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Automatic traffic control stopped{Style.RESET_ALL}")
            self.config["auto_mode"] = False
            self.save_config()

    def print_dashboard(self) -> None:
        """Display a comprehensive dashboard of the traffic system"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{' ' * 20}TRAFFIC CONTROL DASHBOARD{' ' * 20}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}System Status:{Style.RESET_ALL}")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Server: {self.config['server_url']}")
        print(f"  Auto-mode: {'ON' if self.config.get('auto_mode', False) else 'OFF'}")
        
        self.get_accident_status()
        self.get_lane_counters()
        self.get_traffic_lights()
        
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

    def display_menu(self) -> None:
        """Display the main menu"""
        print(f"\n{Fore.CYAN}Traffic Control System - Main Menu{Style.RESET_ALL}")
        print(f"  1. {Fore.GREEN}View Dashboard{Style.RESET_ALL}")
        print(f"  2. View Lane Counters")
        print(f"  3. Update Lane Counters")
        print(f"  4. View Traffic Lights")
        print(f"  5. Update Traffic Light")
        print(f"  6. View Accident Logs")
        print(f"  7. Check Accident Status")
        print(f"  8. Apply Traffic Pattern")
        print(f"  9. {Fore.YELLOW}Start Auto Control{Style.RESET_ALL}")
        print(f"  0. Exit")

    def run(self) -> None:
        """Run the main application loop"""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.print_dashboard()
            
            elif choice == '2':
                self.get_lane_counters()
            
            elif choice == '3':
                self.update_lane_counters()
            
            elif choice == '4':
                self.get_traffic_lights()
            
            elif choice == '5':
                self.update_traffic_light()
            
            elif choice == '6':
                self.log_accident()
            
            elif choice == '7':
                self.get_accident_status()
                
            elif choice == '8':
                patterns = list(self.config.get('patterns', {}).keys())
                if patterns:
                    print(f"\n{Fore.CYAN}Available patterns:{Style.RESET_ALL}")
                    for i, pattern in enumerate(patterns):
                        print(f"  {i+1}. {pattern}")
                    try:
                        pattern_idx = int(input("\nSelect pattern number: ")) - 1
                        if 0 <= pattern_idx < len(patterns):
                            self.apply_traffic_pattern(patterns[pattern_idx])
                        else:
                            print(f"{Fore.RED}Invalid pattern number{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Please enter a number{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}No patterns defined in configuration{Style.RESET_ALL}")
            
            elif choice == '9':
                self.auto_control_traffic()
            
            elif choice == '0':
                print(f"{Fore.GREEN}Exiting traffic control system. Goodbye!{Style.RESET_ALL}")
                break
            
            else:
                print(f"{Fore.RED}Invalid choice, please try again.{Style.RESET_ALL}")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        traffic_system = TrafficControlSystem()
        traffic_system.run()
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)