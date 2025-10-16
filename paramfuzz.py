import argparse
import requests
import sys
import concurrent.futures

# --- Core Logic ---

# Function to run in each thread, now accepting baseline size and threshold
def check_parameter(url, param, fuzz_value, baseline_size, size_threshold):
    fuzz_url = f"{url}?{param}={fuzz_value}"
    
    try:
        response = requests.get(fuzz_url, timeout=5)
        current_size = len(response.content)
        
        # 1. Reflection Check (Quick and easy success indicator)
        if fuzz_value in response.text:
            # Return a descriptive string for success type
            return f"Reflection Found: {param}" 

        # 2. Differential Size Check (Robust detection)
        # Calculate the absolute percentage difference
        # The 'abs' ensures the calculation works whether the size is bigger or smaller
        diff = abs(current_size - baseline_size) / baseline_size
        
        # Check if the difference is greater than the defined threshold (10%)
        if diff > size_threshold:
            # Return a descriptive string for success type
            return f"Size Change: {param} (New Size: {current_size})"

    except requests.exceptions.RequestException:
        pass
    return None


def fuzz_parameters(url, wordlist_file):
    print(f"[+] Target URL: {url}")
    print(f"[+] Wordlist: {wordlist_file}\n")

    # Load parameters from wordlist file
    try:
        with open(wordlist_file, 'r') as f:
            parameters = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] Error: Wordlist file '{wordlist_file}' not found.")
        sys.exit(1)

    # --- Baseline Calculation (NEW BLOCK) ---
    print("[*] Calculating Baseline Response Size...")
    
    try:
        # Get baseline response from the unfuzzed URL
        baseline_response = requests.get(url, timeout=5)
        baseline_status = baseline_response.status_code
        baseline_size = len(baseline_response.content)
        print(f"[+] Baseline: Status={baseline_status}, Size={baseline_size} bytes.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Fatal Error: Could not get baseline response from {url}. Aborting. ({e})")
        sys.exit(1)
        
    # Define acceptable difference threshold (10% change)
    size_threshold = 0.10 
    
    # --- Fuzzing Execution ---
    
    found_params = []
    fuzz_value = "PARAMFUZZVALUE"
    MAX_THREADS = 10 # Set a reasonable limit for concurrent requests

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        
        # Submit tasks to the executor, passing all necessary arguments
        future_to_param = {
            executor.submit(check_parameter, url, param, fuzz_value, baseline_size, size_threshold): param 
            for param in parameters
        }
        
        total_params = len(parameters)
        tested_count = 0

        for future in concurrent.futures.as_completed(future_to_param):
            # The original param name is retrieved here, just for progress display
            param = future_to_param[future] 
            tested_count += 1
            
            # The result is now a string indicating success type OR None
            result_string = future.result() 

            # Update the progress display
            print(f"[*] Fuzzing progress: {len(found_params)} found, {tested_count}/{total_params} tested...", end='\r')

            if result_string:
                found_params.append(result_string) # Append the full descriptive string
                print(f"\n[!!!] FOUND PARAMETER: {result_string}")

    # --- Final Output ---

    print("\n[+] Scan finished.")
    if found_params:
        print("\n[--- Found Potential Parameters ---]")
        for p in found_params:
            print(f"- {p}")
    else:
        print("[-] No potential parameters found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ParamFuzz: Advanced multi-threaded tool for discovering URL parameters (uses Reflection and Size Diff checks).")
    parser.add_argument("-u", "--url", required=True, help="The target URL to fuzz (e.g., https://example.com/page.php)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the parameter wordlist file.")
    
    args = parser.parse_args()
    
    # Ensure the URL is valid before starting
    if not args.url.startswith(('http://', 'https://')):
        print("[-] Error: URL must start with http:// or https://")
        sys.exit(1)

    fuzz_parameters(args.url, args.wordlist)
