Mechanic Shop API

A secure, production-style REST API built with Flask for managing customers, mechanics, service tickets, and inventory in an automotive repair shop. This API implements token authentication, rate limiting, caching, pagination, and relational database management using SQLAlchemy and MySQL.

-----

Features
    Authentication & Security
    - Token-based authentication using python-jose
    - Protected routes using Bearer Token authorization
    - Customer-specific access control
    - Rate limiting to prevent abuse (Flask-Limiter)
    - Cached routes to improve performance (Flask-Caching)


    Customer Management
    - Create, view, update, and delete customers
    - Customer login to generate authentication tokens
    - Pagination support for customer listings
    - Protected route to view a customer's service tickets

    Mechanic Management
    - Create, view, update, and delete mechanics
    - Leaderboard showing mechanics ranked by number of completed tickets
    - Many-to-many relationship with service tickets

    Service Ticket Management
    - Create and view service tickets
    - Assign and remove mechanics from tickets
    - Add and remove multiple mechanics in one request
    - Associate inventory parts with tickets

    Inventory Management
    - Full CRUD operations fo parts inventory
    - Many-to-many relationship between inventory and service tickets
    - Track parts used on service tickets

-----

Technologies Used

    Python 3.11+
    Flask
    Flask-SQLAlchemy
    Marshmallow
    MySQL
    Flask-Limiter
    Flask-Caching
    python-jose (JWT authentication)
    SQLAlchemy ORM
    Postman (API testing)

-----

Project Structure
mechanic_shop/
│
├── app/
│   ├── blueprints/
│   │   ├── customers/
│   │   ├── mechanics/
│   │   ├── service_tickets/
│   │   └── inventory/
│   │
│   ├── utils/
│   │   └── auth.py
│   │
│   ├── models.py
│   ├── extensions.py
│   └── __init__.py
│
├── run.py
├── requirements.txt
├── Mechanic Shop.postman_collection.json
├── .env
└── README.md

-----

Database Relationships
    Customer → ServiceTicket
        One-to-Many

    Mechanic ↔ ServiceTicket
        Many-to-Many

    Inventory ↔ ServiceTicket
        Many-to-Many

-----


Installation & Setup
1. Clone the repository
    git clone https://github.com/kwinsacowski/mechanic_shop_2_6_26_part2
    cd mechanic_shop

2. Create virtual environment
    python -m venv venv

Activate it:
    Windows:
        venv\Scripts\activate

    Mac/Linux:
        source venv/bin/activate

3. Install dependencies
        pip install -r requirements.txt

4. Configure environment variables
        Create a .env file in the root directory:
            DATABASE_URL=mysql+mysqlconnector://username:password@localhost/mechanic_shop
            SECRET_KEY=your_secret_key_here

5. Run the application
        python run.py

    Server runs at:
        http://127.0.0.1:5000

    Authentication
    Login
        POST /customers/login

    Request body:
        {
        "email": "customer@email.com"
        }

    Response:
        {
        "token": "your_jwt_token_here"
        }

    Use Token
        Include in headers:
            Authorization: Bearer your_token_here
 
-----
API Endpoints

    Customers
        Method	Endpoint	Description
        POST	/customers	Create customer
        GET	/customers	Get all customers (paginated)
        GET	/customers/<id>	Get customer
        PUT	/customers/<id>	Update customer
        DELETE	/customers/<id>	Delete customer
        POST	/customers/login	Login customer
        GET	/customers/my-tickets	Get customer's tickets
    Mechanics
        Method	Endpoint	Description
        POST	/mechanics	Create mechanic
        GET	/mechanics	Get mechanics
        PUT	/mechanics/<id>	Update mechanic
        DELETE	/mechanics/<id>	Delete mechanic
        GET	/mechanics/leaderboard/most-tickets	Leaderboard
    Service Tickets
        Method	Endpoint	Description
        POST	/service-tickets	Create ticket
        GET	/service-tickets	Get all tickets
        PUT	/service-tickets/<ticket_id>/edit	Add/remove mechanics
        PUT	/service-tickets/<ticket_id>/add-part/<inventory_id>	Add part
    Inventory
        Method	Endpoint	Description
        POST	/inventory	Create part
        GET	/inventory	Get parts
        PUT	/inventory/<id>	Update part
        DELETE	/inventory/<id>	Delete part

-----
Rate Limiting
    Default limits applied:
        200 requests per day
        50 requests per hour

-----
Caching
    Customer listing endpoint uses caching:
        GET /customers

    Cache duration:
        120 seconds

-----
Testing

Postman collection included:
    Mechanic Shop.postman_collection.json

Import into Postman to test all endpoints.

-----
Security Features
    JWT authentication
    Token validation middleware
    Route protection
    Rate limiting
    Environment variable configuration

-----

Author
    Kayla Salmon