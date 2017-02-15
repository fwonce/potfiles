# About

**Potfiles** (similar to "dotfiles" but not the same) is a supplementary utility intended to coordinate with your favorite cloud-based file hosting solution (Dropbox, OneDrive or even a ["dotfiles" repo](https://github.com/search?q=dotfiles), etc) to manage all your configuration/resource files in one place and synchronize them across multiple computers, in an effective and convenient manner. Using a file hosting solution doesn't get the job done because:

1. Although it is awesome for synchronizing your files in a specific folder, we need to put them back to the original directories within which the software behind them actually read, one by one. That's tedious and easy to fail.
2. In a dotfiles repo, which is basically more like a place for sharing tweaks of those beloved software, there may be a script to link files back to home directory indeed. But there are also many other stuff located other than home directory. Stencils of OmniGraffle,  keymap setting of your favorite IDE, bits of extension configuration of Firefox which the integrated Sync doesn't care about. You can think of plenty of other use cases.

So there need to be a file mapping tool as a complement to file synchronization tool-chain. Potfiles allows you to describe the mapping rules between the hosted files and the real locations in your local harddisk using a simple and self-explanatory DSL. May it be the missing piece of your cyber life arsenal :)

# Get started

Prerequisites: Python3, appdirs (1.4.0).

Let's go.

0. Clone potfiles into any directory you want. `gti clone https://github.com/fwonce/potfiles.git`
0. Put all your files needed to by synchronized under `potfiles/` (since potfiles will search resources under its working directory). You can organize them any way you want, but here are two specific rational approachs:
	- Clone potfiles into your Dropbox (or whatnot) local directory. Thus anything you put under `potfiles/` will be synchronized in the first place, only belonging to you.
	- Already a "dotfiles" user? Potfiles will get alone well with it. Just symlink your local dotfiles repo directory into `potfiles/`.
0. Create a plain text file with ".pdec" extension under `potfiles/conf`, and write the mapping rules (see below) in it. ([Here]() is mine.)
0. Run the command `python(3) -m potbin` under `potfiles/`. Sit tight and watch.

A typical structure:

``` shell
potfiles/
	setup.py & potbin/				# the executable. leave them alone.
	data/file						# the stuff you put under `potfiles/`
	conf/resources.pdec << EOLIST	# "EOLIST" has no special meaning, just for show the following content
		data/file > /target/path	# a line of a mapping rule
	EOLIST
```

Notes:

0. You can put multiple pdec files under `potfiles/conf` to make them more "modular", and all of them will be sourced automatically.
0. The left part of a mapping rule is relative (counted from potfiles/) path to your source file, and the right part is the real path it needs to be located to get your production software work.

# The PotFiles DSL

## Built-in path segment function

A built-in path segment function is a placeholder you can use in target part of a mapping rule. The supported built-in path segment functions are:

- `$userhome` or a tilda '~': User home directory based on the underlying system.
- `$appfolder('appname', 'appauther')`: Locate the application configuration folder based on the underlying system. See [`appdirs`](https://pypi.python.org/pypi/appdirs) also.
- `$iniparser`: Extract a string value from given '.ini' file, relative to the current expanded path.

## Custom path segment variable declaration

At any part of a pdec file, you can write a custom path segment variable declareation like:`$VarName = blah/blah/blah`.

And afterwards in this pdec file, you can reuse this variable in your target part of a mapping rule.

Custom path segment variable declaration can use one or more built-in path segment functions, such as:

```
$FirefoxProfile = $appfolder('Firefox', 'Mozilla')/$iniparser('profiles.ini', 'Profile0', 'Path')
```

And also it's passive, which means one custom path segment variable can use another in it. For instance, we have `$A = a` already and we can declare `$B = $A/a`.

## Mapping rules

A mapping rule is a line of code comprises source part and target part. As mentioned, the source part must be the relative path of `potfiles/`.

If the source part is a file, then the target part can be a directory on your harddisk, or a new file name.

If the source part is a directory, then the target part can be the containing directory for the target, or a new diretory name.

The target part can uses one or more custom path segment variables or built-in path segment functions.

The two parts is seperated be a mapping operator. There are two kinds of mapping operator:

- `>`: Symbolic / Soft linking. In most cases, this should be used, because without replica you have lower chance get conflicted and don't need to write back.
- `|`: Copying. In some cases, the software cannot accept a link file as its underlying configuration / resource file, or it would rewrite it as a normal file after reading the original file content and deleting the link file. For example, Firefox 51's search engine configuration file (`search.json.mozlz4`) is like this. When copy operator used, the modification times of both source and target file will be compared to determine the copying direction. Be aware that in copy mode you produce replica and need to run `python(3) -m potbin` from time to time.

### Usages

0. Link all stuff under a directory one by one to the target location. Just like dotfiles.
	`dotfiles/* > ~`
	Equivalents: `dotfiles/*` (omitting target)

0. A simple one, putting a symbolic link to the given source into the home directory.
	`data/.vimrc > ~/.vimrc`

0. The basename of target part can be omitted if it's the same with the one of the source part. It doesn't matter wheter a trailing slash '/' is appended to target directory.
	`data/.vimrc > ~`

0. Furthermore, if the target is exactly home directory, the whole target path can be omitted. So, the above rule is equivalent to this one:
	`data/.vimrc`

0. The leading dot of a source file will make it more difficult to browse and find that file to some extends. You can use a underscore '_' to replace it and the program will automatically replace it back at runtime. So here's another equivalent:
	`data/_vimrc`
	
0. If the target file name is quite unclear about what it means, for good reasons you would store the source file in your cloud repo with a different semantic file name.
	`data/my_dash_snippet_library.dash > $appfolder('Dash', 'Kapeli')/library.dash`

0. Mapping directories is needed off course because mapping single files one by one is tedious and inappropriate sometimes.
	`data/.vim > ~/.vim` 
	Just like file mapping, these are equivalents of the above one:
	`data/.vim > ~`, `data/_vim > ~` & `data/_vim`
	Target directory name changing for unclear target basename also works:
	`data/vimp_plugins > $userhome/.vimperator/plugins`

0. File copy, if the software doesn't support symlinks:
	`data/bttdata2 | $appfolder('BetterTouchTool')`

0. Similarly, directory copy:
	`data/OmniGraffle/Stencils | ~/Library/Containers/com.omnigroup.OmniGraffle6/Data/Library/Application Support/The Omni Group/OmniGraffle`

# Further ideas

- The ultimate object is to provide a framework for setting up a workstation conforms to your habit and needs in one run. So other actions such as installing your must-have brew/pip/npm packages will be welcome.
- System-specific sync folders for Linux, Mac, Windows.

