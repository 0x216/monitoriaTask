
---

# MonitoriaTask

A Django application for searching movies and actors from the ČSFD database of top 300 films.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation and Setup](#installation-and-setup)
- [Usage](#usage)

## Getting Started

Follow these steps to get the project up and running on your local machine

### Prerequisites

- Python
- pip

### Installation and Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/0x216/monitoriaTask.git
    cd monitoriaTask
    ```

2. **Set up a Virtual Environment**

    If you don't have `virtualenv` installed:

    ```bash
    pip install virtualenv
    ```

    Now, create and activate the virtual environment:

    ```bash
    virtualenv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    Install all the required packages and libraries:

    ```bash
    pip install -r requirements.txt
    ```

4. **Scrape Data from ČSFD**

    Populate the SQLite database by running:

    ```bash
    python manage.py csfd_scrapper
    ```

5. **Run the Django Server**

    ```bash
    python manage.py runserver
    ```

## Usage

Once the server is up:

1. Open your browser.
2. Navigate to [http://127.0.0.1:8000/search](http://127.0.0.1:8000/search).
3. Start searching for movies or actors

