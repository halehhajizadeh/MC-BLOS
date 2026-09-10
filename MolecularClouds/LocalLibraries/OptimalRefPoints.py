"""
Contains functions used to find the optimal number of reference points out of a given set.
Used in the third stage of the BLOS Mapping Method.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections

from .CalculateB import CalculateB
from . import MatchedRMExtinctionFunctions as MREF
#from statistics import mode #Before Python 3.8, errors when there are multiple modes. This is not behavior we desire.
from . import config as config

def mode(listInput):
    '''
    Here we create a different way to obtain the mode.
    :param listInput: The list we want to find the mode of.
    :return: The first mode. If there are many modes, just returns one of them.
    '''
    return collections.Counter(listInput).most_common()[0][0]

def stabilityCheckAlg(TrendDataTable):
    '''
    The following algorithm searches for the number of candidate reference points where the trend of calculated BLOS
     values stabilizes
        - The algorithm checks the values of adjacent pairs of BLOS values
        - If the BLOS values are similar, ie their difference is within a given threshold, then this is called a
        "run"
        - The algorithm searches for the number of reference points where the longest run occurs

    This algorithm is used on every BLOS point that was not used as a reference point.  The optimal number of
    reference points is taken to be the number of reference points where the longest run occurs most often

    We repeat this algorithm over all potential threshold values
    :param TrendDataTable: The input dataframe for which this data is analyzed.
    :return: Optimal_NumRefPoints: The minimal number of reference points needed before the longest stable run.
    '''
    UpperLimit = max([max(abs(np.diff(list(TrendDataTable.loc[number])))) for number in TrendDataTable.index])
    LowerLimit = min([min(abs(np.diff(list(TrendDataTable.loc[number])))) for number in TrendDataTable.index])
    numThresholds = 500 #TODO: potentially make this a parameter in the config file in case we want to change it.
    thresholds = np.linspace(LowerLimit, UpperLimit, numThresholds)

    Optimal_NumRefPoints = []

    for threshold in thresholds:

        LongestRun_NumRefPoints = []
        LongestRun_Length = []

        # For every point within the region of interest that was not used as a reference point:
        for index in range(len(TrendDataTable)):
            y = list(TrendDataTable.loc[index])  # List of BLOS values for the given point
            x = list(np.arange(1, len(y) + 1))  # List of number of reference points

            # -------- STABILITY TREND ALGORITHM --------
            run_length = 1  # To keep track of how many similar values we get in a row
            on_a_run = 0  # To indicate if we are on a run (1) or not (0)
            run_started = []  # To keep track of the number of reference points where the run started
            run = []  # To keep track of the total length of each run

            # For each pair of adjacent BLOS values:
            for i in range(1, len(y)):
                # Find the absolute difference in adjacent BLOS values
                diff = abs(y[i] - y[i - 1])

                if diff <= threshold:
                    # If the difference is below the threshold, then we have started, or are in, a "run" of similar
                    # values
                    run_length += 1
                    if on_a_run == 0:
                        # We have started a new run
                        on_a_run = 1
                        run_started.append(x[i - 1])

                if diff > threshold or i == len(y) - 1:
                    # If the difference was not below the threshold, or, if it is the end of the list of BLOS values
                    if on_a_run == 1:
                        # then if we were on a run, it ends
                        run.append(run_length)
                        on_a_run = 0
                        run_length = 1
            # -------- STABILITY TREND ALGORITHM --------

            if len(run) > 0:
                # We want to find the number of reference points where the longest run occurred
                ind_longestRun = np.where(np.array(run) == max(run))[0][0]
                LongestRun_NumRefPoints.append(run_started[ind_longestRun])
                LongestRun_Length.append(max(run))
        Optimal_NumRefPoints.append(mode(LongestRun_NumRefPoints))
    return Optimal_NumRefPoints

def plotStabilityTrend(TrendDataTable):
    '''
    Generates the stability trend graph for the given reference dataset.
    :param TrendDataTable: Trend Data, PANDAS Table
    :return: fig - the Matplotlib figure of the graph.
    '''
    Identifiers = list(TrendDataTable.index)
    # -------- CREATE A FIGURE --------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300, facecolor='w', edgecolor='k')

    # No title for cleaner publication plots
    ax.set_xlabel('Number of reference points', fontsize=16)
    ax.set_ylabel(r'Calculated $B_\parallel$ ($\mu$G)', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=14)

    x = [int(col) for col in TrendDataTable.columns]
    ax.set_xticks(x)
    ax.set_xticklabels(list(TrendDataTable.columns))

    # Get final BLOS values to determine color (positive vs negative)
    final_values = TrendDataTable.iloc[:, -1].values

    # For each BLOS Point - use thin lines with transparency, color by final sign
    for i, number in enumerate(TrendDataTable.index):
        y_vals = list(TrendDataTable.loc[number])
        final_val = y_vals[-1]

        # Color based on final BLOS value (positive=blue, negative=red)
        if final_val > 0:
            color = 'blue'
        elif final_val < 0:
            color = 'red'
        else:
            color = 'gray'

        ax.plot(x, y_vals, '-', color=color, alpha=0.4, linewidth=0.8, markersize=2)

    # Add a horizontal line at y=0 for reference
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

    # Add legend for color meaning
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='blue', alpha=0.7, linewidth=1.5, label=r'Positive $B_\parallel$'),
                       Line2D([0], [0], color='red', alpha=0.7, linewidth=1.5, label=r'Negative $B_\parallel$')]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)

    plt.tight_layout()
    # -------- CREATE A FIGURE. --------
    return fig

def findTrendData(potentialRefPoints, ExtincRMTable, regionOfInterest):
    '''
    Finds the stability trend data; the calculated BLOS values as a function of the number of reference points (added one by one).
    :param potentialRefPoints: The potential reference points. PANDAS table.
    :param ExtincRMTable: All matched RM-Extinction points. PANDAS table.
    :param regionOfInterest: A RegionOfInterest object that contains all the data for the region of analysis.
    :return: TrendDataTable - The stability trend data, in PANDAS table format.
    '''
    # -------- CREATE A TABLE FOR ALL BLOS DATA --------
    # The rows of this table will represent the number of reference points and the columns of this table will
    # represent the individual BLOS points.  Each entry in the table is a calculated BLOS value.
    AllData = pd.DataFrame()
    # -------- CREATE A TABLE FOR ALL BLOS DATA. --------

    # -------- CALCULATE BLOS AS A FUNCTION OF # REF POINTS --------
    for num in range(len(potentialRefPoints)):
        # -------- Extract {num} points from the table of potential reference points
        # The extracted potential reference points will be referred to as "candidates"
        candidateRefPoints = potentialRefPoints.loc[:num]
        # -------- Extract {num} points from the table of potential reference points.

        #Note: This assumes no weighting scheme.
        fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.calcFiducialVals(candidateRefPoints)
        remainderTable = MREF.rmMatchingPts(ExtincRMTable, candidateRefPoints)

        # -------- Use the candidate reference points to calculate BLOS
        BLOSData = CalculateB(regionOfInterest.AvFilePath, remainderTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange = config.negScaledExtOption)
        BLOSData = BLOSData.set_index('ID#', drop=True)
        # -------- Use the candidate reference points to calculate BLOS

        # -------- Add calculated BLOS to the table of BLOS vs number of reference points
        AllData[str(num + 1)] = BLOSData['Magnetic_Field(uG)']
        # -------- Add calculated BLOS to the table of BLOS vs number of reference points
    # -------- CALCULATE BLOS AS A FUNCTION OF # REF POINTS. --------

    # -------- FIND OPTIMAL NUM REF POINTS --------
    # If a point has been used as a candidate reference point at any time it will not be used to determine the
    # optimal number of reference points
    TrendDataTable = AllData.copy().drop(list(potentialRefPoints['ID#']), errors='ignore')
    TrendDataTable = TrendDataTable.reset_index(drop=True)
    return TrendDataTable

#======================================================================================================================
#Experimental Functions.
#======================================================================================================================

#Minimum number of reference points needed to land in the ballpark of average Av off.
def minRefRMOff(potentialRefPoints, validDev):
    fiducialRM, _, fiducialStd, _ = MREF.calcFiducialVals(potentialRefPoints)
    minPoints = 0
    for num in range(len(potentialRefPoints)):
        minPoints = num

        candidateRefPoints = potentialRefPoints.head(num+1)
        candidateRM, _, candidateRMStd, _ = MREF.calcFiducialVals(candidateRefPoints)
        if abs(candidateRM-fiducialRM) < abs(fiducialStd * validDev):
            break
    return minPoints+1

#Minimum number of reference points needed to land in the ballpark of the average Av on.
def minRefRMOn(MatchedRMPoints, potRMPoints, validDev):
    #Minimum points
    minPoints = 0
    for num in range(len(potRMPoints)):
        minPoints = num
        #Get the off RM
        candidateRefPoints = potRMPoints.head(num + 1)
        candidateRM, _, candidateRMStd, _ = MREF.calcFiducialVals(candidateRefPoints)
        #Get the average remaining RM
        remainingTable = MREF.rmMatchingPts(MatchedRMPoints, candidateRefPoints)
        fiducialRM, _, fiducialStd, _ = MREF.calcFiducialVals(remainingTable)  # MREF.getFiducialValues(MatchedRMPoints)
        #If the off RM is close to the average RM, break
        if abs(candidateRM - fiducialRM) < abs(fiducialStd * validDev):
            break
    #Account for numbering from 1, or exclusive range max.
    minPoints = minPoints+1
    return minPoints