import argparse
import os
import re
import glob
import sys

 
def chop_loaded_log_message(line):
    try:
        fromClass,fromFile = line.split('[')[1].strip(']').strip("Loaded").strip().split("from")
        if 'file' in fromFile:
            fromFile = fromFile[6:]
        return (fromFile.strip(']'),fromClass)
    except:
        print(line)

def chop_unloaded_log_message(line):
    return line.split()[2].strip(']')

def get_sysid(line):
    found = re.search('([0-9a-f]{32})', line)
    if found:
        return found.groups()[0]
    return None

def gather_classes(inFile):
    loadedClasses = {}
    unloadedClasses = {}
    loadedMethods = 0
    loadedConstructors = 0
    unloadedMethods = 0
    unloadedContructors = 0
    foundSysId = False

    with open(inFile) as wrapper:
        for line in wrapper:
            if 'Loaded' in line and 'instance of' not in line:
                loadedFile,loadedClass = chop_loaded_log_message(line)
                if "GeneratedMethodAccessor" in loadedClass:
                    loadedMethods = loadedMethods + 1
                    continue
                if "GeneratedConstructorAccessor" in loadedClass:
                    loadedConstructors = loadedConstructors + 1
                    continue

                if "org.mozilla.javascript" in loadedClass:
                    sysId = get_sysid(loadedClass)
                    if sysId is not None:
                        if sysId in loadedClasses:
                            storeClass = loadedClasses.get(sysId)
                            storeClass['loadedCount'] = storeClass['loadedCount'] + 1
                            if loadedFile not in storeClass['loadedFiles']:
                                storeClass['loadedFiles'].append(loadedFiles)
                            loadedClasses[sysId] = storeClass
                            #print(loadedClasses.keys())
                            continue
                        else:
                            loadedClasses[sysId] = {'loadedCount': 1, 'loadedFiles': [loadedFile]}
                            continue

                if loadedClass in loadedClasses:
                    storeClass = loadedClasses.get(loadedClass)
                    storeClass['loadedCount'] = storeClass['loadedCount'] + 1
                    if loadedFile not in storeClass['loadedFiles']:
                        storeClass['loadedFiles'].append(loadedFile)
                    loadedClasses[loadedClass] = storeClass
                else:
                    loadedClasses[loadedClass] = {'loadedCount': 1, 'loadedFiles': [loadedFile]}

            elif 'Unloading' in line:
                unloadedClass = chop_unloaded_log_message(line)

                if "GeneratedMethodAccessor" in unloadedClass:
                    unloadedMethods = unloadedMethods + 1
                    continue
                if "GeneratedConstructorAccessor" in unloadedClass:
                    unloadedConstructors = unloadedConstructors + 1
                    continue

                if unloadedClass in unloadedClasses:
                    storeClass['unloadedCount'] = storeClass['unloadedCount'] + 1
        return(loadedClasses,unloadedClasses, loadedMethods, loadedConstructors, unloadedMethods, unloadedContructors)




def print_class_info(classes):
    for name, loadedClass in classes[0].items():
        if loadedClass['loadedCount'] > 1:
            print("Found Class: " + name)
            print("Class was loaded " + str(loadedClass['loadedCount']) + " times.")
            print("Class was found in the following files")
            print(loadedClass['loadedFiles'])
            print(" ")

    for name, unloadedClass in classes[1].items():
        print("Found Class: " + name)
        print("Class was unloaded " + str(loadedClass['unloadedCount']) + " times.")
        print(" ")
    
    print("***  Loaded Constructors and Methods  ***")
    print("Methods: " + str(classes[2]))
    print("Constructors: " + str(classes[3]))
    print("\n***  Unloaded Constructors and Methods  ***")
    print("Methods:  " + str(classes[3]))	
    print("Constructors " + str(classes[4]))

def main():
    
    parser = argparse.ArgumentParser(description='Read in a file or set of files, and return the result.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p','--path', help='Path of a file or a folder of files.')
    args = parser.parse_args()

    # Parse paths
    full_paths = [os.path.join(os.getcwd(), path) for path in args.path]
    files = set()
    for path in full_paths:
        if os.path.isfile(path):
            files.add(path)
            
        else:
            files |= set(glob.glob(path + '/*.log'))

    
    for f in files:
        print_class_info(gather_classes(f))
        print('##############################################################################################################################################################################################################################################################################')
     

if __name__ == '__main__':
    main()
