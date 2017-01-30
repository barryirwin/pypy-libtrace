#!/usr/bin/env python

# Thu 21 Jan 2016 (NZDT)
# natkit.py:  Demonstrate using IPflow objects as dictionary keys
# Copyright (C) 2016, Nevil Brownlee, U Auckland | WAND

import plt
import natkit
from plt_testing import *

class flow():
    def __init__(self, ipf, first_n):
        self.ipf = ipf;  self.first_n = first_n
        self.fwd = 1;  self.rev = 0

def test_uri(uri, tag=''):
    test_dict = {}

    t = plt.trace(uri)
    t.start()

    nip = n = 0
    for pkt in t:
        n += 1
        test_println("n = %d" % n, tag+get_tag("n:"+str(n)))
        ipf = natkit.IPflow(pkt)
        if not ipf:
            test_println(" ", tag+get_tag())
            continue
        nip += 1

        test_println("%5d: %d %3d  %5d %5d  %s  %s" % (n,  # v6
           ipf.version, ipf.proto, ipf.src_port, ipf.dst_port,
           ipf.src_prefix, ipf.dst_prefix), tag+get_tag("n:"+str(n)))

        fwd = ipf.fwd_key
        test_print("fwd =",  tag+get_tag("n:"+str(n)))
        for b in fwd.encode(encoding='cp437'):
            test_print_hex(b)
        test_println('')

        rev = ipf.rev_key
        test_println('')
        for b in rev.encode(encoding='cp437'):
            test_print_hex(b)
        test_println('')

        v = test_dict.get(fwd)
        if v:
            v.fwd += 1
        else:
            rev = ipf.rev_key
            v =test_dict.get(rev)
            if v:
                v.rev += 1
            else:
                test_dict[fwd] = flow(ipf, n)
        if nip == 6:
            break

    t.close()
    test_println('')

    sk = sorted(test_dict)
    tot_pkts = 0
    for dk in sk:
        #print "dk = >%s<, val[k] = %d" % (dk, test_dict[dk])
        val = test_dict[dk]
        f = val.ipf
        test_println("      %3d: %d+%d; %d %d  %d->%d  %s->%s" % (
            val.first_n, val.fwd, val.rev,
            f.version, f.proto, f.src_port, f.dst_port,
            f.src_prefix, f.dst_prefix), tag+get_tag("n:"+str(n)))
        tot_pkts += val.fwd+val.rev
    test_println("%s: n = %d, nip = %d, tot_pkts = %d, OK = %s" % \
        (uri, n, nip, tot_pkts, tot_pkts == nip))
    test_println("")

test_uri("pcapfile:anon-v4.pcap", get_tag())
test_uri("pcapfile:anon-v6.pcap", get_tag())
