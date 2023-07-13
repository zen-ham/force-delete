import os, subprocess, ctypes, signal, sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_admin():
    if '.py' in str(sys.argv):
        python = True
    else:
        python = False

    if not python:
        if is_admin():
            # Code of your program here
            pass
            #print("Congrats, you're running me with admin huh?")
        else:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            os.kill(os.getpid(), signal.SIGTERM)


get_admin()

# Get the absolute path of your exe
abs_path = os.path.abspath("Force_Delete.exe")

# Open .reg file and replace placeholder with absolute path
with open('Force_Delete_base.reg', 'r') as file:
    filedata = file.read()
    # Replace the target string
    filedata = filedata.replace(r'C:/path/to/your/Force_Delete.exe', abs_path.replace('\\','/'))
    # Write the file out again
    with open('Force_Delete.reg', 'w') as f:
        f.write(filedata)

# Now we have the .reg file with the correct path inside. Just need to merge it.
subprocess.call(['regedit', '/s', 'Force_Delete.reg'])