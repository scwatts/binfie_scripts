# BASH commands
Some useful BASH commands

## Empty directories
Enumerate empty directories
```bash
find . -empty
```

And to delete:
```bash
find . -empty -delete
```

## Find broken symlinks
```bash
find . -xtype l
```

## Print filenames of `find` results
```bash
find ../long/path/to/search -type f -printf '%f\n'
```

## Forwarding with SOCKS proxy (via ssh)
This requires OpenBSD netcat. Create the tunnel on port 8080
```bash
ssh -vND8080 proxy_server_address
```

Connect via ssh through tunnel to a machine
```bash
ssh -o ProxyCommand='nc.openbsd -x localhost:8080 %h %p'' server_address
```

Download data via rsync through tunnel
```bash
rsync -aPLe "ssh -o ProxyCommand='nc.openbsd -x localhost:8080 %h %p'" server_address:src/ dest/
```

# Here documents and strings
These features of BASH which allows specification of input data. A good use of this is to simulate user input for an
interactive command.
```bash
./command_with_prompts << EOF
yes
all
force
etc
EOF
```

It can be used in simply cases too:
```bash
cat << EOF
this data will
be provided to cat
as if it was done
interactively
EOF
```

## Secrets
Securely generate secret tokens and passwords
```bash
tr -dc '[:punct:][:alnum:]' < /dev/urandom | head -c${1:-32}; echo;
```

## Patching
Generating patches
```bash
diff -u file_a file_b > my_patch.txt
```

Applying a patch
```bash
patch -l < my_patch.txt
```

In some instances, filenames in patches will be prefixed. These may need to be stripped when applying the patch
```bash
patch -lp1 < my_patch.txt
```
