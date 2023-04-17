FROM python:3.9


WORKDIR /app

RUN apt-get update && apt-get install -y portaudio19-dev

COPY requirements.txt ./requirements.txt


RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "vanban_google.py"]