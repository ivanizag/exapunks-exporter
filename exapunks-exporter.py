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
    return byte != 0

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

def getExa(f):
    exa = {}
    exa['lead'] = getByte(f)
    del exa['lead']
    exa['name'] = getString(f)
    exa['source'] = getString(f)
    exa['collapsed'] = getFlag(f)
    exa['global'] = getFlag(f)
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
;; Global: {exa['global']}
{exa['source']}""")
    
def processFile(folder, filename):
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
    saveExaFile(file_info)

def processFolder(folder):
    for filename in os.listdir(folder):
        _, extension = os.path.splitext(filename)
        if extension == ".solution":
            processFile(folder, filename)


if len(sys.argv) != 2 :
    print("Usage: python3 expunks-exporter sourcefolder")
    print("Example: python3 exapunks-exporter ~/.local/share/EXAPUNKS/1234123412341234")

processFolder(sys.argv[1])

