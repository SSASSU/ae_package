import subprocess
import os 

def config():
    command = 'openssl version'

    try:
        os.environ['LD_LIBRARY_PATH'] = "/usr/local/lib/"
        subprocess.run(command, shell=True, check=True)
        print("openssl checked!")

    except subprocess.CalledProcessError as e:
        print("error:", e)
