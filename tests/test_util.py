import io
import pytest
from util import run, match_timestamp, match_ipv4, match_ipv6

LOG_LONG = 'tests/log_example_long'
LOG_SHORT = 'tests/log_example_short'

OUT_FIRST_5 = """
Aug  9 06:51:10 user systemd[1]: Started NTP client/server.
Aug  9 06:51:10 user audit[1]: SERVICE_START pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 msg='unit=chronyd comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
Aug  9 06:51:10 user sssd[1044]: Starting up
Aug  9 06:51:10 user systemd[1]: Starting Authorization Manager...
Aug  9 06:51:10 user systemd[1]: Starting Hostname Service...
""".strip()

OUT_FIRST_4 = """
Aug  9 06:51:10 user systemd[1]: Started NTP client/server.
Aug  9 06:51:10 user audit[1]: SERVICE_START pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 msg='unit=chronyd comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
Aug  9 06:51:10 user sssd[1044]: Starting up
Aug  9 06:51:10 user systemd[1]: Starting Authorization Manager...
""".strip()

OUT_LAST_5 = """
Aug 12 08:42:06 user kernel: audit: type=1106 audit(1597214526.043:744): pid=1992860 uid=0 auid=1000 ses=3 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=PAM:session_close grantors=pam_keyinit,pam_limits,pam_keyinit,pam_limits,pam_systemd,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=/dev/pts/0 res=success'
Aug 12 08:42:06 user kernel: audit: type=1104 audit(1597214526.043:745): pid=1992860 uid=0 auid=1000 ses=3 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=PAM:setcred grantors=pam_localuser,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=/dev/pts/0 res=success'
Aug 12 08:42:34 user systemd[1]: fprintd.service: Succeeded.
Aug 12 08:42:34 user audit[1]: SERVICE_STOP pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 msg='unit=fprintd comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
Aug 12 08:42:34 user kernel: audit: type=1131 audit(1597214554.084:746): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 msg='unit=fprintd comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
""".strip()

OUT_LAST_4 = """
Aug  9 06:51:10 user systemd[1]: Started NTP client/server.
Aug  9 06:51:10 user audit[1]: SERVICE_START pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 msg='unit=chronyd comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
Aug  9 06:51:10 user sssd[1044]: Starting up
Aug  9 06:51:10 user systemd[1]: Starting Authorization Manager...
""".strip()

STDIN_LONG_LOG = None
STDIN_SHORT_LOG = None

with io.open(LOG_LONG) as fin:
    STDIN_LONG_LOG = fin.read()
with io.open(LOG_SHORT) as fin:
    STDIN_SHORT_LOG = fin.read()


test_data_filename = [
    # (args, expected)
    (['-f 5', LOG_LONG], OUT_FIRST_5),
    (['-f 5', LOG_SHORT], OUT_FIRST_4),
    (['-l 5', LOG_LONG], OUT_LAST_5),
    (['-l 5', LOG_SHORT], OUT_LAST_4),
    # With timestamp
    (['-f 5', '-t', LOG_LONG], OUT_FIRST_5),
    (['-f 5', '-t', LOG_SHORT], OUT_FIRST_4),
    (['-l 5', '-t', LOG_LONG], OUT_LAST_5),
    (['-l 5', '-t', LOG_SHORT], OUT_LAST_4),
]

@pytest.mark.parametrize("args,expected", test_data_filename)
def test_filename_input(capsys, args, expected):
    run(args)
    captured = capsys.readouterr()
    assert captured.out.strip() == expected


test_data_stdin = [
    # (args, stdin, expected)
    (['-f 5'], io.StringIO(STDIN_LONG_LOG), OUT_FIRST_5),
    (['-f 5'], io.StringIO(STDIN_SHORT_LOG), OUT_FIRST_4),
    (['-l 5'], io.StringIO(STDIN_LONG_LOG), OUT_LAST_5),
    (['-l 5'], io.StringIO(STDIN_SHORT_LOG), OUT_LAST_4),
    # With timestamp
    (['-f 5', '-t'], io.StringIO(STDIN_LONG_LOG), OUT_FIRST_5),
    (['-f 5', '-t'], io.StringIO(STDIN_SHORT_LOG), OUT_FIRST_4),
    (['-l 5', '-t'], io.StringIO(STDIN_LONG_LOG), OUT_LAST_5),
    (['-l 5', '-t'], io.StringIO(STDIN_SHORT_LOG), OUT_LAST_4),
]

