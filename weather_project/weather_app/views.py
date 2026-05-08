from django.shortcuts import render
from django.contrib import messages
import requests
import datetime
from urllib.parse import quote
from decouple import config
import hashlib, json
from datetime import timedelta

def home(request):
    if request.method == 'POST':
        if 'city' in request.POST:
            city = request.POST.get('city')
            print(city)
        else:
            city = 'Chicago'
    my_waether_api = config('WEATHER_API_KEY')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={my_weather_api}'
    PARAMS ={'units': 'metric'}

    #API_KEY =  ''

    SEARCH_ENGINE_ID = ''
     
    query = city + " 1920x1080"
    page = 1
    start = (page - 1) * 10 + 1
    searchType = 'image'
    city_url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={searchType}&imgSize=xlarge"

    data = requests.get(city_url).json()
    count = 1
    search_items = data.get("items")
    image_url = search_items[1]['link']
    
    
    try:


        data = requests.get(url, PARAMS).json()

        description = data['weather'][0]['description']
        icon = data['weather'][0]['icon']
        temp = data['main']['temp']

        day = datetime.date.today() 

        return render(request, 'index.html',
                      {'description': description, 
                       'icon': icon, 
                       'temp': temp, 
                       'day': day, 'city': city, 'Exception_occurred': False}
                    ) 
    except:
        Exception_occurred = True
        messages.error(request, 'City not found in our database. Please try again.')
        day = datetime.date.today()
        return render(request, 'index.html',
                      {'description': 'Clear Sky', 
                       'icon': '01d', 
                       'temp': '25°C', 
                       'day': day, 'city':'Mexico City',
                       'Exception_occurred': Exception_occurred, 'image': 'https://cdn-icons-png.flaticon.com/512/1163/1163661.png'}
                    )

def home_enhanced(request):
    #---------------- Configuration ----------------#
    WEATHER_API_KEY = config('WEATHER_API_KEY')
    UNSPLASH_ACCESS_KEY = config('UNSPLASH_ACCESS_KEY')
    GROQ_API_KEY = config('GROQ_API_KEY')

    # Default values 
    city = 'Mexico City'
    if request.method == 'POST':
        city = request.POST.get('city', city)

    # ----- Default context -----
    context = {
        'city' : city,
        'temp': '25°C',
        'description': 'Clear Sky',
        'icon': '01d',
        'day': datetime.date.today(),
        'Exception_occurred': False,
        'image_url': 'https://images.pexels.com/photos/3008509/pexels-photo-3008509.jpeg?auto=compress&cs=tinysrgb&w=1600'
    }

    # ----- Fetch weather data -----
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    try: 
        response = requests.get(weather_url)
        response.raise_for_status()
        data = response.json()

        context['temp'] = data['main']['temp']
        context['description'] = data['weather'][0]['description']
        context['icon'] = data['weather'][0]['icon']
        context['day'] = datetime.date.today()
        
        ai_summary = None
        if not context['Exception_occurred']:
            ai_summary = get_ai_summary(context['city'], context['temp'], context['description'])

    except requests.exceptions.HTTPError as e:
        if response.status_code ==404:
            context['Exception_occurred'] = True
            messages.error(request, 'City not found in our database. Please try again.')
        else:
            context['Exception_occurred'] = True
            messages.error(request, 'An error occurred while fetching weather data. Please try again later.')
        return render(request, 'index.html', context)
    
    # ----- Fetch background image -----
    try:
        unsplash_url  = 'https://api.unsplash.com/search/photos'
        params = {
            'query': f'{city} city skyline',
            'client_id': UNSPLASH_ACCESS_KEY,
            'orientation': 'landscape',
            'per_page': 1,
        }
        img_response = requests.get(unsplash_url, params=params)
        img_response.raise_for_status()
        img_data = img_response.json()

        if img_data['results']:
            context['image_url'] = img_data['results'][0]['urls']['regular']
    except Exception:
        pass

    
            
    context = {
        'city': city,
        'temp': context['temp'],
        'description': context['description'],
        'icon': context['icon'],
        'day': context['day'],
        'image_url': context['image_url'],
        'ai_summary': ai_summary,
        'exception_occurred': context['Exception_occurred'],
    }

    if request.META.get('HTTP_HX_REQUEST'):
        return render(request, 'weather_partial.html', context)
    else:  
        return render(request, 'index.html', context)


def get_ai_summary(city, temp, description):
    """This function generates a friendly weather summary using Groq AI"""
    api_key = config('GROQ_API_KEY')
    url = 'https://api.groq.com/openai/v1/chat/completions'

    prompt = f"""
    The current weather in {city} is {temp}°C with {description}.
    Write a short, cheerful summary (2-4 sentences) for a weather app.
    Inlcude a suggestion on what to weat and a possible activity. Do not use emojis.
    Be elegant and concise.
    """

    headers ={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens":150,
        "temperature": 0.7,
    }

    try: 
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if not response.ok:
            print('Error status code:', response.status_code)
            print("Error response from AI API:", response.text)
            return None
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Error fetching AI summary:", str(e))
        return None


ai_cache={}
def get_ai_summary_cahe(city, temp, description):
    key = hashlib.md5(f"{city}_{temp}_{description}".encode()).hexdigest()
    now = datetime.datetime.now()
    if key in ai_cache:
        value, timestamp = ai_cache[key]
        if (now-timestamp).seconds < 3600:
            return value
    
    summary = get_ai_summary(city, temp, description)
    ai_cache[key] = (summary, now)
    return summary

