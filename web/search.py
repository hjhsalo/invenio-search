## $Id$
##
## This file is part of the CERN Document Server Software (CDSware).
## Copyright (C) 2002, 2003, 2004, 2005 CERN.
##
## The CDSware is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## The CDSware is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.  
##
## You should have received a copy of the GNU General Public License
## along with CDSware; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""CDSware Search Engine Web Interface."""

import sys    
from mod_python import apache    

from cdsware.config import weburl,cdsname
from cdsware import search_engine
from cdsware.webuser import getUid, page_not_authorized

__version__ = "$Id$"

def index(req, cc=cdsname, c=None, p="", f="", rg="10", sf="", so="d", sp="", rm="", of="hb", ot="", as="0",
          p1="", f1="", m1="", op1="", p2="", f2="", m2="", op2="", p3="", f3="", m3="", sc="0", jrec="0",
          recid="-1", recidb="-1", sysno="", id="-1", idb="-1", sysnb="", action="",
          d1y="0", d1m="0", d1d="0", d2y="0", d2m="0", d2d="0", verbose="0", ap="1", ln="en"):
    """Main entry point to WebSearch search engine.  See the docstring
       of search_engine.perform_request_search for the detailed
       explanation of arguments.
    """
    
    uid = getUid(req)
    if uid == -1: 
        return page_not_authorized(req, "../search.py")
    need_authentication = 0
    # check c
    if type(c) is list:
        for coll in c:
            if search_engine.coll_restricted_p(coll):
                need_authentication = 1
            else:
                pass
    elif search_engine.coll_restricted_p(c):
        need_authentication = 1
    # check cc
    if type(cc) is list:
        for coll in cc:
            if search_engine.coll_restricted_p(coll):
                need_authentication = 1
            else:
                pass
    elif search_engine.coll_restricted_p(cc):
        need_authentication = 1
    # is authentication needed?
    if need_authentication:
        req.err_headers_out.add("Location", "%s/search.py/authenticate?%s" % (weburl, req.args))
        raise apache.SERVER_RETURN, apache.HTTP_MOVED_PERMANENTLY
    else:
        return search_engine.perform_request_search(req, cc, c, p, f, rg, sf, so, sp, rm, of, ot, as,
                                                    p1, f1, m1, op1, p2, f2, m2, op2, p3, f3, m3, sc, jrec,
                                                    recid, recidb, sysno, id, idb, sysnb, action,
                                                    d1y, d1m, d1d, d2y, d2m, d2d, verbose, ap, ln) 

def authenticate(req, cc=cdsname, c=None, p="", f="", rg="10", sf="", so="d", sp="", rm="", of="hb", ot="", as="0",
                 p1="", f1="", m1="", op1="", p2="", f2="", m2="", op2="", p3="", f3="", m3="", sc="0", jrec="0",
                 recid="-1", recidb="-1", sysno="", id="-1", idb="-1", sysnb="", action="",
                 d1y="0", d1m="0", d1d="0", d2y="0", d2m="0", d2d="0", verbose="0", ap="1", ln="en"):
    """Authenticate the user before launching the search.  See the
       docstring of search_engine.perform_request_search for the
       detailed explanation of arguments.
    """    

    __auth_realm__ = "restricted collection"

    def __auth__(req, user, password):
        """Is user authorized to proceed with the request?"""
        import sys 
        from cdsware.config import cdsname
        from cdsware.webuser import auth_apache_user_collection_p
        from cgi import parse_qs
        # let's parse collection list from given URL request:
        parsed_args = parse_qs(req.args)
        l_cc = parsed_args.get('cc', [cdsname])
        l_c = parsed_args.get('c', [])
        # let's check user authentication for each collection:
        for coll in l_c + l_cc:
            if not auth_apache_user_collection_p(user, password, coll):
                return 0
        return 1

    return search_engine.perform_request_search(req, cc, c, p, f, rg, sf, so, sp, rm, of, ot, as,
                                                p1, f1, m1, op1, p2, f2, m2, op2, p3, f3, m3, sc, jrec,
                                                recid, recidb, sysno, id, idb, sysnb, action,
                                                d1y, d1m, d1d, d2y, d2m, d2d, verbose, ap, ln)

def cache(req, action="show"):
    """Manipulates the search engine cache."""
    return search_engine.perform_request_cache(req, action)

def log(req, date=""):
    """Display search log information for given date."""
    return search_engine.perform_request_log(req, date)

def test(req):
    import cgi
    req.content_type = "text/plain"
    req.send_http_header()    
    args = cgi.parse_qs(req.args)
    req.write("BEG\n")
    req.write("%s\n" % args.get('c'))
    req.write("END\n")
    return "\n"
