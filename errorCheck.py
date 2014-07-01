from fileComparison import *

filesWithError = []
filesUnsuccessful = []

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def openCheck():
	for i in mappedFilesReceived:
		path = find(i, rootReceive)
		file = open(path, "r")
		fileContents = file.read()
		if "Errors" in fileContents:
			filesWithError.append(i)
		if "unsuccessful" in fileContents:
			filesUnsuccessful.append(i)

openCheck()

print("\n/=== ERRORS ===/\n")

if filesWithError == []:
	print("No errors")
else:
	print(filesWithError, "report returned with an error.")
if filesUnsuccessful == []:
	print("No unsuccessful files")
else:
	print(filesUnsuccessful, "report returned with an unsuccessful transaction.")


newFile.write("\n/==================================/\n\n")

newFile.write("Reports returned with error:\n")

if filesWithError == []:
	newFile.write("No errors")
else:
	for i in filesWithError:
		newFile.write(i)
		newFile.write("\n")

newFile.write("\nReports returned with unsuccessful:\n")

if filesUnsuccessful == []:
	newFile.write("No unsuccessful files")
else:
	for i in filesUnsuccessful:
		newFile.write(i)
		newFile.write("\n")