# Thu, 13 Mar 14 (PDT)
# plt-testing.py:  Support routines for testing python-libtrace
# Copyright (C) 2016, Nevil Brownlee, U Auckland | WAND

import ipp, plt

import os      # Contains getcwd
import sys     #   exit and stdout
import re      #   regular expressions
# import socket  #   gethostname

def get_example_trace(fn):
    cwd = os.getcwd()
    basename = os.path.basename(cwd)
    if re.match(r'python-libtrace', basename):
        full_fn = 'pcapfile:' + cwd + '/doc/examples/' + fn
    else:
        full_fn = 'pcapfile:' + cwd + '/' + fn
    print "fullfn = {0}\n" . format(full_fn)
    t = plt.trace(full_fn)
    t.start()
    return t

def print_data(msg, offset, data, mxlen):
    blanks = ' ' * (offset-1)   # print outputs an extra blank
    pad = ' ' * (offset - len(msg) + 1)  # Don't change (caller's) msg!
    print "%s%s" % (msg, pad),  # Trailing comma suppresses the linefeed
    for j in range(len(data)):
        if j == mxlen:
            break
        if j % 32 == 0 and j != 0:
            print "\n%s" % (blanks),
        if j % 8 == 0 and j != 0:
            print ' ',
        print "%02x" % (data[j]),
    print

def print_ip(ip, offset):
    margin = ' ' * offset
    print "%s -> %s, proto=%d, tclass=%x," % (
        ip.src_prefix, ip.dst_prefix, ip.proto, ip.traffic_class)
    print "%sttl=%d, hlen=%d, plen=%d, " % (
        margin, ip.ttl, ip.hdr_len, ip.pkt_len),
    print "mf=%s, frag_offset=%d, ident=%04x" % (
        ip.has_mf, ip.frag_offset, ip.ident)
    
def print_ip6(ip6, offset):
    margin = ' ' * offset
    print "%s -> %s, proto=%d, tclass=%x," % (
        ip6.src_prefix, ip6.dst_prefix, ip6.proto, ip6.traffic_class)
    print "%sttl=%d, hlen=%s, plen=%s" % (
        margin, ip6.hop_limit, ip6.hdr_len, ip6.pkt_len),
    print "flow_label=%x, payload_len=%d, next_hdr=%d" % (
        ip6.flow_label, ip6.payload_len, ip6.next_hdr)
    
def print_tcp(tcp, margin):
    fl = ''
    if tcp.urg_flag:
        fl += 'U'
    if tcp.psh_flag:
        fl += 'P'
    if tcp.rst_flag:
        fl += 'R'
    if tcp.fin_flag:
        fl += 'F'
    if tcp.syn_flag:
        fl += 'S'
    if tcp.ack_flag:
        fl += 'A'
    print "TCP, %s -> %s, %d -> %d, seq=%u, ack=%u" % (
        tcp.src_prefix, tcp.dst_prefix, tcp.src_port, tcp.dst_port,
        tcp.seq_nbr, tcp.ack_nbr)
    print "          flags=%02x (%s), window=%u, checksum=%x, urg_ptr=%u" % (
        tcp.flags, fl, tcp.window, tcp.checksum, tcp.urg_ptr),
    payload = tcp.payload
    if not payload:
        print ", no payload"
    else:
        pd = payload.data
        print_data("\n          payload ", margin, pd, 64)

def print_udp(udp, margin):
    print "UDP, src_port=%u, dest_port=%u, len=%u, checksum=%04x" % (
        udp.src_port, udp.dst_port, udp.len, udp.checksum)
    t = (' ' * 8) + 'UDP'
#    print_data(t, margin, udp.data, 64)

def print_icmp_ip(p, margin):
    print "proto=%d, TTL=%d, pkt_len=%d" % (
       p.proto, p.ttl, p.pkt_len)

