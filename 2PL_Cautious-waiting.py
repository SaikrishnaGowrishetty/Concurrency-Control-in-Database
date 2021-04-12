#program takes the input filename from the command line arguments and creates an output file accordingly
#command for running:- python 2PL_Cautious-waiting.py <inputfilename>
#eg:- python 2PL_Cautious-waiting.py input1.txt
#output text file is created with the name 'Output_of_input1'

import sys

#global variable for timestamp
time = 0
#global variable used for printing Transaction table and Lock table to output file
p = 0

# reads the input file name from command line
ifile = sys.argv[1]
# creates output file for the given input file
ofile = "Output_of_" + ifile
# opens the input file in read mode
inF = open(ifile, "r")
# opens the output file in write mode
outF = open(ofile, "w")

#Handles Begin Transaction request
def Begin_Transaction(Tname,Txlist):
    global time
    time = time+1 # increments the timestamp
    tid = "T"+Tname[1] # extracts transactionid from request
    print("Begin Transaction: "+tid, file=outF)
    #creates the transaction record
    r = {"TID":tid, "TimeStamp":time, "Status":"Active",
         "BlockedBy":"None", "BlockedOperations":[]}
    Txlist[tid] = r #adds the transaction record in transaction table
    return

#Handles Read Transaction request
def Read(Tname,Lklist,Txlist):
    tid = "T" + Tname[1] # extracts transactionid from request
    #Checks the status of Transaction and handles accordingly
    #if status is active, then checks for conflicts
    if (Txlist[tid]["Status"] == "Active"):
        rsrc = Tname[len(Tname)-2] #gets the name of the resource needed
        #if the resource is already locked, checks the lock mode
        if rsrc in Lklist:
            #if lockmode is write then runs the Cautious waiting by comparing timestamps
            if(Lklist[rsrc]["LockMode"] == "W"):
                tid1 = Lklist[rsrc]["TIDList"][0] #gets transactionid of transaction holding the resource
                """if the transaction holding the resource is not blocked then it blocks the requested transaction, 
                otherwise it aborts it"""
                if(Txlist[tid1]["Status"] != "Blocked"):
                    Txlist[tid]["Status"] = "Blocked"
                    Txlist[tid]["BlockedOperations"].append(Tname)
                    Txlist[tid]["BlockedBy"] = tid1
                    print (tid+" is blocked by cautious waiting as item "+rsrc+\
                          " is held by "+tid1+" and "+tid1+" is not blocked",file=outF)
                else:
                    Txlist[tid]["Status"] = "Aborted"
                    Txlist[tid]["BlockedOperations"] = []
                    Txlist[tid]["BlockedBy"] = "None"
                    print (tid + " tries to get R lock on " + rsrc+" ," + tid + \
                          " gets aborted by cautious waiting as rsrc is hold by " + tid1 +" and it is blocked",file=outF)
                    remove_locks(tid,Lklist,Txlist)
            # acquires shared read lock if lockmode is read
            else:
                Read_Lock(tid, rsrc, Lklist)
        #acquires read lock if resource is not locked
        else:
            Read_Lock(tid,rsrc,Lklist)
    #if status is blocked just adds the request to the list of waiting operations
    elif(Txlist[tid]["Status"] == "Blocked"):
        Txlist[tid]["BlockedOperations"].append(Tname)
        print("Because "+tid+" is blocked, we add this to list of waiting operation of "+tid, file=outF)
    # if status is aborted, prints that it is already aborted
    else:
        global p
        p = 0
        print(tid+" is already Aborted.So, no changes in the tables.", file=outF)
    return

#Acquires ReadLock on resource requested
def Read_Lock(TID,Data,Lklist):
    # if dataitem is already in lock table, appends the transaction to TIDList of dataitem
    if Data in Lklist:
        Lklist[Data]["TIDList"].append(TID)
        print("Item " + Data + " is read locked by "+TID, end=' ', file=outF)
        for i in Lklist[Data]["TIDList"]:
            if(i!=TID):
                print(" and "+i, end=' ', file=outF)
        print("", file=outF)
        return
    l = {"DataItem":Data, "LockMode":"R", "TIDList":[TID]} #creates the lock record
    Lklist[Data]=l #adds the record in lock table
    print("Item "+Data+" is read locked by "+ TID, file=outF)
    return

