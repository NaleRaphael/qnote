# qnote

Take notes quickly.


## Installation
- Requirements
    - [python-inquirer](https://github.com/magmax/python-inquirer)
    - [peewee](https://github.com/coleifer/peewee)

- Install
    ```bash
    $ git clone https://github.com/NaleRaphael/qnote.git
    $ pip install qnote
    ```

## Usage
The following commands are based on these two concepts:
- `note`: a fundamental object to present title, content and tags of a note
- `notebook`: a collection of notes

### Command overview
```raw
qnote add [-t | --title <title>] [-c | --content <content>] [-t | --tags <tags>]
qnote clear [-y | --yes]
qnote edit [--uuid <note_uuid>] [--editor <editor_name>]
      edit selected [--editor <editor_name>]
qnote list [--date] [--uuid]
qnote move [--uuid <note_uuid>] [--notebook <notebook_name>]
      move selected [--notebook <notebook_name>]
qnote notebook open <name>
      notebook create <name>
      notebook delete <name> [-f | --force]
      notebook list [--date]
      notebook rename <old-name> <new-name>
      notebook search <pattern>
qnote open [--uuid <note_uuid>]
      open selected
qnote remove [--uuid <note_uuid>]
      remove selected
qnote status [<notebook_name>]
qnote search uuid <pattern_of_uuid>
      search title <pattern_of_title>
      search content <pattern_of_content>
      search tags <tags>
qnote select [--multiple] [--date] [--uuid]
      select clear
      select list [--date] [--uuid]
qnote tag list
      tag clear_empty
      tag rename <old_name> <new_name>
```

### Note management
#### `qnote add`
- Add a new note by entering interactive mode
    ```bash
    $ qnote add
    ```

- Add a new note directly
    ```bash
    $ qnote add --title "# My first note" --content "Good day" --tags "#diary, #misc"
    ```

#### `qnote clear`
- Clear trash can    
    ```bash
    $ qnote clear
    ```

    All notes removed by command `qnote remove` will be moved into a trash can called `[TRASH]` first. You can move them back by `qnote move` or delete them by this command.

    Note that this is an **irreversible** operation, all notes **will be deleted permanently**.

#### `qnote edit`
- Edit specific note
    ```bash
    $ qnote edit [--uuid <note_uuid>] [--editor <editor_name>]
    # --uuid: edit the note with given UUID
    # --editor: edit the note in specific editor
    ```

- Edit note from selected list
    ```bash
    $ qnote edit select [--editor <editor_name>]
    # alias: qnote edit sel
    ```

#### `qnote list`
- List all note in current notebook
    ```bash
    $ qnote list [--date] [--uuid]
    # --date: Show create_time and update_time of notes.
    # --uuid: Show UUID of notes.
    ```

#### `qnote move`
- Move note to another notebook
    ```bash
    $ qnote move [--uuid <note_uuid>] [--notebook <notebook_name>]
    # --uuid: UUID of the notes to move. If this argument is not given, interactive mode will start and user can select notes from notebook.
    # --notebook: Destination of the notes to moved into.
    ```

- Move selected note to another notebook
    ```bash
    $ qnote move selected [--notebook <notebook_name>]
    # --notebook: Destination of the notes to moved into.
    ```

#### `qnote open`
- Open a note (view-only)
    ```bash
    $ qnote open [--uuid <note_uuid>]
    # --uuid: UUID of the note to open. If this argument is not given, interactive mode will start and user can select a note from notebook.
    ```

- Open selected note
    ```bash
    $ qnote open selected
    # alias: qnote open sel
    ```

#### `qnote remove`
- Remove a note from current notebook to trash can
    ```bash
    $ qnote remove [--uuid <note_uuid>]
    # --uuid: UUID of the note to remove. If this argument is not given, interactive mode will start and user can select a note from notebook.
    ```

- Remove selected note
    ```bash
    $ qnote remove selected
    # alias: qnote remove sel
    ```

#### `qnote search`
- Search notes by UUID
    ```bash
    $ qnote search uuid <pattern_of_uuid>
    ```
    Note that hyphen "-" in UUID can be ignored.

    e.g. for a UUID "...685-5878...", we can use "8558" as a query.

- Search notes by title
    ```bash
    $ qnote search title <pattern_of_title>
    ```

- Search notes by content
    ```bash
    $ qnote search content <pattern_of_content>
    ```

- Search notes by tags
    ```bash
    $ qnote search tags <tags>
    ```

    If multiple values are given, they should be separated by commas and enclosed by quotation marks.

    e.g. "#tag_name_1, #tag_name_2, ..."


### Notebook management
#### `qnote notebook`
- Open a notebook
    ```bash
    $ qnote notebook open <name>
    ```

- Create a notebook
    ```bash
    $ qnote notebook create <name>
    ```

- Delete a notebook
    ```bash
    $ qnote notebook delete <name> [-f | --force] [-y | --yes]
    # -f: Forcibly delete specified notebook.
    # -y: Automatically answer YES to the prompt for confirmation.
    ```

    Note that existing notes **will be deleted permanently**.

    Please consider using `qnote remove` to remove those notes to trash can before deleting a notebook if you are not sure that you really don't want to keep those notes.

- List all existing notebooks
    ```bash
    $ qnote notebook list [--date]
    # --date: Show create_time and update_time of notebooks.
    ```

- Rename notebook
    ```bash
    $ qnote notebook rename <old-name> <new-name>
    ```


### Note selection
This is an interesting feature to make you manage notes easier. You can select notes by this command and apply other actions later.

#### `qnote select`
- Select notes
    ```bash
    $ qnote select [--multiple] [--date] [--uuid]
    # --multiple: If this flag is set, user can select multiple notebooks in the interactive mode.
    # --date: Show create_time and update_time of notes.
    # --uuid: Show uuid of notes.
    ```

- Clear selected notes
    ```bash
    $ qnote select clear
    ```

- List all selected notes
    ```bash
    $ qnote select list [--date] [--uuid]
    # --date: Show create_time and update_time of notes.
    # --uuid: Show uuid of notes.
    ```

#### `qnote status`
- Show status of an notebook.
    ```bash
    $ qnote status [<notebook_name>]
    ```

    If no notebook is specified, status of current notebook (which is pointed by `HEAD`) will be shown.


### Tag management
#### `qnote tag`
- List all tags
    ```bash
    $ qnote tag list
    ```

- Clear those tags which no notes are tagged by
    ```bash
    $ qnote tag clear_empty
    ```

- Rename tag
    ```bash
    $ qnote tag rename <old_name> <new_name>
    ```


## Why I made this
I was looking for a note-taking tool which is easy to use, low resource consuming and even extensible since I really want to make some experimental features to make me take notes more conveniently.

But finding such an ideal application seems way more difficult than building one by myself. So I decided to make this tool.

And thanks to the following awesome tools, this project is also inspired by them:
- [xwmx/nb](https://github.com/xwmx/nb)
- [tasdikrahman/tnote](https://github.com/tasdikrahman/tnote)


## Contributing
Feel free to open an issue when you find out a bug.
