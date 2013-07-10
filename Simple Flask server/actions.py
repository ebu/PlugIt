import sqlite3
from utils import action, cache, only_logged_user, only_member_user, user_info

### Basic sample service: polls
# Anonymous users can see polls
# Registered users can vote
# Members can create polls
# Admins can see who selected what
## Data is stored into a simple sqlite database

# Sqlite part: Load the database. If the database doesn't exist, create a new one
coxDB = sqlite3.connect('poll.db', check_same_thread=False)
curDB = coxDB.cursor()

# Create the table if they doesn't exist
curDB.execute("CREATE TABLE IF NOT EXISTS Poll(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)")
curDB.execute("CREATE TABLE IF NOT EXISTS Response(id INTEGER PRIMARY KEY AUTOINCREMENT, pollId INTEGER, title TEXT)")
curDB.execute("CREATE TABLE IF NOT EXISTS Vote(responseId INTEGER, username TEXT)")

# Vacuum, for performances
curDB.execute("VACUUM")

coxDB.commit()

@action(route="/", template="home.html")
@cache(time=5, byUser=True)
def home(request):
    """Show the home page. Send the list of polls"""

    polls = []

    for row in curDB.execute('SELECT id, title FROM Poll ORDER BY title'):
        polls.append({'id': row[0], 'name': row[1]})

    return {'polls': polls}


@action(route="/show/<int:pollId>", template="show.html")
@user_info(props=['ebuio_admin','username'])
def show(request, pollId):
    """Show a poll. We send informations about votes only if the user is an admin"""

    # Get the poll
    curDB.execute('SELECT id, title, description FROM Poll WHERE id = ? ORDER BY title', (pollId,))
    poll = curDB.fetchone()

    if poll is None:
        return {}

    responses = []
    totalVotes = 0
    votedFor = 0

    # Compute the list of responses
    curDB.execute('SELECT id, title FROM Response WHERE pollId = ? ORDER BY title ', (poll[0],))
    resps = curDB.fetchall()

    for rowRep in resps:

        votes = []
        nbVotes = 0

        # List each votes
        for rowVote in curDB.execute('SELECT username FROM Vote WHERE responseId = ?', (rowRep[0],)):

            nbVotes += 1

            # If the user is and admin, saves each votes
            if request.args.get('ebuio_u_ebuio_admin') == 'True':
                votes.append(rowVote[0])

            # Save the vote of the current suer
            if request.args.get('ebuio_u_username') == rowVote[0]:
                votedFor = rowRep[0]

        totalVotes += nbVotes
        responses.append({'id': rowRep[0], 'title': rowRep[1], 'nbVotes': nbVotes, 'votes': votes})

    return {'id': poll[0], 'name': poll[1], 'description': poll[2], 'responses': responses, 'totalVotes': totalVotes, 'votedFor': votedFor}


@action(route="/vote/<int:pollId>/<int:responseId>", template="vote.html")
@only_logged_user()
@user_info(props=['username'])
def vote(request, pollId, responseId):
    """Vote for a poll"""

    username = request.args.get('ebuio_u_username')

    # Remove old votes from the same user on the same poll
    curDB.execute('DELETE FROM Vote WHERE username = ?  AND responseId IN (SELECT id FROM Response WHERE pollId = ?) ', (username, pollId))

    # Save the vote
    curDB.execute('INSERT INTO Vote (username, responseID) VALUES (?, ?) ', (username, responseId))

    coxDB.commit()

    return {'id': pollId}


@action(route="/create/", template="create.html", methods=['GET', 'POST'])
@only_member_user()
def create(request):
    """Create a new poll"""

    errors = []
    success = False
    listOfResponses = ['', '', '']  # 3 Blank lines by default
    title = ''
    description = ''
    id = ''

    if request.method == 'POST':  # User saved the form
        # Retrieve parameters
        title = request.form.get('title')
        description = request.form.get('description')

        listOfResponses = []
        for rep in request.form.getlist('rep[]'):
            if rep != '':
                listOfResponses.append(rep)

        # Test if everything is ok
        if title == "":
            errors.append("Please set a title !")

        if len(listOfResponses) == 0:
            errors.append("Please set at least one response !")

        # Can we save the new question ?
        if len(errors) == 0:
            # Yes. Let save data
            curDB.execute("INSERT INTO Poll (title, description) VALUES (?, ?)", (title, description))

            # The id of the poll
            id = curDB.lastrowid

            # Insert responses
            for rep in listOfResponses:
                curDB.execute("INSERT INTO Response (pollId, title) VALUES (?, ?)", (id, rep))

            coxDB.commit()

            success = True

        # Minimum of 3 lines of questions
        while len(listOfResponses) < 3:
            listOfResponses.append('')

    return {'errors': errors, 'success': success, 'listOfResponses': listOfResponses, 'title': title, 'description': description, 'id': id}


@action(route="/test", template="test.html")
@only_logged_user()
@cache(time=42, byUser=True)
@user_info(props=['username'])
def test(request):
    return {"hello": "Test", "data": request.args.get('data', '')}
