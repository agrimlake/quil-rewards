import requests
import re
import json
import argparse
from dateutil import parser
from datetime import datetime
from datetime import datetime, timedelta

url = "https://quilibrium.com"

def format_with_separator(number, separator=' '):
    """
    Formats a number with a thousands separator.

    Args:
        number (float or int): The number to format.
        separator (str, optional): The character to use as the thousands separator. Default is ' '.

    Returns:
        str: The number formatted with a thousands separator.
    """
    number_str = str(number)
    parts = number_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ''

    reversed_integer_part = integer_part[::-1]
    formatted_integer_part = separator.join([reversed_integer_part[i:i+3] for i in range(0, len(reversed_integer_part), 3)])
    formatted_integer_part = formatted_integer_part[::-1]

    if decimal_part:
        formatted_number = f"{formatted_integer_part}.{decimal_part}"
    else:
        formatted_number = formatted_integer_part

    return formatted_number

def find_javascript_file_url(url):
    """
    Finds the URL of the main JavaScript file on the given website.

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

def convert_numeric_values(obj):
    if isinstance(obj, dict):
        return {k: convert_numeric_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numeric_values(v) for v in obj]
    elif isinstance(obj, str):
        if obj.isdigit():
            return int(obj)
        else:
            try:
                return float(obj)
            except ValueError:
                return obj
    else:
        return obj

def extract_peers(script_content):
    pattern = r"\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*peerId(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}"
    matches = re.findall(pattern, script_content)

    peers_dict = {}
    for match in matches:
        # Ajouter des guillemets doubles autour des clés
        match = re.sub(r"(\w+):", r'"\1":', match)

        # Remplacer les valeurs booléennes !0 et !1 par false et true
        match = match.replace("!0", "true").replace("!1", "false")

        # Supprimer les virgules de fin inutiles
        match = re.sub(r",\s*}", "}", match)

        try:
            peer_data = json.loads(match)
            peer_id = peer_data.get("peerId")
            if peer_id:
                # Convertir les valeurs numériques en entiers ou en flottants
                peer_data = convert_numeric_values(peer_data)
                if peer_id in peers_dict:
                    peers_dict[peer_id].update(peer_data)
                else:
                    peers_dict[peer_id] = peer_data
        except json.JSONDecodeError:
            # Ignorer les correspondances invalides
            pass

    return list(peers_dict.values())


def extract_data_from_javascript(url):
    """
    Extracts data from the main JavaScript file on the given website.

    Args:
        url (str): The URL of the main JavaScript file.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    response = requests.get(url)
    script_content = response.text

    all_data = extract_peers(script_content)

    # Rechercher la date de dernière mise à jour
    last_update_match = re.search(r'Rewards \(Last Updated: ([\d-]+ \d+:\d+[AP]M \w+)\)', script_content)
    if last_update_match:
        last_update_str = last_update_match.group(1)
        last_update_str = last_update_str.replace(" PDT", "")
        last_update = parser.parse(last_update_str)
    else:
        last_update = None

    return all_data, last_update

def get_active_peers_stats(all_data, last_update):
    active_peers = []
    banned_peers = []
    inactive_peers = []
    recent_inactive_peers = []

    current_month = last_update.strftime("%b").lower()
    current_month_presence = f"{current_month}Presence"
    previous_month = (last_update.replace(day=1) - timedelta(days=1)).strftime("%b").lower()

    previous_month_presence = f"{previous_month}Presence"

    for peer in all_data:
        criteria = peer.get('criteria', 'N/A')
        reward = peer.get('reward', 0)

        if criteria != 'N/A':
            banned_peers.append(peer)
        else:
            current_month_active = peer.get(current_month_presence, False)
            previous_month_active = peer.get(previous_month_presence, False)

            if reward == 0:
                inactive_peers.append(peer)
            elif not current_month_active:
                if previous_month_active:
                    recent_inactive_peers.append(peer)
                else:
                    inactive_peers.append(peer)
            else:
                active_peers.append(peer)

    return len(active_peers), len(inactive_peers), len(recent_inactive_peers), len(banned_peers)

def search_peer_by_id(peer_id, all_data):
    """
    Searches for a peer by its PeerId in the given data.

    Args:
        peer_id (str): The PeerId to search for.
        all_data (list): A list of dictionaries containing the data.

    Returns:
        dict or None: The dictionary containing the peer data if found, None otherwise.
    """
    for peer in all_data:
        if peer.get("peerId") == peer_id:
            return peer
    return None

