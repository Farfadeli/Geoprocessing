import json
import sys
import random
import argparse

parser = argparse.ArgumentParser(
        description="creation json nb-das")
parser.add_argument("--file" , help="path of file")
parser.add_argument("--start", help="Début de la légende")
parser.add_argument("--mid", help="milieu de la légende")
parser.add_argument("--end", help="fin de la légende")

args = parser.parse_args()

with open(args.file, 'r') as f:
    json_file = json.load(f)
    output = []
    for e in json_file:
        output.append[{
            "code" : str(e["value"]),
            "color" : '#{:06x}'.format(random.randint(0, 0xFFFFFF)),
            "name" : (args.start if args.start != None else "") + "" + (args.mid if args.mid != None else "") + "" + (args.end if args.end != None else ""),
            "value" : e["value"],
            "percentage" : 0.0,
            "analyticValue": 0.0
        }]
    with open(f"{'/'.join(args.file.split("/")[:-1])}/config.json", "w") as out_file:
        json.dump(output, out_file)