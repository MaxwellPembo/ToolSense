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

for child in $(list_child_processes 71480);
do
  echo killing $child;
  kill -s KILL $child;
done;
rm /Users/carter-fogle/Documents/projects/internet_of_things/project/git/toolsense/server/bin/Debug/net10.0/b8ed3d08c8984395b77ac6cd4412ab85.sh;
