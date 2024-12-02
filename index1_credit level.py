import sys
from datetime import datetime
import os

#dictionary to store guest bookings
guest_booking = {}
#adding for credit level
class InvalidGuestNameError(Exception):
    pass

class InvalidProductError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

class InvalidDateError(Exception):
    pass



class Guest:
    def __init__(self, guest_id, name, reward, reward_rate=100, redeem_rate=1):
        self.guest_id = guest_id
        self.name = name
        self.reward_rate = reward_rate
        self.reward = reward
        self.redeem_rate = redeem_rate

    # Getter methods
    def get_id(self):
        return self.guest_id

    def get_name(self):
        return self.name

    def get_reward_rate(self):
        return self.reward_rate

    def get_reward(self):
        return self.reward

    def get_redeem_rate(self):
        return self.redeem_rate

    def get_reward_points(self, total_cost):
        return round(total_cost * (self.reward_rate / 100))

    def update_reward(self, value):
        self.reward += value

    def set_reward_rate(self, new_rate):
        self.reward_rate = new_rate

    def set_redeem_rate(self, new_rate):
        self.redeem_rate = new_rate

    def display_info(self):
        print(f"ID: {self.guest_id}, Name: {self.name}, Reward Rate: {self.reward_rate}%, "
              f"Reward Points: {self.reward}, Redeem Rate: {self.redeem_rate}%")

class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price

    # Getter methods
    def get_id(self):
        return self.product_id

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

    def display_info(self):
        pass

class ApartmentUnit(Product):
    def __init__(self, product_id, name, price, capacity):
       
        super().__init__(product_id, name, price)
        self.capacity = capacity

    # Getter method for capacity
    def get_capacity(self):
        return self.capacity

    def display_info(self):
        print(f"Apartment ID: {self.product_id}, Name: {self.name}, Rate per Night: ${self.price:.2f}, "
              f"Capacity: {self.capacity} beds")

class SupplementaryItem(Product):
    def __init__(self, product_id, name, price):
        super().__init__(product_id, name, price)

    def display_info(self):
        print(f"Item ID: {self.product_id}, Name: {self.name}, Unit Price: ${self.price:.2f}")

class Order:
    def __init__(self, guest, product, quantity):
        self.guest = guest
        self.product = product
        self.quantity = quantity

    def compute_cost(self):
        original_cost = self.product.get_price() * self.quantity
        discount = 0  # No discount at PASS level
        final_cost = original_cost - discount
        reward_points = self.guest.get_reward_points(final_cost)
        return original_cost, discount, final_cost, reward_points

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

class Bundle(Product):
    def __init__(self, product_id, name, components, price=0):
        super().__init__(product_id, name, price)  # Initialize with default price 0
        self.components = components

    def display_info(self):
        component_details = ', '.join([f"{comp} x{self.components.count(comp)}" for comp in set(self.components)])
        print(f"Bundle ID: {self.product_id}, Name: {self.name}, Components: {component_details}, Price: ${self.price:.2f}")

    
    @staticmethod
    def calculate_bundle_price(components, product_catalog):
        total_price = 0
        for component in components:
            component_lower = component.lower()  # Convert component ID to lowercase
            if component_lower in product_catalog:
                component_price = product_catalog[component_lower].get_price()
                total_price += component_price
                print(f"Component {component_lower} price: ${component_price:.2f}")
            else:
                print(f"Component {component_lower} not found in catalog")
        return total_price * 0.80  # Apply 80% pricing for bundle






