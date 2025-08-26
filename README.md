# Bookito - Online Bookstore

**Bookito** is a comprehensive online bookstore platform developed with Django and Django REST Framework. It provides a robust backend for managing books, authors, customers, and orders, with a secure and well-documented API.

---

## Features

- **User Management**: Secure user authentication and authorization using JWT.
- **Product Management**: Easily manage books, authors, genres, and publishers.
- **Order Processing**: A complete system for handling customer orders, carts, and payments.
- **Payment Integration**: Seamlessly integrated with Zarinpal for online payments.
- **API Documentation**: Automatically generated and interactive API documentation with Swagger and ReDoc.
- **Search and Filtering**: Advanced search capabilities to find books by title, author, or genre.
- **Recommendations**: A recommendation engine to suggest books to users.
- **Security**: Built-in security features such as CSRF protection, secure cookies, and HSTS.

---

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL (or SQLite for development)
- **Authentication**: Simple JWT for token-based authentication
- **API Documentation**: drf-yasg for Swagger and ReDoc generation
- **Payment Gateway**: zarinpal-python-sdk
- **Other Libraries**: A full list of dependencies can be found in the `requirements.txt` file.

---

## Project Structure

The project is organized into several Django apps, each with a specific responsibility:

- `accounts`: Manages user accounts, authentication, and profiles.
- `address`: Handles user addresses.
- `authors`: Manages book authors.
- `books`: Contains models and logic for books, including details, pricing, and stock.
- `customers`: Manages customer information, carts, and orders.
- `dashboard`: Provides an admin dashboard for managing the store.
- `discounts`: Handles discount codes and promotions.
- `genres`: Manages book genres.
- `publishers`: Manages book publishers.
- `recommendations`: Powers the book recommendation engine.
- `reviews`: Allows users to submit reviews for books.
- `translators`: Manages book translators.

---

## Installation and Setup

### Local Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/amirhossein-moloki/bookito.git
    cd bookito
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**:
    Create a `.env` file in the project root and add the necessary environment variables. You can use `.env.new` as a template.

5.  **Apply database migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server**:
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

---

### Running with Docker (Recommended)

This project is fully containerized with Docker. To run it, make sure you have Docker and Docker Compose installed.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/amirhossein-moloki/bookito.git
    cd bookito
    ```

2.  **Configure environment variables**:
    Create a `.env.docker` file by copying the provided template:
    ```bash
    cp .env.example.docker .env.docker
    ```
    Then, open the `.env.docker` file and fill in your actual secret keys and other configurations.

3.  **Build and run the application**:
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images and start the application and database services. The web application will be available at `http://localhost:8000`.

4.  **Stopping the application**:
    To stop the services, press `CTRL+C` in the terminal where `docker-compose` is running, or run the following command in another terminal:
    ```bash
    docker-compose down
    ```

---

## API Documentation

Once the server is running, you can access the API documentation at the following endpoints:

-   **Swagger UI**: `http://127.0.0.1:8000/swagger/`
-   **ReDoc**: `http://127.0.0.1:8000/redoc/`

---

## Contributing

Contributions are welcome! If you have any suggestions or want to improve the project, please fork the repository and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
