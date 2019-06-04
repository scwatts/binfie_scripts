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

## BASH [[…]]
Returns a status of 0 or 1 depending expression evaluation

### String regex
```bash
if [[ $mystring =~ '*regex*' ]]; then
  echo "regex matches";
fi
```

### Check variable set
```bash
if [[ -z ${var+x} ]]; then
  echo "is unset";
fi
```

## Deterministic bits
Some GNU programs accept an fd as a source of random bytes - typically used for /dev/random, /dev/urandom, or /dev/zero. You
can also specify a stream of seeded deterministic bits using openssl. Here is an example that randomly selects 10 files from
a list using a seed rng
```bash
seed=0;
for file in $(find counts/*tsv | shuf -n10 --random-source=<(openssl enc -aes-128-cbc -pass pass:${seed} -nosalt < /dev/zero 2>/dev/null)); do
  # Process files in some way
  my_process $file;
done
```
In cases where no seeding is required, /dev/zero will often suffice.


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

## Here documents
These features of BASH which allows specification of input data. A good use of this is to simulate user input for an
interactive command
```bash
./command_with_prompts << EOF
yes
all
force
etc
EOF
```

It can be used in simple cases too:
```bash
cat << EOF
this data will
be provided to cat
as if it was done
interactively
EOF
```

## Programmatic screen sessions
It is sometimes preferable to run software within screen sessions. Occasionally, executing multiple runs of software each
with their own screen session is desired. To do this, you can programmatically create screens and execute commands:
```bash
mkdir -p 2_mapping/logs
for dir in 2_mapping/M1C*; do
  sample=${dir##*/};
  screen_name=hi_${sample};
  source_cmds="source /home/stephen/other/miniconda3/etc/profile.d/conda.sh; conda activate reddog"
  reddog_command="rubra --config RedDog_config.py --style run RedDog.py 1>../../logs/${sample}.log 2>&1 <<< 'yes'";
  screen -dmS ${screen_name} bash -c "${source_cmds}; cd ${dir}/reddog/; ${reddog_command}";
done
```
For each loop iteration, screen calls the bash executable that will run the commands provided by `-c` in the specified
session. Once all commands have finished the session will terminate. To force session persistence you can append `; exec
bash` to the `-c` argument.


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
