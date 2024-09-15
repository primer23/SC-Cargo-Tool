import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import re  # Import regular expressions to help extract SCU values

# Database with all data
data = {
     "Hurston": {
        "Planetary Locations": {
            "Landing Zone": "Lorville",
            "Orbital Station": "Everus Harbour",
            "Distribution Centres": [
                "HDPC-Farnesway", "HDPC-Cassillo", "Covalex Distribution Centre S1DC06",
                "Greycat Stanton Production Complex-B", "Dupree Industrial Manufacturing Facility", "Sakura Sun Magnolia Workcentre"
            ],
            "Outposts": [
                "HDMS-Oparei", "HDMS-Pinewood", "HDMS-Edmond", "HDMS-Hadley", "HDMS-Thedus", "HDMS-Stanhope"
            ]
        },
        "Moons": {
            "Arial": ["HDMS-Latham", "HDMS-Bezdek"],
            "Aberdeen": ["HDMS-Norgaard", "HDMS-Anderson"],
            "Magda": ["HDMS-Perlman", "HDMS-Hahn"],
            "Ita": ["HDMS-Ryder", "HDMS-Woodruff"]
        }
    },
    "Microtech": {
        "Planetary Locations": {
            "Landing Zone": "New Babbage",
            "Orbital Station": "Port Tressler",
            "Distribution Centres": [
                "microTech Logistics Depot S4LD01", "Cry-Astro Processing Plant 19-02", "Covalex Distribution Centre S4DC05",
                "microTech Logistics Depot S4LD13", "Greycat Stanton IV Production Complex-A", "Cry-Astro Processing Plant 34-12"
            ],
            "Outposts": [
                "Shubin Mining Facility SMO-13", "Shubin Mining Facility SMO-22", "Shubin Mining Facility SMO-18",
                "Shubin Mining Facility SMO-10", "Rayari Deltana Research Outpost"
            ]
        },
        "Moons": {
            "Calliope": ["Rayari Anvik Research Outpost", "Rayari Kaltag Research Outpost", "Shubin Mining Facility SMCa-8", "Shubin Mining Facility SMCa-6"],
            "Cilo": ["Rayari Cantwell Research Outpost", "Rayari McGrath Research Outpost"],
            "Euterpe": ["Devlin Scrap & Salvage", "Bud's Growery"]
        }
    },
    "ArcCorp": {
        "Planetary Locations": {
            "Landing Zone": "Area 18",
            "Orbital Station": "Bajini Point"
        },
        "Moons": {
            "Lyria": ["Shubin Mining Facility SAL-2", "Shubin Mining Facility SAL-5"],
            "Wala": ["ArcCorp Mining Area 048", "ArcCorp Mining Area 045", "ArcCorp Mining Area 061", "ArcCorp Mining Area 056", "Samson & Son's Salvage Center"]
        }
    },
    "Crusader": {
        "Planetary Locations": {
            "Landing Zone": "Orison",
            "Orbital Station": "Seraphin Station"
        },
        "Moons": {
            "Cellin": ["Hickes Research Outpost", "Terra Mills HydroFarm"],
            "Daymar": ["ArcCorp Mining Area 141", "Shubin Mining Facility SCD-1", "Brio's Breaker Yard"],
            "Yela": ["Deakins Research Outpost", "ArcCorp Mining Area 157"]
        }
    },
    "Lagrange Points": {
        "Crusader-Stanton": ["CRU-L1", "CRU-L2", "CRU-L3", "CRU-L4", "CRU-L5"],
        "Hurston-Stanton": ["HUR-L1", "HUR-L2", "HUR-L3", "HUR-L4", "HUR-L5"],
        "ArcCorp-Stanton": ["ARC-L1", "ARC-L2", "ARC-L3", "ARC-L4", "ARC-L5"],
        "MicroTech-Stanton": ["MIC-L1", "MIC-L2", "MIC-L3", "MIC-L4", "MIC-L5"]
    },
    "Jump Points": ["Stanton-Pyro", "Stanton-Terra", "Stanton-Magnus"]
}

# To store mission data
missions = []

# For multi-cargo tracking (temporary before adding the mission)
current_cargo = []

# Function to clear cargo list (for new missions)
def clear_current_cargo():
    global current_cargo
    current_cargo = []

