import os
import platform
import urllib.request

def download_file(url, file_name):
    download_path = os.path.join(os.getcwd(), file_name)
    try:
        print(f"Downloading {file_name} to {download_path}...")
        urllib.request.urlretrieve(url, download_path)
        print(f"Download of {file_name} completed successfully!")
    except Exception as e:
        print(f"An error occurred while downloading {file_name}: {e}")

def download_dependencies():
    sikulix_urls = {
        "Windows": "https://launchpad.net/sikuli/sikulix/2.0.5/+download/sikulixapi-2.0.5-win.jar",
        "Linux": "https://launchpad.net/sikuli/sikulix/2.0.5/+download/sikulixapi-2.0.5-linux.jar",
        "Darwin": "https://launchpad.net/sikuli/sikulix/2.0.5/+download/sikulixapi-2.0.5-mac.jar"
    }
    jython_url = "https://repo1.maven.org/maven2/org/python/jython-standalone/2.7.4/jython-standalone-2.7.4.jar"

    system = platform.system()
    sikulix_url = sikulix_urls.get(system)

    if not sikulix_url:
        print(f"Unsupported operating system: {system}")
        return

    # Download SikuliX API
    sikulix_file_name = "sikulixapi-2.0.5.jar"
    download_file(sikulix_url, sikulix_file_name)

    # Download Jython Standalone
    jython_file_name = "jython-standalone-2.7.4.jar"
    download_file(jython_url, jython_file_name)

if __name__ == "__main__":
    download_dependencies()
