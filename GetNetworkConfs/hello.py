import paramiko

def get_settings(host, user, pw, port, iface):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, password=pw, port=port)
        stdin, stdout, stderr = client.exec_command('cat /etc/resolv.conf')
        data = stdout.read() + stderr.read()

        splited = data.split('\n')
        nameservers = []
        for line in splited:
            if len(line) and line[0] != '#' and 'nameserver' in line:
	        nameservers.append(line.split()[1])

        stdin, stdout, stderr = client.exec_command("ip route | grep default")
        data = stdout.read() + stderr.read()
        splited = data.split()
        defgw = splited[2]

        stdin, stdout, stderr = client.exec_command('ifconfig {0} | grep Mask | cut -d":" -f4'.format(iface))
        netmask = stdout.read() + stderr.read()
        netmask = netmask[:-1]
        client.close()
        return (netmask, defgw, nameservers)
    except Exception as e:
        return "{0} is offline".format(host)

def form_output(response, node_name, host):
    if "offline" in response:
	return "{0}({1}) is offline. Can not get info.\n".format(node_name, host)
    else:
        out = "{0}({1}):\n\tnetmask: {2}\n\tdefault gateway: {3}\n\tDNS: ".format(node_name, host, response[0], response[1])
        for dns in response[2]:
            out += dns + " "
        out += '\n'
        return out

from flask import Flask
app = Flask(__name__)

@app.route('/<name>')
def hello(name):
    user='student'
    pw='student'
    port=22
    iface='eth0'
    if name == 'gw':
        iface='eth1'
        host='192.168.0.1'
    if name == 'u1':
        host='192.168.0.10'
    if name == 'u2':
        host='192.168.0.20'
    if name == 'u3':
        host='192.168.0.30'

    response = get_settings(host, user, pw, port, iface)
    output = form_output(response, name, host)
    return output
if __name__ == "__main__":
    app.run(port='8080')
