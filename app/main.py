## Battlesnake - Medusa

import bottle
import os

    # SNAKE OBJECT
    #     "id": "1234-567890-123456-7890",
    #     "name": "Well Documented Snake",
    #     "status": "alive",
    #     "message": "Moved north",
    #     "taunt": "Let's rock!",
    #     "age": 56,
    #     "health": 83,
    #     "coords": [ [1, 1], [1, 2], [2, 2] ],
    #     "kills": 4,
    #     "food": 12,
    #     "gold": 2

    # THIS IS THE DATA WE RECEIVE FOR EACH 'MOVE'
    # {
    #     "game": "hairy-cheese",
    #     "mode": "classic",
    #     "turn": 4,
    #     "height": 20,
    #     "width": 30,
    #     "snakes": [ <Snake Object>, <Snake Object>, ... ],
    #     "food": [ [1, 2], [9, 3], ... ]
    # }

snakeid = 'f729b53e-3477-447d-b07e-c79d7e326c82'

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )
    return {
        'color': 'green',
        'head': head_url
    }

@bottle.post('/start')
def start():
    data = bottle.request.json
    return {
        'taunt': 'Medusa snake go!'
    }
    
@bottle.post('/move') 
def move():
    data = bottle.request.json
    move_decision = ['north', 'east', 'south', 'west']
    ourSnake = findSnake(data['snakes'])
    head = ourSnake['coords'][0]

    neighbours = {  'north': [head[0], head[1]-1],
                    'east': [head[0]+1, head[1]],
                    'south': [head[0], head[1]+1],
                    'west': [head[0]-1, head[1]]
                }
    
    # Check if each direction is empty; remove if it is not empty
    for direction, coord in neighbours.items():
        if not verifyNeighbours(data, coord):
            move_decision.remove(direction)

    nearestFood = findNearestFood(ourSnake, data['food'])
    
    # Find which directions take us closer to food
    if nearestFood != []:
        if nearestFood[0] < head[0] and 'west' in move_decision:
            move_decision = ['west']
        if nearestFood[0] > head[0] and 'east' in move_decision:
            move_decision = ['east']
        if nearestFood[1] > head[1] and 'south' in move_decision:
            move_decision = ['south']
        if nearestFood[1] < head[1] and 'north' in move_decision:
            move_decision = ['north']
                
    if not move_decision:
        move_decision = ['north']
    
    taunts = {  'north': 'I am a leaf on the wind, see how I soar!',
                'east': 'Y\'all gonna get turned to stone!',
                'south': 'Snake head is coming for you',
                'west': 'Go west young snake.'
            }

    return {
        'move': move_decision[0],
        'taunt': taunts[move_decision[0]]
    }
    
# Takes a list of snakes and returns which is ours
def findSnake(snakes):
    for snake in snakes:
        if snake['id'] == snakeid:
            return snake

# Return the coordinates of the nearest food
def findNearestFood(snake, foodList):
    if foodList == []:
        return []
    
    headLocation = snake['coords'][0]
    nearestFood = foodList[0]
    nearestDistance = calculateDistance(nearestFood, headLocation)
    for food in foodList[1:]:
        if calculateDistance(food, headLocation) < nearestDistance:
            nearestFood = food
            nearestDistance = calculateDistance(nearestFood, headLocation)
            
    return nearestFood

# Distance between our snake's head and the nearest food
def calculateDistance(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

# Input: our data object, coordinates of desired location
# Output: return TRUE if can move there, FALSE if cannot move there
def verifyNeighbours(data, coord):
    return not isWall(data, coord) and not isSnake(data, coord)

# Checks if desired coordinate is a wall
def isWall(data, coord):
    #check if coord is out of bounds
    if coord[0] < 0 or coord[1] < 0:
        return True
    elif coord[0] >= data['width'] or coord[1] >= data['height']:
        return True
    else:
        return False

# Checks if desired coordinate is own tail
def isSnake(data, coord):
    for snake in data['snakes']:
        if coord in snake['coords']:
            return True
    return False

@bottle.post('/end')
def end():
    data = bottle.request.json
    return {
        'taunt': 'Good game all!'
    }

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))