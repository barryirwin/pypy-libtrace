# 1349, Mon  7  Dec 2015 (NZDT)
#
# ipp.py:  IPprefix objects implemented in python
#
# Copyright (C) 2016 by Nevil Brownlee, U Auckland | WAND
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from cipp import ffi, lib
import string, copy

class IPprefix(object):  # New-style class, child of object
    def __init__(self, *args):  # (self, version, addr, length)
        if len(args) > 3 or len(args) < 2:
            raise ValueError("IPprefix expects 2 or 3 arguments")
        if args[0] == 4:
            pref_max = 32
        elif args[0] == 6:
            pref_max = 128
        else:
            raise ValueError("IPprefix version not 4 or 6")
        self.i_ver = args[0]
        if isinstance(args[1], ffi.CData):
             self.i_addr = args[1]
        elif isinstance(args[1], bytearray):
            if self.i_ver == 4:
                self.i_addr = ffi.new("uint8_t[4]");  sz = 4
            else:
                self.i_addr = ffi.new("uint8_t[16]");  sz = 16
            ffi.memmove(self.i_addr, args[1], sz)
        else:
            raise TypeError("Expected 'cdata uint8_t[]' or bytearray!")
        if len(args) == 3:
            if args[2] and not isinstance(args[2], int):
                raise TypeError("Prefix length must be an integer")
            elif args[2] < 0:
                raise ValueError("Prefix length must be > 0")
            elif args[2] > pref_max:
                raise ValueError("Prefix length > 32 (IPv4) or > 128 (IPv6)")
            self.i_len = args[2]  # Prefix length (may be None)
        else:
            self.i_len = None  #####pref_max

    def __str__(self):
        #a = ffi.string(lib.ipaddr2str(self.i_ver, self.i_addr))
        a = ffi.string(lib.ipaddr2str(self.i_ver, \
            self.i_addr)).decode(encoding='utf-8')
        if self.i_ver == 4:
            pref_max = 32
        else:
            pref_max = 128
        if self.i_len:  #####self.i_len < pref_max:
            return (a+'/'+str(self.i_len))
        else:
            return a

    def __hash__(self):
        len = self.i_len
        if not len:
            len = 129
        return lib.ipp_hash(self.i_ver, self.i_addr, len)

    def cmp_addr(self, other):
        if self.i_ver != other.i_ver:
            raise ValueError("Ipprefix versions must be the same (4 or 6)")
        return lib.caddrcmp(self.i_ver, self.i_addr, other.i_addr)
        
    def cmp(self, other):  # Rich compare fundtions
        sc = self.cmp_addr(other)
        if sc == 0:
            if self.i_len and other.i_len:
                if self.i_len != other.i_len:
                    if self.i_len > other.i_len:
                        return 1
                    else:
                        return -1
            else:
                return 0
        return sc
        
    def __lt__(self, other):
        return self.cmp(other) < 0
    def __le__(self, other):
        return self.cmp(other) <= 0
    def __eq__(self, other):
        return self.cmp(other) == 0
    def __nq__(self, other):
        return self.cmp(other) != 0
    def __ge__(self, other):
        return self.cmp(other) >= 0
    def __gt__(self, other):
        return self.cmp(other) > 0

    # Class functions

    def first_bit_different(self, other):
        if not isinstance(other, IPprefix):
            raise TypeError("Expcted an IPprefix")
        if self.i_ver != other.i_ver:
            raise ValueError("IPprefix versions must be the same (4 or 6)")
        #if (not self.i_len) or (not other.i_len):
        #    raise ValueError("One or both IPprefixes has no length")
        fbd = lib.c_fbd(self.i_ver, self.addr, other.addr)
        if self.i_len and other.i_len:
            min_len = self.i_len
            if other.i_len < min_len:
                min_len = other.i_len
            if fbd > min_len:
                return min_len
            else:
                return fbd
        else:
            return fbd

    def is_prefix(self, other):
        fbd = self.first_bit_different(other)
        return fbd >= self.i_len

    def equal(self, other):
        if self.i_ver != other.i_ver:
            return False
        return self.cmp_addr(other) == 0

    def has_bit_set(self, bit_nbr):
        if self.i_ver == 4 and bit_nbr > 32:
            raise ValueError("IPv4 bit number must be < 32")
        if self.i_ver == 6 and bit_nbr > 128:
            raise ValueError("IPv6 bit number must be < 128")
        return bool(lib.c_bit_set(self.i_ver, self.addr, bit_nbr))

    def network(self, net_len):
        if self.i_ver == 4:
            ca = ffi.new("uint8_t[4]");  sz = 4
        else:
            ca = ffi.new("uint8_t[16]");  sz = 16
        ffi.memmove(ca, self.i_addr, sz)
        lib.c_mask_network(ca, sz, self.i_addr, net_len)
        return IPprefix(self.i_ver, ca, net_len)
    
    # IPprefix instance properties

    def set_length(self, new_len):
        if not isinstance(new_len, int):
            raise TypeError("Prefix length must be an integer")
        if new_len < 1:
            raise ValueError("Prefix length must be > 0")
        if self.i_ver == 4 and new_len > 32:
            raise ValueError("IPv4 prefix length must be <= 32")
        if self.i_ver == 6 and new_len > 128:
            raise ValueError("IPv6 prefix length must be <= 128")
        self.i_len = new_len
    def get_length(self):
        return self.i_len
    length = property(get_length, set_length)

    def get_version(self):
        return self.i_ver
    version = property(get_version)

    def get_addr(self):
        return self.i_addr
    addr = property(get_addr)

    def get_width(self):
        return self.length - 1
    width = property(get_width)

    def get_complement(self):
        if self.version == 4:
            ca = ffi.new("uint8_t[4]")
        else:
            ca = ffi.new("uint8_t[16]")
        lib.c_complement(self.i_ver, ca, self.i_addr)
        return IPprefix(self.i_ver, ca, self.i_len)
    complement = property(get_complement)

    def get_is_rfc1918(self):
        global rfc1918s16, rfc1918s12, rfc1918s8
        if rfc1918s16.is_prefix(self):
            return True
        if rfc1918s12.is_prefix(self):
            return True
        if rfc1918s8.is_prefix(self):
            return True
        return False
    is_rfc1918 = property(get_is_rfc1918)


def from_s(s):  # ipp Functions
    length = None;  sa = s.split('/', 2)
    if len(sa) == 2:  # length specified
        try:
            length = int(sa[1])
        except:
            raise ValueError("IPprefix length not an integer")

    if s.find(':') < 0:
        if length and length > 32:
            raise ValueError("IPv4 length must be <= 32")
        ver = 4;  ca = ffi.new("uint8_t[4]")
    else:        
        if length and length > 128:
            raise ValueError("IPv4 length must be <= 128")
        ver = 6;  ca = ffi.new("uint8_t[16]")

    #r = lib.str2ipaddr(ca, ver, sa[0])  # py2
    r = lib.str2ipaddr(ca, ver, sa[0].encode(encoding='UTF-8'))
    if r:
        if length:
            return IPprefix(ver, ca, length)
        return IPprefix(ver, ca)  # s didn't contain /length
    else:
        raise ValueError("Not a valid IPv4 or IPv6 address")


rfc1918s16 = from_s("192.168.0.0/16")
rfc1918s12 = from_s("172.16.0.0/12")
rfc1918s8 = from_s("10.0.0.0/8")
