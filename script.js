document.addEventListener('DOMContentLoaded', function() {
    const createRepoButton = document.getElementById('createRepoButton');
    const resetButton = document.getElementById('resetButton');
    const form = document.getElementById('gitForm');
    
    if (!createRepoButton) {
        console.error('Error: Could not find createRepoButton');
        document.getElementById('message').innerHTML = '<p style="color: red;">Error: Button not found.</p>';
        return;
    }
    if (!resetButton) {
        console.error('Error: Could not find resetButton');
        return;
    }
    if (!form) {
        console.error('Error: Could not find gitForm');
        return;
    }

    createRepoButton.addEventListener('click', createGitHubRepo);
    resetButton.addEventListener('click', resetForm);

    async function createGitHubRepo() {
        const repoName = document.getElementById('gitRepoName').value;
        const accessToken = document.getElementById('gitAccessToken').value;
        const description = document.getElementById('gitDescription').value;
        const isPrivate = document.getElementById('gitPrivate').checked;

        if (!repoName || !accessToken) {
            document.getElementById('message').innerHTML = '<p style="color: red;">Repo Name and Access Token are required.</p>';
            return;
        }

        document.getElementById('loading').style.display = 'block';
        document.getElementById('message').innerHTML = '';

        try {
            const response = await fetch('https://api.github.com/user/repos', {
                method: 'POST',
                headers: {
                    'Authorization': `token ${accessToken}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/vnd.github.v3+json'
                },
                body: JSON.stringify({
                    name: repoName,
                    description: description,
                    private: isPrivate,
                    auto_init: true
                })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';
                saveRepoData(data);
                document.getElementById('message').innerHTML = `<p style="color: green;">Repository "${data.name}" created! Check downloaded file.</p>`;
            } else {
                const errorData = await response.json();
                throw new Error(errorData.message || response.statusText);
            }
        } catch (error) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('message').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            console.error('Error:', error);
        }
    }

    function saveRepoData(repoData) {
        const formData = {
            repoName: document.getElementById('gitRepoName').value,
            repoUrl: document.getElementById('gitRepoUrl').value || repoData.html_url,
            branchName: document.getElementById('gitBranchName').value || 'main',
            accessToken: document.getElementById('gitAccessToken').value,
            description: document.getElementById('gitDescription').value,
            isPrivate: document.getElementById('gitPrivate').checked,
            sshKeyPath: document.getElementById('gitSshKeyPath').value,
            sshKeyContent: document.getElementById('gitSshKeyContent').value,
            cloneCommand: document.getElementById('gitCloneCommand').value || `git clone ${repoData.clone_url}`,
            remoteName: document.getElementById('gitRemoteName').value || 'origin',
            username: document.getElementById('gitUsername').value,
            email: document.getElementById('gitEmail').value,
            lastCommit: document.getElementById('gitLastCommit').value,
            notes: document.getElementById('gitNotes').value,
            cloneUrl: repoData.clone_url
        };

        const content = `
Repository Details:
Name: ${formData.repoName}
URL: ${formData.repoUrl}
Branch Name: ${formData.branchName}
Access Token: ***HIDDEN*** (Original: ${formData.accessToken.length} chars)
Description: ${formData.description || 'N/A'}
Private: ${formData.isPrivate}
SSH Key Path: ${formData.sshKeyPath || 'Not set'}
SSH Key Content: ${formData.sshKeyContent || 'Not set'}
Clone Command: ${formData.cloneCommand}
Remote Name: ${formData.remoteName}
Username: ${formData.username || 'Not set'}
Email: ${formData.email || 'Not set'}
Last Commit Hash: ${formData.lastCommit || 'N/A'}
Notes: ${formData.notes || 'None'}
GitHub Created URL: ${repoData.html_url}

Recommended Git Commands:
# Initialize local repository (if starting fresh)
git init
${formData.username ? `git config user.name "${formData.username}"` : '# git config user.name "YourName"'}
${formData.email ? `git config user.email "${formData.email}"` : '# git config user.email "your@email.com"'}
# Clone the repository
${formData.cloneCommand}
cd ${formData.repoName}
# Set up remote
git remote add ${formData.remoteName} ${formData.cloneUrl}
# Verify remote
git remote -v
# Checkout branch (if not default)
${formData.branchName !== 'main' ? `git checkout -b ${formData.branchName}` : '# Default branch is main'}
# Add SSH key (if provided)
${formData.sshKeyPath ? `ssh-add "${formData.sshKeyPath}"` : '# ssh-add ~/.ssh/id_rsa'}
# Example commit (if initialized locally)
# git add .
# git commit -m "Initial commit"
# git push ${formData.remoteName} ${formData.branchName}
        `.trim();

        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${formData.repoName}_repo_info.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    function resetForm() {
        form.reset();
        document.getElementById('message').innerHTML = '';
        document.getElementById('loading').style.display = 'none';
    }
});
