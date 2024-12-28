import requests
import pandas as pd
from urllib.parse import quote

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    try:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        auth_response.raise_for_status()
        auth_data = auth_response.json()
        return auth_data['access_token']
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

# Function to search for a track and get its ID
def search_track(track_name, artist_name, token):
    try:
        query = f"{quote(track_name)} artist:{quote(artist_name)}"
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
        response.raise_for_status()
        json_data = response.json()
        first_result = json_data['tracks']['items'][0]
        return first_result['id']
    except (KeyError, IndexError, Exception) as e:
        print(f"Error searching track '{track_name}' by '{artist_name}': {e}")
        return None

# Function to get track details
def get_track_details(track_id, token):
    try:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
        response.raise_for_status()
        json_data = response.json()
        image_url = json_data.get('album', {}).get('images', [{}])[0].get('url', None)
        return image_url
    except Exception as e:
        print(f"Error fetching details for track ID {track_id}: {e}")
        return None

# Your Spotify API credentials
client_id = 'd49c126f8c284599bb6d7f6f8a190a94'
client_secret = '9f8bcd7ff17a437188a8fdf46752992c'

# Get Access Token
access_token = get_spotify_token(client_id, client_secret)
if not access_token:
    raise Exception("Failed to retrieve Spotify token.")



# Mapping of accented/special characters to their unaccented equivalents
char_map = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'ñ': 'n', 'Ñ': 'N','ý':'y' , '$':'s',
    'ç': 'c', 'Ç': 'C',
    'ü': 'u', 'Ü': 'U',
    'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
    'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
    'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
    'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U'
}

# Function to replace all mapped characters in a string
def replace_foreign_chars(text):
    if isinstance(text, str):
        for char, replacement in char_map.items():
            text = text.replace(char, replacement)
    return text



# Read your DataFrame
df_spotify = pd.read_csv('data\Most Streamed Spotify Songs 2024.csv', encoding='latin1')
# Apply the replacement to the entire DataFrame
df_spotify= df_spotify.applymap(replace_foreign_chars)

# Add image URLs to the DataFrame
image_urls = []
for i, row in df_spotify.iterrows():
    track_id = search_track(row.get('Track'), row.get('Artist'), access_token)
    if track_id:
        image_urls.append(get_track_details(track_id, access_token))
    else:
        image_urls.append(None)

df_spotify['image_url'] = image_urls

# Save the updated DataFrame
df_spotify.to_csv('/data/spotified_upload.csv', index=False)
