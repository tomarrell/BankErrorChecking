import os, ConfigParser, time, argparse, paramiko

version = "BankErrorCheck v0.6"

config = ConfigParser.ConfigParser()
config.read('config.cfg')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect(config.get("ssh", "host"), username=config.get("ssh", "username"), 
    password=config.get("ssh", "password"))
print("Connected")
ftp = ssh.open_sftp()
ftp.chdir("/")

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
	for dirs in ftp.listdir(root):
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
		folder = rootReports + "/" + subfolder + "/" + i
		ftp.chdir(folder)
		for files in ftp.listdir(folder):
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
print("Files in 'received' folder:", mappedFilesReceived)

print("\n/=== DIFFERENCES ===/\n")

comparison(mappedFilesReceived, filesInSentThatDontMatch)
comparison(mappedFilesSent, filesInReceivedThatDontMatch)

newFile = open("check_" + time.strftime("%d_%m_%y") + "_for_" + date + '.txt', 'w+')
newFile.write(version + "\n\n")
newFile.write("Comparison run: " + time.strftime("%c"))
newFile.write("\n\nDate checked: " + date)
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


################### Incorporation of errorCheck.py ###################

filesWithError = []
filesUnsuccessful = []

def openCheck(directoryList, type):
	for i in directoryList:
		print(rootReports + "/" + type + "/" + i)
		homeDir = rootReports + "/" + type + "/" + i
		ftp.chdir(homeDir)
		for files in ftp.listdir():
			files = files.encode('utf-8')
			path = homeDir + "/" + files
			print(path)
			openReport = ftp.open(path, "r", bufsize="1")
			fileContents = openReport.read()
			if "Errors" in fileContents:
				filesWithError.append(path)
			if "unsuccessful" in fileContents:
				filesUnsuccessful.append(path)

openCheck(matchedDirsReceived, "receive")

print("\n/=== ERRORS ===/\n")

if filesWithError == []:
	print("No errors")
else:
	print(filesWithError, "report returned with an error.")
if filesUnsuccessful == []:
	print("No unsuccessful files")
else:
	print(filesUnsuccessful, "report processed unsuccessfully.")


newFile.write("\n/==================================/\n\n")

newFile.write("Reports processed successfully with error:\n")

if filesWithError == []:
	newFile.write("No errors")
else:
	for i in filesWithError:
		newFile.write(i)
		newFile.write("\n")

newFile.write("\nReports processed unsuccessfully:\n")

if filesUnsuccessful == []:
	newFile.write("No unsuccessful files")
else:
	for i in filesUnsuccessful:
		newFile.write(i)
		newFile.write("\n")