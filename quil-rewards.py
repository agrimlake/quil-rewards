import requests
import argparse
from dateutil import parser
import re

url = "https://quilibrium.com"

def format_with_separator(number, separator=','):
    """
    Format a number with a thousands separator.

    Args:
        number (float or int): The number to format.
        separator (str, optional): The character to use as the thousands separator. Default is ','.

    Returns:
        str: The formatted number with a thousands separator.
    """
    return f"{number:,.2f}".replace(",", separator)

def find_javascript_file_url(url):
    """
    Find the URL of the main JavaScript file on the given website.

    Args:
        url (str): The URL of the website.

    Returns:
        str: The URL of the main JavaScript file.
    """
    response = requests.get(url)
    html_content = response.text

    pattern = r'(/static/js/main.\w+\.js)"'
    matches = re.findall(pattern, html_content)

    if matches:
        return f"{url}{matches[0]}"
    else:
        raise ValueError("JavaScript file not found.")

def load_json_data(url):
    """
    Load JSON data from the specified URL.

    Args:
        url (str): The URL of the JSON file.

    Returns:
        list: A list of dictionaries containing the data.
    """
    response = requests.get(url)
    data = response.json()
    return data

def extract_last_update_from_javascript(url):
    """
    Extract the last update date from the main JavaScript file on the given website.

    Args:
        url (str): The URL of the main JavaScript file.

    Returns:
        datetime: The last update date.
    """
    response = requests.get(url)
    script_content = response.text

    last_update_match = re.search(r'Rewards \(Last Updated: ([\d-]+ \d+:\d+[AP]M \w+)\)', script_content)
    if last_update_match:
        last_update_str = last_update_match.group(1)
        last_update_str = last_update_str.replace(" PDT", "")
        last_update = parser.parse(last_update_str)
    else:
        last_update = None

    return last_update

def get_peer_stats(all_data):
    active_peers = []
    banned_peers = []
    inactive_peers = []
    inactive_1418_peers = []
    new_peers = []

    for peer_id, peer_data in all_data.items():
        if 'criteria' in all_data[peer_id]:
            criteria = all_data[peer_id]['criteria']
        else:
            criteria = "N/A"
        # reward = peer_data.get('total_reward', 0)
        existing_reward = peer_data.get('existing_reward', 0)
        rewards_reward = peer_data.get('rewards_reward', 0)

        if 'pre_1418_reward' in all_data[peer_id]:
            pre_1418_reward = all_data[peer_id]['pre_1418_reward']
        else:
            pre_1418_reward = 0
        
        if "post_1418_reward" in all_data[peer_id]:
            post_1418_reward = all_data[peer_id]['post_1418_reward']
        else:
            post_1418_reward = 0

        if criteria != 'N/A':
            banned_peers.append(peer_id)
        elif post_1418_reward > 0:
            active_peers.append(peer_id)
        elif post_1418_reward == 0 and pre_1418_reward == 0:
            inactive_peers.append(peer_id)
        elif pre_1418_reward > 0 and post_1418_reward == 0:
            inactive_1418_peers.append(peer_id)

        if existing_reward == 0 and rewards_reward == 0 and (pre_1418_reward > 0 or post_1418_reward > 0):    
            new_peers.append(peer_id)
        
    return len(active_peers), len(inactive_peers), len(inactive_1418_peers), len(banned_peers), len(new_peers)

def search_peer_by_id(peer_id, all_data):
    """
    Search for a peer by its PeerId in the provided data.

    Args:
        peer_id (str): The PeerId to search for.
        all_data (dict): A dictionary containing the peer data.

    Returns:
        dict or None: The dictionary containing the peer data if found, None otherwise.
    """
    return all_data.get(peer_id)

def load_peer_ids(args):
    """
    Load PeerIds from the provided file or command-line arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        list: A list of PeerIds.
    """
    if args.peer_ids:
        peer_ids = args.peer_ids
    else:
        try:
            with open(args.file, 'r') as file:
                peer_ids = [line.strip() for line in file]
        except FileNotFoundError:
            raise ValueError(f"The file {args.file} was not found.")
    return peer_ids