class Records:
    def __init__(self):
        self.guests = {}  
        self.products = {} 

    def read_guests(self, filename):
        if not os.path.exists(filename):
            print(f"Error: {filename} does not exist.")
            sys.exit(1)
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) == 5:
                        guest_id, name, reward_rate, reward, redeem_rate = parts
                        guest = Guest(guest_id, name, float(reward), float(reward_rate), float(redeem_rate))
                        self.guests[guest_id] = guest
                        self.guests[name] = guest  # Allow searching by name
                    else:
                        print(f"Skipping invalid guest entry: {line}")

    def read_products(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                product_id = parts[0].lower()  # Convert product_id to lowercase for case-insensitive lookup

                if product_id.startswith('b'):  # Handle bundles
                    name = parts[1].strip()
                    components = [comp.strip().lower() for comp in parts[2:-1]]  # Convert component IDs to lowercase
                    price = float(parts[-1].strip())
                    self.products[product_id] = Bundle(product_id, name, components, price)

                elif product_id.startswith('u'):  # Handle apartment units
                    if len(parts) == 4:
                        name = parts[1].strip()
                        price = float(parts[2].strip())
                        capacity = int(parts[3].strip())
                        apartment = ApartmentUnit(product_id, name, price, capacity)
                        self.products[product_id] = apartment  # Store apartment with lowercase product_id
                    else:
                        print(f"Skipping invalid apartment entry: {line}")

                elif product_id.startswith('si'):  # Handle supplementary items
                    if len(parts) == 3:
                        name = parts[1].strip()
                        price = float(parts[2].strip())
                        item = SupplementaryItem(product_id, name, price)
                        self.products[product_id] = item  # Store supplementary item with lowercase product_id
                    else:
                        print(f"Skipping invalid supplementary item entry: {line}")

                else:
                    print(f"Skipping unknown product type: {line}")
            

    def find_guest(self, value):
        return self.guests.get(value, None)

    def find_product(self, value):
        return self.products.get(value.lower())  # Convert input to lowercase for case-insensitive lookup


    def list_guests(self):
        if not self.guests:
            print("No guests found.")
            return
        print("Existing Guests:")
        print("ID\tName\tReward Rate\tReward Points\tRedeem Rate")
        printed_ids = set()
        for key, guest in self.guests.items():
            if guest.get_id() in printed_ids:
                continue  # Avoid duplicate printing due to name-keyed entries
            print(f"{guest.get_id()}\t{guest.get_name()}\t{guest.get_reward_rate()}%\t\t{guest.get_reward()}\t\t{guest.get_redeem_rate()}%")
            printed_ids.add(guest.get_id())

    def list_products(self, product_type):
        printed_ids = set()
    
        if product_type.lower() == 'apartment':
            print("Existing Apartment Units:")
            print("ID\tName\tRate per Night\tCapacity")
            for key, product in self.products.items():
                if isinstance(product, ApartmentUnit) and product.get_id() not in printed_ids:
                    print(f"{product.get_id()}\t{product.get_name()}\t${product.get_price():.2f}\t\t{product.get_capacity()}")
                    printed_ids.add(product.get_id())
    
        elif product_type.lower() == 'supplementary':
            print("Existing Supplementary Items:")
            print("ID\tName\tUnit Price")
            for key, product in self.products.items():
                if isinstance(product, SupplementaryItem) and product.get_id() not in printed_ids:
                    print(f"{product.get_id()}\t{product.get_name()}\t${product.get_price():.2f}")
                    printed_ids.add(product.get_id())

        elif product_type.lower() == 'bundle':
            print("Existing Bundles:")
            print("ID\tName\tComponents\tPrice")
            for key, product in self.products.items():
                if isinstance(product, Bundle) and product.get_id() not in printed_ids:
                    components_summary = ', '.join([f"{comp} x{product.components.count(comp)}" for comp in set(product.components)])
                    print(f"{product.get_id()}\t{product.get_name()}\t{components_summary}\t${product.get_price():.2f}")
                    printed_ids.add(product.get_id())

        else:
            print("Invalid product type specified. Use 'apartment', 'supplementary', or 'bundle'.")



class Operations:
    def __init__(self, records):
        self.records = records

    def make_booking(self):
        # 1. Guest name
        try:
            guest_name = self.non_empty("Enter the main guest name: ")
            if not guest_name.replace(" ", "").isalpha():
                raise InvalidGuestNameError
            
            # Check if guest exists
            guest = self.records.find_guest(guest_name)
            if not guest:
                # Assign a new unique ID for the guest
                guest_id = str(len(self.records.guests) + 1)
                guest = Guest(guest_id, guest_name, 0)
                self.records.guests[guest_id] = guest
                self.records.guests[guest_name] = guest
                print(f"New guest '{guest_name}' added with ID {guest_id}.")
            else:
                print(f"Welcome back, {guest.get_name()}! You have {guest.get_reward()} reward points.")
        
        except InvalidGuestNameError:
            print("Error: Guest name must contain only alphabet characters. Please try again.")
            return 
        
        # 2. Number of guests
        while True:
            number_of_guests = self.non_empty("Enter the number of guests: ")
            if number_of_guests.isdigit() and int(number_of_guests) > 0:
                number_of_guests = int(number_of_guests)
                break
            else:
                print("Invalid input. Please enter a positive numeric value.")

        # 3. Apartment Selection (Apartment ID)
        while True:
            apartment_id = self.non_empty("Enter the apartment ID (e.g., U12swan): ").strip().lower()  # Only apartment IDs allowed here
            apartment = self.records.find_product(apartment_id)

            if apartment and isinstance(apartment, ApartmentUnit):
                print(f"Apartment selected: {apartment.get_name()}, Rate per night: ${apartment.get_price():.2f}")
                break
            else:
                print("Invalid apartment ID. Please try again.")

        # 4. Check-in date
        while True:
            check_in_str = self.non_empty("Enter the check-in date (dd-mm-yyyy): ")
            check_in_date = self.validate_date(check_in_str)
            if check_in_date:
                break
            else:
                print("Invalid date format. Please enter in dd-mm-yyyy format.")

        # 5. Check-out date
        while True:
            check_out_str = self.non_empty("Enter the check-out date (dd-mm-yyyy): ")
            check_out_date = self.validate_date(check_out_str)
            if check_out_date:
                if check_out_date > check_in_date:
                    break
                else:
                    print("Check-out date must be after check-in date.")
            else:
                print("Invalid date format. Please enter in dd-mm-yyyy format.")
        
        booking_date_obj = datetime.now()

        # Validate check-in date against booking date
        if check_in_date < booking_date_obj:
            raise InvalidDateError("Check-in date cannot be earlier than the booking date.")

        # Validate check-out date against check-in date
        if check_out_date <= check_in_date:
            raise InvalidDateError("Check-out date must be after the check-in date.")

        # 6. Length of stay
        length_of_stay = (check_out_date - check_in_date).days
        print(f"Length of stay: {length_of_stay} nights")

        # 7. Booking date
        booking_date = datetime.now().strftime("%d/%m/%Y %H:%M")  
        print(f"Booking date: {booking_date}")

        # 8. Supplementary items (now allows both items and bundles)
        supplementary_total = 0
        supplementary_items = []
        while True:
            add_suppl = self.non_empty("Do you want to order any supplementary items or bundles? (y/n): ").lower()
            if add_suppl == 'n':
                break
            elif add_suppl == 'y':
                product_id = self.non_empty("Enter the product ID (e.g., SI1 for item or B1 for bundle): ").strip().lower()
                product = self.records.find_product(product_id)

                if product:
                     
                     if isinstance(product, Bundle):
                        print(f"Bundle selected: {product.get_name()}. Components: {', '.join(product.components)}")
                        # Calculate bundle price
                        bundle_price = Bundle.calculate_bundle_price(product.components, self.records.products)
                        product.price = bundle_price  # Update the bundle's price with the calculated value
                        supplementary_total += bundle_price
                        supplementary_items.append(Order(guest, product, 1))  # Add bundle as 1 item
                        print(f"Added Bundle {product.get_name()} (${bundle_price:.2f})")

                     elif isinstance(product, SupplementaryItem):
                        while True:
                            quantity = self.non_empty("Enter the quantity: ")
                            if quantity.isdigit() and int(quantity) > 0:
                                quantity = int(quantity)
                                break
                            else:
                                print("Invalid quantity. Please enter a positive number.")
                        
                        cost = product.get_price() * quantity
                        supplementary_total += cost
                        supplementary_items.append(Order(guest, product, quantity))
                        print(f"Added {quantity} x {product.get_name()} (${product.get_price():.2f} each)")
                else:
                    print("Invalid product ID. Please try again.")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")




        # Calculate total cost
        original_cost = apartment.get_price() * length_of_stay
        total_cost = original_cost + supplementary_total  

        # 9. Rewards - Ask if guest wants to use their reward points
        discount = 0
        if guest.get_reward() >= 100:
            redeem_points = self.non_empty(f"You have {guest.get_reward()} reward points. Would you like to redeem them? (y/n): ").lower()
            if redeem_points == 'y':
                discount = (guest.get_reward() // 100)  # Every 100 points = 1 dollar discount
                total_cost -= discount
                print(f"Discount applied: ${discount:.2f}")
                guest.update_reward(-discount * 100)  # Deduct used points

        # New reward points based on the final total cost
        reward_points = guest.get_reward_points(total_cost)
        guest.update_reward(reward_points)

        # Update booking records
        if guest_name not in guest_booking:
            guest_booking[guest_name] = []
        guest_booking[guest_name].append({
            'apartment_id': apartment.get_id(),
            'apartment_rate': apartment.get_price(),
            'nights': length_of_stay,
            'check_in_date': check_in_str,
            'check_out_date': check_out_str,
            'booking_date': booking_date,
            'supplementary_total': supplementary_total,
            'total_cost': total_cost,
            'reward_points': reward_points
        })

        # Print receipt here
        self.print_receipt(guest_name, number_of_guests, apartment, check_in_str, check_out_str,
                        length_of_stay, booking_date, supplementary_items, supplementary_total, total_cost, reward_points)
       
                
    def print_receipt(self, guest_name, number_of_guests, apartment, check_in, check_out,
                        nights, booking_date, supplementary_items, supplementary_total, total_cost, reward_points):

            print("\n---Booking Information---")
            print(f"Guest's Name: {guest_name}")
            print(f"Number of Guests: {number_of_guests}")
            print(f"Apartment ID: {apartment.get_id()}")
            print(f"Apartment Rate: ${apartment.get_price():.2f} per night")
            print(f"Check-in Date: {check_in}")
            print(f"Check-out Date: {check_out}")
            print(f"Length of Stay: {nights} nights")
            print(f"Booking Date: {booking_date}")

            # Show supplementary items, including bundles
            print("--------------------------------------------------------")
            if supplementary_items:
                print("Supplementary Items and Bundles:")
                print("ID\tName\tQuantity\tUnit Price\tCost")
                for item in supplementary_items:
                    print(f"{item.product.get_id()}\t{item.product.get_name()}\t{item.quantity}\t\t${item.product.get_price():.2f}\t\t${item.product.get_price() * item.quantity:.2f}")

                print(f"Sub-total (Supplementary Items): ${supplementary_total:.2f}")
                print("--------------------------------------------------------")
            
            print(f"Total Cost: ${total_cost:.2f} (AUD)")
            print(f"Reward Points Earned: {reward_points} points")
            print("Thank you for your booking! We hope you will have an enjoyable stay.")
            print("========================================================")
            #debugging
            print(f"Total supplementary cost including bundles: ${supplementary_total:.2f}")
            print(f"Total cost (including apartment): ${total_cost:.2f}")




    def display_guests(self):
        self.records.list_guests()

    def display_apartments(self):
        self.records.list_products('apartment')

    def display_supplementary_items(self):
        self.records.list_products('supplementary')

    def exit_program(self):
        print("Program exiting. Thank you. Goodbye!")
        sys.exit()

    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Make a booking")
            print("2. Display existing guests")
            print("3. Display existing apartment units")
            print("4. Display existing supplementary items")
            print("5. Exit")
            choice = self.non_empty("Choose an option: ")

            if choice == '1':
                self.make_booking()
            elif choice == '2':
                self.display_guests()
            elif choice == '3':
                self.display_apartments()
            elif choice == '4':
                self.display_supplementary_items()
            elif choice == '5':
                self.exit_program()
            else:
                print("Invalid choice. Please choose again.")

    @staticmethod
    def non_empty(prompt):
        while True:
            user_input = input(prompt).strip()
            if user_input:
                return user_input
            else:
                print("Input cannot be empty. Please try again.")

    @staticmethod
    def validate_date(date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            return None


def main():
    records = Records()
    records.read_guests('guests.csv')
    records.read_products('products.csv')

    operations = Operations(records)

    operations.menu()

if __name__ == "__main__":
    main()
