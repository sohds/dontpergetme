import json
import openai
import pandas as pd
import time

with open('ChatGPT_api_key.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    print(data)
    
def gpt_prompt_attractions(city):
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
                            
                            Here's an example that best represents the features of San Francisco as a tourist destination:
                            1. Golden Gate Bridge: Iconic and striking, the Golden Gate Bridge is a suspension bridge that spans the Golden Gate, the narrow strait where San Francisco Bay opens to the Pacific Ocean. Known for its towering red-orange spires and stunning architectural beauty, the bridge offers spectacular views of the rugged Northern California coastline.
                            2. Alcatraz Island: Located in the chilly waters of San Francisco Bay, Alcatraz Island is most famous for its former federal prison that once held notorious criminals. Today, it’s a fascinating historic site where visitors can learn about the prison’s storied past, explore the remnants, and enjoy panoramic views of the surrounding bay.
                            3. Fisherman’s Wharf: A bustling hub of activity, Fisherman's Wharf is famous for its historic waterfront, delicious seafood, unique shopping experiences, and sea lion sightings at Pier 39. It's a vibrant area that offers a glimpse into San Francisco's maritime heritage.
                            4. Cable Cars: An enduring symbol of San Francisco, the cable cars offer a nostalgic way to explore the steep streets of the city. Riding these historic trams provides not only a practical means of transportation but also spectacular views of the city’s diverse neighborhoods.
                            5. Lombard Street: Known as the “crookedest street in the world,” Lombard Street is famous for its eight sharp turns that zigzag down a steep, flower-lined hill. It's a popular spot for photographs and offers a quirky example of creative city planning.
                            6. Chinatown: San Francisco's Chinatown is the oldest in North America and one of the largest Chinese enclaves outside Asia. It's a vibrant tapestry of Chinese cultural sites, authentic restaurants, shops, temples, and bustling street scenes.
                            7. The Presidio: Once a U.S. Army military fort, the Presidio is now a stunning public park that is part of the Golden Gate National Recreation Area. It features forested areas, miles of walking trails, scenic overlooks, and views of the Golden Gate Bridge.
                            8. The Painted Ladies: One of the most photographed locations in San Francisco, the Painted Ladies are Victorian and Edwardian houses painted in multiple colors that enhance their architectural details. Set against the backdrop of the modern city skyline, they provide a charming contrast that symbolizes the city’s historical depth.
                        
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
cities_df['description'] = cities_df['city'].apply(gpt_prompt_attractions)

# Save the updated DataFrame to a new CSV file
cities_df.to_csv('dataset/travel_destination_query.csv', index=False)