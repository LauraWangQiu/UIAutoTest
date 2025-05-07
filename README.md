# UIAutoTest

> Authors:  
> Paula Alemany Rodríguez  
> Pablo Iglesias Rodrigo  
> Andrés García Navarro  
> Cristina Mora Velasco  
> Francisco Miguel Galván Muñoz  
> Yi (Laura) Wang Qiu  

UI Automatization tests using [Sikulix](https://sikulix.github.io/docs/) and python scripts.

## Prerequisites

> [!IMPORTANT]
> Sikulix needs the whole machine: mouse cursor, keyboard and an unlocked screen for test automatization. Do not expect to use your PC in the usual way.

As stated in the [Sikulix's official documentation](https://sikulix.github.io/docs/start/installation), you will need:

- Windows, macOS or Linux
- Java 8+ installed
- All 64-bit version

For this project, it will be developed and only tested for Windows systems. Please read the documentation from the web above for more information.

Additionally, [Python](https://www.python.org/downloads/) will be used as the scripting language to interact with the Sikulix API.

### Other aspects

> [!NOTE] All the images must have sufficient quality to be clicked and displayed in the executable large enough.

> [!NOTE] Screen resolution must be on 100% without scaling.

### Download Sikulix API and Jython

```py
python downloadDependencies.py
```

### Install Python packages requirements

```cmd
pip install -r requirements.txt
```

## Try it

```ps
java -cp "sikulixapi-2.0.5.jar;jython-standalone-2.7.4.jar" org.python.util.jython test_script.py
```

```ps
python UIAutoTest.py
```
