import csv
import argparse

def checkArgs():
    parser = argparse.ArgumentParser(description='Parse CSV file')
    parser.add_argument('csvFile', help='CSV file to parse')
    args = parser.parse_args()

    #print(args.csvFile)
    if not ".csv" in args.csvFile:
        print("Error File is not valid CSV")
        return 1
    
    try:
        open(args.csvFile, "r")
    except IOError:
        print("Error File does not exist")
        return 1



checkArgs()

