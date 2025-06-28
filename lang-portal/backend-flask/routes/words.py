from flask import request, jsonify, g
from flask_cors import cross_origin
import json
import sqlite3

def load(app):
  # Endpoint: POST /words to create a new word
  @app.route('/words', methods=['POST'])
  @cross_origin()
  def create_word():
    try:
      # Validate content type
      if request.content_type != 'application/json':
          return jsonify({
              'error': 'Content type must be application/json'
          }), 400

      # Get request data
      data = request.get_json()
      if not data:
          return jsonify({
              'error': 'Request body is required'
          }), 400

      # Required fields
      required_fields = ['kanji', 'romaji', 'english', 'parts']
      
      # Validate required fields
      for field in required_fields:
          if field not in data:
              return jsonify({
                  'error': f'Missing required field: {field}'
              }), 400

      # Validate parts is a valid JSON string
      try:
          parts = json.dumps(data['parts'])  # Convert to JSON string
      except (TypeError, ValueError):
          return jsonify({
              'error': 'Invalid JSON format for parts field'
          }), 400

      # Insert the word into the database
      cursor = app.db.cursor()
      cursor.execute('''
          INSERT INTO words (kanji, romaji, english, parts)
          VALUES (?, ?, ?, ?)
      ''', (data['kanji'], data['romaji'], data['english'], parts))
      word_id = cursor.lastrowid
      app.db.commit()

      # Initialize word review record
      cursor.execute('''
          INSERT INTO word_reviews (word_id)
          VALUES (?)
      ''', (word_id,))
      app.db.commit()

      # If groups are provided, associate the word with those groups
      if 'groups' in data and isinstance(data['groups'], list):
          for group_id in data['groups']:
              cursor.execute('''
                  INSERT INTO word_groups (word_id, group_id)
                  VALUES (?, ?)
              ''', (word_id, group_id))
          app.db.commit()

      return jsonify({
          'message': 'Word created successfully',
          'word_id': word_id
      }), 201

    except sqlite3.IntegrityError as e:
        app.db.rollback()
        return jsonify({
            'error': 'Database error: ' + str(e)
        }), 400
    except Exception as e:
        app.db.rollback()
        return jsonify({
            'error': str(e)
        }), 500
    finally:
        app.db.close()

  # Endpoint: GET /words with pagination (50 words per page)
  @app.route('/words', methods=['GET'])
  @cross_origin()
  def get_words():
    try:
      cursor = app.db.cursor()

      # Get the current page number from query parameters (default is 1)
      page = int(request.args.get('page', 1))
      # Ensure page number is positive
      page = max(1, page)
      words_per_page = 50
      offset = (page - 1) * words_per_page

      # Get sorting parameters from the query string
      sort_by = request.args.get('sort_by', 'kanji')  # Default to sorting by 'kanji'
      order = request.args.get('order', 'asc')  # Default to ascending order

      # Validate sort_by and order
      valid_columns = ['kanji', 'romaji', 'english', 'correct_count', 'wrong_count']
      if sort_by not in valid_columns:
        sort_by = 'kanji'
      if order not in ['asc', 'desc']:
        order = 'asc'

      # Query to fetch words with sorting
      cursor.execute(f'''
        SELECT w.id, w.kanji, w.romaji, w.english, 
            COALESCE(r.correct_count, 0) AS correct_count,
            COALESCE(r.wrong_count, 0) AS wrong_count
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        ORDER BY {sort_by} {order}
        LIMIT ? OFFSET ?
      ''', (words_per_page, offset))

      words = cursor.fetchall()

      # Query the total number of words
      cursor.execute('SELECT COUNT(*) FROM words')
      total_words = cursor.fetchone()[0]
      total_pages = (total_words + words_per_page - 1) // words_per_page

      # Format the response
      words_data = []
      for word in words:
        words_data.append({
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"]
        })

      return jsonify({
        "words": words_data,
        "total_pages": total_pages,
        "current_page": page,
        "total_words": total_words
      })

    except Exception as e:
      return jsonify({"error": str(e)}), 500
    finally:
      app.db.close()

  # Endpoint: GET /words/:id to get a single word with its details
  @app.route('/words/<int:word_id>', methods=['GET'])
  @cross_origin()
  def get_word(word_id):
    try:
      cursor = app.db.cursor()
      
      # Query to fetch the word and its details
      cursor.execute('''
        SELECT w.id, w.kanji, w.romaji, w.english,
               COALESCE(r.correct_count, 0) AS correct_count,
               COALESCE(r.wrong_count, 0) AS wrong_count,
               GROUP_CONCAT(DISTINCT g.id || '::' || g.name) as groups
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        LEFT JOIN word_groups wg ON w.id = wg.word_id
        LEFT JOIN groups g ON wg.group_id = g.id
        WHERE w.id = ?
        GROUP BY w.id
      ''', (word_id,))
      
      word = cursor.fetchone()
      
      if not word:
        return jsonify({"error": "Word not found"}), 404
      
      # Parse the groups string into a list of group objects
      groups = []
      if word["groups"]:
        for group_str in word["groups"].split(','):
          group_id, group_name = group_str.split('::')
          groups.append({
            "id": int(group_id),
            "name": group_name
          })
      
      return jsonify({
        "word": {
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"],
          "groups": groups
        }
      })
      
    except Exception as e:
      return jsonify({"error": str(e)}), 500