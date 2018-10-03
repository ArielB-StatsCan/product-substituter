import dataset as ds
import substitution as sub
import timer as tim

tim.Timer.startTimer()

path = "P:\\Research\\CPI ADS Initiative\\4-Scanner Data (Sept 2016 on)\\Simple Implementation Plus (SI+)\\Data\\"

# Construct the product sales DataFrame
prodSalesDataSets = {9: ds.fromFile(path + "aggregatedSales_9.csv")}

# Construct the product description DataFrame
prodDescData = ds.fromFile(path + "productDescriptions.csv")

# Construct the outlet DataFrames
outletDataSets = {9: ds.fromFile(path + "outlets_9.csv")}

# Generate a dataset of TPOs
tpoData = ds.fromFile(path + "tpos_unassigned_9.csv")

# Construct the Substituter
substituter = sub.Substituter(prodDescData, prodSalesDataSets, outletDataSets)

# Substitute missing products
substituter.substitute(tpoData,
                       currentPeriodID = 9,
                       geoAggKey = 'City',
                       lowerQuantityCutoff = 0.5,
                       upperQuantityCutoff = 1,
                       neighbourCount = None,
                       relaunchDistanceCutoff = 0.01,
                       lowerDistanceCutoff = 0.5,
                       upperDistanceCutoff = 1,
                       samplingStrategy = 'top_proportional',
                       tpoMatchedFilePath = path + "tposMatched.csv",
                       details = True,
                       suggestionsFilePath = path + "suggestions.csv",
                       suggest = False,
                       summaryFilePath = path + "summary.csv")

print("\nElapsed time: " + str(tim.Timer.elapsedTime()))