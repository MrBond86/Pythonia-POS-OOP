# Pythonia-POS-OOP
A Point of Sales (POS) system for Pythonia, a serviced apartment company managing three buildings—Swan, Goose, and Duck. This system allows booking managers to process apartment bookings (1-7 nights), manage supplementary item orders, and generate receipts for guests. It has different level as per new features added.
#Features
#PASS Level (Core Functionality)
  Guest Management: Add, view, and manage guests with unique IDs and reward points.
  Product Management: Track apartment units and supplementary items with unique IDs, names, and prices.
  Order Processing: Create and manage bookings, calculate costs, rewards, and generate formatted receipts.
  Centralized Records: Store and retrieve guest and product data from text files.
  CREDIT Level (Enhanced Functionality)
  Automatic calculation of booking duration and booking timestamp.
  Custom exception handling for input validation.
  Support for bundled products with discounts.
#DI Level (Advanced Features)
  Support for multi-product orders.
  Options to adjust global reward and redeem rates.
#HD Level (Premium Features)
  CSV-based order storage and reporting.
  Generate key business statistics (e.g., top guests, popular products).
  Support for command-line arguments to load guest, product, and order files.

#How to Use
    Clone the repository or download the code.
    Ensure guests.txt and products.txt files are present in the same directory.
    Run the program using Python:
    bash
    Copy code
    python ProgFunA2_<YourStudentID>.py  
    Follow the on-screen menu to perform operations like booking, viewing guests/products, and generating statistics.
