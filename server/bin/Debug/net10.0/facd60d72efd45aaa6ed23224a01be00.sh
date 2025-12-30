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

ps 33164;
while [ $? -eq 0 ];
do
  sleep 1;
  ps 33164 > /dev/null;
done;

for child in $(list_child_processes 33958);
do
  echo killing $child;
  kill -s KILL $child;
done;
rm /Users/carter-fogle/Documents/projects/internet_of_things/project/git/toolsense/server/bin/Debug/net10.0/facd60d72efd45aaa6ed23224a01be00.sh;
