import csv
from flask import Flask

# Data for IPL Teams
teams_data = {
    "CSK": {
        "batsmen": ["Rahul Tripathi", "Shreyas Gopal", "Shaik Rasheed", "Anshul Kamboj", "Andre Siddharth"],
        "wicketkeepers": ["MS Dhoni", "Vansh Bedi"],
        "allrounders": ["Ravindra Jadeja", "Shivam Dube", "Rachin Ravindra", "Ravichandran Ashwin", "Deepak Hooda", "Kamlesh Nagarkoti", "Jamie Overton", "Vijay Shankar"],
        "fast_bowlers": ["Matheesha Pathirana", "Khaleel Ahmed", "Nathan Ellis", "Mukesh Choudhary"],
        "spinners": ["Noor Ahmad", "Gurjapneet Singh", "Shreyas Gopal"]
    },
    "MI": {
        "batsmen": ["Rohit Sharma", "Suryakumar Yadav", "Tilak Varma", "Naman Dhir", "Bevon Jacobs", "Arjun Tendulkar"],
        "wicketkeepers": ["Ryan Rickelton", "Robin Minz", "Krishnan Shrijith"],
        "allrounders": ["Hardik Pandya", "Will Jacks", "Mitchell Santner", "Raj Bawa", "Vignesh Puthur"],
        "fast_bowlers": ["Jasprit Bumrah", "Trent Boult", "Deepak Chahar", "Reece Topley", "Lizaad Williams", "Arjun Tendulkar", "Ashwani Kumar"],
        "spinners": ["Karn Sharma", "AM Ghazanfar"]
    },
    "RCB": {
        "batsmen": ["Virat Kohli", "Rajat Patidar", "Devdutt Padikkal", "Rovman Powell", "Ajinkya Rahane", "Manish Pandey", "Swastik Chhikara"],
        "wicketkeepers": ["Phil Salt", "Jitesh Sharma", "Luvnith Sisodia"],
        "allrounders": ["Liam Livingstone", "Krunal Pandya", "Swapnil Singh", "Tim David", "Romario Shepherd", "Manoj Bhandage", "Jacob Bethell"],
        "fast_bowlers": ["Josh Hazlewood", "Bhuvneshwar Kumar", "Rasikh Salam", "Vaibhav Arora", "Umran Malik"],
        "spinners": ["Suyash Sharma"]
    },
    "KKR": {
        "batsmen": ["Rinku Singh", "Nitish Rana", "Andre Russell", "Abhinav Manohar", "Sachin Baby", "Aniket Verma"],
        "wicketkeepers": ["Rahmanullah Gurbaz", "Atharva Taide"],
        "allrounders": ["Sunil Narine", "Andre Russell", "Harshit Rana", "Kamindu Mendis"],
        "fast_bowlers": ["Spencer Johnson", "Umran Malik", "Harshal Patel", "Simarjeet Singh", "Jaydev Unadkat", "Brydon Carse", "Eshan Malinga"],
        "spinners": ["Adam Zampa", "Rahul Chahar", "Zeeshan Ansari"]
    },
    "GT": {
        "batsmen": ["Shubman Gill", "Jos Buttler", "Vijay Shankar", "Vaibhav Suryavanshi", "Shubham Dubey"],
        "wicketkeepers": ["Jos Buttler", "Kunal Singh Rathore"],
        "allrounders": ["Hardik Pandya", "Rachin Ravindra", "Will Jacks", "Mitchell Santner", "Raj Bawa", "Vignesh Puthur"],
        "fast_bowlers": ["Mohammed Siraj", "Kagiso Rabada", "Arjun Tendulkar", "Lizaad Williams", "Reece Topley", "Ashwani Kumar", "Satyanarayana Raju"],
        "spinners": ["Rashid Khan", "Maheesh Theekshana", "Kumar Kartikeya", "Bevon Jacobs"]
    },
    "LSG": {
        "batsmen": ["Ayush Badoni", "Himmat Singh", "Harnoor Singh", "Pyla Avinash", "Pravin Dubey"],
        "wicketkeepers": ["Rishabh Pant", "Vishnu Vinod", "Aryan Juyal"],
        "allrounders": ["Marcus Stoinis", "Mitchell Marsh", "Abdul Samad", "Aaron Hardie", "Suryansh Shedge"],
        "fast_bowlers": ["Avesh Khan", "Akash Deep", "Yash Thakur", "Lockie Ferguson", "Xavier Bartlett"],
        "spinners": ["Ravi Bishnoi", "Shahbaz Ahmed"]
    },
    "PBKS": {
        "batsmen": ["Shashank Singh", "Prabhsimran Singh", "Harnoor Singh", "Pyla Avinash"],
        "wicketkeepers": ["Josh Inglis", "Vishnu Vinod"],
        "allrounders": ["Shreyas Iyer", "Harpreet Brar", "Aaron Hardie", "Suryansh Shedge", "Pravin Dubey"],
        "fast_bowlers": ["Lockie Ferguson", "Yash Thakur", "Kuldeep Sen", "Xavier Bartlett"],
        "spinners": ["Mayank Markande", "Pravin Dubey"]
    },
    "RR": {
        "batsmen": ["Sanju Samson", "Yashasvi Jaiswal", "Shimron Hetmyer", "Vaibhav Suryavanshi", "Shubham Dubey"],
        "wicketkeepers": ["Sanju Samson", "Dhruv Jurel", "Kunal Singh Rathore"],
        "allrounders": ["Riyan Parag", "Nitish Rana", "Yudhvir Charak"],
        "fast_bowlers": ["Jofra Archer", "Tushar Deshpande", "Sandeep Sharma", "Fazalhaq Farooqi", "Ashok Sharma"],
        "spinners": ["Wanindu Hasaranga", "Maheesh Theekshana", "Kumar Kartikeya"]
    },
    "DC": {
        "batsmen": ["Harry Brook", "Karun Nair", "Faf du Plessis", "Sameer Rizvi", "Karun Nair"],
        "wicketkeepers": ["KL Rahul", "Donovan Ferreira", "Abishek Porel", "Tristan Stubbs"],
        "allrounders": ["Axar Patel", "Sameer Rizvi", "Ashutosh Sharma", "Darshan Nalkande", "Madhav Tiwari", "Ajay Mandal", "Tripurana Vijay", "Manvanth Kumar L"],
        "fast_bowlers": ["Mitchell Starc", "T Natarajan", "Mohit Sharma", "Mukesh Kumar", "Dushmantha Chameera", "Darshan Nalkande"],
        "spinners": ["Kuldeep Yadav", "Ashutosh Sharma", "Ajay Mandal"]
    },
    "SRH": {
        "batsmen": ["Travis Head", "Abhinav Manohar", "Nitish Kumar Reddy", "Abhinav Manohar"],
        "wicketkeepers": ["Heinrich Klaasen", "Ishan Kishan", "Aryan Juyal"],
        "allrounders": ["Abhishek Sharma", "Harshal Patel", "Brydon Carse", "Kamindu Mendis"],
        "fast_bowlers": ["Mohammed Shami", "Pat Cummins", "Rahul Chahar", "Simarjeet Singh", "Eshan Malinga"],
        "spinners": ["Adam Zampa", "Kamindu Mendis", "Zeeshan Ansari"]
    }
}

# Create CSV file and write data
with open('ipl_team_lineups.csv', 'w', newline='') as csvfile:
    fieldnames = ['Team', 'Role', 'Player']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()  # Write headers

    # Iterate through the teams and players
    for team_name, team_info in teams_data.items():
        for role, players in team_info.items():
            for player in players:
                writer.writerow({'Team': team_name, 'Role': role, 'Player': player})

print("Player data saved to ipl_team_lineups.csv")

app = Flask(__name__)