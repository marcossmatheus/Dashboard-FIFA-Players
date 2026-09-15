from flask import Flask, render_template, jsonify, request, abort
import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html

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
    """Fetches recent news for a player using Google News RSS feed."""
    players = get_players_data()
    player = next((p for p in players if p['id'] == player_id), None)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    player_name = player['name']
    query = urllib.parse.quote(f'"{player_name}" football soccer')
    url = f'https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en'

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        items = channel.findall('item') if channel is not None else []

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
            source = source_el.text if source_el is not None else 'News'

            # Strip HTML tags from description if any
            import re
            description = re.sub(r'<[^>]+>', '', description).strip()
            # Limit preview length
            if len(description) > 200:
                description = description[:197] + '...'

            # Remove source suffix from Google News titles (e.g., " - BBC Sport")
            if ' - ' in title:
                parts = title.rsplit(' - ', 1)
                title = parts[0]
                if not source or source == 'News':
                    source = parts[1]

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
    app.run(debug=True, port=5000)
