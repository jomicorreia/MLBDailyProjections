import numpy as np
import pandas as pd
from scipy import stats
import mysql.connector
import os
import datetime as dt
from itertools import chain
import matplotlib.pyplot as plt


def getDates(day, month, year, numdays, cursor):
    base = dt.date(year, month, day)
    dateList = [base - dt.timedelta(days=x) for x in range(0, numdays)]

    # get date ids from database
    gameIDs = []
    for date in dateList:
        findGame = "SELECT iddates FROM dates WHERE date = %s"
        findGameData = (date,)
        cursor.execute(findGame, findGameData)

        for game in cursor:
            gameIDs.append(game[0])

    return gameIDs


if __name__ == "__main__":
    cnx = mysql.connector.connect(user='root',
                                  host='127.0.0.1',
                                  database='baseball')
    cursor = cnx.cursor()

    # dates to retrieve data for batter test data
    # start date
    year = 2017
    month = 7
    day = 23

    numdays = 4

    gameIDs = getDates(day, month, year, numdays, cursor)

    # select data with cooresponding game id and other constraints
    pitcherConstraints = ['rotogrindersPoints', 'saberSimPoints', 'rotowirePoints', 'dkpoints']
    pitcherConstraintsValues = {}
    pitcherConstraintsTypes ={}

    for con in pitcherConstraints:
        var1 = raw_input("Enter operand for constraint " + con + ": ")
        pitcherConstraintsTypes[con] = var1
        var0 = raw_input("Enter value for constraint " + con + ": ")
        pitcherConstraintsValues[con] = var0

    constraintsString = "("
    for constraint in pitcherConstraints:
        constraintString = constraint + " " + pitcherConstraintsTypes[constraint] + " " + pitcherConstraintsValues[constraint]
        if pitcherConstraints[-1] != constraint:
            constraintString = constraintString + ' AND '
        constraintsString = constraintsString + constraintString

    constraintsString = constraintsString + ")"

    features = ['rotogrindersPoints', 'saberSimPoints', 'rotowirePoints']
    targets = ['dkpoints']

    featuresString = ""
    for feat in features:
        featuresString = featuresString + feat
        if features[-1] != feat:
            featuresString = featuresString + ", "

    targetsString = ""
    for tar in targets:
        targetsString = targetsString + tar
        if targets[-1] != tar:
            featuresString = targetsString + ", "

    print "Loading data..."

    getTestData = "SELECT pitcherID, "
    getTestData = getTestData + featuresString
    getTestData = getTestData + ", "
    getTestData = getTestData + targetsString
    getTestData = getTestData + " FROM pitchersdaily LEFT JOIN pitchers ON pitchersdaily.pitcherID = pitchers.idpitchers WHERE pitchersdaily.pgameID = %s AND "
    getTestData = getTestData + constraintsString

    numpyDataArrays = []
    # execute command + load into numpy array
    for game in gameIDs:
        testVariables = (game, )
        cursor.execute(getTestData, testVariables)

        results = cursor.fetchall()
        numRows = cursor.rowcount

        D = np.fromiter(chain.from_iterable(results), dtype=float, count=-1)

        D = D.reshape(numRows, -1)
        numpyDataArrays.append(D)

    iterDataSets = iter(numpyDataArrays)
    next(iterDataSets)
    testData = numpyDataArrays[0]
    for dataArray in iterDataSets:
        testData = np.vstack((testData, dataArray))


    # Test Coorelations
    pitcherIDs, testX = np.split(testData, [1], 1)
    testX, testY = np.split(testX, [len(features)], 1)

    featuresToTest = np.shape(testX)[1]

    i = 0
    while i < featuresToTest:
        featureData = testX[:, i]
        targetData = testY[:, 0]
        coorVariable = stats.pearsonr(featureData, targetData)
        print "Linear Coorelation of " + features[i] + " is: " + str(coorVariable[0])

        print "Plotting " + features[i] + " versus " + targets[0]

        plt.plot(featureData, targetData, 'ro')
        plt.xlabel(features[i])
        plt.ylabel(targets[0])
        plt.show()

        i = i + 1
