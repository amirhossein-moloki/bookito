Here’s the improved and more visually appealing version of the project description in English:

---

# **Online Bookstore (Bookito)**

This project is an **Online Bookstore** built using **Django** and **Django REST Framework**. The source code for this project is open to the public, and you can submit a **Pull Request** to contribute changes.

---

## **Features**

- **User Management & Authentication** with **JWT**
- **Online Payment Integration** with **Zarinpal**
- **Postex & Zarinpal API Integration** (API keys required)
- **Order & Cart Management**
- **Book Categorization & Search**
- **API Documentation** using **Swagger** & **ReDoc**
- **Enhanced Security** including **CSRF**, **Secure Cookies**, and **HSTS**

---

## **Installation & Setup**

1. **Clone the repository:**
    ```bash
    git clone https://github.com/amirhossein-moloki/bookito.git
    cd bookito
    ```

2. **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Set up environment variables** (such as `DJANGO_SECRET_KEY`, `ZARINPAL_MERCHANT_ID`, and API keys for Postex & Zarinpal).

4. **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5. **Run the server:**
    ```bash
    python manage.py runserver
    ```

---

## **API Documentation**

After running the server, visit the following endpoints for API documentation:

- **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **ReDoc:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## **Contributing**

You can fork this repository and make your changes.

After making changes, submit a **Pull Request**.

For any inquiries or suggestions, feel free to contact me at:
- **Email:** [amirh.moloki@gmail.com](mailto:amirh.moloki@gmail.com)

---

## **License**

This project is open-source and free to use for everyone.