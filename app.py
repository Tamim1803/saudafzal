from flask import Flask, jsonify, request, render_template, send_from_directory
from serpapi import GoogleSearch
import time
import os

current_dir = os.getcwd()

# Initialize the Flask app with a custom template directory
app = Flask(__name__, template_folder=current_dir)

# Cache configuration
CACHE_DURATION = 6048  # Cache duration in seconds 

# Custom static file serving
@app.route('/<path:filename>')
def serve_static_files(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return "File not found", 404

class ScholarAPI:
    def __init__(self):
        self.api_key = "626809aa2306ed9f692097aca4621a59a25521a982fe46c9fae2b87017ee79cb"
        self.author_id = "f34uj7UAAAAJ"
        self.last_fetch_time = 0
        self.cached_data = None

    def get_scholar_data(self):
        current_time = time.time()
        # Check if cache is valid
        if self.cached_data and (current_time - self.last_fetch_time) < CACHE_DURATION:
            print("Returning cached data")
            return self.cached_data

        params = {
            "engine": "google_scholar_author",
            "author_id": self.author_id,
            "hl": "en",
            "num": "100",
            "sort": "pubdate",
            "api_key": self.api_key
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Print the raw data received from the API
            # print("Raw data from API:", results)

            # Format the data
            formatted_data = self._format_scholar_data(results)
            
            # Print the formatted data
            print("Formatted data:", formatted_data)

            # Update cache
            self.cached_data = formatted_data
            self.last_fetch_time = current_time
            
            return formatted_data
        except Exception as e:
            print(f"Error fetching scholar data: {e}")
            # Return cached data if available, otherwise return empty data
            return self.cached_data if self.cached_data else self._get_empty_data()

    def _format_scholar_data(self, results):
        # Extract author info
        author_info = results.get('author', {})
        
        # Format publications
        publications = []
        for article in results.get('articles', []):
            pub = {
                "title": article.get('title', ''),
                "authors": article.get('authors', ''),
                "journal": article.get('publication', ''),
                "year": article.get('year', ''),
                "citations": article.get('cited_by', {}).get('value', 0),
                "link": article.get('link', '')
            }
            publications.append(pub)

        # Construct full response
        return {
            "profile": {
                "name": author_info.get('name', ''),
                "affiliation": author_info.get('affiliations', ''),
                "email": author_info.get('email', ''),
                "interests": author_info.get('interests', []),
                "citations": {
                    "total": results.get('cited_by', {}).get('table', [{}])[0].get('citations', {}).get('all', 0),
                    "h_index": next((item.get('h_index', {}).get('all', 0) for item in results.get('cited_by', {}).get('table', []) if 'h_index' in item), 0),
                    "i10_index": next((item.get('i10_index', {}).get('all', 0) for item in results.get('cited_by', {}).get('table', []) if 'i10_index' in item), 0)

                }
            },
            "publications": publications
        }

    def _get_empty_data(self):
        return {
            "profile": {
                "name": "Mohammad Saud Afzal",
                "affiliation": "Indian Institute of Technology Kharagpur",
                "email": "Verified email at civil.iitkgp.ac.in",
                "interests": [],
                "citations": {"total": 0, "h_index": 0, "i10_index": 0}
            },
            "publications": []
        }

# Initialize Scholar API
scholar_api = ScholarAPI()

# Route to serve the HTML content
@app.route('/')
def index():
    return render_template('new_index.html')

@app.route('/<path:filename>')
def serve_static_file(filename):
    # Serve static files from the custom directory
    return send_from_directory('public_html', filename)

# API endpoint for publications with search and filter capabilities
@app.route('/api/publications')
def get_publications():
    data = scholar_api.get_scholar_data()
    publications = data['publications']
    
    search_term = request.args.get('search', '').lower()
    year_filter = request.args.get('year')
    
    # Apply search filter
    if search_term:
        publications = [
            pub for pub in publications
            if search_term in pub['title'].lower() or
               search_term in pub['authors'].lower() or
               search_term in pub['journal'].lower() or
               search_term in str(pub['year']).lower()
        ]
    
    # Apply year filter
    if year_filter:
        publications = [
            pub for pub in publications
            if str(pub['year']) == year_filter
        ]
    
    return jsonify(publications)

# Placeholder image endpoint
@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder_image(width, height):
    return f"Placeholder image {width}x{height}", 200

if __name__ == '__main__':
    app.run()
