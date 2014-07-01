import os, configparser, time, argparse

config = configparser.ConfigParser()
config.read('config.cfg')

parser = argparse.ArgumentParser(description='Collect the date of reports to check.')
parser.add_argument("date", help="Enter the 7 digit date in format of YYYYMMDD")
args = parser.parse_args()

rootReports = config.get("directories", "root_reports")
rootSend = config.get("directories", "send_report_directory")
rootReceive = config.get("directories", "receive_report_directory")

sentDirectories = []
receivedDirectories = []

matchedDirsSent = []
matchedDirsReceived = []

mappedFilesSent = []
mappedFilesReceived = []

filesInSentThatDontMatch = []
filesInReceivedThatDontMatch = []

date = args.date
# date = "20140501"

def mapDirectories(root, listToSave):
	for dirs in os.listdir(root):
	    listToSave.append(dirs)
	print(sentDirectories)

def matchingDirs(directory, listToSave):
	if date == "0":
		for i in directory:
			listToSave.append(i)
			print("Added folder to checking list")
	else:
		for i in directory:
			print(i)
			if date == i[0:8]:
				listToSave.append(i)
				print("Added folder to checking list")
			else:
				print("Not equal to entered date")

def getFileFromDir(directory, listToSave, subfolder):
	for i in directory:
		folder = rootReports + subfolder + "/" + i
		for files in os.listdir(folder):
			listToSave.append(files)

def comparison(directory, listToSave):
	if directory == mappedFilesSent:
		against = mappedFilesReceived
		againstHumanReadable = "received"
	else:
		against = mappedFilesSent
		againstHumanReadable = "sent"
	for i in directory:
		try:
			against.index(i)
		except ValueError:
			print(i + " is not present within the " + againstHumanReadable + " folder." )
			listToSave.append(i)


mapDirectories(rootSend, sentDirectories)
mapDirectories(rootReceive, receivedDirectories)

print("\n/=======/\n")

matchingDirs(sentDirectories, matchedDirsSent)

print("\n/=======/\n")

matchingDirs(receivedDirectories, matchedDirsReceived)

print("\n/=======/\n")

print(matchedDirsSent)
print(matchedDirsReceived)

print("\n/=======/\n")

getFileFromDir(matchedDirsSent, mappedFilesSent, "send")
getFileFromDir(matchedDirsReceived, mappedFilesReceived, "receive")

print("Files in 'sent' folder:", mappedFilesSent)
print("Files in 'sent' folder:", mappedFilesReceived)

print("\n/=== DIFFERENCES ===/\n")

comparison(mappedFilesReceived, filesInSentThatDontMatch)
comparison(mappedFilesSent, filesInReceivedThatDontMatch)

newFile = open("check_" + time.strftime("%d_%m_%y") + "_for_" + date + '.txt', 'w+')
newFile.write("Comparison run: " + time.strftime("%c"))
newFile.write("\n\nDate compared: " + date)
newFile.write("\n\nThe output compares the two directories (as specified in config.cfg):\n\n" + rootSend + "\nand\n" + rootReceive + "\n\n")
newFile.write("/==================================/\n\n")
newFile.write("The files present in the send folder that are not present within the receive foler:\n")
for i in filesInSentThatDontMatch:
	newFile.write(i)
	newFile.write("\n")

if config.getboolean("directories", "show_ghost_reports") == True:
	newFile.write("\n\nThe files present in the received folder that are not present within the send foler:\n")
	for i in filesInReceivedThatDontMatch:
		newFile.write(i)
		newFile.write("\n")