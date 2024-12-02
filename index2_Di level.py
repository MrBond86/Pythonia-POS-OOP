import sys
from datetime import datetime
import os

# Global dictionary to store guest bookings
guest_booking = {}

# Custom exceptions for handling different validation errors
class InvalidGuestNameError(Exception):
    pass

class InvalidProductError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

class InvalidDateError(Exception):
    pass

class InvalidInputError(Exception):
    pass

class Guest:
    def __init__(self, guest_id, name, reward, reward_rate=100, redeem_rate=1):
        self.guest_id = guest_id
        self.name = name
        self.reward = reward
        self.reward_rate = reward_rate
        self.redeem_rate = redeem_rate

    # Adjust reward rate for all guests
    def adjust_reward_rate(self, new_rate):
        if new_rate <= 0 or not isinstance(new_rate, (int, float)):
            raise InvalidInputError("Invalid reward rate. Please enter a positive number.")
        self.reward_rate = new_rate

    # Adjust redeem rate for all guests
    def adjust_redeem_rate(self, new_rate):
        if new_rate <= 0 or not isinstance(new_rate, (int, float)):
            raise InvalidInputError("Invalid redeem rate. Please enter a positive number.")
        self.redeem_rate = new_rate

    def get_reward_points(self, total_cost):
        return round(total_cost * (self.reward_rate / 100))

    def get_id(self):
        return self.guest_id

    def get_name(self):
        return self.name

    def get_reward(self):
        return self.reward 

    def update_reward(self, points):
        self.reward += points

    def display_info(self):
        print(f"ID: {self.guest_id}, Name: {self.name}, Reward Rate: {self.reward_rate}%, Reward Points: {self.reward}, Redeem Rate: {self.redeem_rate}%")

class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price

    def get_id(self):
        return self.product_id

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

    def display_info(self):
        print(f"Product ID: {self.product_id}, Name: {self.name}, Price: ${self.price:.2f}")

class ApartmentUnit(Product):
    def __init__(self, product_id, name, price, capacity):
        super().__init__(product_id, name, price)
        self.capacity = capacity

    def display_info(self):
        print(f"Apartment ID: {self.product_id}, Name: {self.name}, Price: ${self.price:.2f}, Capacity: {self.capacity} beds")

class SupplementaryItem(Product):
    pass

class Bundle(Product):
    def __init__(self, product_id, name, components, price=0):
        super().__init__(product_id, name, price)
        self.components = components

    def display_info(self):
        components_details = ', '.join([f"{comp} x{self.components.count(comp)}" for comp in set(self.components)])
        print(f"Bundle ID: {self.product_id}, Name: {self.name}, Components: {components_details}, Price: ${self.price:.2f}")

    @staticmethod
    def calculate_bundle_price(components, product_catalog):
        total_price = sum(product_catalog[comp].get_price() for comp in components)
        return total_price * 0.80  # Apply 80% discount for bundles

class Order:
    def __init__(self, guest, product, quantity):
        self.guest = guest
        self.product = product
        self.quantity = quantity

    def compute_cost(self):
        return self.product.get_price() * self.quantity, 0, self.product.get_price() * self.quantity, self.guest.get_reward_points(self.product.get_price() * self.quantity)

    def display_receipt(self):
        original_cost, discount, final_cost, reward_points = self.compute_cost()
        print("========================================================")
        print(f"Guest Name: {self.guest.get_name()}")
        print(f"Product: {self.product.get_name()} (ID: {self.product.get_id()})")
        print(f"Unit Price: ${self.product.get_price():.2f}")
        print(f"Quantity: {self.quantity}")
        print(f"Original Cost: ${original_cost:.2f}")
        print(f"Discount: ${discount:.2f}")
        print(f"Final Total Cost: ${final_cost:.2f}")
        print(f"Earned Reward Points: {reward_points}")
        print("========================================================")

