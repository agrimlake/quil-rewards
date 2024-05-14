# Quilibrium Rewards Tool

This Python script allows you to search and display reward information for specific peers in the Quilibrium network. You can find this information directly on the Quilibrium website at https://quilibrium.com/rewards. It allows you to extract reward data from the Quilibrium website and provides a detailed breakdown of rewards for each peer. 
It also provides some estimates/assumptions regarding the presence or absence of peers on the Quilibrium network (unreliable information).

## Features

- Searches for reward information for specific peers using their PeerId
- Displays reward details, including reward amount, monthly presence, criteria, existing balance, etc.
- Calculates and displays global statistics on the reward distribution for all nodes. (Be cautious, values may be unreliable)
- Supports searching for peers from a file or by passing PeerIds directly as command-line arguments

## Prerequisites

- Python 3.8 or higher
- requests module (installed via pip or pip3 below)

## Installation
Clone this repository or download the quil-rewards.py script.
Install the required dependencies by running the following command:
```bash 
pip install -r requirements.txt
```
or
```bash 
pip3 install -r requirements.txt
```

## Usage
Modify the peers.lst file and add the PeerIds of the peers you want to search for, one per line.
Run the script using one of the following methods:
Without arguments (will use peers.lst by default):
```bash 
python3 quil-rewards.py
```

By specifying PeerIds directly as arguments:
```bash 
python3 quil-rewards.py --peer_ids <peer_id_1> <peer_id_2> ...
```

By specifying a file containing PeerIds:
```bash 
python3 quil-rewards.py --file <path_to_file>
```
The script will display the reward information for each found peer, as well as global statistics on the reward distribution.

## Usage example
```bash 
python3 quil-rewards.py --peer_ids QmaBCDEF1234567890 QmXYZ0987654321
```

This will search for reward information for the peers with PeerIds QmaBCDEF1234567890 and QmXYZ0987654321 and display the corresponding details.
## Contributing
Contributions are welcome! If you find any bugs, have suggestions for improvements, or want to add new features, feel free to open an issue or submit a pull request.

