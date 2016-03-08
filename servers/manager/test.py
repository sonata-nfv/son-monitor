import json, yaml





def main():
    filename = '/home/panos/NetBeansProjects/sonataDev/MonitoringSrv/prometheus-0.17.0rc2.linux-amd64/rules/123458.rules'
    with open('test_out.yml', 'r') as conf_file:
        conf = yaml.load(conf_file)
    for rf in conf['rule_files']:
	print rf
        if filename in rf:
	    print "file found"	
            return
    conf['rule_files'].append(filename)
    print conf['rule_files']
    with open('test_out.yml', 'w') as yml:
        yaml.dump(conf, yml)


if __name__ == "__main__":
    main()
