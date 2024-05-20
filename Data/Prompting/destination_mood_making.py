import json
import openai
import pandas as pd
import time

with open('ChatGPT_api_key.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    print(data)
    
def gpt_prompt_citymood(city):
    openai.api_key = data['API_KEY']
    query = f"Can you give me a description focused on the characteristics of {city} as a tourist destination?"
    index = 1
    while True:
        try:
            print(f"{index}. {city}'s Mood Query status: START")
            response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful tourist assistant."},
                {"role": "user", 
                "content": '''
                When describing a city as a tourist destination, please provide a detailed description that includes its overall atmosphere, historical and cultural significance, and any distinctive features that contribute to the city's character.

                Here's an example that best represents the features of New York as a tourist destination:
    
                    New York City, often referred to as "The Big Apple," is a vibrant metropolis known for its fast-paced lifestyle, iconic skyline, and cultural diversity. 
                    The city's atmosphere is electric, with bustling streets, bright lights, and an ever-present sense of movement. 
                    Its skyline is dominated by towering skyscrapers, including the Empire State Building and One World Trade Center. 
                    Times Square epitomizes the energy of the city, with its dazzling lights and bustling crowds. 
                    Central Park provides a green oasis amidst the urban landscape, offering a place for relaxation and recreation. 
                    The Statue of Liberty stands as a symbol of freedom and democracy, welcoming visitors from around the world. 
                    New York is also renowned for its cultural institutions, such as the Metropolitan Museum of Art and Broadway theaters, where world-class performances take place. 
                    The diverse neighborhoods, from the historic charm of Greenwich Village to the vibrant streets of Chinatown, reflect the city's multicultural fabric. 
                    The fast-paced atmosphere, coupled with the city's role as a global hub for finance, fashion, and media, creates a unique and dynamic environment.

                Please use this format and style to describe the characteristics of {city} as a tourist destination.
             '''},
                {"role": "user", "content": query}
                ]
            )
            print(f"{index}. {city}'s Mood Query status: COMPLETE")
            print()
            index += 1
            return response.choices[0].message.content
    
        except openai.error.RateLimitError:
            print("Rate limit exceeded, waiting to retry...")
            time.sleep(5)


# Load your CSV file
cities_df = pd.read_csv('dataset/travel_destination_query.csv')

# Generate descriptions for each city
cities_df['City Mood'] = cities_df['city'].apply(gpt_prompt_citymood)

# Save the updated DataFrame to a new CSV file
cities_df.to_csv('dataset/destination_mood.csv', index=False)