def compute_all_quil(all_data, last_update):
    """
    Compute and display the total rewards distribution for all nodes.

    Args:
        all_data (dict): A dictionary containing the peer data.
        last_update (datetime): The last update date.
    """
    total_reward = 0
    total_existing_balance = 0
    pre1418_balance = 0
    post1418_balance = 0

    for peer in all_data.keys():
        if "total_reward" in all_data[peer]:
            total_reward += all_data[peer]["total_reward"]
            total_existing_balance += all_data[peer]["existing_reward"]
            pre1418_balance += all_data[peer]["pre_1418_reward"]
            post1418_balance += all_data[peer]["post_1418_reward"]
    
    active_peers, inactive_peers, inactive_1418_peers, banned_peers, new_peers = get_peer_stats(all_data)

    print("=" * 80)
    print(f"Info: Last data update from {url}: {last_update}")
    print("Info: This is the total rewards distribution for all nodes...")
    print(f"\tTotal created Peers: {format_with_separator(len(all_data))} Nodes")

    print(f"\t\tActive Peers            : {format_with_separator(active_peers)}")
    print(f"\t\tInactive Peers < 12 May : {format_with_separator(inactive_peers)}")
    print(f"\t\tInactive Peers < 1.4.18 : {format_with_separator(inactive_1418_peers)}")
    print(f"\t\tNew Peers > 12 May      : {format_with_separator(new_peers)}")
    print(f"\t\tBanned Peers            : {format_with_separator(banned_peers)}")
    print()

    print(f"\tDistributed Rewards for all nodes  : {format_with_separator(total_reward)} QUIL")
    print(f"\tDistributed Rewards before 12 May  : {format_with_separator(total_existing_balance + pre1418_balance)} QUIL")
    print("\t----")
    print(f"\tTotal rewards for {format_with_separator(len(all_data))} Nodes: {format_with_separator(total_reward)} QUIL")
    print("=" * 80)

def print_peer_info(peer_id, peer_data):
    """
    Print the information for a given peer.

    Args:
        peer_id (str): The PeerId of the peer.
        peer_data (dict): The dictionary containing the peer data.
    """
    print(f"Peer ID: {peer_id}")
    
    existing_reward = peer_data.get('existing_reward', 0)
    rewards_reward = peer_data.get('rewards_reward', 0)
    pre_1418_reward = peer_data.get('pre_1418_reward', 0)
    post_1418_reward = peer_data.get('post_1418_reward', 0)
    
    print(f"Rewards before 2024 (Existing)                   : {format_with_separator(existing_reward)}")
    print(f"Rewards between January and May 12               : {format_with_separator(rewards_reward)}")
    print(f"Rewards between May 12 and v1.4.18               : {format_with_separator(pre_1418_reward)}")
    print(f"Rewards after v1.4.18 until today                : {format_with_separator(post_1418_reward)}")
    
    total_reward = existing_reward + rewards_reward + pre_1418_reward + post_1418_reward
    print(f"Total rewards                                    : {format_with_separator(total_reward)}")
    
    criteria = peer_data.get('criteria', 'N/A')
    if criteria != 'N/A':
        print(f"Criteria: {criteria}")
        
    print("---")
    return existing_reward, rewards_reward, pre_1418_reward, post_1418_reward

