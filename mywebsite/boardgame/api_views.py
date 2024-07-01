import requests
from django.http import JsonResponse
import xml.etree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search_games(request):
    query = request.GET.get('query', '').lower()

    if query:
        url = f'https://www.boardgamegeek.com/xmlapi/search?search={query}&type=boardgame'
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            exact_matches = []
            partial_matches = []

            for item in root.findall('boardgame'):
                name_elem = item.find('name')
                year_elem = item.find('yearpublished')  # Extract publication year
                if name_elem is not None:
                    game_name = name_elem.text
                    game = {
                        'id': item.attrib['objectid'],
                        'name': game_name,
                        'year': year_elem.text if year_elem is not None else 'N/A'  # Handle missing year
                    }
                    if game_name.lower().startswith(query):
                        exact_matches.append(game)
                    elif query in game_name.lower():
                        partial_matches.append(game)

            # Combine exact matches and partial matches, with exact matches first
            games = exact_matches + partial_matches
            return JsonResponse(games, safe=False)

    return JsonResponse({'error': 'BGG API error'}, status=400)


@csrf_exempt
def game_details(request):
    game_id = request.GET.get('game_id', '')

    if game_id:
        url = f'https://www.boardgamegeek.com/xmlapi/boardgame/{game_id}?stats=1'
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            item = root.find('boardgame')
            
            game = {
                'id': item.attrib['objectid'],
                'name': '',
                'description': '',
                'min_players': '',
                'max_players': '',
                'min_playtime': '',
                'max_playtime': '',
                'age': '',
                'weight': '',
            }
            
            if item is not None:
                # Retrieve primary name if available
                primary_name = ''
                for name_elem in item.findall('name'):
                    if name_elem.attrib.get('primary', '') == 'true':
                        primary_name = name_elem.text
                        break
                
                game['name'] = primary_name if primary_name else ''
                game['description'] = item.find('description').text if item.find('description') is not None else ''
                game['min_players'] = item.find('minplayers').text if item.find('minplayers') is not None else ''
                game['max_players'] = item.find('maxplayers').text if item.find('maxplayers') is not None else ''
                game['age'] = item.find('age').text if item.find('age') is not None else ''

                # Extract and format weight to two decimal places
                weight_elem = item.find('statistics').find('ratings').find('averageweight')
                if weight_elem is not None:
                    try:
                        weight = float(weight_elem.text)
                        game['weight'] = '{:.2f}'.format(weight)
                    except ValueError:
                        game['weight'] = ''
                        
                # Check for minplaytime and maxplaytime first
                min_playtime_elem = item.find('minplaytime')
                max_playtime_elem = item.find('maxplaytime')
                if min_playtime_elem is not None and max_playtime_elem is not None:
                    game['min_playtime'] = min_playtime_elem.text
                    game['max_playtime'] = max_playtime_elem.text
                else:
                    # If minplaytime and maxplaytime are not available, use playingtime
                    game['min_playtime'] = item.find('playingtime').text if item.find('playingtime') is not None else ''
          
            return JsonResponse(game, safe=False)

    return JsonResponse({'error': 'No game_id provided or BGG API error'}, status=400)
