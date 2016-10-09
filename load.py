from collections import OrderedDict
import json
import sys
import jsonformat

fleetDb = None
shipDb = None
equiptName = None
shipRarity = None

label = '_ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def init():
    global fleetDb, shipDb, equiptName, shipRarity
    fleetDb = json.load(open('fleets.json'), object_pairs_hook = OrderedDict)
    shipDb = json.load(open('ships.json'), object_pairs_hook = OrderedDict)
    t = json.load(open('static.json'))
    equiptName = t['equiptName']
    shipRarity = t['shipRarity']

def load(filename):
    f = open(filename)
    lastLine = ''
    for line in f:
        if lastLine.startswith('GET /pve/deal/'):
            node = lastLine.split('/')[3]
            node = node[0] + '-' + node[2] + '/' + label[int(node) % 100]
            data = json.loads(line[:-1])
            save(node, data)

        elif lastLine.startswith('GET /campaign/challenge/'):
            node = lastLine.split('/')[3]
            node = 'C' + node[0] + '-' + node[2]
            data = json.loads(line[:-1])
            save(node, data)

        lastLine = line

def end():
    jsonformat.save({k:v for k,v in fleetDb.items()}, 'fleets.json')
    jsonformat.save({k:v for k,v in shipDb.items()}, 'ships.json')

def save(node, data):
    if 'warReport' not in data:
        return

    fleet = data['warReport']['enemyFleet']
    ships = data['warReport']['enemyShips']

    f = OrderedDict()
    f['title'] = fleet['title']
    f['formation'] = int(fleet['formation'])
    f['ships'] = [ int(s['shipCid']) for s in ships ]
    f['shipNames'] = [ s['title'] for s in ships ]

    if node[0] == 'C':
        fleetDb[node] = f
    else:
        if node not in fleetDb:
            fleetDb[node] = [ ]
        if f not in fleetDb[node]:
            fleetDb[node].append(f)
        if len(fleetDb[node]) > 3:
            print('!!!!! more than 3 fleets ' + node + '!!!!!')

    for ship in ships:
        s = OrderedDict()
        s['title']  = ship['title']
        s['rarity'] = shipRarity[str(ship['shipCid'])]
        s['type']   = int(ship['type'])
        s['level']  = int(ship['level'])
        s['hp']     = int(ship['hp'])
        s['atk']    = int(ship['atk'])
        s['tpd']    = int(ship['torpedo'])
        s['def']    = int(ship['def'])
        s['aa']     = int(ship['airDef'])
        s['eva']    = int(ship['miss'])
        s['as']     = int(ship['antisub'])
        s['rec']    = int(ship['radar'])
        s['speed']  = int(ship['speed'])
        s['range']  = int(ship['range'])

        s['eq'] = [ None, None, None, None ]
        s['cap'] = [ None, None, None, None ]
        for i in range(4):
            s['eq'][i] = equiptName[str(ship['equipment'][i])]
            s['cap'][i] = int(ship['capacitySlotMax'][i])
        id_ = str(ship['shipCid'])
        if id_ not in shipDb:
            shipDb[id_] = s
        elif shipDb[id_] != s:
            print('!!!!! unmatch ship data ' + ship['title'] + '!!!!!')

if __name__ == '__main__':
    init()
    for i in range(1, len(sys.argv)):
        load(sys.argv[i])
    end()