@pytest.mark.parametrize("args,stdin,expected", test_data_stdin)
def test_stdin_input(capsys, args, stdin, expected):
    run(args, stdin)
    captured = capsys.readouterr()
    assert captured.out.strip() == expected


def test_error_file_not_found():
    with pytest.raises(FileNotFoundError):
        run(['-f 10', 'log_non_existing'])
    with pytest.raises(FileNotFoundError):
        run(['-l 10', 'log_non_existing'])
    with pytest.raises(FileNotFoundError):
        run(['log_non_existing'])


test_data_timestamp = [
    ('Aug  9 06:51:10 user systemd[1]: Started NTP client/server.', True),
    ('Aug 11 17:59:42 user cupsd[1154]: REQUEST loSubscrip', True),
    ('Aug 11 23:59:42 user cupsd[1154]: REQUEST loSubscrip', True),
    ('00:00:00', True),
    # False
    ('', False),
    ('foo bar \n', False),
    ('Aug 11 38:59:42 user cupsd[1154]: REQUEST localhost - - "POST / HTTP/1.1" 200 187 Renew-Subscrip', False),
    ('Aug 11 23:79:42 user cupsd[1154]: REQUEST localhost - - "POST / HTTP/1.1" 200 187 Renew-Subscrip', False),
    ('Aug 11 23:59:92 user cupsd[1154]: REQUEST localhost - - "POST / HTTP/1.1" 200 187 Renew-Subscrip', False),
]

@pytest.mark.parametrize("line,expected", test_data_timestamp)
def test_match_timestamp(line, expected):
    assert match_timestamp(line) == expected


test_data_ipv4 = [
    ('Aug  9 06:51:12 user avahi-daemon[1023]: Joining mDNS multicast group on interface virbr0.IPv4 with address 192.168.122.1.', True),
    ('Aug  9 06:51:12 user avahi-daemon[1023]: Registering new address record for 192.168.122.1 on virbr0.IPv4.', True),
    ('Aug  9 06:51:12 user dnsmasq-dhcp[1407]: DHCP, IP range 192.168.122.2 -- 192.168.122.254, lease time 1h', True),
    ('Aug  9 06:51:17 user avahi-daemon[1023]: Registering new address record for 192.168.1.169 on wlp2s0.IPv4.', True),
    ('Aug  9 06:51:17 user dnsmasq[1407]: using nameserver 127.0.0.1#53', True),
    ('Aug  9 06:51:22 user chronyd[1092]: Selected source 162.159.200.123', True),
    ('0.0.0.0', True),
    ('1.1.1.1', True),
    ('47.47.47.47', True),
    ('183.183.183.183', True),
    ('241.241.241.241', True),
    ('255.255.255.255', True),
    # False
    ('', False),
    ('256.256.256.256', False),
    ('356.356.556.956', False),
    ('Aug  9 06:51:17 user dnsmasq[1407]: using nameserver #53', False),
]

@pytest.mark.parametrize("line,expected", test_data_ipv4)
def test_match_ipv4(line, expected):
    assert match_ipv4(line) == expected


test_data_ipv6 = [
    ('2001:0db8:0000:0000:0000:ff00:0042:8329', True),
    ('0000:0000:0000:0000:0000:0000:0000:0001', True),
    ('2001:0db8:0000:0000:0000:ff00:0042:8329', True),
    ('2001:0DB8:0000:0000:0000:FF00:0042:8329', True),
    ('Aug  9 06:51:17 user avahi-daemon[1023]: Registering new address record for 2001:0db8:0000:0000:0000:ff00:0042:8329 on wlp2s0.IPv6.', True),
    # False
    ('', False),
    ('20R1:0db8:0000:0000:T000:ff00:0042:8329', False),
]

@pytest.mark.parametrize("line,expected", test_data_ipv6)
def test_match_ipv6(line, expected):
    assert match_ipv6(line) == expected


def test_integration_ipv4_first(capsys):
    run(['-f 40', '-i', LOG_LONG])
    captured = capsys.readouterr()
    assert captured.out.strip() == 'Aug  9 06:51:17 user avahi-daemon[1023]: Registering new address record for 192.168.1.169 on wlp2s0.IPv4'


def test_integration_ipv6_first(capsys):
    run(['-f 39', '-I', LOG_LONG])
    captured = capsys.readouterr()
    assert captured.out.strip() == 'Aug  9 06:51:17 user avahi-daemon[1023]: Registering new address record for 2001:0db8:0000:0000:0000:ff00:0042:8329 on wlp2s0.IPv6'
