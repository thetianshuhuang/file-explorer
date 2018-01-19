# file-explorer

## fileexplorerCommand:
Assigned to ctrl+x, ctrl+f.

Behaves like the open file command in Emacs. Enter a filepath; if the filepath is a directory, the directory contents will be displayed. If the filepath is a file, the file will be opened. If the filepath is neither a directory or file, a new file will be created at that filepath.

## Directory options:
- List current directory contents:
```
.
```
- List parent directory contents:
```
..
```
- List open folders in project:
```
...
```
- The parent directory operator can be used multiple timmes in a directory. For example,
```
\home\user\dir\..\..
```
will display the contents of \home.
- 'Clean' output (do not display file properties):
```
\filepath -c
```
- CSV output (output directory contents as comma-separated values):
```
\filepath -v
```

## Behavior:
- Calling the fileexplorerCommand while viewing a previous directory output will close the previous output view before opening a new one.
- The filepath will be interpreted as an absolute filepath if it starts with "/" (linux) or "C:\" (or equivalent drive letter, windows).
- Relative filepaths will be appended to either the previously opened filepath, the first opened folder, or the operating system default, in that order, depending on whether the previous exists.