# Function to gather all possible locations from the data
def gather_all_locations():
    all_locations = []
    for planet in data:
        if "Planetary Locations" in data[planet]:
            planetary_locations = data[planet]["Planetary Locations"]
            all_locations.extend([loc for loc in planetary_locations.values() if isinstance(loc, str)])
            for loc_list in planetary_locations.values():
                if isinstance(loc_list, list):
                    all_locations.extend(loc_list)
        if "Moons" in data[planet]:
            for moon_locations in data[planet]["Moons"].values():
                all_locations.extend(moon_locations)
        if planet == "Lagrange Points":
            for points in data[planet].values():
                all_locations.extend(points)
        if planet == "Jump Points":
            all_locations.extend(data[planet])
    return all_locations

# Filter options based on user input in the search box
def filter_search_options(search_text, options):
    search_text = search_text.lower()
    if search_text == '':
        return options  # Show all options if no input
    else:
        return [item for item in options if search_text in item.lower()]  # Filtered list

# Update combobox with filtered values but do not auto-open
def update_combobox_with_filtered_values(combobox, filtered_values):
    combobox['values'] = filtered_values

# Initialize window and frames
root = tk.Tk()
root.title("Star Citizen Cargo Mission Tool")
root.geometry("1500x800")  # Adjusted for wider and taller space

# Main Frame
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky='nsew')

# Configure column and row weight to allow resizing
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=2)  # Set weight for wider right side for summary table

# Main Page
tk.Label(main_frame, text="Mission List", font=("Arial", 16)).grid(row=0, column=0, pady=10, columnspan=2)

# Missions table at the top
missions_table = ttk.Treeview(main_frame, columns=("Type", "Pickup", "Dropoff", "Commodity", "SCU"), show='headings', height=10)
missions_table.heading("Type", text="Mission Type")
missions_table.heading("Pickup", text="Pickup Location")
missions_table.heading("Dropoff", text="Dropoff Location")
missions_table.heading("Commodity", text="Commodity Type")
missions_table.heading("SCU", text="SCU Amount")
missions_table.grid(row=1, column=0, pady=10, sticky='nsew')

# Move the summary table to the right
summary_frame = tk.Frame(main_frame)
summary_frame.grid(row=1, column=1, rowspan=20, padx=20, sticky='nsew')  # Move it to the right and increase height
summary_frame.grid_rowconfigure(0, weight=1)

# Add the Summarise button to the top of the summary table
summarise_button = ttk.Button(summary_frame, text="Summarise", command=lambda: update_summary())
summarise_button.grid(row=0, column=0, pady=10)

# Add the summary table below the summarise button
summary_table = ttk.Treeview(summary_frame, columns=("Description", "Value"), show='headings', height=20)  # Taller summary table
summary_table.heading("Description", text="Description")
summary_table.heading("Value", text="Value")
summary_table.grid(row=1, column=0, sticky='nsew')

# Add Mission Section below the missions table (in the same column)
add_mission_frame = tk.Frame(main_frame)
add_mission_frame.grid(row=2, column=0, pady=10, padx=5, sticky='nsew')

tk.Label(add_mission_frame, text="Add Mission", font=("Arial", 16)).grid(row=0, column=0, columnspan=4)

# Pickup Location
tk.Label(add_mission_frame, text="Pickup Location:").grid(row=1, column=0, pady=10, padx=10, sticky='e')
pickup_combobox = ttk.Combobox(add_mission_frame, values=gather_all_locations(), width=30)
pickup_combobox.grid(row=1, column=1, pady=5, padx=5)

# Dropoff Location
tk.Label(add_mission_frame, text="Dropoff Location:").grid(row=1, column=2, pady=5, padx=5, sticky='e')
dropoff_combobox = ttk.Combobox(add_mission_frame, values=gather_all_locations(), width=30)
dropoff_combobox.grid(row=1, column=3, pady=5, padx=5)

# Commodity Type and SCU fields for adding multiple entries
tk.Label(add_mission_frame, text="Commodity:").grid(row=2, column=0, pady=5, padx=5, sticky='e')
cargo_entry = ttk.Entry(add_mission_frame, width=20)
cargo_entry.grid(row=2, column=1, pady=5, padx=5)

