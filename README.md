CRYPTO EXECUTION SIMULATOR
-------------------------------------------------------------

Author: Gaurvi Dohare
Project Type: Real-time trading simulation tool
Language: Python

1. PROJECT OVERVIEW
-------------------------------------------------------------

The Crypto Execution Simulator is a Python-based application that
simulates cryptocurrency trade execution using real-time Level-2
order book data from cryptocurrency exchanges.

The goal of this project is to analyze the cost of executing trades
in a live market environment by estimating important metrics such as:

• Slippage
• Market Impact
• Transaction Fees
• Net Execution Cost
• Maker/Taker Probability
• Internal Processing Latency

This project is intended for learning concepts related to:

• Market microstructure
• Order book dynamics
• Trade execution modeling
• Real-time financial data processing


2. FEATURES
-------------------------------------------------------------

• Real-time order book data streaming using WebSockets
• Simulation of trade execution using live market data
• Estimation of trading metrics such as slippage and market impact
• Graphical User Interface (GUI) built using PyQt5
• Numerical computation using NumPy
• Machine learning models using scikit-learn


3. TECHNOLOGY STACK
-------------------------------------------------------------

Programming Language
• Python 3.8+

Libraries
• PyQt5
• websockets
• NumPy
• scikit-learn


4. PROJECT STRUCTURE
-------------------------------------------------------------

crypto-execution-simulator/

│
├── trade_simulator.py      # Main application
├── requirements.txt        # Python dependencies
├── README.txt              # Project documentation
└── demo.mp4                # Demonstration video


5. INSTALLATION
-------------------------------------------------------------

1. Clone or download the repository.

2. Create a virtual environment (recommended):

python -m venv venv

Activate it:

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate


3. Install dependencies

pip install -r requirements.txt


6. RUNNING THE APPLICATION
-------------------------------------------------------------

Run the simulator using:

python trade_simulator.py

The GUI will open where you can input trade parameters and run
the simulation.


7. DISCLAIMER
-------------------------------------------------------------

This project is for educational and research purposes only.
It does not execute real trades and should not be used for
actual financial decision-making.