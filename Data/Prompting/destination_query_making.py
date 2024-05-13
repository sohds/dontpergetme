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
                            When a tourist attraction is suggested, Please provide a description focused on the characteristics of each tourist attraction.
                            
                            Here's an example that best represents the features of New York as a tourist destination:
                            1. The Statue of Liberty. Located in New York Harbor, this massive statue symbolizes America's freedom and independence.
                            2. Times Square. One of the most famous squares in the world, it is a symbolic place of New York.
                            3. Empire State Building. One of the most famous landmarks in the world, it provides a beautiful view.
                            4. Brooklyn Bridge. An iconic bridge connecting Brooklyn and Manhattan, it offers beautiful architecture and scenery.
                            5. Museums. New York is rich in world-renowned museums, including the Metropolitan Museum, Guggenheim Museum, art galleries, and other museums.
                            6. The fresh smell of grass in Central Park, the scent of fallen leaves in autumn, and the fragrance of blooming flowers in spring add a touch of nature to the city. Also, the fresh sea smell coming from the Hudson River momentarily makes you forget the noise and hustle of the city.
                        
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
cities_df = pd.read_csv('../Crawling/dataset/travel-destination/travel_destination.csv')

# Generate descriptions for each city
cities_df['description'] = cities_df['city'].apply(chat_gpt)

# Save the updated DataFrame to a new CSV file
cities_df.to_csv('travel_destination_query.csv', index=False)