tk.Label(add_mission_frame, text="SCU Amount:").grid(row=2, column=2, pady=5, padx=5, sticky='e')
scu_entry = ttk.Entry(add_mission_frame, width=20)
scu_entry.grid(row=2, column=3, pady=5, padx=5)

# Table to display added commodity entries for Multi/Direct Mission
cargo_table = ttk.Treeview(add_mission_frame, columns=("Pickup", "Dropoff", "Commodity", "SCU"), show='headings', height=5)
cargo_table.heading("Pickup", text="Pickup Location")
cargo_table.heading("Dropoff", text="Dropoff Location")
cargo_table.heading("Commodity", text="Commodity Type")
cargo_table.heading("SCU", text="SCU Amount")
cargo_table.grid(row=3, column=0, columnspan=4, pady=10)

# Function to add commodity entry to the table
def add_cargo():
    cargo_type = cargo_entry.get()
    scu = scu_entry.get()
    pickup = pickup_combobox.get()
    dropoff = dropoff_combobox.get()
    if pickup and dropoff and cargo_type and scu:
        current_cargo.append((pickup, dropoff, cargo_type, scu))
        cargo_table.insert("", "end", values=(pickup, dropoff, cargo_type, scu))
    cargo_entry.delete(0, tk.END)
    scu_entry.delete(0, tk.END)

# Function to remove selected cargo for multi mission
def remove_cargo():
    selected_item = cargo_table.selection()
    for item in selected_item:
        cargo_table.delete(item)
        index = int(item[-1])
        current_cargo.pop(index)

# Move Add Commodity and Remove Commodity buttons to the top right of the commodities box
add_cargo_button = ttk.Button(add_mission_frame, text="Add Commodity", command=add_cargo)
add_cargo_button.grid(row=1, column=4, pady=5, padx=5, sticky='nsew')

remove_cargo_button = ttk.Button(add_mission_frame, text="Remove Commodity", command=remove_cargo)
remove_cargo_button.grid(row=2, column=4, pady=5, padx=5, sticky='nsew')

# Function to add the mission (whether direct or multi) to the mission table
def add_multi_mission():
    mission_type = "Multi" if len(set([x[0] for x in current_cargo])) > 1 else "Direct"

    # Combine data into a single entry for missions_table
    cargo_types = {}
    scu_amounts = {}

    for pickup, dropoff, cargo_type, scu in current_cargo:
        # Group by cargo type and dropoff location
        if (cargo_type, dropoff) not in cargo_types:
            cargo_types[(cargo_type, dropoff)] = []
        cargo_types[(cargo_type, dropoff)].append(pickup)
        if dropoff not in scu_amounts:
            scu_amounts[dropoff] = {}
        if cargo_type not in scu_amounts[dropoff]:
            scu_amounts[dropoff][cargo_type] = 0
        scu_amounts[dropoff][cargo_type] += int(scu)

    combined_pickups = ', '.join(set([x[0] for x in current_cargo]))
    combined_dropoffs = ', '.join(set([x[1] for x in current_cargo]))

    combined_cargo = ', '.join(
        [f"{cargo_type} ({', '.join(pickups)})" for (cargo_type, dropoff), pickups in cargo_types.items()]
    )
    
    combined_scu = ', '.join(
        [f"{cargo_type}: {scu_amounts[dropoff][cargo_type]} SCU ({dropoff})" for dropoff in scu_amounts for cargo_type in scu_amounts[dropoff]]
    )

    missions_table.insert("", "end", values=(mission_type, combined_pickups, combined_dropoffs, combined_cargo, combined_scu))

    clear_current_cargo()
    cargo_table.delete(*cargo_table.get_children())  # Clear commodity table entries

# Make the Add Mission button bigger
add_mission_button_multi = ttk.Button(add_mission_frame, text="Add Mission", command=add_multi_mission)
add_mission_button_multi.grid(row=4, column=1, pady=10, padx=10, columnspan=2, ipadx=30, ipady=10)

