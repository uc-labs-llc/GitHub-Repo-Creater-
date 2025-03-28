from flask import Flask, render_template, request, send_file
import requests
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        # Gather all form data
        repo_name = request.form.get('gitRepoName')
        access_token = request.form.get('gitAccessToken')
        repo_url = request.form.get('gitRepoUrl', '')
        branch_name = request.form.get('gitBranchName', '')
        description = request.form.get('gitDescription', '')
        template = request.form.get('template', 'empty')
        is_private = request.form.get('isPrivate') == 'on'
        ssh_key_path = request.form.get('gitSshKeyPath', '')
        ssh_key_content = request.form.get('gitSshKeyContent', '')
        clone_command = request.form.get('gitCloneCommand', '')
        remote_name = request.form.get('gitRemoteName', '')
        username = request.form.get('gitUsername', '')
        email = request.form.get('gitEmail', '')
        last_commit = request.form.get('gitLastCommit', '')
        notes = request.form.get('gitNotes', '')

        if not repo_name or not access_token:
            error = "Repo Name and Access Token are required."
            return render_template('index.html', error=error)

        headers = {'Authorization': f'token {access_token}', 'Accept': 'application/vnd.github.v3+json'}
        data = {'name': repo_name, 'description': description, 'private': is_private, 'auto_init': True}

        try:
            response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
            response.raise_for_status()
            repo_data = response.json()

            # Apply template
            owner = repo_data['owner']['login']
            templates = {
                'python': [
                    {'path': 'README.md', 'content': base64.b64encode(b'# Python Project\nA simple Python project template.').decode('utf-8')},
                    {'path': '.gitignore', 'content': base64.b64encode(b'__pycache__\n*.pyc\nvenv/').decode('utf-8')}
                ],
                'nodejs': [
                    {'path': 'README.md', 'content': base64.b64encode(b'# Node.js Project\nA simple Node.js project template.').decode('utf-8')},
                    {'path': '.gitignore', 'content': base64.b64encode(b'node_modules/\n*.log').decode('utf-8')}
                ]
            }

            if template != 'empty' and template in templates:
                for file in templates[template]:
                    requests.put(
                        f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file['path']}",
                        headers=headers,
                        json={
                            'message': f"Add {file['path']} for {template} template",
                            'content': file['content']
                        }
                    )

            # Generate detailed content
            content = f"""
Repository Details:
Name: {repo_name}
URL: {repo_url or repo_data['html_url']}
Branch Name: {branch_name or 'main'}
Access Token: ***HIDDEN*** (Original: {len(access_token)} chars)
Description: {description or 'N/A'}
Template: {template}
Private: {is_private}
SSH Key Path: {ssh_key_path or 'Not set'}
SSH Key Content: {ssh_key_content or 'Not set'}
Clone Command: {clone_command or f"git clone {repo_data['clone_url']}"}
Remote Name: {remote_name or 'origin'}
Username: {username or 'Not set'}
Email: {email or 'Not set'}
Last Commit Hash: {last_commit or 'N/A'}
Notes: {notes or 'None'}
GitHub Created URL: {repo_data['html_url']}

Recommended Git Commands:
# Initialize local repository (if starting fresh)
git init
{ f'git config user.name "{username}"' if username else '# git config user.name "YourName"' }
{ f'git config user.email "{email}"' if email else '# git config user.email "your@email.com"' }
# Clone the repository
{clone_command or f"git clone {repo_data['clone_url']}"}
cd {repo_name}
# Set up remote
git remote add {remote_name or 'origin'} {repo_data['clone_url']}
# Verify remote
git remote -v
# Checkout branch (if not default)
{ f'git checkout -b {branch_name}' if branch_name and branch_name != 'main' else '# Default branch is main' }
# Add SSH key (if provided)
{ f'ssh-add "{ssh_key_path}"' if ssh_key_path else '# ssh-add ~/.ssh/id_rsa' }
# Example commit (if initialized locally)
# git add .
# git commit -m "Initial commit"
# git push {remote_name or 'origin'} {branch_name or 'main'}
            """.strip()

            buffer = io.BytesIO(content.encode('utf-8'))
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name=f"{repo_name}_repo_info.txt", mimetype='text/plain')

        except requests.RequestException as e:
            error_msg = e.response.json().get('message', 'Unknown error') if e.response else str(e)
            error = f"Failed to create repo: {error_msg}"
            return render_template('index.html', error=error)

    return render_template('index.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)
