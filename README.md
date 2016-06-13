# Lab2635 Soundboard Proxy

A script for the Lab2635 group that acts as a proxy for 
sending messages to the Discord channel soundboard bot through
the Discord API instead of emulating input to the Discord app.

The script uses a low-level keyboard hook to detect key bindings. If
you experience slow typing it's probably because of the script. 
Unfortunately nothing can be done about it.

Finally, this script likely isn't useful to anyone except gamers
in the Lab 2635 group, sorry about that! Feel free to learn from the
code or use it for your own projects.

## Dependencies

 - PyYAML >= 3.11

## Build

    git clone https://github.com/chutchinson/discord-soundboard-proxy
    python setup.py install
    
## Usage

    lab2635_soundboard.py --config config.yaml
    
  If you do not specify a configuration file, then the script
  assumes the configuration file is named `config.yaml` in the
  current working directory (the directory the script is being
  executed from).
  
## Configuration

  All configuration options are *required* except for key bindings.
  
| Key          | Description                              | Default |
| ------------ | ---------------------------------------- | ------- |
| email        | User's email address                     | n/a     |
| password     | User's password                          | n/a     |
| server       | Server name where soundboard bot lives   | n/a     |
| channel      | Text channel to send bot messages to     | n/a     |
| bot          | Mentionable name of the soundboard bot   | n/a     |
| bindings     | Dictionary of key bindings               | n/a     |

  See `examples/config.yaml` for a sample configuration file.
      
## Key Bindings

  The following keys are available for binding:

    # letters / digits
    a b c d e f g h i j k l m n o p q r s t u v w x y z
    0 1 2 3 4 5 6 7 8 9
    
    # number pad
    n0 n1 n2 n3 n4 n5 n6 n7 n8 n9
    f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12
    
    # arrow keys
    left up right down
    
    # modifiers
    ctrl alt shift
    
    # utilities
    insert home pgup pgdn del end
    esc
    
  Modifiers can be combined with `+`:

    ctrl+shift+a
    alt+f4
    
  Key bindings are configured in the configuration file as YAML
  dictionary entries:
  
     bindings:
       ctrl+shift+a: goal      # plays the 'goal' sound effect
       alt+f4: random          # plays the 'random' sound effect