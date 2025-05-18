import streamlit as st
import lxml
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import openai
from datetime import datetime
import csv
import pandas as pd
import pickle
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def main():
    st.set_page_config(page_title="CrickBUDDY", page_icon="🏏")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Home", "Live Scores", "Schedule", "Player Search"])
    
    if page == "Home":
        st.title("🏏 CrickBUDDY")
        st.write("Your one-stop destination for live scores, player stats, and match schedules")
        
    elif page == "Live Scores":
        st.title("Live Matches")
        live_matches = get_live_matches()
        for match in live_matches:
            st.write(match)
            
    elif page == "Schedule":
        st.title("Upcoming Matches")
        matches = get_schedule()
        for match in matches:
            st.write(match)
            
    elif page == "Player Search":
        st.title("Player Search")
        player_name = st.text_input("Enter player name")
        if player_name:
            player_data = get_player_stats(player_name)
            if "error" in player_data:
                st.error(player_data["error"])
            else:
                display_player_stats(player_data)

def get_live_matches():
    link = "https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")
    
    page = page.find("div", class_="cb-col cb-col-100 cb-bg-white")
    matches = page.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")
    
    return [match.text.strip() for match in matches]

def get_schedule():
    link = "https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")
    
    match_containers = page.find_all("div", class_="cb-col-100 cb-col")
    matches = []
    
    for container in match_containers:
        date = container.find("div", class_="cb-lv-grn-strip text-bold")
        match_info = container.find("div", class_="cb-col-100 cb-col")
        
        if date and match_info:
            match_date = date.text.strip()
            match_details = match_info.text.strip()
            matches.append(f"{match_date} - {match_details}")
    
    return matches

def get_player_stats(player_name):
    query = f"{player_name} cricbuzz"
    profile_link = None
    try:
        results = search(query, num_results=5)
        for link in results:
            if "cricbuzz.com/profiles/" in link:
                profile_link = link
                print(f"Found profile: {profile_link}")
                break
                
        if not profile_link:
            return {"error": "No player profile found"}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
    
    # Get player profile page
    c = requests.get(profile_link).text
    cric = BeautifulSoup(c, "lxml")
    profile = cric.find("div", id="playerProfile")
    pc = profile.find("div", class_="cb-col cb-col-100 cb-bg-white")
    
    # Name, country, and image
    name = pc.find("h1", class_="cb-font-40").text
    country = pc.find("h3", class_="cb-font-18 text-gray").text
    image_url = None
    images = pc.findAll('img')
    for image in images:
        image_url = image['src']
        break  # Just get the first image

    # Personal information and rankings
    personal = cric.find_all("div", class_="cb-col cb-col-60 cb-lst-itm-sm")
    role = personal[2].text.strip()
    
    icc = cric.find_all("div", class_="cb-col cb-col-25 cb-plyr-rank text-right")
    # Batting rankings
    tb = icc[0].text.strip()   # Test batting
    ob = icc[1].text.strip()   # ODI batting
    twb = icc[2].text.strip()  # T20 batting
    
    # Bowling rankings
    tbw = icc[3].text.strip()  # Test bowling
    obw = icc[4].text.strip()  # ODI bowling
    twbw = icc[5].text.strip() # T20 bowling

    # Summary of the stats
    summary = cric.find_all("div", class_="cb-plyr-tbl")
    batting = summary[0]
    bowling = summary[1]

    # Batting statistics
    bat_rows = batting.find("tbody").find_all("tr")
    batting_stats = {}
    for row in bat_rows:
        cols = row.find_all("td")
        format_name = cols[0].text.strip().lower()  # e.g., "Test", "ODI", "T20"
        batting_stats[format_name] = {
            "matches": cols[1].text.strip(),
            "runs": cols[3].text.strip(),
            "highest_score": cols[5].text.strip(),
            "average": cols[6].text.strip(),
            "strike_rate": cols[7].text.strip(),
            "hundreds": cols[12].text.strip(),
            "fifties": cols[11].text.strip(),
        }

    # Bowling statistics
    bowl_rows = bowling.find("tbody").find_all("tr")
    bowling_stats = {}
    for row in bowl_rows:
        cols = row.find_all("td")
        format_name = cols[0].text.strip().lower()  # e.g., "Test", "ODI", "T20"
        bowling_stats[format_name] = {
            "balls": cols[3].text.strip(),
            "runs": cols[4].text.strip(),
            "wickets": cols[5].text.strip(),
            "best_bowling_innings": cols[9].text.strip(),
            "economy": cols[7].text.strip(),
            "five_wickets": cols[11].text.strip(),
        }

    # Create player stats dictionary
    player_data = {
        "name": name,
        "country": country,
        "image": image_url,
        "role": role,
        "rankings": {
            "batting": {
                "test": tb,
                "odi": ob,
                "t20": twb
            },
            "bowling": {
                "test": tbw,
                "odi": obw,
                "t20": twbw
            }
        },
        "batting_stats": batting_stats,
        "bowling_stats": bowling_stats
    }

    return jsonify(player_data)


