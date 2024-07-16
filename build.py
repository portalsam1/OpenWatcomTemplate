import os, glob, json, subprocess, platform, shutil, pathlib, sys;
from pathlib import Path;

watcomDirectory = "/c/WATCOM"
includeDirectory = watcomDirectory + "/h"
binaryDirectory = watcomDirectory + "/binnt64"

extraCompilerFlags = ""

processorList = ["8086", "186", "286", "386", "486", "Pentium", "Pentium Pro"]
coProcessorList = ["None", "287", "387", "Pentium Internal", "Pentium Pro Internal"]
memoryModels = ["Small", "Medium", "Compact", "Large", "Huge"]

sourceFileExtensions = ["c", "cc", "cpp", "c++"]

emulatorPath = "/c/Program Files/DOSBox-X"
emulatorArguments = "-userconf -nopromptfolder -c \"MOUNT C " + str(pathlib.Path().resolve()) + "\" -c \"C:\" -c \"cd out\" -c \"cls\" -c \"main.exe\""

def configurePaths():
    global watcomDirectory
    global includeDirectory
    global binaryDirectory
    global emulatorPath
    
    print("OpenWatcom Path Configurator:\n")

    print("Enter the path that the OpenWatcom installation resides in.")
    print("If you are on Windows, make sure youre running in a bash environment or things may act unexpectedly.")

    watcomPath = input("\nWatcom Directory (Default: /c/WATCOM): ")
    if watcomPath == "":
        watcomDirectory = "/c/WATCOM"
    else:
        watcomDirectory = watcomPath

    includeDirectory = watcomDirectory + "/h"

    print("\nEnter the subfolder in which the compiler binaries reside for your operating system.")
    print("Windows Ex.: /binnt64")

    binaryPath = input("\nBinary Directory (Default: /binnt64): ")
    if binaryPath == "":
        binaryDirectory = "/binnt64"
    else:
        binaryDirectory = binaryPath

    print("\nEnter the path in where your DOSBox-X installation is.")

    dosboxPath = input("\nDOSBox-X Directory (Default: /c/Program Files/DOSBox-X): ")
    if dosboxPath == "":
        emulatorPath = "/c/Program Files/DOSBox-X"
    else:
        emulatorPath = dosboxPath

    print("\nWriting to config...")

    with open("build.json", "a+") as file:
        file.seek(0)
        data = {}

        try:
            data = json.loads(file.read())
        except json.JSONDecodeError:
            print("Configuration file either is invalid or does not exist yet, overwriting...")
        
        file.truncate(0)
        
        data["watcomDirectory"] = watcomDirectory
        data["binaryDirectory"] = binaryDirectory
        data["dosboxPath"] = emulatorPath

        json.dump(data, file, indent=4)
        file.truncate()

    print("Done!")

def configureBuild():
    configureFlags = ""
    print("OpenWatcom Build Configurator:\n")

    print("Select processor to target.")
    for index, item in enumerate(processorList, start = 0):
        print(str(index) + ". [" + item + "]")

    processorChoice = 0
    while True:
        try:
            processorChoice = int(input("\nSelection: "))
            if processorChoice < 0 or processorChoice > len(processorList) - 1:
                raise ValueError
        except ValueError:
            print("\nInvalid Choice.")
        else: break
    
    configureFlags += "-" + str(processorChoice) + " "

    print("\nSelect math co-processor to generate code for.")
    for index, item in enumerate(coProcessorList, start = 0):
        print(str(index) + ". [" + item + "]")

    coProcessorChoice = 0
    while True:
        try:
            coProcessorChoice = int(input("\nSelection: "))
            if coProcessorChoice < 0 or coProcessorChoice > len(coProcessorList) - 1:
                raise ValueError
        except ValueError:
            print("\nInvalid Choice.")
        else: break

    match coProcessorChoice:
        case 1: configureFlags += "-fp2 "
        case 2: configureFlags += "-fp3 "
        case 3: configureFlags += "-fp5 "
        case 4: configureFlags += "-fp6 "

    print("\nSelect memory model.")
    for index, item in enumerate(memoryModels, start = 0):
        print(str(index) + ". [" + item + "]")

    memoryModelChoice = 0
    while True:
        try:
            memoryModelChoice = int(input("\nSelection: "))
            if memoryModelChoice < 0 or memoryModelChoice > len(memoryModels) - 1:
                raise ValueError
        except ValueError:
            print("\nInvalid Choice.")
        else: break

    match memoryModelChoice:
        case 0: configureFlags += "-ms"
        case 1: configureFlags += "-mm"
        case 2: configureFlags += "-mc"
        case 3: configureFlags += "-ml"
        case 4: configureFlags += "-mh"

    print("\nWriting to config...")

    with open("build.json", "a+") as file:
        file.seek(0)
        data = {}

        try:
            data = json.loads(file.read())
        except json.JSONDecodeError:
            print("Configuration file either is invalid or does not exist yet, overwriting...")
        
        file.truncate(0)
        
        data["extraCompilerFlags"] = configureFlags

        json.dump(data, file, indent=4)
        file.truncate()

    print("Done!")

