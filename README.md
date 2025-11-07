# SHL-Assessment-Recommender

An AI-powered tool that recommends relevant SHL assessments based on query or a job description. It scrapes product data from SHL's official catalog and uses NLP techniques (TF-IDF + cosine similarity) for intelligent recommendations.

## Features

- Scrapes SHL assessment data including description, duration, and test type.
- REST API using **FastAPI** to handle recommendations.
- Frontend built with **Streamlit** for interactive querying.
- Supports similarity-based retrieval using **TF-IDF** and **cosine similarity**.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/itsmohitnamdeo/SHL-Assessment-Recommender.git
cd SHL-Assessment-Recommender
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Scrape Product Data

Use the scraper to fetch product data from SHL's catalog (approx. 500 items by default):

```bash
python product_catalog.py
```

> This will generate a file `product_catalog.csv`.


## Run the API

Start the FastAPI backend:

```bash
uvicorn api:app --reload --port 8000
```

* Test: Visit [http://localhost:8000/health](http://localhost:8000/health)
* Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)


## Launch the Streamlit App

Start the frontend in a new terminal:

```bash
streamlit run app.py
```

* Visit [http://localhost:8501](http://localhost:8501) to use the recommender.

## Screenshots

- SHL-Assessment-Recommender

<img width="1366" height="726" alt="shl_assessment_reommender" src="https://github.com/user-attachments/assets/840b73dd-dfff-40a2-b157-71c3fd7b5ee2" />


## API Requests

- /health

<img width="385" height="203" alt="health" src="https://github.com/user-attachments/assets/8d536a62-c5ef-41f9-a36e-6dda00034561" />


- /recommend

<img width="1357" height="729" alt="recommend" src="https://github.com/user-attachments/assets/a69bc1c7-eecd-400f-bf0c-89f4c5d21fc0" />

<img width="1366" height="726" alt="shl_assessment_reommender" src="https://github.com/user-attachments/assets/a6855e0f-ca6f-4df0-b453-981c77bd20d4" />


## Contact

If you have any questions, suggestions, or need assistance related to the SHL-Assessment-Recommender, feel free to reach out to Me.

- MailId - namdeomohit198@gmail.com
- Mob No. - 9131552292
- Portfolio : https://itsmohitnamdeo.github.io
- Linkedin : https://www.linkedin.com/in/mohit-namdeo