@app.route('/schedule')
def schedule():
    link = f"https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    # Find all match containers
    match_containers = page.find_all("div", class_="cb-col-100 cb-col")

    matches = []

    # Iterate through each match container
    for container in match_containers:
        # Extract match details
        date = container.find("div", class_="cb-lv-grn-strip text-bold")
        match_info = container.find("div", class_="cb-col-100 cb-col")
        
        if date and match_info:
            match_date = date.text.strip()
            match_details = match_info.text.strip()
            matches.append(f"{match_date} - {match_details}")
    
    return jsonify(matches)


@app.route('/live')
def live_matches():
    link = f"https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    page = page.find("div",class_="cb-col cb-col-100 cb-bg-white")
    matches = page.find_all("div",class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    live_matches = []

    for i in range(len(matches)):
        live_matches.append(matches[i].text.strip())
    
    return jsonify(live_matches)





# Step 1: Read the CSV file and fetch player details
# Remove or comment out this line since it's being overwritten
# openai.api_key = 'your-openai-api-key'  

def get_team_lineup(team_name):
    team_lineup = {
        "batsmen": [],
        "wicketkeepers": [],
        "allrounders": [],
        "fast_bowlers": [],
        "spinners": []
    }
    
    try:
        print(f"Attempting to read lineup for team: {team_name}")
        with open('ipl_team_lineups.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Team'].upper() == team_name.upper():
                    team_lineup[row['Role']].append(row['Player'])
                    print(f"Added player {row['Player']} as {row['Role']}")
        
        if all(len(players) == 0 for players in team_lineup.values()):
            print(f"Warning: No players found for team {team_name}")
            
    except FileNotFoundError:
        print(f"Error: ipl_team_lineups.csv not found in {os.getcwd()}")
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
    
    return team_lineup

# Step 2: Generate Dream11 team using OpenAI
def generate_dream11_team(team1_lineup, team2_lineup, match_date, team1, team2):
    # Check if API key exists
    if not os.getenv('OPENAI_API_KEY'):
        return "Error: OpenAI API key not found in environment variables"

    prompt = f"""
    Given the upcoming match details for {team1} vs {team2} on {match_date}, please provide:

    1. Best Dream11 Team Selection (11 players) from the following playing XIs:
    - {team1}: {', '.join(team1_lineup['batsmen'] + team1_lineup['wicketkeepers'] + team1_lineup['allrounders'] + team1_lineup['fast_bowlers'] + team1_lineup['spinners'])}
    - {team2}: {', '.join(team2_lineup['batsmen'] + team2_lineup['wicketkeepers'] + team2_lineup['allrounders'] + team2_lineup['fast_bowlers'] + team2_lineup['spinners'])}
    - Consider current form, recent performances, and pitch conditions.
    - Include player roles (Captain, Vice-Captain).
    - Prioritize players who are likely to score maximum Dream11 points:
      * Batting points (Runs, Strike Rate, Boundaries)
      * Bowling points (Wickets, Economy Rate)
      * Fielding points (Catches, Run-outs, Stumpings)
      * Bonus points for milestones

    2. Team Analysis:
    - Recent form of key players
    - Head-to-head statistics
    - Performance at the venue
    - Current injuries or availability issues
    - Impact of playing conditions

    Please provide the Dream11 team selection with point predictions and justification for Captain/Vice-Captain choices.
    """

    try:
        client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert cricket analyst and Dream11 specialist with deep knowledge of current cricket statistics, player forms, and match conditions. You excel at predicting player performances and creating optimal Dream11 teams based on recent data, pitch conditions, and historical matchups."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        if not response.choices or not response.choices[0].message:
            return "Error: No response received from OpenAI API"
            
        answer = response.choices[0].message.content
        return answer
    except openai.error.AuthenticationError:
        return "Error: Invalid OpenAI API key"
    except openai.error.RateLimitError:
        return "Error: OpenAI API rate limit exceeded"
    except Exception as e:
        return f"Error generating Dream11 team: {str(e)}"

# Step 3: API route to get the Dream11 team based on user input
@app.route('/predict-playing-xi', methods=['POST'])
def predict_playing_xi():
    try:
        print("Received predict-playing-xi request")
        data = request.json
        if not data:
            print("No data provided in request")
            return jsonify({"error": "No data provided"}), 400
            
        match_date = data.get('date')
        team1 = data.get('team1')
        team2 = data.get('team2')

        print(f"Processing request for teams: {team1} vs {team2} on {match_date}")

        if not match_date or not team1 or not team2:
            print("Missing required fields")
            return jsonify({"error": "Date and team names are required"}), 400

        # Get team lineups from the CSV file
        team1_lineup = get_team_lineup(team1)
        team2_lineup = get_team_lineup(team2)

        print(f"Team 1 lineup count: {sum(len(players) for players in team1_lineup.values())}")
        print(f"Team 2 lineup count: {sum(len(players) for players in team2_lineup.values())}")

        # Check if lineups are empty
        if all(len(players) == 0 for players in team1_lineup.values()):
            print(f"No players found for team {team1}")
            return jsonify({"error": f"No players found for team {team1}"}), 404
        if all(len(players) == 0 for players in team2_lineup.values()):
            print(f"No players found for team {team2}")
            return jsonify({"error": f"No players found for team {team2}"}), 404

        # Generate Dream11 team using OpenAI
        print("Generating Dream11 team...")
        dream11_team = generate_dream11_team(team1_lineup, team2_lineup, match_date, team1, team2)
        
        print(f"Dream11 team generation result type: {type(dream11_team)}")
        print(f"Dream11 team starts with error?: {dream11_team.startswith('Error:') if isinstance(dream11_team, str) else False}")

        # Check if there was an error in generation
        if isinstance(dream11_team, str) and dream11_team.startswith("Error:"):
            print(f"Error in Dream11 generation: {dream11_team}")
            return jsonify({"error": dream11_team}), 500
            
        return jsonify({"result": dream11_team})
        
    except Exception as e:
        print(f"Unexpected error in predict_playing_xi: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/predict-win', methods=['POST'])
def predict_win():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['batting_team', 'bowling_team', 'city', 'target', 'score', 'wickets', 'overs']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
        # Validate numeric fields
        try:
            target = float(data.get('target', 0))
            score = float(data.get('score', 0))
            wickets = int(data.get('wickets', 0))
            overs = float(data.get('overs', 0))
            
            if target <= 0 or score < 0 or wickets < 0 or overs < 0 or overs > 20:
                return jsonify({'error': 'Invalid numeric values provided'}), 400
                
        except ValueError:
            return jsonify({'error': 'Invalid numeric values provided'}), 400

        pipe = pickle.load(open('pipe.pkl', 'rb'))
        
        batting_team = data.get('batting_team')
        bowling_team = data.get('bowling_team')
        selected_city = data.get('city')
        target = data.get('target')
        score = data.get('score')
        wickets = data.get('wickets')
        overs = data.get('overs')
        
        runs_left = target - score
        balls_left = 120 - (overs * 6)
        wickets = 10 - wickets
        crr = score / overs
        rrr = (runs_left * 6) / balls_left
        
        df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [wickets],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })
        
        result = pipe.predict_proba(df)
        batting_team_prob = round(result[0][1] * 100)
        bowling_team_prob = round(result[0][0] * 100)
        
        return jsonify({
            'batting_team': batting_team,
            'bowling_team': bowling_team,
            'batting_team_probability': batting_team_prob,
            'bowling_team_probability': bowling_team_prob
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)