# Format: https://www.reddit.com/r/exapunks/comments/973luq/current_solution_file_format/

import os
import sys

def getInt32(f):
    bytes = f.read(4)
    return int.from_bytes(bytes, byteorder='little')

def getByte(f):
    byte = f.read(1)
    return byte

def getString(f):
    # Pascal string with int32 size 
    size = getInt32(f)
    bytes = f.read(size)
    return bytes.decode('ascii')

def getFlag(f):
    byte = f.read(1)
    return byte != b'\x00'


scoreNames = {0: 'cycles', 1: 'size', 2: 'activity'}
def getScore(f):
    score = {}
    count = getInt32(f)
    for i in range(count):
        type = getInt32(f)
        if type in scoreNames:
            type = scoreNames[type]
        score[type] = getInt32(f)
    return score

def printBitmap(bitmap):
    for i in range(10):
        for j in range(10):
            if bitmap[i*10 + j]:
                print("#", end='')
            else:
                print(" ", end='')
        print()

def getExa(f):
    exa = {}
    exa['lead'] = getByte(f)
    del exa['lead']
    exa['name'] = getString(f)
    exa['source'] = getString(f)
    exa['collapsed'] = getFlag(f)
    exa['local'] = getFlag(f)
    exa['bitmap'] = [getFlag(f) for _ in range(100)]
    del exa['bitmap']
    return exa

def getExas(f):
    exas = []
    count = getInt32(f)
    return [getExa(f) for _ in range(count)]

def saveExaFile(file_info):
    folder = file_info["level_id"].lower() + "-" + file_info["level_name"]
    os.makedirs(folder, exist_ok = True)
    filename = os.path.join(folder, file_info["name"].lower() + ".exa")
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, mode="w") as f:
        f.write(f""";;; Solution name: {file_info['name']}
;;; Level id: {file_info['level_id']}
;;; Level name: {file_info['level_name']}
""")
        for s in ['cycles', 'size', 'activity']:
            if s in file_info['score']:
                f.write(f";;; {s.capitalize()}: {file_info['score'][s]}\n")
        for exa in file_info['exas']:
            f.write(f"""
;; Exa name: {exa['name']}
;; Local: {exa['local']}
{exa['source']}""")

def saveScores(scores):
    filename = "top-scores.txt"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, mode="w") as f:
        f.write("Level-name: cycles, size, activity\n")
        for level, data in sorted(scores.items()):
            if 'cycles' in data and 'size' in data and 'activity' in data:
                f.write(f"{level}: {data['cycles']}, {data['size']}, {data['activity']}\n")

def updateTopScores(file_info, scores):
    if file_info['wins'] > 0:
        return

    level = file_info["level_id"].lower() + "-" + file_info["level_name"]
    data = {}
    if level in scores:
        data = scores[level]
    for s in ['cycles', 'size', 'activity']:
        if s in file_info['score']:
            if s not in data or file_info['score'][s] < data[s]:
                data[s] = file_info['score'][s]
    scores[level] = data
    
def processFile(folder, filename, scores):
    file_info = {}
    with open(os.path.join(folder, filename), mode='rb') as f:
        level, _ = os.path.splitext(filename)
        level = "-".join(level.split("-")[:-1])
        file_info['version'] = getInt32(f)
        file_info['level_id'] = getString(f)
        file_info['level_name'] = level
        file_info['name'] = getString(f)
        file_info['wins'] = getInt32(f)
        file_info['redshift_size'] = getInt32(f)
        file_info['score'] = getScore(f)
        file_info['exas'] = getExas(f)
        file_info['rest'] = f.read(-1)
    updateTopScores(file_info, scores)
    saveExaFile(file_info)

def processFolder(folder):
    scores = {}
    for filename in os.listdir(folder):
        _, extension = os.path.splitext(filename)
        if extension == ".solution":
            processFile(folder, filename, scores)
    saveScores(scores)

if len(sys.argv) != 2 :
    print("Usage: python3 expunks-exporter.py sourcefolder")
    print("Example: python3 exapunks-exporter.py ~/.local/share/EXAPUNKS/1234123412341234")

processFolder(sys.argv[1])

