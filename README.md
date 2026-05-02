# Auto-Completion (Auto-Suggest) Web Application

A complete auto-completion web application built with Flask, SQLite, HTML, CSS, and JavaScript.

## Features

- **Real-time Search**: Get instant suggestions as you type
- **Debounced Requests**: Optimized API calls with 300ms debouncing
- **Responsive Design**: Works on desktop and mobile devices
- **SQLite Database**: Sample product data included
- **Clean UI**: Modern gradient design with smooth animations

## Project Structure

```
autocomplete-python/
├── app.py                  # Flask backend
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore file
├── templates/
│   └── index.html        # Frontend HTML
└── static/
    ├── script.js         # JavaScript for autocomplete
    └── style.css         # Styling
```

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd autocomplete-python
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

The app will start on: **http://127.0.0.1:5000**

## Usage

1. Open your browser and go to `http://127.0.0.1:5000`
2. Start typing in the search box
3. Suggestions will appear automatically
4. Click on a suggestion to select it

## Sample Data

The database includes these sample products:
- apple
- application
- appetite
- banana
- bat
- ball
- cat
- car
- carbon

## API Endpoints

### GET /
Renders the main HTML page.

### GET /search?q=query
Returns autocomplete suggestions based on the query parameter.

**Parameters:**
- `q` (string): Search query

**Response:**
```json
["apple", "application", "appetite"]
```

## Technologies Used

- **Backend**: Flask 3.1.3
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Server**: Flask Development Server

## Features Explained

### Debouncing
The JavaScript implements 300ms debouncing to reduce API calls while the user is typing.

### Database Query
Uses SQL LIKE operator to search product names starting with the query:
```sql
SELECT name FROM products WHERE name LIKE 'query%' LIMIT 5
```

### Responsive UI
- Mobile-friendly design
- Smooth animations and transitions
- Hover effects on suggestions

## Future Enhancements

- Add user authentication
- Implement search history
- Add more sophisticated search algorithms
- Include product descriptions
- Add pagination for results
- Implement fuzzy matching

## License

This project is open source and available under the MIT License.

## Author

Created with ❤️ for learning Flask and Web Development.
