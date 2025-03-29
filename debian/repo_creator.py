#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import base64

class GitHubRepoCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repo Creator (Tkinter)")
        self.root.geometry("400x700")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(False, False)

        self.hide_taskbar_icon(self.root.winfo_id()) # Hide the icon        

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#1a1a1a", foreground="#ffeb3b", font=("Arial", 10, "bold"))
        style.configure("TEntry", fieldbackground="#333", foreground="#ffffff", bordercolor="#444", background="#333")
        style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"), bordercolor="#1a1a1a")
        style.configure("TCheckbutton", background="#1a1a1a", foreground="#ffeb3b")
        style.configure("TCombobox", fieldbackground="#333", foreground="#ffffff", background="#444")
        style.map("TButton", background=[("active", "#45a049")])
        style.map("TCheckbutton", background=[("active", "#1a1a1a")])

        main_frame = ttk.Frame(root, padding="10", style="TFrame")
        main_frame.pack(fill="both", expand=True)
        main_frame.configure(style="TFrame")
        style.configure("TFrame", background="#1a1a1a")

        ttk.Label(main_frame, text="GitHub Repo Creator", style="TLabel").grid(row=0, column=0, columnspan=2, pady=10)

        self.fields = {}
        row = 1
        self.create_field(main_frame, "Repo Name *", "gitRepoName", "", row); row += 1
        self.create_field(main_frame, "Repo URL", "gitRepoUrl", "", row); row += 1
        self.create_field(main_frame, "Branch Name", "gitBranchName", "", row); row += 1
        self.create_field(main_frame, "Access Token *", "gitAccessToken", "", row); row += 1
        self.create_field(main_frame, "Description", "gitDescription", "", row, is_text=True); row += 1
        
        ttk.Label(main_frame, text="Template", style="TLabel").grid(row=row, column=0, sticky="w", pady=(5, 0))
        self.template_var = tk.StringVar(value="empty")
        template_combo = ttk.Combobox(main_frame, textvariable=self.template_var, values=["empty", "python", "nodejs"], style="TCombobox", state="readonly")
        template_combo.grid(row=row, column=1, sticky="ew", padx=5); row += 1
        
        ttk.Label(main_frame, text="Private Repository", style="TLabel").grid(row=row, column=0, sticky="w", pady=(5, 0))
        self.private_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, variable=self.private_var, style="TCheckbutton").grid(row=row, column=1, sticky="w"); row += 1
        self.create_field(main_frame, "SSH Key Path", "gitSshKeyPath", "", row); row += 1
        self.create_field(main_frame, "SSH Key Content", "gitSshKeyContent", "", row, is_text=True); row += 1
        self.create_field(main_frame, "Clone Command", "gitCloneCommand", "", row); row += 1
        self.create_field(main_frame, "Remote Name", "gitRemoteName", "", row); row += 1
        self.create_field(main_frame, "Username", "gitUsername", "", row); row += 1
        self.create_field(main_frame, "Email", "gitEmail", "", row); row += 1
        self.create_field(main_frame, "Last Commit Hash", "gitLastCommit", "", row); row += 1
        self.create_field(main_frame, "Notes", "gitNotes", "", row, is_text=True); row += 1

        ttk.Button(main_frame, text="Create Repo and Save", command=self.create_repo, style="TButton").grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        ttk.Button(main_frame, text="Clear Form", command=self.clear_form, style="TButton").grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        self.status = tk.Label(main_frame, text="", bg="#1a1a1a", fg="#ffffff", wraplength=350)
        self.status.grid(row=row, column=0, columnspan=2, pady=10)

    def create_field(self, parent, label, key, default, row, is_text=False):
        ttk.Label(parent, text=label, style="TLabel").grid(row=row, column=0, sticky="w", pady=(5, 0))
        if is_text:
            widget = tk.Text(parent, height=3, width=30, bg="#333", fg="#ffffff", insertbackground="white", relief="flat", borderwidth=1)
            widget.insert("1.0", default)
        else:
            widget = ttk.Entry(parent, width=30, style="TEntry")
            widget.insert(0, default)
        widget.grid(row=row, column=1, sticky="ew", padx=5)
        self.fields[key] = widget

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_into(widget))
        widget.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

    def paste_into(self, widget):
        try:
            clipboard = self.root.clipboard_get()
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", clipboard)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, clipboard)
        except tk.TclError:
            pass

    def get_field_value(self, key):
        widget = self.fields[key]
        return widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get()

    def create_repo(self):
        repo_name = self.get_field_value("gitRepoName")
        access_token = self.get_field_value("gitAccessToken")
        description = self.get_field_value("gitDescription")
        template = self.template_var.get()
        is_private = self.private_var.get()

        if not repo_name or not access_token:
            self.status.config(text="Repo Name and Access Token are required.", fg="red")
            return

        self.status.config(text="Creating repository...", fg="white")

        headers = {'Authorization': f'token {access_token}', 'Accept': 'application/vnd.github.v3+json'}
        data = {'name': repo_name, 'description': description, 'private': is_private, 'auto_init': True}

        try:
            response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
            response.raise_for_status()
            repo_data = response.json()

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

            self.save_details(repo_data)
            self.status.config(text=f"Repository '{repo_name}' created! File saved to Downloads.", fg="green")
        except requests.RequestException as e:
            error_msg = e.response.json().get('message', 'Unknown error') if e.response else str(e)
            messagebox.showerror("Error", f"Failed to create repo: {error_msg}")
            self.status.config(text="Creation failed.", fg="red")

    def save_details(self, repo_data):
        form_data = {key: self.get_field_value(key) for key in self.fields}
        form_data['isPrivate'] = self.private_var.get()
        form_data['template'] = self.template_var.get()
        form_data['cloneUrl'] = repo_data['clone_url']

        content = f"""
Repository Details:
Name: {form_data['gitRepoName']}
URL: {form_data['gitRepoUrl'] or repo_data['html_url']}
Branch Name: {form_data['gitBranchName'] or 'main'}
Access Token: ***HIDDEN*** (Original: {len(form_data['gitAccessToken'])} chars)
Description: {form_data['gitDescription'] or 'N/A'}
Template: {form_data['template']}
Private: {form_data['isPrivate']}
SSH Key Path: {form_data['gitSshKeyPath'] or 'Not set'}
SSH Key Content: {form_data['gitSshKeyContent'] or 'Not set'}
Clone Command: {form_data['gitCloneCommand'] or f"git clone {repo_data['clone_url']}"}
Remote Name: {form_data['gitRemoteName'] or 'origin'}
Username: {form_data['gitUsername'] or 'Not set'}
Email: {form_data['gitEmail'] or 'Not set'}
Last Commit Hash: {form_data['gitLastCommit'] or 'N/A'}
Notes: {form_data['gitNotes'] or 'None'}
GitHub Created URL: {repo_data['html_url']}

Recommended Git Commands:
# Initialize local repository (if starting fresh)
git init
{ f'git config user.name "{form_data["gitUsername"]}"' if form_data["gitUsername"] else '# git config user.name "YourName"' }
{ f'git config user.email "{form_data["gitEmail"]}"' if form_data["gitEmail"] else '# git config user.email "your@email.com"' }
# Clone the repository
{form_data['gitCloneCommand'] or f"git clone {repo_data['clone_url']}"}
cd {form_data['gitRepoName']}
# Set up remote
git remote add {form_data['gitRemoteName'] or 'origin'} {repo_data['clone_url']}
# Verify remote
git remote -v
# Checkout branch (if not default)
{ f'git checkout -b {form_data["gitBranchName"]}' if form_data["gitBranchName"] != 'main' else '# Default branch is main' }
# Add SSH key (if provided)
{ f'ssh-add "{form_data["gitSshKeyPath"]}"' if form_data["gitSshKeyPath"] else '# ssh-add ~/.ssh/id_rsa' }
# Example commit (if initialized locally)
# git add .
# git commit -m "Initial commit"
# git push {form_data['gitRemoteName'] or 'origin'} {form_data['gitBranchName'] or 'main'}
        """.strip()

        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        filename = os.path.join(downloads_dir, f"{form_data['gitRepoName']}_repo_info.txt")
        with open(filename, 'w') as f:
            f.write(content)

    def clear_form(self):
        if messagebox.askyesno("Confirm", "Clear all fields?"):
            for key, widget in self.fields.items():
                if isinstance(widget, tk.Text):
                    widget.delete("1.0", tk.END)
                else:
                    widget.delete(0, tk.END)
            self.private_var.set(False)
            self.template_var.set("empty")
            self.status.config(text="Form cleared.", fg="yellow")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubRepoCreator(root)
    root.mainloop()
