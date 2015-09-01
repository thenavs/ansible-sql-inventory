add some data:
```bash
./hosts.py --group-add all
./hosts.py --group-add linux
./hosts.py --group-add dbservers
./hosts.py --group-add ec2_group
./hosts.py --host-add sql-slave-00 --groups ec2_group,linux
./hosts.py --set ansible_ssh_host 192.168.1.10 --group all
```
verify with ansible
```bash
ansible all -i hosts.py -m debug -a "var=ansible_ssh_host"
```

group_vars still works, just needs to be in the same directory as hosts.py