# Function to update the summary table
def update_summary():
    total_scu = 0
    pickup_totals = defaultdict(int)
    dropoff_totals = defaultdict(int)
    commodity_totals = defaultdict(lambda: defaultdict(int))

    # Regular expression to extract SCU values
    scu_pattern = re.compile(r'(\d+)\sSCU')

    # Loop through all missions in the mission table to calculate totals
    for row_id in missions_table.get_children():
        mission = missions_table.item(row_id)['values']
        _, pickups, dropoffs, cargo, scu = mission

        # Extract SCU amounts from the text using the regex pattern
        scu_values = [int(match.group(1)) for match in scu_pattern.finditer(scu)]
        total_scu += sum(scu_values)  # Add all SCU values to the total

        # Update pickup and dropoff totals based on extracted SCU values
        for pickup in pickups.split(', '):
            pickup_totals[pickup] += sum(scu_values)  # Add SCU for each pickup
        for dropoff in dropoffs.split(', '):
            dropoff_totals[dropoff] += sum(scu_values)  # Add SCU for each dropoff

        # Update commodity totals (splitting cargo based on location)
        for c in cargo.split(', '):
            # Split based on the assumption that it's formatted as "cargo_type (locations)"
            if ' (' in c:
                cargo_type, locs = c.split(' (')
                locs = locs.strip(')')
            else:
                # If the format is incorrect or missing, treat the whole entry as cargo_type without locations
                cargo_type = c
                locs = 'Unknown'

            # Update the commodity totals for each location
            for loc in locs.split(', '):
                commodity_totals[cargo_type][loc] += sum(scu_values)

    # Find the location with the highest pickup and dropoff totals
    highest_pickup = max(pickup_totals.items(), key=lambda x: x[1])[0] if pickup_totals else None
    highest_dropoff = max(dropoff_totals.items(), key=lambda x: x[1])[0] if dropoff_totals else None

    # Sort pickups and dropoffs from most to least
    sorted_pickups = sorted(pickup_totals.items(), key=lambda x: x[1], reverse=True)
    sorted_dropoffs = sorted(dropoff_totals.items(), key=lambda x: x[1], reverse=True)

    # Update summary table
    summary_table.delete(*summary_table.get_children())  # Clear the existing summary table

    # Add total SCU
    summary_table.insert("", "end", values=("Total SCU", total_scu))

    # Add highest pickup and dropoff location
    if highest_pickup:
        summary_table.insert("", "end", values=("Highest Pickup Location", highest_pickup))
    if highest_dropoff:
        summary_table.insert("", "end", values=("Highest Dropoff Location", highest_dropoff))

    # Add sorted pickup locations
    for pickup, total in sorted_pickups:
        summary_table.insert("", "end", values=(f"Pickup: {pickup}", total))

    # Add sorted dropoff locations
    for dropoff, total in sorted_dropoffs:
        summary_table.insert("", "end", values=(f"Dropoff: {dropoff}", total))

    # Add commodity totals (sorted alphabetically by commodity)
    for commodity, locations in sorted(commodity_totals.items()):
        for location, total_scu in sorted(locations.items()):
            summary_table.insert("", "end", values=(f"Commodity: {commodity} to {location}", total_scu))

# Enable searchable dropdown
def make_combobox_searchable(combobox):
    def on_keyrelease(event):
        if event.widget == combobox:
            search_text = combobox.get()
            filtered_values = filter_search_options(search_text, combobox.original_values)
            update_combobox_with_filtered_values(combobox, filtered_values)

    combobox.original_values = gather_all_locations()
    combobox.bind('<KeyRelease>', on_keyrelease)

# Make the pickup and dropoff comboboxes searchable
make_combobox_searchable(pickup_combobox)
make_combobox_searchable(dropoff_combobox)

# Function to reset the entire interface (missions, summary, and cargo)
def refresh_program():
    # Clear all tables and reset variables
    missions_table.delete(*missions_table.get_children())
    cargo_table.delete(*cargo_table.get_children())
    summary_table.delete(*summary_table.get_children())
    clear_current_cargo()
    pickup_combobox.set('')
    dropoff_combobox.set('')
    cargo_entry.delete(0, tk.END)
    scu_entry.delete(0, tk.END)

# Add the Refresh button at the top of the main frame
refresh_button = ttk.Button(main_frame, text="Refresh", command=refresh_program)
refresh_button.grid(row=0, column=1, pady=0, padx=0, sticky='e')

# Running the main loop
root.mainloop()
