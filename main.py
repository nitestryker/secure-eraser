from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import tempfile
import uuid
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>Secure Eraser Web Interface</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body {
                padding: 20px;
            }
            .container {
                max-width: 800px;
            }
            .form-group {
                margin-bottom: 1rem;
            }
            .report-container {
                margin-top: 20px;
                padding: 20px;
            }
        </style>
    </head>
    <body data-bs-theme="dark">
        <div class="container">
            <h1 class="mb-4">Secure File Eraser</h1>
            <p class="lead">A cryptographically secure file erasure application with military-grade security standards and custom patterns.</p>
            
            <div class="alert alert-warning">
                <strong>Note:</strong> This is a demo interface. For security-critical operations, 
                please use the command-line tool directly.
            </div>
            
            <div class="alert alert-info">
                <strong>New Features:</strong> 
                <ul>
                    <li>Military-grade security standards (NIST 800-88, HMG IS5, DoD variants)</li>
                    <li>Custom wiping pattern support with user-defined hex patterns</li>
                    <li>Enhanced verification and detailed HTML/PDF reports</li>
                </ul>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h3>Available Operations</h3>
                </div>
                <div class="card-body">
                    <a href="/demo" class="btn btn-primary">Run Demo</a>
                    <a href="/commands" class="btn btn-secondary">View Commands</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/demo')
def demo():
    # Create a temporary file for the demo that will be deleted after use
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', prefix='secure_eraser_demo_') as temp:
        temp.write("This is a test file for secure deletion demo.\n")
        temp.write("It contains sensitive information that needs to be securely erased.\n")
        temp_path = temp.name
    
    # Run the secure_eraser command
    report_path = os.path.join(tempfile.gettempdir(), f'report_{uuid.uuid4().hex[:8]}.html')
    
    cmd = [
        'python', 'secure_eraser.py',
        '--file', temp_path,
        '--method', 'nist_purge',  # Use NIST SP 800-88 Purge standard
        '--verify',
        '--report-format', 'html',
        '--report-path', report_path,
        '--verbose'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + "\n" + result.stderr
        
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report_content = f.read()
            # Clean up the temporary report file after reading it
            try:
                os.remove(report_path)
            except Exception as e:
                print(f"Warning: Could not clean up temp report file: {e}")
        else:
            report_content = "Report file not generated."
            
        # Clean up the temporary file that was created for the demo if it still exists
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Warning: Could not clean up temp file: {e}")
            
        return f"""
        <html>
        <head>
            <title>Secure Eraser Demo</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding: 20px;
                }}
                .container {{
                    max-width: 900px;
                }}
                .output-container {{
                    background-color: #282c34;
                    color: #abb2bf;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    font-family: monospace;
                }}
                .report-container {{
                    margin-top: 20px;
                    padding: 20px;
                    border: 1px solid #444;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container">
                <h1 class="mb-4">Secure Eraser Demo - NIST 800-88 Purge Standard</h1>
                <div class="alert alert-info mb-4">
                    <strong>Using Military-Grade Standard:</strong> 
                    This demo uses the NIST SP 800-88 Purge standard for secure data erasure, 
                    which is recommended for sanitizing media containing sensitive information.
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h3>Command Output</h3>
                    </div>
                    <div class="card-body">
                        <div class="output-container">{output}</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3>HTML Report</h3>
                    </div>
                    <div class="card-body">
                        <div class="report-container">
                            {report_content}
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>Secure Eraser Demo Error</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        </head>
        <body data-bs-theme="dark">
            <div class="container">
                <h1 class="mb-4">Error Running Demo</h1>
                <div class="alert alert-danger">
                    <p>{str(e)}</p>
                </div>
                <div>
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/commands')
def commands():
    cmd = ['python', 'secure_eraser.py', '--help']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        help_text = result.stdout
        
        return f"""
        <html>
        <head>
            <title>Secure Eraser Commands</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                }}
                .command-container {{
                    background-color: #282c34;
                    color: #abb2bf;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    font-family: monospace;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container">
                <h1 class="mb-4">Secure Eraser Commands</h1>
                
                <div class="card">
                    <div class="card-header">
                        <h3>Available Commands</h3>
                    </div>
                    <div class="card-body">
                        <div class="command-container">{help_text}</div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)