def merge_rewards_data(existing_data, rewards_data, pre_1418_data, post_1418_data, disqualified_data):
    """
    Merge the rewards data from different sources into a single dictionary.

    Args:
        existing_data (list): A list of dictionaries containing the existing rewards data.
        rewards_data (list): A list of dictionaries containing the rewards data.
        pre_1418_data (list): A list of dictionaries containing the pre-1.4.18 rewards data.
        post_1418_data (list): A list of dictionaries containing the post-1.4.18 rewards data.
        disqualified_data (list): A list of dictionaries containing the disqualified peers data.

    Returns:
        dict: A dictionary containing the merged rewards data.
    """
    merged_data = {}
    index = 0
    list_name = ["existing_data", "rewards_data", "pre_1418_data", "post_1418_data"]
    for data_source in [existing_data, rewards_data, pre_1418_data, post_1418_data]:
        print(f"Processing file...{list_name[index]}")
        index += 1
        for peer_data in data_source:
            peer_id = peer_data['peerId']
            reward = float(peer_data.get('reward', 0))

            if peer_id not in merged_data:
                merged_data[peer_id] = {
                    'peerId': peer_id,
                    'existing_reward': 0,
                    'rewards_reward': 0,
                    'pre_1418_reward': 0,
                    'post_1418_reward': 0,
                    'total_reward': 0,
                    'criteria': 'N/A'
                }

            if data_source == existing_data:
                merged_data[peer_id]['existing_reward'] = reward
            elif data_source == rewards_data:
                merged_data[peer_id]['rewards_reward'] = reward
                for month, presence in peer_data.items():
                    if month.endswith('Presence'):
                        merged_data[peer_id][month.capitalize()] = presence
            elif data_source == pre_1418_data:
                merged_data[peer_id]['pre_1418_reward'] = reward
            elif data_source == post_1418_data:
                merged_data[peer_id]['post_1418_reward'] = reward

            merged_data[peer_id]['total_reward'] += reward

    for peer_data in disqualified_data:
        peer_id = peer_data['peerId']
        if peer_id not in merged_data:
            merged_data[peer_id] = {
                'peerId': peer_id,
                'existing_reward': 0,
                'rewards_reward': 0,
                'pre_1418_reward': 0,
                'post_1418_reward': 0,
                'total_reward': 0,
                'criteria': 'N/A'
            }

        merged_data[peer_id]['criteria'] = peer_data.get('criteria', 'N/A')

    return merged_data

def main():
    existing_url = f"{url}/rewards/existing.json"
    rewards_url = f"{url}/rewards/rewards.json"
    pre_1418_url = f"{url}/rewards/pre-1.4.18.json"
    post_1418_url = f"{url}/rewards/post-1.4.18.json"
    disqualified_url = f"{url}/rewards/disqualified.json"

    existing_data = load_json_data(existing_url)
    rewards_data = load_json_data(rewards_url)
    pre_1418_data = load_json_data(pre_1418_url)
    post_1418_data = load_json_data(post_1418_url)
    disqualified_data = load_json_data(disqualified_url)

    all_data = merge_rewards_data(existing_data, rewards_data, pre_1418_data, post_1418_data, disqualified_data)

    try:
        javascript_file_url = find_javascript_file_url(url)
        last_update = extract_last_update_from_javascript(javascript_file_url)
    except ValueError as e:
        print(e)
        return

    parser = argparse.ArgumentParser(description='Find your rewards on the Quilibrium website')
    parser.add_argument('--file', type=str, default='peers.lst', help='File with PeerIds (one per line)')
    parser.add_argument('--peer_ids', type=str, nargs='+', help='List of PeerIds separated by spaces')
    args = parser.parse_args()

    peer_ids = load_peer_ids(args)
    
    compute_all_quil(all_data, last_update)

    total_existing_balance = 0
    total_reward = 0
    for peer_id in peer_ids:
        peer_data = search_peer_by_id(peer_id, all_data)

        if peer_data:
            existing_reward, rewards_reward, pre_1418_reward, post_1418_reward = print_peer_info(peer_id, peer_data)
            total_existing_balance += existing_reward + rewards_reward
            total_reward += pre_1418_reward + post_1418_reward
        else:
            print(f"No peer found with ID: {peer_id}")
        

    print(f"==>\tTotal Existing Balance (< 12 May)  : {total_existing_balance} QUIL")
    print(f"==>\tTotal Reward           (>= 12 May) : {total_reward} QUIL")
    print(f"==>\tTotal                              : {total_existing_balance + total_reward} QUIL")
    print("---")

if __name__ == "__main__":
    main()