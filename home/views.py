from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests
from joblib import load
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
import re

# Create your views here.
#Removal of HTML Contents
def remove_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

#Removal of Punctuation Marks
def remove_punctuations(text):
    return re.sub('\[[^]]*\]', '', text)

# Removal of Special Characters
def remove_characters(text):
    return re.sub("[^a-zA-Z]", " ", text)

#Removal of stopwords
def remove_stopwords_and_lemmatization(text):
    final_text = []
    text = text.lower()
    text = nltk.word_tokenize(text)

    for word in text:
        if word not in set(stopwords.words('english')):
            lemma = nltk.WordNetLemmatizer()
            word = lemma.lemmatize(word)
            final_text.append(word)
    return " ".join(final_text)

#Total function
def cleaning(text):
    text = remove_html(text)
    text = remove_punctuations(text)
    text = remove_characters(text)
    text = remove_stopwords_and_lemmatization(text)
    return text

def index(request):
    if(request.session.has_key('account_id')):
        content = {}
        content['title'] = 'Home'
        content['url'] = ''
        if(request.method == 'POST'):
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            model = load(str(BASE_DIR) + '/model/modelLGR.pkl')
            # https://www.flipkart.com/asus-zenfone-2-laser-ze550kl-black-16-gb/product-reviews/itme9j58yzyzqzgc?pid=MOBE9J587QGMXBB7
            url_link = request.POST['url']
            response = requests.get(url_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = soup.find_all('div', class_='col-12-12')
            reviews_list = []
            dict_data = {}
            for rv in reviews:
                data_bkp = rv.text
                data = rv.text
                data = data.replace('Permalink', '')
                data = data.replace('Report', '')
                data = data.replace('Abuse', '')
                data = data.replace('Certified Buyer', '')
                data = data.replace('READ MORE', '')
                data = data.replace('month', '')
                data = data.replace('days ago', '')
                data_cleaned = cleaning(data)
                predict_data = model.predict([data_cleaned])
                predicted_str = ''
                predicted_class = ''
                if predict_data == 1:
                    predicted_str = 'Genuine'
                    predicted_class = 'success'
                elif predict_data == 0:
                    predicted_str = 'Fake'
                    predicted_class = 'danger'
                else:
                    predicted_str = 'Cannot Say'
                    predicted_class = 'warning'
                dict_data = {'data': data_bkp, 'predict' : predicted_str, 'class' : predicted_class}
                reviews_list.append(dict_data)
            for i in range(0,11):
                reviews_list.pop(0)
            reviews_list_len = len(reviews_list)
            reviews_list.pop(reviews_list_len - 1)
            content['loaded_reviews'] = reviews_list
            content['url'] = url_link
            content['prediction'] = reviews_list
        return render(request, 'home/index.html', content)
    else:
        return HttpResponseRedirect(reverse('account-login'))

def about(request):
    if(request.session.has_key('account_id')):
        content = {}
        content['title'] = 'About'
        return render(request, 'home/about.html', content)
    else:
        return HttpResponseRedirect(reverse('account-login'))
