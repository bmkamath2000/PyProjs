import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys


def is_stale(sent_time, received_time, threshold_minutes=30):
    """
    Determines if a sensor reading is stale by comparing sent and received timestamps.
    
    Args:
        sent_time (str): UTC timestamp when the reading was sent, in ISO format.
        received_time (str): UTC timestamp when the reading was received, in ISO format.
        threshold_minutes (int): Maximum allowed time difference in minutes.
    
    Returns:
        bool: True if the difference exceeds the threshold, False otherwise.
    """
    sent = datetime.strptime(sent_time, "%Y-%m-%dT%H:%M:%SZ")
    received = datetime.strptime(received_time, "%Y-%m-%dT%H:%M:%SZ")
    return (received - sent) > timedelta(minutes=threshold_minutes)


def main():
    # Ensure exactly one command-line argument (input JSON file) is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.json>")
        sys.exit(1)
    
    # Attempt to load and parse the input JSON file
    try:
        with open(sys.argv[1], 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        sys.exit(1)
    
    # List to store detected anomalies
    anomalies = []
    
    # Dictionary to maintain a rolling history of magnetic field values per sensor
    sensor_history = defaultdict(list)
    
    # Process each data cluster in the input
    for cluster in data['data_clusters']:
        received_time = cluster['received_time']  # Time when this cluster was received
        # Sort readings by sent_time to process in chronological order
        sorted_readings = sorted(cluster['readings'], key=lambda x: x['sent_time'])
        
        for reading in sorted_readings:
            sent_time = reading['sent_time']
            sensor_id = reading['sensor_id']
            magnetic_field = reading['magnetic_field']
            
            # Skip readings that arrived too late (stale data)
            if is_stale(sent_time, received_time):
                continue
            
            # Retrieve or initialize history for this sensor
            history = sensor_history[sensor_id]
            
            # Only check for anomalies if we have at least 5 previous readings
            if len(history) >= 5:
                average = sum(history) / len(history)
                # Flag anomaly if current reading is more than 5x the average
                if magnetic_field > 5 * average:
                    anomalies.append({
                        'magnetic_field': magnetic_field,
                        'sensor_id': sensor_id,
                        'sent_time': sent_time
                    })
            
            # Add current reading to the sensor's history
            history.append(magnetic_field)
            # Keep only the most recent 5 readings
            if len(history) > 5:
                history.pop(0)
    
    # Sort anomalies by sent_time for chronological output
    anomalies.sort(key=lambda x: x['sent_time'])
    
    # Prepare and print the result in JSON format
    result = {"anomalies": anomalies}
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