def loadConfig():
    global watcomDirectory
    global binaryDirectory
    global extraCompilerFlags
    global includeDirectory
    global emulatorPath

    with open("build.json", "a+") as file:

        file.seek(0)
        data = {}

        try:

            data = json.loads(file.read())

            if "watcomDirectory" in data:
                watcomDirectory = data["watcomDirectory"]
            if "binaryDirectory" in data:
                binaryDirectory = data["binaryDirectory"]
            if "extraCompilerFlags" in data:
                extraCompilerFlags = data["extraCompilerFlags"]
            if "dosboxPath" in data:
                emulatorPath = data["dosboxPath"]

            includeDirectory = watcomDirectory + "/h"
            
        except json.JSONDecodeError:
            print("Configuration could not be read! It is reccomended you run 'configure path' and 'configure build'!")

def resetConfig():
    print("Removing config...")
    os.remove("build.json")

def setupEnvironment():
    global watcomDirectory
    global includeDirectory
    global binaryDirectory
    global emulatorPath

    environment = os.environ.copy()

    if platform.system() == "Windows":
        environment["WATCOM"] = watcomDirectory[2:]
        environment["INCLUDE"] = includeDirectory[2:]
        environment["PATH"] = binaryDirectory[2:] + ";" + emulatorPath[2:] + ";" + environment["PATH"]
    else:
        environment["WATCOM"] = watcomDirectory
        environment["INCLUDE"] = includeDirectory
        environment["PATH"] = binaryDirectory + ":" + emulatorPath + ":" + environment["PATH"]

    return environment

def assembleSources():
    sourceFiles = ""
    for extension in sourceFileExtensions:
        for file in glob.glob("src/**/*." + extension, recursive=True):
            sourceFiles += file + " "
    return sourceFiles

def build():
    global extraCompilerFlags

    environment = setupEnvironment()
    sources = assembleSources()

    loadConfig()

    args = "wcl -bt=dos " + str(extraCompilerFlags) + " " + str(sources)
    compiler = subprocess.Popen(args, env=environment, shell=False)
    compiler.wait()

    outputFiles = glob.glob("*.exe") + glob.glob("*.obj") + glob.glob("*.err")
    for file in outputFiles:
        try:
            shutil.move(file, "out/")
        except: pass
        try:
            os.remove(file)
        except: pass

def run():
    global emulatorPath
    global emulatorArguments

    environment = setupEnvironment()
    
    args = emulatorPath[2:] + "/dosbox-x " + str(emulatorArguments)
    emulator = subprocess.Popen(args, env=environment, shell=False)
    emulator.wait()

def clean():
    print("Cleaning...")
    for file in glob.glob("out/**"):
        os.remove(file)

def main():
    loadConfig()
    if len(sys.argv) > 1:
        match sys.argv[1]:
            case "build": build(); return
            case "run": run(); return
            case "reset": resetConfig(); return
            case "clean": clean(); return
            case "configure":
                if len(sys.argv) > 2:
                    match sys.argv[2]:
                        case "path": configurePaths(); return
                        case "build": configureBuild(); return
                        case _: print("Please specify an option to configure, valid options: [path, build].")
                else:
                    print("Please specify an option to configure, valid options: [path, build].")
            case _:
                        print("Please specify a valid action, valid actions: [build, run, reset, clean, configure].")
    else:
        print("Please specify a valid action, valid actions: [build, run, reset, clean, configure].")

if __name__ == "__main__":
    main()