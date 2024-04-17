import subprocess
from dataclasses import dataclass
import os
import sys

@dataclass
class NetworkChangeEvent:
    type: str
    value: str

@dataclass
class NetworkInterface:
    device: str
    state: str

detect_network_change_commands: list[str] = [
    '$networkChange = [System.Net.NetworkInformation.NetworkChange]',
    '$onChangeNetwork = { $mtu = $(get-netipinterface | where-object ConnectionState -EQ "Connected" | sort-object NlMtu | select-object -first 1).NlMtu ; write-host "MTU:$mtu" }',
    'Register-ObjectEvent -InputObject $networkChange -EventName NetworkAddressChanged -Action $onChangeNetwork | Out-Null',
    'Wait-Event'
]

def monitor_network_change():
    proc_monitor = subprocess.Popen([
        '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', 
        '-c', 
        ';'.join(detect_network_change_commands)],
        stdout=subprocess.PIPE)
    while True:
        line = proc_monitor.stdout.readline()
        if not line and proc_monitor.poll() is not None:
            break
        msg = line.decode('utf8').rstrip('\n')
        vv = msg.split(':')
        if len(vv) < 2 or not msg:
            continue
        yield NetworkChangeEvent(type = vv[0], value = vv[1])

def enumerate_network_devices():
    result = subprocess.run([
        'ip', '-brief', 'a'
    ], check=True, stdout=subprocess.PIPE)
    out = [x for x in result.stdout.decode('utf8').split('\n') if x]
    for o in out:
        vv = [x for x in o.split(' ') if x]
        yield NetworkInterface(device=vv[0], state=vv[1])


def set_mtu(nif: NetworkInterface, mtu: int):
    subprocess.run([
        'ip', 'link', 'set', 'dev', nif.device, 'mtu', str(mtu)
    ], check=True)

def check_permission():
    if os.getuid() != 0:
        print('Operation not permitted | require root priviledge', file=sys.stderr)
        exit(1)

def main():
    check_permission()

    active_ifs = [x for x in enumerate_network_devices() if x.state == 'UP']
    print(f'target interfaces | [{",".join((x.device for x in active_ifs))}]')

    print('start to watch network state...')
    for event in monitor_network_change():
        if event.type == 'MTU':
            mtu = int(event.value) - 28 # 28 = header bytes
            for nif in active_ifs:
                print(f'set mtu | device: {nif.device} | mtu: {mtu}')
                set_mtu(nif, mtu)


if __name__ == '__main__':
    main()