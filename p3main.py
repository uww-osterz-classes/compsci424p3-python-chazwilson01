"""
COMPSCI 424 Program 3
Name: Charlie Wilson 
"""

import os
import sys
import threading  # standard Python threading library
import random
# (Comments are just suggestions. Feel free to modify or delete them.)

# When you start a thread with a call to "threading.Thread", you will
# need to pass in the name of the function whose code should run in
# that thread.

# If you want your variables and data structures for the banker's
# algorithm to have global scope, declare them here. This may make
# the rest of your program easier to write. 
#  
# Most software engineers say global variables are a Bad Idea (and 
# they're usually correct!), but systems programmers do it all the
# time, so I'm allowing it here.
num_resources = 0
num_processes = 0
available =list()
max = list(list())
allocated = list(list())
need = []
request = list(list())
# Let's write a main method at the top
def main():
    global request, available, max, allocated, total, need, num_processes, num_resources
    # Code to test command-line argument processing.
    # You can keep, modify, or remove this. It's not required.
    if len(sys.argv) < 3:
        sys.stderr.write("Not enough command-line arguments provided, exiting.")
        sys.exit(1)

    print("Selected mode:", sys.argv[1])
    print("Setup file location:", sys.argv[2])

    # 1. Open the setup file using the path in argv[2]
    
    with open(sys.argv[2], 'r') as setup_file:
        # 2. Get the number of resources and processes from the setup
        # file, and use this info to create the Banker's Algorithm
        # data structures
        file = list()
        for line in setup_file: 
            data = line.split() 
            file.append(data)
            
        num_resources = int(file[0][0])
        print(num_resources, "resources")
        num_processes = int(file[1][0])
        print(num_processes, "processes")

        request = [[0 for i in range(num_resources)]for j in range(num_processes)]
        
        available_list = file[3]
        available = [int(i) for i in available_list]
        print(available, "Available ")

        max_list = file[5:10]
        max = [list( map(int,i) ) for i in max_list]
        print(max, "max ")

        allocated_list = file[11:]
        allocated = [list( map(int,i) ) for i in allocated_list]
        print(allocated, "allocated")
        # 3. Use the rest of the setup file to initialize the data structures
        # (you fill in this part)
    
    # 4. Check initial conditions to ensure that the system is
    # beginning in a safe state: see "Check initial conditions"
    # in the Program 3 instructions
    for p in range(0, len(max)):
        for r in range(0, len(max[0])):
            if allocated[p][r] > max[p][r]:
                print("Condition not met")

    isSafeState()
                        

    # 5. Go into either manual or automatic mode, depending on
    # the value of args[0]; you could implement these two modes
    # as separate methods within this class, as separate classes
    # with their own main methods, or as additional code within
    # this main method.

    mode = input("choose mode (manual or auto): ")

    if mode.lower() == "manual":
        manual()
    elif mode.lower() == "auto":
        threads = list()
        for i in range(int(num_processes)):
            p1 = threading.Thread(target=auto, args = (i,))
            threads.append(p1)
            p1.start()
        
        for index, thread in enumerate(threads):
            
            thread.join()



def auto(process):
    global num_processes, num_resources, max
    array_lock = threading.Lock()
    requests = 3
    releases = 3
    cmd = "request"

    while requests != 0 or releases != 0:
        # print(f'Thread: {process} || Requests: {3-requests} || Releases: {3-releases}')
        if requests == releases:
            cmd = "request"
            resource = random.randint(0, num_resources-1)

            I = random.randint(1, int(max[process][resource]) )
            with array_lock:
                handleRequest(process, resource, I)
            requests -= 1
        else: 
            cmd = "release"
            lst = []
            while len(lst) < num_resources:
                resource = random.randint(0, num_resources-1)
                if int(allocated[process][resource]) != 0:
                    break
                if resource not in lst:
                    lst.append(resource)
                
            
            I = random.randint(1, int(allocated[process][resource]) )
            
            with array_lock:
                handleRelease(process, resource, I)
            releases -= 1

    # printData()
    # print()
    # print()

                

def manual():
    global available, max, allocated, total, need, num_processes, num_resources

    cmd = input("Enter command: ")
    
    while cmd.lower() != "end":
        lst = cmd.split()
        if len(lst) != 6:
            print("Valid command not entered. Enter command in following format:")
            print("(request or release) I of R for P")
        else:
            I = int(lst[1])
            resource = int(lst[3])-1
            process = int(lst[5])-1

            if lst[0].lower() == "request":
                # print("Before: ")
                # printData()
                handleRequest(process, resource, I)

            elif lst[0].lower() == "release":
                # print("Before: ")
                # printData()
                handleRelease(process, resource, I)

            else:
                print("Valid command not entered. Enter command in following format:")
                print("(request or release) I of R for P")
        cmd = input("Enter command: ")

def handleRequest(process, resource, I):
    global available, max, allocated
    previousAll = allocated.copy()
    previousAval = available.copy()
    granted = False
    if I <= available[resource]:
        if I >= 0 and I <= max[process][resource]:
            allocated[process][resource] += I
            available[resource]  -= I
            if isSafeState():
                granted = True
                print(f'Process {process + 1} requests {I} units of resource {resource + 1}: granted ')
            else: 
                allocated[process][resource] = previousAll[process][resource]
                available[resource] = previousAval[resource]
    if not granted:
        print(f'Process {process + 1} requests {I} units of resource {resource + 1}: denied ')

    # printData()
    return granted

def handleRelease(process, resource, I):

    global available, max, allocated

    previousAll = allocated.copy()
    previousAval = available.copy()
    granted = False
    if I >= 0 and I <= allocated[process][resource]:
        allocated[process][resource] -= I
        available[resource] += I
        if isSafeState():
            granted = True
            print(f'Process {process + 1} releases {I} units of resource {resource + 1}: granted ')
        else: 
            allocated[process][resource] = previousAll[process][resource]
            available[resource] = previousAval[resource]
    if not granted:
        print(f'Process {process + 1} releases {I} units of resource {resource + 1}: denied ')  
    return granted
# fill in other methods here as desired
def findNeed(need, max, allocated):
     
     for i in range(len(max)):
        for j in range(len(max[0])):
            need[i][j] = max[i][j] - allocated[i][j] 

def isSafeState():
    global available, max, allocated, total, need, num_processes, num_resources
    found = False
    avail = available
    maxm = max
    allot = allocated
    num_processes = num_processes
    num_resources = num_resources
    for i in range (num_processes):
        l = []
        for j in range(num_resources):
            l.append(0)
        need.append(l)
    findNeed(need, maxm, allot)
    finish = [0] * num_processes

    safeSeq = [0] * num_processes

    work = [0] * num_resources

    for i in range(num_resources):
        work[i] = avail[i] 

    count = 0

    while(count < num_processes):

        for p in range(num_processes):

            if(finish[p] == 0):

                for j in range(num_resources):
                    if(need[p][j] > work[j]):
                        break
                
                if (j == num_resources -1):

                    for k in range(num_resources):

                        work[k] += allot[p][k]
                    safeSeq[count] = p
                    count += 1

                    finish[p] = 1

                    found = True
        
        if(found == False):
            # print("System is not in safe state")
            return False
        
    # print("System is in safe state.")
    return True
def printData():
    global available, allocated
    print(available)
    print()

    for r in allocated:
        for c in r:
            print(c, end = " ")
        print()
main() # call the main function