import os, ConfigParser, time, argparse, paramiko, getpass

version = "BankErrorCheck v1.1"

config = ConfigParser.RawConfigParser()
config.read("config.cfg")

save = ""

if config.get("ssh", "host") == "":
	hostInput = raw_input("There is no SSH host in the config.cfg file. Please enter the SSH host: ")
	userInput = raw_input("Please enter the username: ")
	passwordInput = getpass.getpass("Please enter the password: ")
	save = raw_input("Would you like to save these details to config.cfg? ( y / n ) ")
	if save == "y" or save == "Y":
		config.set("ssh", "host", hostInput)
		config.set("ssh", "username", userInput)
		config.set("ssh", "password", passwordInput)
		with open('config.cfg', 'wb') as configfile:
    			config.write(configfile)


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
if config.get("ssh", "host") == "" and (save != "y" or save != "Y"):
	ssh.connect(hostInput, username=userInput, password=passwordInput)
else:
	ssh.connect(config.get("ssh", "host"), username=config.get("ssh", "username"), password=config.get("ssh", "password"))
print("Connected")
ftp = ssh.open_sftp()
ftp.chdir("/")

parser = argparse.ArgumentParser(description='Collect the date of reports to check.')
parser.add_argument("date", help="Enter the 7 digit date in format of YYYYMMDD")
args = parser.parse_args()

rootReportsSend = config.get("directories", "root_reports_send")
rootReportsReceive = config.get("directories", "root_reports_receive")
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

def getFileFromDir(directory, listToSave, subfolder, rootReport):
	for i in directory:
		folder = rootReport + "/" + subfolder + "/" + i
		ftp.chdir(folder)
		for files in ftp.listdir(folder):
			listToSave.append(files)

def comparison(directory, listToSave):
	for i in mappedFilesSent:
		i = i[0:-4]
		return i
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

getFileFromDir(matchedDirsSent, mappedFilesSent, config.get("directories", "directory_name_send"), rootReportsSend)
getFileFromDir(matchedDirsReceived, mappedFilesReceived, config.get("directories", "directory_name_receive"), rootReportsReceive)

print("Files in 'sent' folder:", mappedFilesSent)
print("\n")
print("Files in 'received' folder:", mappedFilesReceived)

print("\n/=== DIFFERENCES ===/\n")

comparison(mappedFilesReceived, filesInSentThatDontMatch)
comparison(mappedFilesSent, filesInReceivedThatDontMatch)



newFile = open("check_" + time.strftime("%d_%m_%y") + "_for_" + date + '.txt', 'w+')
newFile.write(version + "\n")
newFile.write("Comparison run: " + time.strftime("%c"))
newFile.write("\n\nDate checked: " + date)
newFile.write("\n\nThe output compares the two directories (as specified in config.cfg):\n\n" + "SEND = " + rootSend + "\n" + "RECEIVE = " +  rootReceive + "\n\n")
newFile.write("/===================ALL REPORTS==================/\n\n")
newFile.write("Send Reports: %s\n" % (len(mappedFilesSent)))
for i in mappedFilesSent:
	newFile.write(i + "\n")
newFile.write("\n")
newFile.write("Received reports: %s\n" % (len(mappedFilesReceived)))
for i in mappedFilesReceived:
	newFile.write(i + "\n")
newFile.write("\n/=================MISSING REPORTS================/\n\n")
newFile.write("Sent reports with missing received report: %s\n" % (len(filesInReceivedThatDontMatch)))
if filesInReceivedThatDontMatch == []:
	newFile.write("No missing received reports\n")
else:
	for i in filesInReceivedThatDontMatch:
		newFile.write(i + " ===> ??")
		newFile.write("\n")

if config.getboolean("directories", "show_ghost_reports") == True:
	newFile.write("\n\nReceived report with missing sent report: %s\n" % (len(filesInSentThatDontMatch)))
	if filesInSentThatDontMatch == []:
		newFile.write("No missing sent reports\n")
	else:
		for i in filesInSentThatDontMatch:
			newFile.write("?? <=== " + i)
			newFile.write("\n")


################### Incorporation of errorCheck.py ###################

filesWithError = []
filesUnsuccessful = []

def openCheck(directoryList, type):
	for i in directoryList:
		homeDir = rootReportsReceive + "/" + type + "/" + i
		ftp.chdir(homeDir)
		for files in ftp.listdir():
			files = files.encode('utf-8')
			path = homeDir + "/" + files
			openReport = ftp.open(path, "r", bufsize="1")
			fileContents = openReport.read()
			if "Errors" in fileContents:
				filesWithError.append(path)
			if "Failed" in fileContents:
				filesWithError.append(path)
			if "unsuccessful" in fileContents:
				filesUnsuccessful.append(path)

openCheck(matchedDirsReceived, config.get("directories", "directory_name_receive"))

print("\n/=== ERRORS ===/\n")

if filesWithError == []:
	print("No errors")
else:
	print(filesWithError, "report returned with an error.")
if filesUnsuccessful == []:
	print("No unsuccessful files")
else:
	print(filesUnsuccessful, "report processed unsuccessfully.")


newFile.write("\n/=====================ERRORS=====================/\n\n")

newFile.write("Reports processed successfully with error: %s\n" % (len(filesWithError)))

if filesWithError == []:
	newFile.write("No errors")
else:
	for i in filesWithError:
		newFile.write(i)
		newFile.write("\n")

newFile.write("\nReports processed unsuccessfully: %s\n" % (len(filesUnsuccessful)))

if filesUnsuccessful == []:
	newFile.write("No unsuccessful files")
else:
	for i in filesUnsuccessful:
		newFile.write(i)
		newFile.write("\n")