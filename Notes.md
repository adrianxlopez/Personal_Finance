# Notes
## Personal Notes
To preview markdown notes use the following command ``` cmd + Shift + v ```

## GitHub Notes
To clone a repository onto a local computer do the following: 

1. Ensure that Git is install in the computer
    ```
    git --version
    ```
2. Clone the repository from Github
    ```
    git clone {insert link to repo from github}
    ```
    This will create a folder under the working directory so it is advised to switch under the working directory you would like this repo to be in. 

3. Navigate into the project folder/open the folder on visual studio code to have access to all the files in the repository 

## Python Environments 
A python virtual environment is an isolated space where you can install packages to a specific project - to avoid conflicts between dependencies across different projects. Essentially it standardizes the dependencies along where ever the project will be executed. 

1. Create a virtual environment 
```
python -m venv venv
```
This will create a folder containing the python interpreter and site packages.The second argument will be used to for the name of the folder, in this case ```venv```. If using windows, **must** use the powershell to create the environment or command prompt. 

2. Activating the virtual environment 

There will be multiple ways to activate the environment depending on the OS and terminal type. 
```
Mac OS/Linux

source venv/bin/active
```
```
Windows CMD 

venv\Scripts\active
```
```
Windows Powershell

.\venv\Scripts\Active.ps1
```
To confirm that the environment is running, the prompt will show the following:  ```(venv) username$```

3. Install your dependencies 

Use pip to install packages into your virtual environment only
- Tip 1: Use ``` pip list ``` to check all installed packages and their versions if the project is already running without a environment so you can install the same versions of packages. 
- Tip 2: Use the following to install specific versions of packages ``` pip install pandas==2.0.1```
- Tip 3: Create a requirements.txt file with all the packages and versions in the specific format and install using ```pip install -r requirements.txt```: 
```
pandas==2.0.1
numpy==1.24.4
```


4. Save Dependencies 

Once the project runs properly
```
pip freeze > requirements.txt 
```
This file will contain all packages and versions required 

5. To re-create on another device 

``` 
python -m venv venv
follow step 2 depending on OS 
pip install -r requirements.txt
```