def load_peer_ids(args):
    """
    Loads the PeerIds from the provided file or command-line arguments.

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
            raise ValueError(f"The file {args.file} not found")
    return peer_ids

def print_all_peers(all_data):
    for peer in all_data:
        print_peer_info(peer, 0, 0)

def compute_all_quil(all_data, last_update):
    """
    Computes and prints the total rewards distribution for all nodes.

    Args:
        all_data (list): A list of dictionaries containing the data.
    """
    reward = sum(peer.get('reward', 0) for peer in all_data)
    existing_balance = sum(peer.get('existingBalance', 0) for peer in all_data)
    active_peers, inactive_peers, recent_inactive_peers, banned_peers = get_active_peers_stats(all_data, last_update)

    print(f"==============================================================================\n")
    print(f"info: Last data update from {url} : {last_update} PDT")
    print(f"Info: This is the total rewards distribution for all nodes...\n")
    print(f"\tTotal created Peers : {format_with_separator(len(all_data))} Nodes")

    print(f"\t\tActive Peers          ( == Month      )  : {format_with_separator(active_peers)}")
    print(f"\t\tRecent Inactive Peers ( <= Month - 1  )  : {format_with_separator(recent_inactive_peers)}")
    print(f"\t\tInactive Peers        ( >= Month - 2  )  : {format_with_separator(inactive_peers)}")
    print(f"\t\tBanned Peers                             : {format_with_separator(banned_peers)}")
    print("")

    print(f"\tDistributed Rewards for all nodes          : {format_with_separator(reward, ',')} QUIL")
    print(f"\tDistributed Rewards in 2023                : {format_with_separator(existing_balance, ',')} QUIL")
    print("\t----")
    print(f"\tTotal rewards for {format_with_separator(len(all_data))} Nodes : {format_with_separator(existing_balance + reward, ',')} QUIL\n")
    print(f"==============================================================================\n")

def print_peer_info(peer, total_existing_balance, total_reward):
    """
    Prints the information for a given peer and updates the total existing balance and reward.

    Args:
        peer (dict): The dictionary containing the peer data.
        total_existing_balance (float): The total existing balance to update.
        total_reward (float): The total reward to update.

    Returns:
        tuple: The updated total existing balance and total reward.
    """
    print(f"Peer ID: {peer['peerId']}")
    reward = peer.get('reward', 0)
    total_reward += reward
    print(f"Reward: {reward}")

    for month, presence in peer.items():
        if month.endswith('Presence'):
            print(f"{month.capitalize().replace('presence', '')} Presence: {presence}")

    print(f"Range: {peer.get('range', 'N/A')}")
    print(f"Criteria: {peer.get('criteria', 'N/A')}")
    existing_balance = peer.get('existingBalance', 0)
    total_existing_balance += existing_balance
    print(f"Existing Balance: {existing_balance}")
    print("---")

    return total_existing_balance, total_reward

def main():


    try:
        javascript_file_url = find_javascript_file_url(url)
        all_data, last_update = extract_data_from_javascript(javascript_file_url)
    except ValueError as e:
        print(e)
        return

    parser = argparse.ArgumentParser(description='Find your rewards on Quilibrium website')
    parser.add_argument('--file', type=str, default='peers.lst', help='File with PeerIds (One by line)')
    parser.add_argument('--peer_ids', type=str, nargs='+', help='List of PeerId separeted by space')
    args = parser.parse_args()

    peer_ids = load_peer_ids(args)
    
    compute_all_quil(all_data, last_update)

    total_existing_balance = 0
    total_reward = 0

    for peer_id in peer_ids:
        peer = search_peer_by_id(peer_id, all_data)

        if peer:
            total_existing_balance, total_reward = print_peer_info(peer, total_existing_balance, total_reward)
        else:
            print(f"No peer found with ID: {peer_id}")

    print(f"==>\tTotal Existing Balance : {total_existing_balance} QUIL")
    print(f"==>\tTotal Reward           : {total_reward} QUIL")
    print(f"==>\tTotal                  : {total_existing_balance + total_reward} QUIL")
    print("---")

if __name__ == "__main__":
    main()
