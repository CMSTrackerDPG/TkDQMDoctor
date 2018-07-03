#!/bin/bash
# Exports environment variables defined in a .env file
# Example usage: . expenv.sh local.env


while IFS='=' read -r env_var env_val || [[ -n "$line" ]]; do
    echo "exporting ${env_var}"
    export ${env_var}=${env_val}
done < "$1"
if [ -f ".env" ]; then
    echo -e "\e[31mremoving\e[39m old \e[34m.env\e[39m file..."
    rm .env
fi
echo -e "\e[32mcopying \e[34m$1\e[39m to \e[34m.env\e[39m..."
cp "$1" .env
echo -e "\e[92m==DONE EXPORTING=="
