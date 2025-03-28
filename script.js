document.getElementById('repoForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const repoName = document.getElementById('gitRepoName').value;
    const accessToken = document.getElementById('gitAccessToken').value;
    const description = document.getElementById('gitDescription').value;
    const template = document.getElementById('template').value;
    const isPrivate = document.getElementById('isPrivate').checked;

    if (!repoName || !accessToken) {
        document.getElementById('status').textContent = 'Repo Name and Access Token are required.';
        document.getElementById('status').style.color = 'red';
        return;
    }

    document.getElementById('status').textContent = 'Creating repository...';
    document.getElementById('status').style.color = 'white';

    const headers = {
        'Authorization': `token ${accessToken}`,
        'Accept': 'application/vnd.github.v3+json'
    };
    const repoData = {
        name: repoName,
        description: description,
        private: isPrivate,
        auto_init: true
    };

    fetch('https://api.github.com/user/repos', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(repoData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => { throw new Error(error.message || 'Unknown error'); });
        }
        return response.json();
    })
    .then(data => {
        const owner = data.owner.login;
        const repoUrl = data.html_url;

        // Template files
        const templates = {
            python: [
                { path: 'README.md', content: btoa('# Python Project\nA simple Python project template.') },
                { path: '.gitignore', content: btoa('__pycache__\n*.pyc\nvenv/') }
            ],
            nodejs: [
                { path: 'README.md', content: btoa('# Node.js Project\nA simple Node.js project template.') },
                { path: '.gitignore', content: btoa('node_modules/\n*.log') }
            ]
        };

        if (template !== 'empty' && templates[template]) {
            const promises = templates[template].map(file => {
                return fetch(`https://api.github.com/repos/${owner}/${repoName}/contents/${file.path}`, {
                    method: 'PUT',
                    headers: headers,
                    body: JSON.stringify({
                        message: `Add ${file.path} for ${template} template`,
                        content: file.content
                    })
                });
            });
            return Promise.all(promises).then(() => data);
        }
        return data;
    })
    .then(repoData => {
        const content = `
Repository Details:
Name: ${repoName}
URL: ${repoData.html_url}
Description: ${description || 'N/A'}
Template: ${template}
Private: ${isPrivate}
GitHub Created URL: ${repoData.html_url}
        `.trim();

        const blob = new Blob([content], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${repoName}_repo_info.txt`;
        link.click();
        document.getElementById('status').textContent = `Repository '${repoName}' created! File downloaded.`;
        document.getElementById('status').style.color = 'green';
    })
    .catch(error => {
        const errorMsg = error.message || 'Unknown error';
        alert(`Failed to create repo: ${errorMsg}`);
        document.getElementById('status').textContent = 'Creation failed.';
        document.getElementById('status').style.color = 'red';
    });
});
