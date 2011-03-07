import re, os

#   Fields: date-time,connector-id,session-id,sequence-number,local-endpoint,remote-endpoint,event,data,context
IDX_DATE_TIME = 0
IDX_CONNECTOR_ID = 1
IDX_SESSION_ID = 2
IDX_SEQUENCE_NUMBER = 3
IDX_LOCAL_ENDPOINT = 4
IDX_REMOTE_ENDPOINT = 5
IDX_EVENT = 6
IDX_DATA = 7
IFX_CONTEXT = 8


def analyze_file(filename, from_addresses):
    mail_cnt = 0
    blocked_mail_cnt = 0
    
    f = open(filename)
    f.readline()    # erste Zeile ist komisch, ueberspringen
    while True:
        line = f.readline()
        if line == "":
            break
        
        if line[0] == '#':
            continue
            
        columns = line.split(',', 9)
        if columns[IDX_EVENT] == '+':
            mail_from = None
            mail_cnt += 1
        
        if columns[IDX_DATA].startswith('MAIL FROM'):
            match = re.match('MAIL FROM:\s*<(.*)>', columns[IDX_DATA])
            mail_from = match.groups()[0]
        
        if 'Recipient not authorized' in columns[IDX_DATA] or \
           'blocked by' in columns[IDX_DATA]:
           
            blocked_mail_cnt += 1
            #print mail_from
            if not mail_from in from_addresses:
                from_addresses[mail_from] = 1
            else:
                from_addresses[mail_from] += 1
            
    f.close()
    return (mail_cnt, blocked_mail_cnt)

def all_files():
    mail_cnt = 0
    blocked_mail_cnt = 0
    from_addresses = {}
    log_dir = "\\\\awt05\\c$\\Program Files\\Microsoft\\Exchange Server\\TransportRoles\\Logs\\ProtocolLog\\SmtpReceive"
    for item in os.listdir(log_dir):
        #print "FILE: %s" % item
        a, b = analyze_file(os.path.join(log_dir, item), from_addresses)
        mail_cnt += a
        blocked_mail_cnt += b

    for item in from_addresses.iteritems():
        print "%s\t%s" % (item[1], item[0])

    print "Mail Count: %s" % mail_cnt
    print "Blocked Mail Count: %s (%.2f%%)" % (blocked_mail_cnt, 100. * blocked_mail_cnt / mail_cnt)
        
if __name__ == '__main__':
    all_files()