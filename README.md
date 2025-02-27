<h1>Gelbooru & Safebooru Client by MIMIC95</h1>

Supported Platforms
-  Windows 10/11
-  Arch Linux
-  Others.

<h2>Showcase</h2>




https://github.com/user-attachments/assets/0277ced9-0f1f-423c-a08b-24ba787ac34d




<h4>Features</h4>
- Download pictures from Safebooru (no API key required) and Gelbooru (API key required). <br/>
- Display downloaded pictures within the application, maintaining aspect ratios.<br/>
- User interface with controls to navigate to the previous or next picture using buttons or keyboard arrow keys.<br/>
- Autoplay feature that automatically displays downloaded images in a loop.<br/>
- Backup images function to save search results to a user-selected folder.<br/>
- Toggle button to switch between Gelbooru (NSFW) and Safebooru (SFW) searches.<br/>
- Slider to control the delay of the autoplay feature.<br/>
- Label displaying image information: URL, image size, and autoplay delay.<br/>
- Clicking the information label opens the image URL in the default browser.<br/>
- Double-clicking the image opens it in the default image viewer.<br/>
- Smart cleanup function that removes old search results when starting a new search.<br/>
- Smart download function to download images efficiently without causing delays or unresponsiveness in the program.<br/>

<hr>

<h2>Setup Guide</h2>

To use the program to access Gelbooru you only need to make a Gelbooru account, google it. <br/>
Technically you don't need a Gelbooru account or API Key but it might cause issues when accessing the API excessively.<br/>

![image](https://github.com/user-attachments/assets/80f7bf9b-f3e5-4d14-b8d8-706b38470294)


Go to Options

![image](https://github.com/user-attachments/assets/1b04d040-6cf2-4fe1-a62c-631fa7f65289)


Scroll all the way down to 

![image](https://github.com/user-attachments/assets/efb64f02-cce3-454a-ac51-a9f7066dfe9a)


copy what ever is between &api_key= and &user_id=... 
&api_key=<b>YOURAPIKEYISHERE</b>&user_id=34287

Input your API Key and add tags.

Tags:
There are posetive tags and negative tags, negative tags have a - in front of them, example:

Negative Tag:
-Furry

Posetive Tag:
Furry

Multiple Tags:
Elf+-Furry (Elf but no Furry)


The Backup Button allows you to copy the downloaded images to where ever you choose.
I kept the UI very simple by default it will always search for 100 results which is the maximum amount per search.

You can adjust autoplay speed with the slider it ranges from 0.5 to 10s.

I did not test this on any VM or a new PC so let me know if you encounter any issues.

As a programmer, I understand that some antivirus programs might flag this application as a potential threat. 
This is because the program performs actions that are commonly associated with malicious software, such as:

1. **Downloading Files**: The application downloads images from the internet, which can be seen as suspicious behavior by antivirus software.
2. **Opening Files**: The program opens downloaded images using system commands (`os.system`), which can be misinterpreted as an attempt to execute malicious code.
3. **File Operations**: The application reads, writes, and copies files on your system, which is a common behavior of malware.

However, I assure you that this program is not a virus. 
It is designed to download and display images from Gelbooru based on user-specified tags and an API key. 
The actions it performs are necessary for its functionality and are not harmful to your system. 
The source code is available for review, and you can see that it does not contain any malicious code.

By using any of my programs, you assume full responsibility for any potential negative outcomes. 
I do not provide any warranties of any kind, express or implied, regarding the use of these programs.
