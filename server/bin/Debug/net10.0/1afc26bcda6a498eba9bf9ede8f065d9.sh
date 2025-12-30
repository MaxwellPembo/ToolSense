function list_child_processes () {
    local ppid=$1;
    local current_children=$(pgrep -P $ppid);
    local local_child;
    if [ $? -eq 0 ];
    then
        for current_child in $current_children
        do
          local_child=$current_child;
          list_child_processes $local_child;
          echo $local_child;
        done;
    else
      return 0;
    fi;
}

ps 6058;
while [ $? -eq 0 ];
do
  sleep 1;
  ps 6058 > /dev/null;
done;

for child in $(list_child_processes 93736);
do
  echo killing $child;
  kill -s KILL $child;
done;
rm /Users/carter-fogle/Documents/projects/internet_of_things/project/git/toolsense/server/bin/Debug/net10.0/1afc26bcda6a498eba9bf9ede8f065d9.sh;