class Records:
    def __init__(self):
        self.guests = {}
        self.products = {}

    def read_guests(self, filename):
        if not os.path.exists(filename):
            print(f"Error: {filename} does not exist.")
            return

        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        guest_id, name, reward_rate, reward, redeem_rate = line.split(',')
                        self.guests[guest_id] = Guest(guest_id, name, float(reward), int(reward_rate), int(redeem_rate))
        except Exception as e:
            print(f"An error occurred while reading {filename}: {e}")

    def read_products(self, filename):
        if not os.path.exists(filename):
            print(f"Error: {filename} does not exist.")
            sys.exit(1)
        
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                product_id = parts[0].strip()

                if product_id.lower().startswith('b'):  # Handle bundles
                    if len(parts) < 6:  # Ensure there are enough parts to unpack for a bundle
                        print(f"Skipping invalid bundle entry: {line}")
                        continue
                    name = parts[1].strip()
                    components = parts[2:-1]  # Assumes all but the last part are component IDs
                    price = float(parts[-1].strip())
                    self.products[product_id] = Bundle(product_id, name, components, price)

                elif product_id.lower().startswith('u'):  # Handle apartment units
                    if len(parts) != 4:  # Ensure there are exactly four parts for an apartment unit
                        print(f"Skipping invalid apartment entry: {line}")
                        continue
                    name = parts[1].strip()
                    price = float(parts[2].strip())
                    capacity = int(parts[3].strip())
                    self.products[product_id] = ApartmentUnit(product_id, name, price, capacity)

                elif product_id.lower().startswith('si'):  # Handle supplementary items
                    if len(parts) != 3:  # Ensure there are exactly three parts for a supplementary item
                        print(f"Skipping invalid supplementary item entry: {line}")
                        continue
                    name = parts[1].strip()
                    price = float(parts[2].strip())
                    self.products[product_id] = SupplementaryItem(product_id, name, price)

                else:
                    print(f"Skipping unknown or improperly formatted product type: {line}")

    def find_guest(self, value):
        return self.guests.get(value, None)

    def find_product(self, value):
        return self.products.get(value, None)

    def list_guests(self):
        if not self.guests:
            print("No guests found.")
            return
        print("Existing Guests:")
        for guest_id, guest in self.guests.items():
            print(f"ID: {guest_id}, Name: {guest.get_name()}, Reward Rate: {guest.reward_rate}%, Reward Points: {guest.reward}, Redeem Rate: {guest.redeem_rate}%")

    def list_products(self, product_type):
        if product_type.lower() == 'apartment':
            print("Existing Apartment Units:")
            for product_id, product in self.products.items():
                if isinstance(product, ApartmentUnit):
                    print(f"ID: {product_id}, Name: {product.get_name()}, Price: ${product.get_price():.2f}, Capacity: {product.capacity} beds")
        elif product_type.lower() == 'supplementary':
            print("Existing Supplementary Items:")
            for product_id, product in self.products.items():
                if isinstance(product, SupplementaryItem):
                    print(f"ID: {product_id}, Name: {product.get_name()}, Price: ${product.get_price():.2f}")
        elif product_type.lower() == 'bundle':
            print("Existing Bundles:")
            for product_id, product in self.products.items():
                if isinstance(product, Bundle):
                   components_summary = ', '.join([f"{comp} x{product.components.count(comp)}" for comp in set(product.components)])
                   print(f"ID: {product_id}, Name: {product.get_name()}, Components: {components_summary}, Price: ${product.price:.2f}")
                else:
                    print("Invalid product type specified. Use 'apartment', 'supplementary', or 'bundle'.")

