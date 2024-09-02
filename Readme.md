# Multiplayer Tic Tac Toe Game
Welcome to the Multiplayer Tic-Tac-Toe game! This project is a Python-based implementation using Pygame for the client-side and Python's socket library for the server-client architecture. The game allows two players to connect over a network and play Tic-Tac-Toe against each other.

## Libraries Used
1. pygame
2. socket
3. threading
4. logging
5. queue

## Prerequisites

- Python 3.x
- pygame
```commandline
pip install pygame
```
- A modern web browser (optional, for opening social links)

## Setup Instructions
### 1. Clone Repository
```commandline
git clone https://github.com/yourusername/tic-tac-toe-multiplayer.git
cd tic-tac-toe-multiplayer
```
### 2. Install Dependencies
```commandline
pip install pygame
```
### 3. Running the Server
The server must be running before clients can connect. To start the server, use the following command:
```commandline
python server.py
```
The server listens for incoming connections and pairs up two players for a game.
### 4. Running the Client
Each player must run a client to connect to the server. Use the following command to start the client:
```commandline
python game_client.py
```
The client will attempt to connect to the server and wait for another player to join.
### 5. Playing the Game
Once two players are connected:
- The game randomly assigns "X" and "O" to the players.
- The game begins when both players are ready.
- The first player to get three of their marks in a row (vertically, horizontally, or diagonally) wins.
- If all tiles are filled and there is no winner, the game ends in a draw.

## How the Server and Clients Work
### Server
- The server uses Python's socket and select libraries to handle multiple client connections.
- It pairs two clients into a game, assigning each player a mark ("X" or "O").
- The server relays messages between the paired clients, updating the game state based on player moves.
- When a game ends, the server can reset or remove the game pair.

### Client
- The client uses Pygame for the graphical interface and sound.
- It connects to the server using a TCP connection and listens for incoming messages (like opponent moves).
- The client sends messages to the server, such as player moves, using the pickle module for serialization.

## Why Threading is Used
Threading is used in both the server and client to handle multiple tasks concurrently:
- **Server:** The server uses threading to manage multiple client connections simultaneously. Each client is handled in its own thread, allowing the server to receive and send messages to different clients without blocking the entire server process.


- **Client:** The client uses threading to listen for incoming messages from the server while the main game loop runs. This allows the game to remain responsive to user input while still receiving updates from the opponent.

## Logging

The server includes a logging mechanism to track important events and facilitate debugging. The log file, `server_log.log`, records the following details:

- **New Connections:** Logs every time a new player connects to the server, including their IP address and port.
- **Closed Connections:** Logs whenever a player disconnects from the server.
- **Message Exchange:** Records each message sent between players, specifying the sender, receiver, and content of the message.
- **Errors:** Logs any errors or exceptions encountered during socket creation, binding, or message transmission.

### Log Format

Each log entry includes a timestamp, log level (INFO or ERROR), and a message describing the event.

### Example Log Entry
```server_log.log
2024-09-03 12:45:32,101 - INFO - New connection accepted from ('127.0.0.1', 54321) 2024-09-03 12:45:45,256 - INFO - Message from ('127.0.0.1', 54321) to ('127.0.0.1', 54322): {'action': 'move', 'position': (1, 1)} 2024-09-03 12:46:00,789 - INFO - Closed connection from 127.0.0.1 : 54321
```

This logging system helps in monitoring the server's activity and diagnosing issues during development and production.
