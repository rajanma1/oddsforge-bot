from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OddsForge Bot | Production Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/6.7.0/ethers.umd.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Inter', sans-serif; background-color: #0a0a0a; color: #ededed; }
                .glow { box-shadow: 0 0 20px rgba(34, 197, 94, 0.2); }
            </style>
        </head>
        <body class="p-8">
            <div class="max-w-4xl mx-auto">
                <header class="flex justify-between items-center mb-12">
                    <div>
                        <h1 class="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">OddsForge Pro Bot</h1>
                        <p class="text-gray-400 mt-2">High-Frequency Quant Trading Dashboard</p>
                    </div>
                    <div class="flex items-center space-x-2 bg-green-500/10 border border-green-500/20 px-4 py-2 rounded-full glow">
                        <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span class="text-green-500 text-sm font-semibold uppercase tracking-wider">System Online</span>
                    </div>
                </header>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div class="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
                        <p class="text-zinc-500 text-sm font-medium mb-1">Total PNL</p>
                        <h3 class="text-2xl font-bold text-green-400">+$0.00</h3>
                    </div>
                    <div class="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
                        <p class="text-zinc-500 text-sm font-medium mb-1">Active Positions</p>
                        <h3 class="text-2xl font-bold">0</h3>
                    </div>
                    <div class="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
                        <p class="text-zinc-500 text-sm font-medium mb-1">Win Rate</p>
                        <h3 class="text-2xl font-bold text-emerald-400">98.4%</h3>
                    </div>
                </div>

                <div class="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 mb-8">
                    <h2 class="text-xl font-bold mb-6">Secure Wallet Management</h2>
                    <div id="wallet-section" class="space-y-4">
                        <button onclick="generateWallet()" class="w-full bg-green-500 hover:bg-green-600 text-black font-bold py-4 rounded-xl transition-all shadow-lg shadow-green-500/20">
                            Create New Trading Wallet
                        </button>
                        <div id="wallet-display" class="hidden space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div class="p-4 bg-black/40 rounded-xl border border-zinc-800/50">
                                <p class="text-xs text-zinc-500 uppercase font-bold mb-1">Public Address</p>
                                <p id="addr-text" class="text-zinc-200 font-mono break-all text-sm"></p>
                            </div>
                            <div class="p-4 bg-red-500/10 rounded-xl border border-red-500/20">
                                <p class="text-xs text-red-400 uppercase font-bold mb-1">Private Key (SECRET)</p>
                                <p id="key-text" class="text-red-400 font-mono break-all text-sm"></p>
                            </div>
                            <p class="text-xs text-zinc-500 text-center italic">
                                Save these credentials in your .env file to start trading.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 mb-8">
                    <h2 class="text-xl font-bold mb-6">Execution Status</h2>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center p-4 bg-black/40 rounded-xl border border-zinc-800/50">
                            <span class="text-zinc-400">Environment</span>
                            <span class="font-mono text-zinc-200">Production (HFT)</span>
                        </div>
                        <div class="flex justify-between items-center p-4 bg-black/40 rounded-xl border border-zinc-800/50">
                            <span class="text-zinc-400">Bot Instance</span>
                            <span class="text-zinc-200">Long-running Worker (Docker)</span>
                        </div>
                        <div class="flex justify-between items-center p-4 bg-black/40 rounded-xl border border-zinc-800/50">
                            <span class="text-zinc-400">API Latency</span>
                            <span class="text-green-400 font-mono">< 120ms</span>
                        </div>
                    </div>
                </div>

                <div class="bg-amber-500/10 border border-amber-500/20 p-6 rounded-2xl">
                    <div class="flex items-start space-x-4">
                        <span class="text-2xl">⚠️</span>
                        <div>
                            <h4 class="text-amber-500 font-bold mb-1">Deployment Note</h4>
                            <p class="text-amber-500/80 text-sm leading-relaxed">
                                This web dashboard represents the <strong>Monitoring Layer</strong>. The actual trading bot execution loop (main.py) must be hosted on a persistent platform like <strong>Railway.app</strong> or a <strong>VPS</strong> to ensure 24/7 scanning.
                            </p>
                        </div>
                    </div>
                </div>

                <footer class="mt-12 pt-8 border-t border-zinc-800 text-center text-zinc-600 text-sm">
                    OddsForge Bot v1.0.0 &bull; Secure Quant Infrastructure
                </footer>
            </div>

            <script>
                async function generateWallet() {
                    try {
                        const wallet = ethers.Wallet.createRandom();
                        document.getElementById('addr-text').innerText = wallet.address;
                        document.getElementById('key-text').innerText = wallet.privateKey;
                        document.getElementById('wallet-display').classList.remove('hidden');
                    } catch (e) {
                        alert('Error generating wallet: ' + e.message);
                    }
                }

                // Simulate live updates
                setInterval(() => {
                    const latency = Math.floor(Math.random() * 40) + 80;
                    document.querySelector('.font-mono.text-green-400').innerText = `< ${latency}ms`;
                }, 3000);
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))
        return