class Operations:
    def __init__(self, records):
        self.records = records

    def make_booking(self):
        today = datetime.today().date()

        # Get and validate the guest name
        while True:
            try:
                guest_name = self.non_empty("Enter the main guest name: ")
                if not guest_name.replace(" ", "").isalpha():
                    raise InvalidGuestNameError("Invalid input: Guest name must contain only letters and spaces.")
                break
            except InvalidGuestNameError as e:
                print(e)

        # Retrieve or create a new guest record
        guest = self.records.find_guest(guest_name)
        if not guest:
            guest_id = str(len(self.records.guests) + 1)
            guest = Guest(guest_id, guest_name, 0)  # Starting with 0 reward points
            self.records.guests[guest_id] = guest
            self.records.guests[guest_name] = guest
            print(f"New guest '{guest_name}' added with ID {guest_id}.")
        else:
            print(f"Welcome back, {guest.get_name()}! You have {guest.get_reward()} reward points.")

        # Get and validate the number of guests
        while True:
            try:
                number_of_guests = int(self.non_empty("Enter the number of guests: "))
                if number_of_guests <= 0:
                    raise InvalidQuantityError("Invalid input: The number of guests must be a positive integer.")
                break
            except ValueError:
                print("Invalid input: Please enter a valid number for guests.")
            except InvalidQuantityError as e:
                print(e)

        # Validate and retrieve the apartment ID
        while True:
            try:
                apartment_id = self.non_empty("Enter the apartment ID (e.g., U12swan): ")
                
                # Ensure it starts with 'U' and is long enough to have a number and building name
                if not apartment_id.startswith("U") or len(apartment_id) < 3:
                    raise InvalidProductError("Invalid format: Apartment ID should start with 'U' followed by digits and end with a building name (e.g., U12swan).")
                
                # Find where the numeric part ends
                i = 1  # Start after 'U'
                while i < len(apartment_id) and apartment_id[i].isdigit():
                    i += 1
                
                # Check if a number was found and is followed by a building name
                number_part = apartment_id[1:i]
                building_part = apartment_id[i:]
                
                if not number_part.isdigit() or building_part not in ["swan", "duck", "goose"]:
                    raise InvalidProductError("Invalid format: Apartment ID should start with 'U' followed by digits and end with a building name (e.g., U12swan).")
                
                # Retrieve the apartment product
                apartment = self.records.find_product(apartment_id)
                if not apartment or not isinstance(apartment, ApartmentUnit):
                    raise InvalidProductError("Invalid apartment ID: Apartment does not exist. Please try again.")
                break

            except InvalidProductError as e:
                print(e)


        # Get and validate the check-in date
        while True:
            try:
                check_in_str = self.non_empty("Enter the check-in date (dd-mm-yyyy): ")
                check_in_date = self.validate_date(check_in_str)
                
                if not check_in_date:
                    raise InvalidDateError("Invalid date format: Please enter the date in dd-mm-yyyy format.")
                elif check_in_date.date() < today:
                    raise InvalidDateError("Invalid check-in date: The check-in date cannot be in the past.")
                break
            except InvalidDateError as e:
                print(e)

        # Get and validate the check-out date
        while True:
            try:
                check_out_str = self.non_empty("Enter the check-out date (dd-mm-yyyy): ")
                check_out_date = self.validate_date(check_out_str)
                
                if not check_out_date:
                    raise InvalidDateError("Invalid date format: Please enter the date in dd-mm-yyyy format.")
                elif check_out_date <= check_in_date:
                    raise InvalidDateError("Invalid check-out date: Check-out date must be after the check-in date.")
                break
            except InvalidDateError as e:
                print(e)

        # Calculate length of stay based on validated dates
        length_of_stay = (check_out_date - check_in_date).days
        print(f"Length of stay: {length_of_stay} nights")

        # Check if extra beds are required based on the apartment's capacity
        orders = []
        if number_of_guests > apartment.capacity:
            # Calculate the number of extra beds needed
            extra_beds_needed = (number_of_guests - apartment.capacity + 1) // 2
            if extra_beds_needed > 2:
                print("Booking cannot proceed: too many guests for the apartment, and extra beds limit exceeded.")
                return
            
            # Check for a standalone extra bed or a bundle with extra beds
            extra_bed_product = None
            for product in self.records.products.values():
                # Identify by ID or keyword in name, e.g., 'extra bed'
                if isinstance(product, SupplementaryItem) and ("extra bed" in product.name.lower() or product.get_id().startswith("SIExtraBed")):
                    extra_bed_product = product
                    break

            # Offer extra bed product if available
            if extra_bed_product:
                confirm_extra_beds = input(f"Apartment capacity is {apartment.capacity}, {number_of_guests} guests are selected.\n"
                                        f"Would you like to add {extra_beds_needed} extra bed(s) at ${extra_bed_product.get_price()} each? (y/n): ").strip().lower()
                if confirm_extra_beds == 'y':
                    orders.append(Order(guest, extra_bed_product, extra_beds_needed))
                    print(f"Added {extra_beds_needed} extra bed(s).")
                else:
                    print("Booking cancelled: unable to accommodate selected number of guests without extra beds.")
                    return
            else:
                print("No extra bed product is available in the inventory to accommodate additional guests.")
                return

        # Add the apartment booking to orders
        orders.append(Order(guest, apartment, length_of_stay))
        print(f"Apartment booked for {length_of_stay} nights.")

        # Continue with supplementary items or bundles if needed
        while True:
            additional_product_id = self.non_empty("Enter product ID for supplementary items or bundles, or type 'done' to finish: ")
            if additional_product_id.lower() == 'done':
                break
            product = self.records.find_product(additional_product_id)
            if not product:
                print("Product not found, please try again.")
                continue

            if isinstance(product, Bundle):
                orders.append(Order(guest, product, 1))
                print(f"Added bundle: {product.get_name()}")
            else:
                while True:
                    try:
                        quantity = int(self.non_empty("Enter quantity: "))
                        if quantity < 1:
                            print("Invalid quantity: Quantity must be at least 1.")
                            continue
                        orders.append(Order(guest, product, quantity))
                        print(f"Added {quantity} x {product.get_name()}")
                        break
                    except ValueError:
                        print("Invalid input: Please enter a numeric value for quantity.")

        # Calculate initial cost before applying rewards
        total_cost = sum(order.compute_cost()[2] for order in orders)
        print(f"Total initial cost: ${total_cost:.2f}")

        # Reward point deduction if guest has enough points
        if guest.get_reward() >= 100:
            use_rewards = input("Would you like to use your reward points? (y/n): ").strip().lower()
            if use_rewards == 'y':
                discount_points = min(guest.get_reward(), (total_cost // 10) * 100)  # Calculate max discount points
                discount_amount = discount_points / 10
                print(f"Applying a discount of ${discount_amount:.2f} from reward points.")
                total_cost -= discount_amount
                guest.update_reward(-discount_points)  # Deduct used points
                print(f"New total cost after discount: ${total_cost:.2f}")
                print(f"Remaining reward points: {guest.get_reward()}")

        # Update guest's reward points after calculating total cost
        reward_points_earned = int(total_cost)
        guest.update_reward(reward_points_earned)
        print(f"Reward points earned from this booking: {reward_points_earned} points")
        print(f"Total reward points after booking: {guest.get_reward()}")

        # Store booking in guest's history (optional for history management)
        guest_booking[guest.get_name()] = {
            'apartment': apartment.get_name(),
            'nights': length_of_stay,
            'total_cost': total_cost,
            'orders': [(order.product.get_name(), order.quantity) for order in orders]
        }

        # Display receipt for all orders
        print("\nBooking Summary:")
        for order in orders:
            order.display_receipt()
        print(f"Overall total cost: ${total_cost:.2f}")
        print("Thank you for your booking!")


    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Make a booking")
            print("2. Add/update information of an apartment unit")
            print("3. Add/update information of supplementary items")
            print("4. Add/update information of bundles")
            print("5. Adjust the reward rate of all guests")
            print("6. Adjust the redeem rate of all guests")
            print("7. Exit")
            choice = self.non_empty("Choose an option: ")

            if choice == '1':
                self.make_booking()
            elif choice == '2':
                self.add_or_update_apartment_unit()
            elif choice == '3':
                self.add_or_update_supplementary_items()
            elif choice == '4':
                self.add_or_update_bundle()
            elif choice == '5':
                self.adjust_reward_rate()
            elif choice == '6':
                self.adjust_redeem_rate()
            elif choice == '7':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please choose again.")

    def add_or_update_apartment_unit(self):
        unit_info = self.non_empty("Enter apartment unit info (id rate capacity): ")
        parts = unit_info.split()
        if len(parts) != 3 or not parts[0].startswith('U'):
            print("Invalid format. Please use the format: U<number><building> <rate> <capacity>")
            return
        unit_id, rate, capacity = parts
        try:
            rate = float(rate)
            capacity = int(capacity)
            self.records.products[unit_id] = ApartmentUnit(unit_id, unit_id, rate, capacity)
            print(f"Apartment unit {unit_id} updated with rate ${rate} and capacity {capacity}.")
        except ValueError:
            print("Invalid rate or capacity. Please ensure they are numbers.")

    def add_or_update_supplementary_item(self):
        # Prompt for the supplementary item ID
        item_id = self.non_empty("Enter supplementary item ID (e.g., SIExtraBed, SICarPark): ")

        # Check if the item already exists in the records
        existing_item = self.records.find_product(item_id)

        # If item exists, confirm update, else add new item
        if existing_item:
            print(f"Item with ID '{item_id}' already exists as '{existing_item.get_name()}' with price ${existing_item.get_price():.2f}.")
            update_choice = input("Would you like to update this item? (y/n): ").strip().lower()
            if update_choice != 'y':
                print("Update cancelled.")
                return
        else:
            print(f"Adding a new supplementary item with ID '{item_id}'.")

        # Prompt for item name and price
        item_name = self.non_empty("Enter supplementary item name (e.g., Extra Bed, Car Park): ")
        while True:
            try:
                item_price = float(self.non_empty("Enter supplementary item price: $"))
                if item_price <= 0:
                    print("Price must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input: Please enter a numeric value for price.")

        # Create or update the supplementary item in records
        new_item = SupplementaryItem(item_id, item_name, item_price)
        self.records.products[item_id] = new_item
        print(f"Supplementary item '{item_name}' (ID: {item_id}) has been {'updated' if existing_item else 'added'} with a price of ${item_price:.2f}.")


    def add_or_update_bundle(self):
        # Prompt for the bundle ID
        bundle_id = self.non_empty("Enter bundle ID (e.g., B1, B2): ")

        # Check if the bundle already exists in the records
        existing_bundle = self.records.find_product(bundle_id)

        # If bundle exists, confirm update, else add new bundle
        if existing_bundle:
            print(f"Bundle with ID '{bundle_id}' already exists as '{existing_bundle.get_name()}' with price ${existing_bundle.get_price():.2f}.")
            update_choice = input("Would you like to update this bundle? (y/n): ").strip().lower()
            if update_choice != 'y':
                print("Update cancelled.")
                return
        else:
            print(f"Adding a new bundle with ID '{bundle_id}'.")

        # Prompt for bundle name and validate
        bundle_name = self.non_empty("Enter bundle name (e.g., Family Pack, Deluxe Bundle): ")

        # Prompt for components (product IDs) in the bundle
        components = []
        while True:
            component_id = self.non_empty("Enter component product ID (or type 'done' to finish): ")
            if component_id.lower() == 'done':
                if not components:
                    print("A bundle must have at least one component.")
                    continue
                break

            # Check if the component ID exists in the records
            component = self.records.find_product(component_id)
            if not component:
                print(f"Component with ID '{component_id}' not found. Please add it first or use an existing item.")
                continue
            components.append(component_id)
            print(f"Added component: {component.get_name()} (ID: {component_id})")

        # Calculate the bundle price as 80% of the sum of individual component prices
        bundle_price = round(0.8 * sum(self.records.find_product(comp_id).get_price() for comp_id in components), 2)

        # Create or update the bundle in records
        new_bundle = Bundle(bundle_id, bundle_name, components, bundle_price)
        self.records.products[bundle_id] = new_bundle
        print(f"Bundle '{bundle_name}' (ID: {bundle_id}) has been {'updated' if existing_bundle else 'added'} with a price of ${bundle_price:.2f}.")

    def adjust_reward_rate(self):
    # Prompt for the new reward rate and validate
        while True:
            try:
                new_rate = float(self.non_empty("Enter new reward rate (as a percentage): "))
                if new_rate <= 0:
                    print("Reward rate must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input: Please enter a numeric value for the reward rate.")

        # Update the reward rate for all guests
        for guest in self.records.guests.values():
            guest.adjust_reward_rate(new_rate)

        print(f"Reward rate has been adjusted to {new_rate}% for all guests.")

    def adjust_redeem_rate(self):
        while True:
            try:
                new_rate = float(self.non_empty("Enter new redeem rate (as a percentage): "))
                if new_rate <= 0:
                    print("Redeem rate must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input: Please enter a numeric value for the redeem rate.")

        for guest in self.records.guests.values():
            guest.adjust_redeem_rate(new_rate)
        print(f"Redeem rate has been adjusted to {new_rate}% for all guests.")

    
    def non_empty(self, prompt):
        while True:
            user_input = input(prompt).strip()
            if user_input:
                return user_input
            else:
                print("Input cannot be empty. Please try again.") 
    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            print("Invalid date format. Please enter in dd-mm-yyyy format.")
            return None

def main():
    # Initialize records and load data from files
    records = Records()
    records.read_guests('guests.csv')
    records.read_products('products.csv')
    
    # Initialize operations and start the menu
    operations = Operations(records)
    operations.menu()

if __name__ == "__main__":
    main()
