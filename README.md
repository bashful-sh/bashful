# .bashful-git

Universal Bash & Shell script bundle and package manager for Ubuntu/Debian
based Linux distributions.

## Automatic Install & Setup

For (Ubuntu/Debian) base distributions, run the following script.

```sh
git clone git@github.com:oceaster/.bashful-git ~/.bashful
rm -rf ~/.bashful/.git
rm -rf ~/.bashful/.gitignore
rm -rf ~/.bashful/README.md
rm ~/.bashrc
mv ~/.bashful/.bashrc ~/
```

You have now successfully clone the repository, renamed it, removed
git assets, and

## Manual Install & Setup

If you are trying to install bashful _(latest)_ via git from source you
should run the following command(s):

### Download/Clone Source Code

#### (1). Do not preserve git

You will only need to avoid this step if you are contributing code to
to the public, main branch. Which is most unlikely...

```sh
git clone git@github.com:oceaster/.bashful-git ~/.bashful
rm -rf ~/.bashful/.git
rm -rf ~/.bashful/.gitignore
rm -rf ~/.bashful/README.md
```

#### (2). _Preserve git assets_

If you would like to preserve the `.git` directory then using bashful
becomes different.

```sh
git clone git@github.com:oceaster/.bashful-git ~/.bashful-git
```

### User `~/.bashrc` File

#### (1). **Do not preserve user `bashrc` file**

If you do not wish to preserve the contents of your `.bashrc` file (recommended)
then all you need to do is run the following command(s):

```sh
rm ~/.bashrc
mv ~/.bashful/.bashrc ~/
```

#### (2). _Preserve the user `.bashrc` file_

If you want to preserve your `.bashrc` file contents (not recommended) then use
the follow command(s):

```sh
cat ~/.bashful/.bashrc >> ~/.bashrc
```
