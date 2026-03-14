# so firstly lets import libraries
import csv
import sys
import math

# lets declare the radius of Earth as mentioned
earth_radius = 6371000.0

# lets create a class called Person which acts as my main data structure 
class Person :
    def __init__(self, first, last, lat, lon, elev, zip_code):
        self.full_name = f"{first} {last}"
        self.zip_code = zip_code

        # Calculate and store 3D (x, y, z) coordinates
        # This is done only once, on creation
        self.x, self.y, self.z = self.to_cartesian(lat, lon, elev)

        self.assigned = False # to check if they have been put in a neighborhood

    def to_cartesian(self, lat, lon, elev):
        # this will help convert lat lon elev to 3D

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        # to convert degrees into radians

        r = earth_radius + elev #the total radius from center of Earth

        x = r * math.cos(lat_rad) * math.cos(lon_rad)
        y = r * math.cos(lat_rad) * math.sin(lon_rad)
        z = r * math.sin(lat_rad)

        return x, y, z
    
    def __repr__(self):
        return self.full_name # shows the persons name

def calculate_distance(p1: Person, p2: Person) -> float:
    # to calculate the 3D distance between two people 
    return math.sqrt(
        (p1.x - p2.x)**2 +
        (p1.y - p2.y)**2 +
        (p1.z - p2.z)**2
    )

def read_and_clean_data(csv_filepath):
    valid_people = []
    try:
        with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader : 
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    elev = float(row['Elevation'])
                    first = row['First Name']
                    last = row['Last Name']
                    zip_code = row['ZIP code']

                    if not first or not last :
                        continue

                    valid_people.append(Person(first, last, lat, lon, elev, zip_code))
                
                except(ValueError,TypeError, KeyError):
                    print(f"Skipping row due to error: {e}. Row data: {row}", file=sys.stderr)
                    continue

    
    except FileNotFoundError:
        print(f"Error: File not found at {csv_filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    return valid_people

def group_neighborhoods(people, max_distance):
    final_nieghborhoods = []

    for person in people:
        if person.assigned:
            continue

        new_group = []

        new_group.append(person)
        person.assigned = True

        for other_person in people:
            if other_person.assigned:
                continue

            distance = calculate_distance(person, other_person)
            if distance <= max_distance:
                new_group.append(other_person)
                other_person.assigned = True

            elif person.zip_code == other_person.zip_code:
                if person.zip_code:
                    new_group.append(other_person)
                    other_person.assigned = True

        final_nieghborhoods.append(new_group)        
    return final_nieghborhoods
        
def format_and_print(neighborhoods):
    output_lines = []
    
    for group in neighborhoods:
      
        names = [person.full_name for person in group]
        
       
        names.sort()
        
        output_lines.append(names)
    
    
    output_lines.sort(key=lambda name_list: name_list[0])
    
    
    for line in output_lines:
        print(",".join(line))


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <distance> <csv_file.csv>", file=sys.stderr)
        sys.exit(1)
        
    try:
        proximity_distance = float(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid distance '{sys.argv[1]}'. Must be a number.", file=sys.stderr)
        sys.exit(1)
        
    csv_filepath = sys.argv[2]
    
    all_people = read_and_clean_data(csv_filepath)
    
    neighborhood_groups = group_neighborhoods(all_people, proximity_distance)
    
    format_and_print(neighborhood_groups)


# so to run this using our test cases as an example
# i ran the code this way
# python main.py 1000 citizen_location.csv
# this is for the test case given
# python task_3.py 1000 test1.csv 
# similarly for 2 and 3
    