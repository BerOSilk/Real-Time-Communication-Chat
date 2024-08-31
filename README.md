<h1>Welcome to Main-Chat</h1>
<h4>Created by Baraa AbuKhalil (BeroSilk)</h4>

>[!NOTE]
>This version is not the final version, there will be updates in the future.

<h1>Key features</h1>
<h3>User Authentication</h3>

- **User Registration**: Allows new users to create accounts by providing necessary information.
- **User Login**: Enables registered users to log in securely to access booking features.

<h3>User Settings</h3>

- **Show Neccessary Settings**: Allows the user see his current settings.
- **Change Changable Settings**: Allows the user to change some settings.

<h3>Users List</h3>

- **Users List**: Showing Users that registered in the app.
- **Sort Users List**: Sort Users by status (online -> DND -> IDLE -> [Offline/Invisible])
- **New message**: Showing the number of new messages (un-seen messages).

<h3>Global Users Search</h3>

- **Search by Names**: Users can search by usernames, display names, or both.
- **Showing Search Reasults**: Show the found users.

<h3>Communicate</h3>

- **Sending Messages between Users**: Send messages between each others to communicate.
- **Real Time Communication**: Allows the user on the other side to recieve the message at the same real time.
- **Files Messages**: Allows the user to send files as message.
- **Message sound Notification**: it will play a sound to notify the user that a new message came.
- **Reply to a message**: Allows the user to reply to a message

<h3>User Profile</h3>

- **User info**: Showing the user information such as username, display name, profile picture, and status.
- **Global Actions buttons**: Allows the user to report, block the user, or add the user as a friend.
- **Global Chat Actions buttons**: Allows the user to see pinned messages, media files, or search in the chat.

<h1>APIs<h1>

### - **Authentication**: Allows the user to register or login in the app
### - **Render**: Render chats, profiles.
### - **Request pfp**: Retriving and render Profile Pictures from the database.
### - **Send**: Send the message to the user and store it in the database.
### - **Update**: Update user settings in the database and the page.

<h1>Sockets</h1>
<h3>Python</h3>

- **app.py**

| socket method | name | Description |
| --- | --- | --- |
| on | request data | Requesting the data from javascript to send the message to the user. |
| emit | receive data | Emit the data from python to javascript to load the message sent to the user. |
| on | send logout request | Requesting data from javascript to show that the user is offline now. | 
| emit | logout request | Emit the data from python to javascript to show that the user is offline. |
| on | py login request | Requesting data from javascript to show that the user is online now. |
| emit | login request | Emit the data from python to javascript to show that the user is online. |

<h3>JavaScript</h3>

- **main.js**

| socket method | name | Description |
| --- | --- | --- |
| on | receive data | Requesting the data from python to load the message sent to the user. |
| emit | request data | Emit the data from javascript to python to send the message to the user. |
| on | login request | Requesting the data from python to show that the user is online. |
| on | logout request | Requesting the data from python to show that the user is offline. |

- **index.html**

| socket method | name | Description |
| --- | --- | --- |
| emit | send logout request | Emit the data from javascript to python to show that the uesr is offline now. |

- **main.html**
| socket method | name | Description |
| --- | --- | --- |
| emit | py login request | Emit the data from javascript to python to show that the user is online. |