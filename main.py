import copy
import math
import string
import pandas as pd
import random as rd
import re

def preprocess(file):
    file = file.drop(columns=["A", "B"])
    for idx, val in file.iterrows():
        file.loc[idx, "Tweet"] = re.sub(r"(?:\@|http?\://)\S+", "", file.loc[idx, "Tweet"]) # Removes @ and website
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].replace("#", "") # Removes hashtags
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].replace("@", "") # Removes remaining @ symbols
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].lower() # Converts into lowercase
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].strip() # Removes leading and trailing whitespaces
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].translate(str.maketrans('', '', string.punctuation)) # Removes puncuation characters
        file.loc[idx, "Tweet"] = file.loc[idx, "Tweet"].replace("  ", " ") # Removes double spaces
    return file

def jacardDistance(A, B):
    # From the formula provided
    return 1 - ((len(A.intersection(B)))/(len(A.union(B))))

def k_means(tweets, k, max_iter):

    centroids = []
    prevCentroids = ["a"]

    # Finds k random tweets to serve as the initial centroids
    temp = rd.sample(range(0, len(tweets) - 1), k)
    for i in range(0, len(temp)):
        centroids.append(tweets.loc[temp[i], "Tweet"])

    iter = 0

    while (convergenceCheck(centroids, prevCentroids) == False and iter < max_iter):
        print("Running iteration " + str(iter))
        clusters = assignClusters(tweets, centroids)
        prevCentroids = copy.deepcopy(centroids)
        centroids = updateCentroids(clusters, centroids, k)
        iter+=1
        # print(centroids)
        # print(prevCentroids)

    print("SSE: " + str(computeError(clusters)))

    for i in range(0, k):
        print(str(len(clusters[i])) + " entries for cluster centered around: " + centroids[i])

def assignClusters(tweets, centroids):

    clusters = dict()

    for i in range(len(tweets)):
        A = set(tweets.loc[i, "Tweet"].split(" ")) # For computing Jacard Distance
        leastDistance = 2 # Every Jacard Distance will be [0,1]
        for j in range(len(centroids)):
            # print(centroids[j])
            B = set(centroids[j].split(" ")) # For computing Jacard Distance

            currDistance = jacardDistance(A, B) # Find the nearest centroid
            if (currDistance < leastDistance):
                leastDistance = currDistance # Assign current nearest centroid
                currCluster = j # Assign current nearest cluster number
                # print(leastDistance)
        if leastDistance == 1: # If it can't find one, assign it to a random one
            currCluster = rd.randint(0, len(centroids) - 1)
        clusters.setdefault(currCluster, []).append([tweets.loc[i, "Tweet"]]) # Add the tweet and cluster pair
        idx = len(clusters.setdefault(currCluster, [])) - 1
        clusters.setdefault(currCluster, [])[idx].append(leastDistance) # Also include the distance from the nearest cluster for calculating error
        # if leastDistance != 1:
        #     print(clusters.loc[i, "Tweet"])
        #     print(clusters.loc[i, "Cluster"])
        #     print(leastDistance)
    return clusters

def updateCentroids(clusters, centroids, k):

    dis = 0
    currSum = 0

    newCentroids = []
    # for i in range(0, k):
    #     cluster.append(clusters[clusters["Cluster"] == centroids[i]])
    #     cluster[i].reset_index(inplace=True)
    #     # print(len(cluster[i].index))


    for i in range(0, k):
        minDistArr = []
        minDist = math.inf
        idx = -1

        max = len(clusters[i])
        max = int(max)

        for j in range(0, max):
            minDistArr.append([]) # DP calculations
            currSum = 0
            for k in range(0, max):
                if j != k:
                    if k < j:
                        dis = minDistArr[k][j] # DP
                    else:
                        A = set(tweets.loc[j, "Tweet"].split(" "))
                        B = set(tweets.loc[k, "Tweet"].split(" "))
                        # print(A)
                        # print(B)
                        dis = jacardDistance(A, B) # Calculate the distance between every tweet
                    minDistArr[j].append(dis)
                    currSum += dis # Add the distances up
                else:
                    minDistArr[j].append(0)

            if currSum < minDist: # Find the tweet with the lowest distance
                minDist = currSum
                idx = j
        # print(clusters[centroids[i]][idx])
        newCentroids.append(clusters[i][idx][0])
        print("Cluster " + str(i) + " has computed a new centroid")
    return newCentroids

def convergenceCheck(centroidsA, centroidsB):
    # If the centroids haven't changed then k-means has converged
    for i in range(0, len(centroidsA)):
        if centroidsA[i] != centroidsB[i]:
            return False
    return True

def computeError(clusters):
    # From the formula provided
    sse = 0
    for i in range(len(clusters)):
        for j in range(0, len(clusters[i])):
            # print(clusters[i][j][1])
            sse += clusters[i][j][1] * clusters[i][j][1]
            # print(sse)
    return sse

if __name__ == '__main__':

    col_names = ["A","B","Tweet"]
    file = pd.read_csv("usnewshealth.txt", delimiter="|", names=col_names)
    tweets = preprocess(file)

    k = 100
    max_iter = 10

    k_means(tweets, k, max_iter)
