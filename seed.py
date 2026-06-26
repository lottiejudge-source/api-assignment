from database import db, Duties, Coins, JoinCoinsAndDuties

def seed_data():
    db.connect(reuse_if_open=True)

    JoinCoinsAndDuties.delete().execute()
    Duties.delete().execute()
    Coins.delete().execute()
    


    coins = [
        {"coin_name": "Assemble", "coin_complete": False}, 
        {"coin_name": "Automate", "coin_complete": True}, 
        {"coin_name": "Call Security", "coin_complete": False}, 
        {"coin_name": "Going Deeper", "coin_complete": False}, 
        {"coin_name": "Houston, Prepare to Launch", "coin_complete": False}, 
    ]

    created_coins = {}
    for coin in coins:
        created_row = Coins.create(**coin)
        created_coins[created_row.coin_name] = created_row

    duties = [
            {"duty_name": "D5", "duty_description": "Build and operate a Continuous Integration (CI) capability, employing version control of source code and related artefacts."},
            {"duty_name": "D7", "duty_description": "Provision cloud infrastructure using APIs, continually improve infrastructure-as-code, considering use of industry leading technologies as they become available (e.g. Serverless, Containers)."},
            {"duty_name": "D8", "duty_description": "Evolve and define architecture, utilising the knowledge and experience of the team to design in an optimal user experience, scalability, security, high availability and optimal performance."},
            {"duty_name": "D9", "duty_description": "Apply leading security practices throughout the Software Development Lifecycle (SDLC)."},
            {"duty_name": "D10", "duty_description": "Implement a good coverage of monitoring (metrics, logs), ensuring that alerts are visible, tuneable and actionable."},
            {"duty_name": "D11", "duty_description": "Keep up with cutting edge by committing to continual training and development - utilise web resources for self-learning; horizon scanning; active membership of professional bodies such as Meetup Groups; subscribe to relevant publications."}
    ]

    created_duties = {}
    for duty in duties: 
        created_row = Duties.create(**duty)
        created_duties[created_row.duty_name] = created_row

    joins = [
            {"coin": "Assemble", "duties": ["D8"]},
            {"coin": "Automate", "duties": ["D5", "D7", "D10"]},
            {"coin": "Call Security", "duties": ["D9"]},
            {"coin": "Going Deeper", "duties": ["D11"]},
            {"coin": "Houston, Prepare to Launch", "duties": ["D5", "D7", "D10"]}
         ]
    
    for join in joins: 
        coin_join = created_coins[join["coin"]]

        for duty_name in join["duties"]:
            duty_join = created_duties[duty_name]

            JoinCoinsAndDuties.create(coin=coin_join, duty=duty_join)

    db.close()        

if __name__ == "__main__":
    seed_data()