## Required installs
Install Ruby and Jekyll. Note that the [official instructions](https://jekyllrb.com/docs/installation/windows/) does not work for Ubuntu 22.04 (Jammy Jellyfish). Therefore we will use `rbenv`, a tool for managing Ruby environments.

### Set up Ruby
Note, I'm running Ubuntu 22.04 in WSL 2.4.13
```sh
sudo apt update
sudo apt install git curl libssl-dev libreadline-dev zlib1g-dev autoconf bison build-essential libyaml-dev libreadline-dev libncurses5-dev libffi-dev libgdbm-dev
```
Install `rbenv`
```sh
curl -fsSL https://github.com/rbenv/rbenv-installer/raw/HEAD/bin/rbenv-installer | bash
```
Refresh your terminal with `source ~/.bashrc` or simply open a new terminal

Now you can install Ruby:
```sh
# Install a specific Ruby version. Jekyll Requires 2.7.0 or higher. This step takes a while: 
# The version should match your .ruby-version file
rbenv install 3.4.2

# Set the global Ruby version: 
rbenv global 3.4.2

# Verify the installation: 
ruby -v
```
### Set up Jekyll
```sh
gem update

gem install jekyll bundler

# install other required gems
bundle install
```

## Usefull commands when blogging:
Preview the site locally:
```sh
bundle exec jekyll serve --draft
```

## Credits
This blog uses the [Reverie theme](https://github.com/amitmerchant1990/reverie). I modified the theme to use the [giscus](https://giscus.app/) commenting system, which is free and open source. For theme customization, I recommend this [blog](https://lazyren.github.io/devlog/use-utterances-for-jekyll-comments.html) by DaeIn Lee.