#Handles Write Transaction request
def Write(Tname,Lklist,Txlist):
    tid = "T" + Tname[1] #extracts transactionid from request
    # Checks the status of Transaction and handles accordingly
    # if status is active, then checks for conflicts
    if(Txlist[tid]["Status"] == "Active"):
        rsrc = Tname[len(Tname)-2] #gets the name of the resource needed
        #if the resource is already locked, checks the lock mode
        if rsrc in Lklist:
            #if rsrc is in read mode and if this is the only transaction accessing, upgrades it to write mode
            if(Lklist[rsrc]["LockMode"] == "R" and len(Lklist[rsrc]["TIDList"]) == 1
                and Lklist[rsrc]["TIDList"][0] == tid):
                Write_Lock(tid, rsrc, Lklist)
                return
            #if rsrc in shared mode then runs the Cautious waiting by comparing timestamps
            else:
                for i in Lklist[rsrc]["TIDList"]:
                    if(i!=tid):
                        """if the transaction holding the resource is not blocked then it blocks the requested 
                        transaction, otherwise it aborts it"""
                        if(Txlist[i]["Status"] != "Blocked"):
                            print (tid + " is blocked by cautious waiting as item " + rsrc + \
                                  " is held by " + i + " and " + i + " is not blocked",file=outF)
                            Txlist[tid]["BlockedBy"] = Txlist[tid]["BlockedBy"] + ", " + i
                            if Tname not in Txlist[tid]["BlockedOperations"]:
                                Txlist[tid]["Status"] = "Blocked"
                                Txlist[tid]["BlockedOperations"].append(Tname)
                        else:
                            Txlist[tid]["Status"] = "Aborted"
                            Txlist[tid]["BlockedOperations"] = []
                            Txlist[tid]["BlockedBy"] = "None"
                            print (tid + " tries to upgrade R lock on " + rsrc + " to W lock, " + tid + \
                                  " gets aborted by cautious waiting as as rsrc is hold by " + i +" and it is blocked",file=outF)
                            remove_locks(tid, Lklist, Txlist)
                        Txlist[tid]["BlockedBy"] = Txlist[tid]["BlockedBy"].replace("None, ", "")
                return
        else:
            Write_Lock(tid,rsrc,Lklist)
    # if status is blocked just adds the request to the list of waiting operations
    elif(Txlist[tid]["Status"] == "Blocked"):
        Txlist[tid]["BlockedOperations"].append(Tname)
        print("Because " + tid + " is blocked, we add this to list of waiting operation of " + tid, file=outF)
    # if status is aborted, prints that it is already aborted
    else:
        global p
        p = 0
        print(tid+" is already Aborted.So, no changes in the tables.", file=outF)
    return

#Acquires WriteLock on resource requested
def Write_Lock(TID,Data,Lklist):
    # if dataitem is already in lock table, appends the transaction to TIDList of dataitem
    if Data in Lklist:
        Lklist[Data]["LockMode"] = "W"
        print("Read lock upgraded to write lock on item " + Data + " by " + TID, file=outF)
        return
    l = {"DataItem":Data, "LockMode":"W", "TIDList":[TID]} #creates the lock record
    Lklist[Data]=l #adds the record in lock table
    return

#Handles End Transaction request
def End_Transaction(Tname,Txlist,Lklist):
    tid = "T" + Tname[1] #extracts transactionid from request
    # if status is aborted, prints that it is already aborted
    if (Txlist[tid]["Status"] == "Aborted"):
        global p
        p = 0
        print(tid + " is already Aborted.So, no changes in the tables.", file=outF)
    #commits transaction and release it's locks
    else:
        Txlist[tid]["Status"] = "Committed"
        Txlist[tid]["BlockedOperations"] = []
        Txlist[tid]["BlockedBy"] = "None"
        print("Commits " + tid + ". ", file=outF)
        remove_locks(tid, Lklist, Txlist)
    return

