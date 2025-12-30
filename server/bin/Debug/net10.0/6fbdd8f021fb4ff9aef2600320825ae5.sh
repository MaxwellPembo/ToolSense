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

ps 35559;
while [ $? -eq 0 ];
do
  sleep 1;
  ps 35559 > /dev/null;
done;

for child in $(list_child_processes 43893);
do
  echo killing $child;
  kill -s KILL $child;
done;
rm /Users/carter-fogle/Documents/projects/internet_of_things/project/git/toolsense/server/bin/Debug/net10.0/6fbdd8f021fb4ff9aef2600320825ae5.sh;
