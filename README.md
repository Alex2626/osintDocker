# OSINT (Shodan, Tinfoleak & Dorks)

## Contents
1. [Project description](#project-description)
2. [Features](#features)
3. [How to run](#how-to-run)
4. [References](#references)
5. [License](#license)


# Project description

This project use OSINT techniques and tools to obtain information from open sources of an organization or company and use the information obtained to determine possible attack points or vulnerabilities.

In this project has been used three tools or projects to achive our goals:

	* ## Tinfoleak: With this project we can search in twitter about a profile, hastagh or words in tweets -> https://github.com/vaguileradiaz/tinfoleak
	* ## Shodan: Used by the app to obtain the devices connected to Internet from our objetive and could make our organization/company vulnerable. We use queries with key words about deprecated technologies, open ports... -> https://www.shodan.io/
	* ## Dorks: Google and Bing are the search engines selected to find documents, webs or pass using the powerful of DORKS. To use the latest DORKS we refresh our list using Google Hacking Data Base, in this site we can find the latest dorks for the latest vulnerabilities. -> https://www.exploit-db.com/google-hacking-database && https://github.com/USSCltd/dorks

# Features

This app was developing by modules in order to use the differents projects (Tinfoleak, Shodan and Dorks) and in the future will add others functionalities. 
This project is intended to work on any plataform (Windows, Mac or Linux) and for this reason I developed it to work in Docker.

The modules using differents forms to make it work:

	* ## Tinfoleak: This module use the 2.1 version from this software because it´s the version that allows to run it from a CLI.
	* ## Shodan:    Using the CLI who offers Shodan for Linux distro, we install it before of run the app.
	* ## Dorks:     With the project https://github.com/USSCltd/dorks we obtain the links to the data that I want to obtain about the objetive. Using phanthomjs we call the dorks.js

Every module have their conf file where it´s posible to change the objetive, queries, etc. You can change it before or after build and run the Docker image/container.


# How to run

You have two options to run this app: building the Docker image using the DockerFile including in this repo or with a DockerHub account and pulling the image from my repository in DockerHub.

## 1. Using DockerFile

		* 1.1. Build the Docker image using: docker build -t xxxxx/xxxx:tag .
		* 1.2. Run the image: docker run –t –i –-name  xxxxx/xxxxxx
			* 1.2.1. If you have modified the conf files: docker exec -i -t osint /osint-auto/scriptMaster.py
			* 1.2.2. If you haven´t modified the conf files you can open the container with a shell, and modify it: docker exec –t –i –-name xxxxx/xxxxx:tag /bin/bash
				   And you will be in the container and execute the app from here.

## 2. Using DockerHub
		* 2.1. Login or signin.
		* 2.2. Search the project "asanchezdev/osint-automatization".
		* 2.3. Pull the image.
		* 2.4. Follow the step 1.2. 



# License

This project is of public domain and can be used by anybody under his responsibility. It was created with defensive proposites, if you use it for other achivements is your responsability
