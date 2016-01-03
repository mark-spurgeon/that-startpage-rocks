#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib2

def parseDomain(domain):
    domain = domain.lower().replace('http://',"").replace('https://',"")
    if '/' in domain:
        domain = str(domain.split('/')[0])
        domain = domain.encode('ascii', 'ignore')
    #Get top level domains
    url = "https://publicsuffix.org/list/public_suffix_list.dat"
    h = httplib2.Http()
    r, content = h.request(url, "GET")
    if content:
        new_domain= None
        for line in content.split("\n"):
            if not line.startswith("//"):
                domaintoplevel = line.lower()
                domaintoplevel = "."+str(domaintoplevel)
                try:
                    if domain.endswith(domaintoplevel):
                        domain_no_ext = domain.replace(domaintoplevel,'')
                        if "." in domain_no_ext:
                            domain_no_ext = domain_no_ext.split('.')[-1]
                        new_domain = domain_no_ext+domaintoplevel
                except:
                    pass
        return new_domain
    else:
        return None
#testing
if __name__=="__main__":
    print parseDomain("www.curse.com")
