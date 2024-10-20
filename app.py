from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/get_m4a', methods=['GET'])
def get_m4a():
    # Get the videoID from the request arguments
    ytvideo_id = request.args.get('videoID')
    
    if not ytvideo_id:
        return jsonify({"error": "No videoID provided"}), 400
    
    # Target URL
    url = f"https://video.genyt.net/{ytvideo_id}"
    
    # Headers to simulate a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # Send GET request to the page
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error retrieving the page: {e}"}), 500
    
    # Parse the HTML content
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        return jsonify({"error": f"Error parsing the page: {e}"}), 500
    
    # Find all div elements where the download links might be located
    divs = soup.find_all('div', class_='col-xl-3 col-lg-4 col-md-3 col-sm-4 col-6 mb-2')
    
    # Iterate through the divs and extract href if the download attribute ends with '.m4a'
    for div in divs:
        link_tag = div.find('a', download=True)  # Ensure 'download' attribute is present
        if link_tag and link_tag.get('download', '').endswith('.m4a' or '.mp4' or 'mp3'):
            href = link_tag.get('href')
            if href:
                return jsonify({"m4a_url": href}), 200
    
    # If no valid links are found, return a not found error
    return jsonify({"error": "No M4A format URLs found"}), 404

# Main entry point
if __name__ == '__main__':
    app.run(debug =True, port=5000)
