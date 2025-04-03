import os
import subprocess
import sys
import time

def main():
    print("Checking if PyInstaller is installed...")
    try:
        subprocess.run(["pip", "install", "pyinstaller"], check=True)
        print("PyInstaller installed successfully.")
    except Exception as e:
        print(f"Error installing PyInstaller: {e}")
        print("Try installing manually with: pip install pyinstaller")
        return
    
    print("Starting PyInstaller compilation process...")
    print("Logging output to 'compilation_log.txt'")
    
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Open a log file
    with open("compilation_log.txt", "w") as log_file:
        log_file.write(f"Starting compilation at: {time.ctime()}\n\n")
        
        # PyInstaller command
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",  # No console window
            f"--icon={os.path.join(os.getcwd(), 'media/ICON.ico')}",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/ChakraPetch-Regular.ttf')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/browser_selection.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/additional_software_offer.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'media/DesktopBackground.png')};media",
            "--add-data", f"{os.path.join(os.getcwd(), 'configs/barebones.json')};configs",
            "--distpath", "./dist",
            "--name", "talon",
            os.path.join(os.getcwd(), "init.py")
        ]
        
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
