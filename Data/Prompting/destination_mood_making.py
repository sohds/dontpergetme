import json
import openai
import pandas as pd
import time

with open('ChatGPT_api_key.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    print(data)
    
def chat_gpt(city):
    openai.api_key = data['API_KEY']
    query = f"Can you give me a description focused on the characteristics of {city} as a tourist destination?"
    while True:
        try:
            print(city, 'query status: START')
            response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful tourist assistant."},
                {"role": "user", 
                "content": '''
                When describing a city as a tourist destination, please provide a detailed description that includes its historical landmarks, cultural significance, unique attractions, and overall atmosphere. 
                Make sure to highlight key places of interest, famous landmarks, and any distinctive features that contribute to the city's character.
                
                Here's an example that best represents the features of San Francisco as a tourist destination:
                San Francisco is a vibrant city known for its iconic landmarks, diverse culture, and picturesque landscapes. The Golden Gate Bridge, with its towering red-orange spires, is a must-see attraction, offering stunning views of the bay and the rugged Northern California coastline. Alcatraz Island, once a notorious federal prison, now serves as a fascinating historic site with panoramic views of the surrounding waters. Fisherman’s Wharf is a bustling area where visitors can enjoy fresh seafood, unique shopping experiences, and sea lion sightings at Pier 39. The city's famous cable cars provide a nostalgic way to explore its steep streets, offering spectacular views of diverse neighborhoods. Lombard Street, known as the “crookedest street in the world,” features eight sharp turns down a flower-lined hill, making it a popular spot for photos. San Francisco's Chinatown is the oldest in North America, offering a vibrant tapestry of Chinese cultural sites, authentic restaurants, and bustling markets. The Presidio, once a U.S. Army fort, is now a beautiful public park with miles of trails, scenic overlooks, and views of the Golden Gate Bridge. The Painted Ladies, a row of colorful Victorian houses, stand in charming contrast to the modern city skyline.
                
                Please use this format and style to describe the characteristics of {city} as a tourist destination.
                '''},
                {"role": "user", "content": query}
                ]
            )
            print(city, "query status: COMPLETE")
            print()
            return response.choices[0].message.content
    
        except openai.error.RateLimitError:
            print("Rate limit exceeded, waiting to retry...")
            time.sleep(5)


# Load your CSV file
cities_df = pd.read_csv('dataset/travel_destination_query.csv')

# Generate descriptions for each city
cities_df['City Mood'] = cities_df['city'].apply(chat_gpt)

# Save the updated DataFrame to a new CSV file
cities_df.to_csv('dataset/destination_mood.csv', index=False)