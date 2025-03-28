from flask import Flask, render_template, request, Response
import requests
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data
        repo_name = request.form.get('gitRepoName')
        access_token = request.form.get('gitAccessToken')
        description = request.form.get('gitDescription', '')
        is_private = 'gitPrivate' in request.form  # Checkbox

        if not repo_name or not access_token:
            return render_template('index.html', message="Repo Name and Access Token are required.", message_color="red")

        # GitHub API call
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'name': repo_name,
            'description': description,
            'private': is_private,
            'auto_init': True
        }

        try:
            response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
            response.raise_for_status()
            repo_data = response.json()

            # Generate file content
            file_content = generate_file_content(repo_data, request.form)
            return Response(
                file_content,
                mimetype='text/plain',
                headers={'Content-Disposition': f'attachment; filename={repo_name}_repo_info.txt'}
            )
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', 'Unknown error') if e.response else str(e)
            return render_template('index.html', message=f"Error: {error_msg}", message_color="red")

    return render_template('index.html', message="", message_color="")

def generate_file_content(repo_data, form_data):
    form_data_dict = {
        'repoName': form_data.get('gitRepoName', ''),
        'repoUrl': form_data.get('gitRepoUrl', repo_data['html_url']),
        'branchName': form_data.get('gitBranchName', 'main'),
        'accessToken': form_data.get('gitAccessToken', ''),
        'description': form_data.get('gitDescription', ''),
        'isPrivate': 'gitPrivate' in form_data,
        'sshKeyPath': form_data.get('gitSshKeyPath', ''),
        'sshKeyContent': form_data.get('gitSshKeyContent', ''),
        'cloneCommand': form_data.get('gitCloneCommand', f"git clone {repo_data['clone_url']}"),
        'remoteName': form_data.get('gitRemoteName', 'origin'),
        'username': form_data.get('gitUsername', ''),
        'email': form_data.get('gitEmail', ''),
        'lastCommit': form_data.get('gitLastCommit', ''),
        'notes': form_data.get('gitNotes', ''),
        'cloneUrl': repo_data['clone_url']
    }

    content = f"""
Repository Details:
Name: {form_data_dict['repoName']}
URL: {form_data_dict['repoUrl']}
Branch Name: {form_data_dict['branchName']}
Access Token: ***HIDDEN*** (Original: {len(form_data_dict['accessToken'])} chars)
Description: {form_data_dict['description'] or 'N/A'}
Private: {form_data_dict['isPrivate']}
SSH Key Path: {form_data_dict['sshKeyPath'] or 'Not set'}
SSH Key Content: {form_data_dict['sshKeyContent'] or 'Not set'}
Clone Command: {form_data_dict['cloneCommand']}
Remote Name: {form_data_dict['remoteName']}
Username: {form_data_dict['username'] or 'Not set'}
Email: {form_data_dict['email'] or 'Not set'}
Last Commit Hash: {form_data_dict['lastCommit'] or 'N/A'}
Notes: {form_data_dict['notes'] or 'None'}
GitHub Created URL: {repo_data['html_url']}

Recommended Git Commands:
# Initialize local repository (if starting fresh)
git init
{ f'git config user.name "{form_data_dict["username"]}"' if form_data_dict["username"] else '# git config user.name "YourName"' }
{ f'git config user.email "{form_data_dict["email"]}"' if form_data_dict["email"] else '# git config user.email "your@email.com"' }
# Clone the repository
{form_data_dict['cloneCommand']}
cd {form_data_dict['repoName']}
# Set up remote
git remote add {form_data_dict['remoteName']} {form_data_dict['cloneUrl']}
# Verify remote
git remote -v
# Checkout branch (if not default)
{ f'git checkout -b {form_data_dict["branchName"]}' if form_data_dict["branchName"] != 'main' else '# Default branch is main' }
# Add SSH key (if provided)
{ f'ssh-add "{form_data_dict["sshKeyPath"]}"' if form_data_dict["sshKeyPath"] else '# ssh-add ~/.ssh/id_rsa' }
# Example commit (if initialized locally)
# git add .
# git commit -m "Initial commit"
# git push {form_data_dict['remoteName']} {form_data_dict['branchName']}
    """.strip()
    return content

if __name__ == '__main__':
    app.run(debug=True, port=5000)
