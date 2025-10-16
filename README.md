# ParamFuzz 🕵️‍♂️: Advanced Multi-threaded URL Parameter Fuzzer

ParamFuzz is a **robust and fast Python-based tool** designed for the reconnaissance phase of penetration testing and bug hunting. It discovers potential GET parameters on a target URL by employing both simple reflection checks and **advanced differential analysis**.

---

## ✨ Key Features

* **Advanced Differential Analysis:** Compares the baseline response size (in bytes) of the target URL with the fuzzed request. A significant change in size indicates that the server successfully processed the parameter, even if the value wasn't reflected.
* **Multi-threaded Execution:** Utilizes Python's `concurrent.futures.ThreadPoolExecutor` to send requests simultaneously, drastically increasing scan speed and efficiency.
* **Reflection Check:** Includes a basic check to catch parameters that echo the input value (`PARAMFUZZVALUE`) back in the response body.
* **CLI Support:** Simple command-line interface using `argparse` for easy use.

---

## 🚀 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Creater-0/ParamFuzz.git](https://github.com/Creater-0/ParamFuzz.git)
    cd ParamFuzz
    ```
2.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💡 Usage

Run the tool by specifying a target URL (`-u`) and a wordlist file (`-w`).

```bash
python paramfuzz.py -u <target_url> -w <wordlist_file>

