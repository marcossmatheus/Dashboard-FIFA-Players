from flask import Flask, render_template, jsonify, request, abort
import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html

# ─── Translation helpers ───────────────────────────────────────────────────────
_PT_COMMON_WORDS = {
    'de', 'do', 'da', 'dos', 'das', 'e', 'em', 'no', 'na', 'os', 'as',
    'que', 'com', 'para', 'por', 'um', 'uma', 'é', 'são', 'se', 'ao',
    'pelo', 'pela', 'após', 'será', 'seu', 'sua', 'vai', 'não', 'mais',
}

def _is_portuguese(text: str) -> bool:
    """Heuristic: text is likely Portuguese if it contains common PT words."""
    words = set(re.findall(r'[a-záéíóúàâêôãõüç]+', text.lower()))
    matches = words & _PT_COMMON_WORDS
    return len(matches) >= 1

def _translate_to_pt(text: str) -> str:
    """Translate *text* to Portuguese-BR using the MyMemory free API."""
    if not text or _is_portuguese(text):
        return text
    try:
        params = urllib.parse.urlencode({
            'q': text,
            'langpair': 'en|pt-BR',
        })
        url = f'https://api.mymemory.translated.net/get?{params}'
        req = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (compatible; TranslateBot/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
        translated = result.get('responseData', {}).get('translatedText', '')
        # MyMemory returns original text or error message on failure
        if translated and translated.upper() != text.upper() and 'MYMEMORY WARNING' not in translated:
            return translated
        return text
    except Exception:
        return text

app = Flask(__name__)

def get_players_data():
    with open('data/players.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    players = get_players_data()
    # Extract unique countries for the filter
    countries = sorted(list(set(p['country'] for p in players)))
    return render_template('index.html', players=players, countries=countries)

@app.route('/player/<player_id>')
def player_profile(player_id):
    players = get_players_data()
    player = next((p for p in players if p['id'] == player_id), None)
    if not player:
        abort(404)
        
    # Get other players for the comparison dropdown (exclude current)
    other_players = sorted([p for p in players if p['id'] != player_id], key=lambda x: x['name'])
    
    return render_template('player.html', player=player, other_players=other_players)

@app.route('/api/players')
def api_players():
    players = get_players_data()
    
    # Optional query parameters for filtering and sorting
    country = request.args.get('country')
    sort_by = request.args.get('sort_by')
    
    if country and country != 'All':
        players = [p for p in players if p['country'] == country]
        
    if sort_by == 'age':
        players = sorted(players, key=lambda x: x['age'])
    elif sort_by == 'name':
        players = sorted(players, key=lambda x: x['name'])
        
    return jsonify(players)

@app.route('/api/player/<player_id>')
def api_player(player_id):
    players = get_players_data()
    player = next((p for p in players if p['id'] == player_id), None)
    if player:
        return jsonify(player)
    return jsonify({"error": "Player not found"}), 404

@app.route('/api/player/<player_id>/news')
def api_player_news(player_id):
    """Fetches recent news for a player using Google News RSS feed in Brazilian Portuguese."""
    players = get_players_data()
    player = next((p for p in players if p['id'] == player_id), None)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    player_name = player['name']

    def fetch_rss(query_term):
        query = urllib.parse.quote(query_term)
        url = f'https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419'
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            return response.read()

    try:
        # First try search with player name and "futebol" for precise soccer news
        xml_data = None
        try:
            xml_data = fetch_rss(f'"{player_name}" futebol')
        except Exception:
            xml_data = None

        items = []
        if xml_data:
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            if channel is not None:
                items = channel.findall('item')

        # Fallback to searching just the name in pt-BR feed if no results
        if not items:
            try:
                xml_data = fetch_rss(f'"{player_name}"')
                if xml_data:
                    root = ET.fromstring(xml_data)
                    channel = root.find('channel')
                    if channel is not None:
                        items = channel.findall('item')
            except Exception:
                pass

        news = []
        for item in items[:5]:
            title_el = item.find('title')
            link_el = item.find('link')
            desc_el = item.find('description')
            date_el = item.find('pubDate')
            source_el = item.find('source')

            title = html.unescape(title_el.text) if title_el is not None and title_el.text else ''
            link = link_el.text if link_el is not None else '#'
            description = html.unescape(desc_el.text or '') if desc_el is not None else ''
            pub_date = date_el.text if date_el is not None else ''
            source = source_el.text if source_el is not None else 'Notícias'

            # Remove source suffix from Google News titles (e.g., " - ge" or " - Lance!")
            if ' - ' in title:
                parts = title.rsplit(' - ', 1)
                title = parts[0]
                if not source or source == 'Notícias':
                    source = parts[1]

            # Strip HTML tags and entities from description
            import re
            description = re.sub(r'<[^>]+>', '', description).strip().replace('\xa0', ' ')
            if source and description.endswith(source):
                description = description[:-len(source)].strip()
            # If description matches or contains just title, avoid repeating it identically
            if description == title:
                description = ''
            # Limit preview length
            if len(description) > 200:
                description = description[:197] + '...'

            # Translate title and description to Portuguese if needed
            title = _translate_to_pt(title)
            if description:
                description = _translate_to_pt(description)

            news.append({
                'title': title,
                'preview': description,
                'link': link,
                'date': pub_date,
                'source': source
            })

        return jsonify({"player": player_name, "news": news})

    except Exception as e:
        return jsonify({"player": player_name, "news": [], "error": str(e)}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
