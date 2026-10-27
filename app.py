import streamlit as st
import os
import networkx as nx
import time
from google import genai

# Page Configuration
st.set_page_config(
    page_title="SpectreOps | Red Team Attack Emulation",
    page_icon="🛡️",
    layout="wide"
)

# Custom Cyberpunk Theme Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stSidebar { background-color: #161b22; }
    .terminal-box { 
        background-color: #010409; 
        color: #00ff66; 
        padding: 15px; 
        border-radius: 6px; 
        font-family: monospace; 
        border: 1px solid #30363d;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ SpectreOps: Red Team Attack Emulation & Path Visualizer")
st.markdown("### Interactive Cyber Attack Simulation & Automated Reporting Platform")

# Initialize Network Topology Graph
class NetworkLab:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.setup_network()

    def setup_network(self):
        nodes = [
            ("External Gateway", {"type": "Router", "status": "Secure", "ip": "192.168.1.1"}),
            ("Web Application", {"type": "Server", "status": "Vulnerable", "ip": "192.168.1.10"}),
            ("Internal Database", {"type": "Database", "status": "Protected", "ip": "192.168.2.20"}),
            ("Admin Workstation", {"type": "Endpoint", "status": "Isolated", "ip": "192.168.2.50"})
        ]
        for node, attrs in nodes:
            self.graph.add_node(node, **attrs)

        edges = [
            ("External Gateway", "Web Application", {"port": 80, "protocol": "HTTP"}),
            ("Web Application", "Internal Database", {"port": 3306, "protocol": "MySQL"}),
            ("Web Application", "Admin Workstation", {"port": 22, "protocol": "SSH"})
        ]
        self.graph.add_edges_from(edges)

    def simulate_attack(self, vector):
        if vector == "SQL Injection (Web App)":
            return [
                "[+] Phase 1: Initiating Nmap stealth scan on 192.168.1.10...",
                "[+] Phase 2: Discovered open port 80 running Apache/2.4.49.",
                "[+] Phase 3: Injecting payload into login parameter: ' OR '1'='1 --",
                "[!] SUCCESS: Bypassed authentication on Web Application node.",
                "[+] Phase 4: Pivoting to Internal Database via stored connection strings..."
            ]
        elif vector == "SSH Brute-Force (Admin Workstation)":
            return [
                "[+] Phase 1: Scanning port 22 on Admin Workstation (192.168.2.50)...",
                "[+] Phase 2: Launching Hydra dictionary attack against SSH service...",
                "[!] SUCCESS: Found valid credentials (admin / admin123).",
                "[+] Phase 3: Establishing interactive reverse shell connection..."
            ]
        return ["[+] Scanning target topology...", "[!] Select an attack vector to proceed."]

lab = NetworkLab()

# Sidebar Controls
st.sidebar.header("🎯 Simulation Controls")
selected_vector = st.sidebar.selectbox(
    "Select Attack Vector",
    ["SQL Injection (Web App)", "SSH Brute-Force (Admin Workstation)"]
)

run_simulation = st.sidebar.button("🚀 Launch Attack Simulation", type="primary")

# Layout Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌐 Target Network Topology")
    st.write("Current Subnet Architecture & Nodes:")
    for node, data in lab.graph.nodes(data=True):
        st.markdown(f"- **{node}** (`{data['ip']}`) — *Status: {data['status']}*")

    st.markdown("---")
    st.subheader("💻 Live Terminal Output")
    terminal_placeholder = st.empty()
    terminal_placeholder.markdown('<div class="terminal-box">[+] System ready. Awaiting simulation trigger...</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📑 Automated Red Team Report")
    report_placeholder = st.empty()
    report_placeholder.info("Run a simulation to generate the AI-powered MITRE ATT&CK assessment report.")

# Execution Logic
if run_simulation:
    logs = lab.simulate_attack(selected_vector)
    
    # Animate Terminal Output
    terminal_output = ""
    for log in logs:
        terminal_output += log + "\n"
        terminal_placeholder.markdown(f'<div class="terminal-box">{terminal_output}</div>', unsafe_allow_html=True)
        time.sleep(0.5)

    # Gemini API Report Generation
    with st.spinner("Analyzing attack vectors and generating MITRE ATT&CK report via Gemini Flash..."):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                report_placeholder.error("⚠️ GEMINI_API_KEY environment variable missing. Please add it to your Streamlit Secrets.")
            else:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are an expert Red Team Security Lead. Analyze the following attack simulation logs for '{selected_vector}':
                
                Logs:
                {chr(10).join(logs)}
                
                Provide a professional Red Team Assessment Report containing:
                1. Executive Summary & Risk Level
                2. MITRE ATT&CK Mapping (Tactics and Techniques IDs)
                3. Root Cause Vulnerability Analysis
                4. Blue Team Remediation Recommendations
                
                Format using clean Markdown.
                """
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                report_placeholder.markdown(response.text)
        except Exception as e:
            report_placeholder.error(f"⚠️ Error generating AI report: {str(e)}")
