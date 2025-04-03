import os
import subprocess
import sys
import time
import glob
import shutil
from pathlib import Path

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("Installing dependencies from requirements.txt...")
    
    req_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(req_file):
        print("WARNING: requirements.txt not found in current directory")
        return False
    
    try:
        subprocess.run(["pip", "install", "-r", req_file], check=True)
        print("All dependencies from requirements.txt installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def find_system_dlls():
    """Find system DLLs in Windows System directory"""
    system32_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
    ucrt_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'ucrt')
    
    # The list of DLLs we need to bundle
    dll_list = [
        'api-ms-win-core-path-l1-1-0.dll',
        'api-ms-win-crt-conio-l1-1-0.dll',
        'api-ms-win-crt-convert-l1-1-0.dll',
        'api-ms-win-crt-environment-l1-1-0.dll',
        'api-ms-win-crt-filesystem-l1-1-0.dll',
        'api-ms-win-crt-heap-l1-1-0.dll',
        'api-ms-win-crt-locale-l1-1-0.dll',
        'api-ms-win-crt-math-l1-1-0.dll',
        'api-ms-win-crt-multibyte-l1-1-0.dll',
        'api-ms-win-crt-process-l1-1-0.dll',
        'api-ms-win-crt-runtime-l1-1-0.dll',
        'api-ms-win-crt-stdio-l1-1-0.dll',
        'api-ms-win-crt-string-l1-1-0.dll',
        'api-ms-win-crt-time-l1-1-0.dll',
        'api-ms-win-crt-utility-l1-1-0.dll'
    ]
    
    # Also look for VC++ redistributable DLLs that might be needed
    redist_dlls = [
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'msvcp140.dll'
    ]
    
    dll_list.extend(redist_dlls)
    
    # Create a temporary directory to collect DLLs
    temp_dll_dir = os.path.join(os.getcwd(), 'temp_dlls')
    os.makedirs(temp_dll_dir, exist_ok=True)
    
    # Try to find each DLL
    dll_paths = []
    for dll in dll_list:
        # Check System32 first
        system32_dll = os.path.join(system32_path, dll)
        if os.path.exists(system32_dll):
            dll_dest = os.path.join(temp_dll_dir, dll)
            try:
                shutil.copy2(system32_dll, dll_dest)
                dll_paths.append(dll_dest)
                print(f"Found and copied: {dll}")
            except Exception as e:
                print(f"Error copying {dll}: {e}")
            continue
            
        # Check UCRT path
        ucrt_dll = os.path.join(ucrt_path, dll)
        if os.path.exists(ucrt_dll):
            dll_dest = os.path.join(temp_dll_dir, dll)
            try:
                shutil.copy2(ucrt_dll, dll_dest)
                dll_paths.append(dll_dest)
                print(f"Found and copied: {dll}")
            except Exception as e:
                print(f"Error copying {dll}: {e}")
            continue
            
        # Try to find in PATH
        for path_dir in os.environ.get('PATH', '').split(os.pathsep):
            if not path_dir:
                continue
            path_dll = os.path.join(path_dir, dll)
            if os.path.exists(path_dll):
                dll_dest = os.path.join(temp_dll_dir, dll)
                try:
                    shutil.copy2(path_dll, dll_dest)
                    dll_paths.append(dll_dest)
                    print(f"Found and copied: {dll}")
                except Exception as e:
                    print(f"Error copying {dll}: {e}")
                break
                
        # Check Program Files for Visual C++ Redistributable
        for program_files in ['C:\\Program Files', 'C:\\Program Files (x86)']:
            for pattern in [os.path.join(program_files, 'Microsoft Visual Studio', '**', dll),
                           os.path.join(program_files, 'Windows Kits', '**', dll)]:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    dll_dest = os.path.join(temp_dll_dir, dll)
                    try:
                        shutil.copy2(matches[0], dll_dest)
                        dll_paths.append(dll_dest)
                        print(f"Found and copied: {dll}")
                    except Exception as e:
                        print(f"Error copying {dll}: {e}")
                    break
            
        if dll not in [os.path.basename(p) for p in dll_paths]:
            print(f"Could not find: {dll}")
    
    return dll_paths

def main():
    print("Checking if required modules are installed...")
    
    # Install PyInstaller first
    try:
        subprocess.run(["pip", "install", "pyinstaller"], check=True)
        print("PyInstaller installed successfully.")
    except Exception as e:
        print(f"Error installing PyInstaller: {e}")
        return
    
    # Install dependencies from requirements.txt
    if not install_requirements():
        print("WARNING: Failed to install some dependencies from requirements.txt")
        print("Continuing with compilation, but some modules might be missing.")
    
    print("Locating system DLLs...")
    dll_paths = find_system_dlls()
    
    if not dll_paths:
        print("No system DLLs found. Compilation might not include all necessary files.")
    
    print("Starting PyInstaller compilation process...")
    print("Logging output to 'compilation_log.txt'")
    
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Open a log file
    with open("compilation_log.txt", "w") as log_file:
        log_file.write(f"Starting compilation at: {time.ctime()}\n\n")
        
        # PyInstaller command with additional hidden imports for common dependencies
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",  # No console window
            "--hidden-import=wmi",       # For Windows Management
            "--hidden-import=win32com",  # For COM objects
            "--hidden-import=win32com.client",
            "--hidden-import=pythoncom",
            "--hidden-import=requests",  # Add requests explicitly
            "--collect-all=requests",    # Collect all of requests package
            f"--icon={os.path.join(os.getcwd(), 'media/ICON.ico')}",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/ChakraPetch-Regular.ttf')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/browser_selection.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/additional_software_offer.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/DesktopBackground.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'configs/barebones.json')};configs",
            "--distpath", "./dist",
            "--name", "talon"
        ]
        
        # Add DLLs to PyInstaller command
        for dll_path in dll_paths:
            dll_name = os.path.basename(dll_path)
            pyinstaller_cmd.extend(["--add-binary", f"{dll_path};."])
            
        # Add the script to compile
        pyinstaller_cmd.append(os.path.join(os.getcwd(), "init.py"))
        
        # Log the command
        log_file.write("Running command:\n")
        log_file.write(" ".join(pyinstaller_cmd) + "\n\n")
        print("Running PyInstaller compilation...")
        
        # Run the command
        try:
            process = subprocess.Popen(
                pyinstaller_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time to both console and log
            for line in process.stdout:
                sys.stdout.write(line)
                log_file.write(line)
                
            process.wait()
            exit_code = process.returncode
            
            # Check result
            log_file.write(f"\nCompilation finished with exit code: {exit_code}\n")
            if exit_code == 0:
                success_msg = "SUCCESS: Compilation completed successfully."
                log_file.write(f"{success_msg}\n")
                print(f"\n{success_msg}")
                print("Executable should be available in the 'dist' directory.")
                
                # Clean up temp DLL directory
                temp_dll_dir = os.path.join(os.getcwd(), 'temp_dlls')
                if os.path.exists(temp_dll_dir):
                    shutil.rmtree(temp_dll_dir)
            else:
                error_msg = f"ERROR: Compilation failed with exit code {exit_code}"
                log_file.write(f"{error_msg}\n")
                print(f"\n{error_msg}")
                print("Check compilation_log.txt for details.")
                
        except Exception as e:
            error_msg = f"ERROR during compilation: {str(e)}"
            log_file.write(f"{error_msg}\n")
            print(error_msg)

if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()  # This will keep the window open until user presses Enter
