import requests

# URL of the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

def get_lane_counters():
    response = requests.get(f"{BASE_URL}/lane-counters")
    if response.status_code == 200:
        return response.json()
    print(f"Failed to get lane counters: {response.status_code}")
    return None

def update_lane_counters(counters):
    response = requests.post(f"{BASE_URL}/lane-counters", json=counters)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to update lane counters: {response.status_code}")
    return None

def get_traffic_lights():
    response = requests.get(f"{BASE_URL}/traffic-lights")
    if response.status_code == 200:
        return response.json()
    print(f"Failed to get traffic lights: {response.status_code}")
    return None

def update_traffic_light(light_id, red, yellow, green):
    light_status = {
        "id": light_id,
        "red": red,
        "yellow": yellow,
        "green": green
    }
    response = requests.post(f"{BASE_URL}/traffic-lights", json=light_status)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to update traffic light: {response.status_code}")
    return None

def main():
    while True:
        print("1. Get lane counters")
        print("2. Update lane counters")
        print("3. Get traffic lights")
        print("4. Update traffic light")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            counters = get_lane_counters()
            if counters:
                print(f"Lane Counters: {counters}")
        
        elif choice == '2':
            top = int(input("Enter top lane count: "))
            bottom = int(input("Enter bottom lane count: "))
            left = int(input("Enter left lane count: "))
            right = int(input("Enter right lane count: "))
            counters = {
                "top": top,
                "bottom": bottom,
                "left": left,
                "right": right
            }
            updated_counters = update_lane_counters(counters)
            if updated_counters:
                print(f"Updated Lane Counters: {updated_counters}")

        elif choice == '3':
            lights = get_traffic_lights()
            if lights:
                for light in lights:
                    print(f"Light {light['id']} - Position: {light['pos']}, Red: {light['red']}, Yellow: {light['yellow']}, Green: {light['green']}, Direction: {light['direction']}")
        
        elif choice == '4':
            light_id = int(input("Enter traffic light ID to update: "))
            red = input("Enter red status (True/False): ").lower() == 'true'
            yellow = input("Enter yellow status (True/False): ").lower() == 'true'
            green = input("Enter green status (True/False): ").lower() == 'true'
            updated_lights = update_traffic_light(light_id, red, yellow, green)
            if updated_lights:
                print("Updated Traffic Lights:")
                for light in updated_lights:
                    print(f"Light {light['id']} - Position: {light['pos']}, Red: {light['red']}, Yellow: {light['yellow']}, Green: {light['green']}, Direction: {light['direction']}")
        
        elif choice == '5':
            break
        
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
