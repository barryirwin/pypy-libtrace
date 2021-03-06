
import plt, ipp
import os

# try-internet.py: test program for pypy plt

print "- - - - -"

print "NO_COMRESSION = %d" % plt.NO_COMPRESSION

base = "/Users/jbro111"  # OSX
#base = "/home/nevil"      # Ubuntu

#fn = "pypy/small-sample.erf"
#fn = "tcp-analyse/fdt-p5.pcap"
#fn = "pypy/small-sample.pcap"
#fn = "pypy/1000packets.pcap.gz"  # vlan id 1051 (Waikato)
fn = "pypy/anon-v6.pcap"
#fn = "pypy/anon-v4.pcap"

trace_format = "pcapfile"

full_fn = base + '/' + fn
print "%s: isfile %s" % (full_fn, os.path.isfile(full_fn))

uri = trace_format + ':' + full_fn
print ">> uri = %s" % uri

t = plt.trace(uri)
t.start()
print "+++ started"

out_fn = base + '/' + "pypy/pylt/plt/test-out.pcap"
out_uri =  trace_format + ':' + out_fn
print ">> out_uri = %s" % out_uri

out_t = plt.output_trace(out_uri)
out_t.start_output()

def print_first(s):
    for x in range(16):
        if x%8 == 0:
            print "",
        print "%02x" % s[x],

def print_all(s):
    for x,b in enumerate(s):
        if x%8 == 0:
            print "",
        print "%02x" % b,
    print
    
def qfmt(fs, v):
    if v:
        return fs % v
    else:
        return str(v)
    
nip = n = 0
for pkt in t:
    n += 1
    if n == 3:  #17:  # 1-org
        break
        
    tobj = pkt.transport
    print "tobj=%s, type(tobj)=%s, wlen=%d" % (tobj, type(tobj), pkt.wire_len)
    #plt.Data_dump(tobj, "tobj from pkt")

    ip = pkt.ip
    if not ip:
        print "pkt %d: not IP" % n
        continue
    nip += 1
    #plt.Data_dump(ip.pi, "ip from pkt")
    print "--- n=%d ---  cap_len=%d" % (n, pkt.capture_len)

    sa = ip.src_prefix;  da = ip.dst_prefix
    print "sa = %s, da= %s" % (sa, da)

    r = ip.test_l3_cksm()
    print "test_l3_cksm() returned %s" % r
    
    pr = ip.test_trans_cksm()
    print "test_trans_cksm() returned %s" % pr
        
    if ip.version == 4:
        nsa = ipp.from_s("1.2.3.4");  nda = ipp.from_s("5.6.7.8")
    else:
        nsa = ipp.from_s("1:2:3:4::");  nda = ipp.from_s("::5:6:7:8")
    ip.src_prefix = nsa;  ip.dst_prefix = nda
    sa = ip.src_prefix;  da = ip.dst_prefix
    print "sa = %s, da= %s" % (sa, da)

    d = ip.data
    print_all(d)
    print "ver=%d, proto=%d, traffic_class=%s, hop_limit=%d" % (
        ip.version, ip.proto, qfmt("%x", ip.traffic_class), ip.hop_limit)
    ip.traffic_class = 0x34
    print "ip.traffic_class = %s" % qfmt("%x", ip.traffic_class)

    print "pkt_len=%s, hdr_len=%s" % (
        qfmt("%d",ip.pkt_len), qfmt("%d", ip.hdr_len))

    ip.set_l3_cksm()
    ip.set_trans_cksm()
    out_t.write_packet(pkt)
    
print "EOF - - -"

out_t.close_output()
