# pk_init_git_repo.sh

A simple Bash script to quickly initialize a local Git repository, create a corresponding GitHub repository using the GitHub CLI (`gh`), and push the initial commit to the `main` branch.

## 🔧 Features

- Prompts the user for a new GitHub repository name.
- Initializes a local Git repository in the current directory.
- Creates a GitHub repository with the same name.
- Adds a `README.md` file as initial content.
- Commits and pushes the content to the `main` branch.
- Checks if the user is authenticated with GitHub CLI (`gh`), and initiates login if not.

## ✅ Requirements

- [Git](https://git-scm.com/) installed and available in your `PATH`.
- [GitHub CLI (`gh`)](https://cli.github.com/) installed.
- A GitHub account.
- An active internet connection.

## 🔐 Authentication

The script uses `gh auth status` to check whether you are already authenticated with GitHub CLI.  
If not, it automatically launches the interactive login flow using `gh auth login`.

You only need to authenticate once per system. Auth status is stored locally in `~/.config/gh/`.

## 🖥️ Usage

1. Make the script executable:

   ```bash
   chmod +x pk_init_git_repo.sh
   ```
   
2. create a file .gitignore in the root of your repo with the following content:

   ```bash
   /pk_init_git_repo.sh
   ```

3. Run the script:

   ```bash
   ./pk_init_git_repo.sh
   ```

4. Follow the prompts:
   - Enter the name of the GitHub repository to create.
   - If not logged in, complete the login via browser.
   - The script creates a local folder, initializes Git, creates a GitHub repo, and pushes to `main`.

## 📁 Example

```
$ ./pk_init_git_repo.sh
GitHub login detected: Logged in to github.com as your-username
Enter the name of the new GitHub repository: my-awesome-project
✅ Repository 'my-awesome-project' was successfully created and pushed.
```

## 🔄 Behavior

- A new folder with the entered repository name is created in the current working directory.
- If the folder already exists, the script will fail.
- The GitHub repository is public by default. You can change this by modifying the `gh repo create` line:

   ```bash
   gh repo create "$repo_name" --source=. --remote=origin --push --private
   ```

## ⚠️ Notes

- This script assumes you want a **new repository**. It does not work inside existing Git repositories.

## 📜 License

MIT License
