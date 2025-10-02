# whatsapp_go/setup.py
import subprocess
import sys
import os

class InstallPackages:
    """
    This Class installs required Python packages if not already installed.
    """

    @staticmethod
    def install():
        try:
            get_pckg = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
            installed_packages = [r.decode().split('==')[0] for r in get_pckg.split()]
            
            required_packages = ['PyJWT']  # Add any additional packages here
            
            for packg in required_packages:
                if packg in installed_packages:
                    print(f"{packg} is already installed.")
                else:
                    print(f"Installing {packg}...")
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', packg])
        except Exception as e:
            print(f"Failed to install required packages: {e}")
