commit_id=441438abd1ac652551dbe4d408dfcec8a499b8bf

# Download url is: https://update.code.visualstudio.com/commit:${commit_id}/server-linux-x64/stable
curl -sSL "https://update.code.visualstudio.com/commit:${commit_id}/server-linux-x64/stable" -o /d/yuanshen/vscode-server-linux-x64.tar.gz

# mkdir -p ~/.vscode-server/bin/${commit_id}
# # assume that you upload vscode-server-linux-x64.tar.gz to /tmp dir
# tar zxvf /tmp/vscode-server-linux-x64.tar.gz -C ~/.vscode-server/bin/${commit_id} --strip 1
# touch ~/.vscode-server/bin/${commit_id}/0