#Remove all the locks that a transaction holds if it is committed or aborted
def remove_locks(tid,Lklist,Txlist):
    for i in list(Lklist.keys()):
        tx = Lklist[i]["TIDList"]
        #removes the record from lock table if it is the only transaction holding it
        if(len(tx) == 1 and tx[0] == tid):
            Lklist.pop(i)
            print("Released "+tid+" lock on "+i, file=outF)
            Restart_Blocked(i, Lklist, Txlist) #resumes blocked operations
        elif tid in tx:
            Lklist[i]["TIDList"].remove(tid) #removes transaction from TIDList of Dataitem
            print("Released "+tid+" lock on "+i, file=outF)
            if(Lklist[i]["LockMode"] == "R" and len(Lklist[i]["TIDList"]) == 1):
                Restart_Blocked(i, Lklist, Txlist) #resumes blocked operations
    return

#Restarts the blocked operations as soon as the required resources are unlocked
def Restart_Blocked(i,Lklist,Txlist):
    #loops through the transactions in increasing order of timestamp
    for (key, value) in sorted(list(Txlist.items()), key=lambda x: x[1]["TimeStamp"], reverse=False):
        l = value["BlockedOperations"] #gets the blocked operations of transaction
        if (len(l)>0):
            k = Txlist[key]["BlockedOperations"][0] #gets first blocked operation
            #compares resource released and the resource required for blocked operation. If same, resumes the operation
            if (k[len(k) - 2] == i and Txlist[key]["Status"] == "Blocked"):
                print(key+" resumes and executes waiting operations ", file=outF)
                #updates the transaction record
                Txlist[key]["Status"] = "Active"
                Txlist[key]["BlockedBy"] = "None"
                Txlist[key]["BlockedOperations"].remove(k)
                print("executing Operation: "+k, file=outF)
                if (k[0] == "r"):
                    Read(k, Lklist, Txlist)
                elif (k[0] == "w"):
                    Write(k, Lklist, Txlist)
                #loops through all other waiting operations and executes them
                while(len(l)>0):
                    tx = Txlist[key]["BlockedOperations"][0]
                    Txlist[key]["BlockedOperations"].remove(tx)
                    print("executing Operation: " + tx, file=outF)
                    if (tx[0] == "r"):
                        Read(tx, Lklist, Txlist)
                    elif (tx[0] == "w"):
                        Write(tx, Lklist, Txlist)
    return

def main():
    #reads input file into a string
    ip = inF.read()
    #replaces spaces, newlines and stores the transactions into a list by splitting string using ";"
    t = ip.replace("\n","").replace(" ","").split(";")
    #Dictionary for Transaction Table
    Txlist={}
    #Dictionary for Lock Table
    Lklist={}
    #loop through the transactions list and executes them
    for j in t:
        if(j!=""):
            global p
            p = 1
            print("\nOperation "+j+";", file=outF)
            #compares the request and calls the corresponding function
            if(j[0]=="b"):
                Begin_Transaction(j,Txlist)
            elif(j[0]=="e"):
                End_Transaction(j,Txlist,Lklist)
            elif(j[0]=="r"):
                Read(j,Lklist,Txlist)
            elif(j[0]=="w"):
                Write(j,Lklist,Txlist)
            #prints Transaction table and Lock table to output file
            if(p==1):
                print("\nTransaction Table:", file=outF)
                for i in Txlist:
                    print(Txlist[i], file=outF)
                print("\nLock Table:", end=' ', file=outF)
                if(len(Lklist)==0):
                    print(" No Locks", file=outF)
                else:
                    print("", file=outF)
                    for i in Lklist:
                        print(Lklist[i], file=outF)
    return

if __name__ == "__main__":
    main()