def print_icmp(icmp, offset):  # IPv4 only  (IPv6 uses ICMP6 protocol)
    margin = ' ' * offset
    print "%sICMP, type=%u, code=%u, checksum=%04x,  wlen=%d, clen=%d, %s" % (
        margin, icmp.type, icmp.code, icmp.checksum,
        icmp.wire_len, icmp.capture_len, icmp.time)
    pd = p = icmp.payload
    #print "-2- pd =",
    #for j in range(0,8):
    #    print "%02x" % pd[j],
    #print
    type = icmp.type;  pt = 'IP  '
    if type == 0 or type == 8:  # Echo Reply, Echo Request
        if type == 8:
            which = 'request,'
        else:
            which = 'reply,  '
        echo = icmp.echo
        print "%sEcho %s ident=%04x, sequence=%d" % (
            margin, which, echo.ident, echo.sequence)
        pt = 'Echo'
    elif type == 3:  # Destination Unreachable
        print "%sDestination unreachable," % (margin),
        print_icmp_ip(p, margin);  pd = p.data
    elif type == 4:  # Source Quench
        print "%sSource quench," % (margin),
        print_icmp_ip(p, margin);  pd = p.data
    elif type == 5:  # Redirect
        redirect = icmp.redirect;
        print "%sRedirect, gateway=%s," % (margin, redirect.gateway),
        print_icmp_ip(p, margin);  pd = p.data
    elif type == 11:  # Time Exceeded
        print "%sTime exceeded," % (margin),
        print_icmp_ip(p, margin);  pd = p.data
    elif type == 12:  # Parameter problem
        print "%sParameter Probl\em," % (margin),
        print_icmp_ip(p, margin);  pd = p.data
    else:
        pt = "Other"
    t = margin + pt
    print_data(t, offset+len(pt), pd, 64)

def print_ip6_info(ip6):
    print "%s -> %s, TTL=%d" % (
        ip6.src_prefix, ip6.dst_prefix, ip6.ttl)


def print_icmp6(icmp6, offset):  # IPv6 only
    margin = ' ' * (offset-3)
    print "%sICMP6: stype=%u, code=%u, checksum=%04x, wlen=%d, clen=%d, %s" % (
        margin, icmp6.type, icmp6.code, icmp6.checksum,
        icmp6.wire_len, icmp6.capture_len, icmp6.time)
    margin = ' ' * offset
    type = icmp6.type;  pd = p = icmp6.payload;  pt = 'Echo'
    if type == 1:  # Destination Unreachable
        print "%sDestination unreachable:" % (margin),
        pt = 'IP6 '
        print_ip6_info(p);  pd = p.data
    elif type == 128 or type == 129:  # Echo Request, Echo Reply
        if type == 128:
            which = 'request:'
        else:
            which = 'reply:  '
        echo = icmp6.echo
        print "%sEcho %s ident=%04x, sequence=%d" % (
            margin, which, echo.ident, echo.sequence)
        pt = 'Data'
    elif type == 2:  # Packet Too Big
        print "%sPacket Too Big; MTU=%d:" % (margin, icmp6.toobig.mtu),
        pt = 'IP  '
        print_ip6_info(p);  pd = p.data
    elif type == 3:  # Time Exceeded
        print "%sTime Exceeded:" % (margin),
        pt = 'IP6 '
        print_ip6_info(p);  pd = p.data
    elif type == 4:  # Parameter Problem
        print "%sParameter Problem; pointer=%d," % (margin, icmp6.param.pointer),
        pt = 'IP6 '
        print_ip6_info(p);  pd = p.data
    else:
        if type == 133:
            s = "Router Solicitation"
        elif type == 134:
            s = "Router Advertisment"
        elif type == 135:
            s = "Neighbour Solicitation"
        elif type == 136:
            s = "Neighbour Advertisment"
        elif type == 137:
            s = "Redirect"
        elif type ==138:
            s = "Router Renumbering"
        else:
            s = "Other"
        if type == 135 or type == 136:
            print "%s%s: target_prefix=%s, src_prefix=%s" % (
                margin, s, icmp6.neighbour.target_prefix, icmp6.src_prefix)
        else:
            print "%s%s: src_prefix=%s" % (margin, s, icmp6.src_prefix)
        pt = 'Data'
    t = margin + pt
    print_data(t, offset+3, pd, 64)
