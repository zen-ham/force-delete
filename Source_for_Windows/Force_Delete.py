import sys, os, psutil, shutil, ctypes, signal, time


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def EXIT():
    print('EXITING')
    os.kill(os.getpid(), signal.SIGTERM)


if not is_admin():
    print('This script is best ran from an admin powershell instance.')
    EXIT()


if len(sys.argv) < 2:
    print("No file/folder argument found.")
    EXIT()
else:
    delf = sys.argv[1]


def take_ownership(path):
    #command = f'takeown /F {path} /R /D Y'
    command = f'''powershell -command "Start-Process cmd -ArgumentList '/c takeown /f \\"{path}\\" && icacls \\"{path}\\" /grant *S-1-3-4:F /t /c /l' -Verb runAs"'''
    os.system(command)


def remove_folder(folder_name):
    shutil.rmtree(folder_name)


def get_all_files_in_path(path):
    drives = [path]
    listos = []
    for o in drives:
        for root, dirs, files in os.walk(str(o), topdown=True, onerror=None, followlinks=False):
            for f in files:
                listo = os.path.join(root, f)
                listos.append(f"{listo}\n")
    return listos


procs = []
for proc in psutil.process_iter(['pid', 'name']):
    procs.append(proc)


def multikill(kill_procs):
    for proc in kill_procs:
        try:
            os.kill(proc[0], 9)
        except:
            os.system(f'taskkill /F /IM "{proc[1]}" /T')


def delete_file_or_path(file_path):
    print(f'Deleting {file_path}')
    if os.path.exists(file_path):
        take_ownership(file_path)
        if os.path.isdir(file_path):
            files = get_all_files_in_path(file_path)
        else:
            files = file_path

        try:
            remove_folder(file_path)
        except Exception as e:
            kill_procs = []
            print(e)
            print(f'Failed, finding process')
            #if file_path.lower().endswith('.exe'):
            print('First pass')
            for proc in procs:
                try:
                    if file_path in proc.exe():
                        print(f"Found process {proc.pid} ({proc.name()}) accessing {file_path}.")
                        kill_procs.append([proc.pid, proc.name()])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            multikill(kill_procs)
            try:
                remove_folder(file_path)
            except:
                pass
            time.sleep(0.1)
            try:
                remove_folder(file_path)
            except:
                print('Second pass')

                for proc in procs:
                    try:
                        for item in proc.open_files():
                            # print(item.path)
                            if file_path in item.path or file_path.replace('\\', '/') in item.path:
                                print(f"Found process {proc.pid} ({proc.name()}) accessing {file_path}.")
                                kill_procs.append([proc.pid, proc.name()])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                    #print(f"Killed process {proc[1]} ({proc[1]}).")
                print('Finished second pass')
                multikill(kill_procs)
                remove_folder(file_path)
                try:
                    os.unlink(file_path)
                except:
                    pass
        if os.path.exists(file_path):
            print('Success! Path removed.')
    else:
        print('File did not exist')


delete_file_or_path(delf)

#time.sleep(5)