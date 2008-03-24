# -*- coding: utf-8 -*-
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# pylint: disable-msg=C0301
# pylint: disable-msg=E1102

"""WebSearch module regression tests."""

__revision__ = "$Id$"

import unittest
import re
import urlparse, cgi
from sets import Set

from mechanize import Browser, LinkNotFoundError, HTTPError

from invenio.config import CFG_SITE_URL, CFG_SITE_NAME, CFG_SITE_LANG
from invenio.testutils import make_test_suite, \
                              run_test_suite, \
                              make_url, test_web_page_content, \
                              merge_error_messages
from invenio.urlutils import same_urls_p
from invenio.search_engine import perform_request_search

def parse_url(url):
    parts = urlparse.urlparse(url)
    query = cgi.parse_qs(parts[4], True)

    return parts[2].split('/')[1:], query

class WebSearchWebPagesAvailabilityTest(unittest.TestCase):
    """Check WebSearch web pages whether they are up or not."""

    def test_search_interface_pages_availability(self):
        """websearch - availability of search interface pages"""

        baseurl = CFG_SITE_URL + '/'

        _exports = ['', 'collection/Poetry', 'collection/Poetry?as=1']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

    def test_search_results_pages_availability(self):
        """websearch - availability of search results pages"""

        baseurl = CFG_SITE_URL + '/search'

        _exports = ['', '?c=Poetry', '?p=ellis', '/cache', '/log']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

    def test_search_detailed_record_pages_availability(self):
        """websearch - availability of search detailed record pages"""

        baseurl = CFG_SITE_URL + '/record/'

        _exports = ['', '1', '1/', '1/files', '1/files/']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

    def test_browse_results_pages_availability(self):
        """websearch - availability of browse results pages"""

        baseurl = CFG_SITE_URL + '/search'

        _exports = ['?p=ellis&f=author&action_browse=Browse']

        error_messages = []
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return

    def test_help_page_availability(self):
        """websearch - availability of Help Central page"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help',
                                               expected_text="Help Central"))
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/?ln=fr',
                                               expected_text="Centre d'aide"))

    def test_search_tips_page_availability(self):
        """websearch - availability of Search Tips"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search-tips',
                                               expected_text="Search Tips"))
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search-tips?ln=fr',
                                               expected_text="Conseils de recherche"))

    def test_search_guide_page_availability(self):
        """websearch - availability of Search Guide"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search-guide',
                                               expected_text="Search Guide"))
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search-guide?ln=fr',
                                               expected_text="Guide de recherche"))

class WebSearchTestLegacyURLs(unittest.TestCase):

    """ Check that the application still responds to legacy URLs for
    navigating, searching and browsing."""

    def test_legacy_collections(self):
        """ websearch - collections handle legacy urls """

        browser = Browser()

        def check(legacy, new, browser=browser):
            browser.open(legacy)
            got = browser.geturl()

            self.failUnless(same_urls_p(got, new), got)

        # Use the root URL unless we need more
        check(make_url('/', c=CFG_SITE_NAME),
              make_url('/', ln=CFG_SITE_LANG))

        # Other collections are redirected in the /collection area
        check(make_url('/', c='Poetry'),
              make_url('/collection/Poetry', ln=CFG_SITE_LANG))

        # Drop unnecessary arguments, like ln and as (when they are
        # the default value)
        check(make_url('/', c='Poetry', as=0),
              make_url('/collection/Poetry', ln=CFG_SITE_LANG))

        # Otherwise, keep them
        check(make_url('/', c='Poetry', as=1),
              make_url('/collection/Poetry', as=1, ln=CFG_SITE_LANG))

        # Support the /index.py addressing too
        check(make_url('/index.py', c='Poetry'),
              make_url('/collection/Poetry', ln=CFG_SITE_LANG))


    def test_legacy_search(self):
        """ websearch - search queries handle legacy urls """

        browser = Browser()

        def check(legacy, new, browser=browser):
            browser.open(legacy)
            got = browser.geturl()

            self.failUnless(same_urls_p(got, new), got)

        # /search.py is redirected on /search
        # Note that `as' is a reserved word in Python 2.5
        check(make_url('/search.py', p='nuclear') + 'as=1',
              make_url('/search', p='nuclear') + 'as=1')

        # direct recid searches are redirected to /record
        check(make_url('/search.py', recid=1, ln='es'),
              make_url('/record/1', ln='es'))

    def test_legacy_search_help_link(self):
        """websearch - legacy Search Help page link"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search/index.en.html',
                                               expected_text="Help Central"))

    def test_legacy_search_tips_link(self):
        """websearch - legacy Search Tips page link"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search/tips.fr.html',
                                               expected_text="Conseils de recherche"))

    def test_legacy_search_guide_link(self):
        """websearch - legacy Search Guide page link"""
	self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/help/search/guide.en.html',
                                               expected_text="Search Guide"))

class WebSearchTestRecord(unittest.TestCase):
    """ Check the interface of the /record results """

    def test_format_links(self):
        """ websearch - check format links for records """

        browser = Browser()

        # We open the record in all known HTML formats
        for hformat in ('hd', 'hx', 'hm'):
            browser.open(make_url('/record/1', of=hformat))

            if hformat == 'hd':
                # hd format should have a link to the following
                # formats
                for oformat in ('hx', 'hm', 'xm', 'xd'):
                    target = make_url('/record/1/export/%s' % oformat)
                    try:
                        browser.find_link(url=target)
                    except LinkNotFoundError:
                        self.fail('link %r should be in page' % target)
            else:
                # non-hd HTML formats should have a link back to
                # the main detailed record
                 target = make_url('/record/1')
                 try:
                     browser.find_link(url=target)
                 except LinkNotFoundError:
                     self.fail('link %r should be in page' % target)

        return


class WebSearchTestCollections(unittest.TestCase):

    def test_traversal_links(self):
        """ websearch - traverse all the publications of a collection """

        browser = Browser()

        try:
            for as in (0, 1):
                browser.open(make_url('/collection/Preprints', as=as))

                for jrec in (11, 21, 11, 27):
                    args = {'jrec': jrec, 'cc': 'Preprints'}
                    if as:
                        args['as'] = as

                    url = make_url('/search', **args)
                    try:
                        browser.follow_link(url=url)
                    except LinkNotFoundError:
                        args['ln'] = CFG_SITE_LANG
                        url = make_url('/search', **args)
                        browser.follow_link(url=url)

        except LinkNotFoundError:
            self.fail('no link %r in %r' % (url, browser.geturl()))

    def test_collections_links(self):
        """ websearch - enter in collections and subcollections """

        browser = Browser()

        def tryfollow(url):
            cur = browser.geturl()
            body = browser.response().read()
            try:
                browser.follow_link(url=url)
            except LinkNotFoundError:
                print body
                self.fail("in %r: could not find %r" % (
                    cur, url))
            return

        for as in (0, 1):
            if as:
                kargs = {'as': 1}
            else:
                kargs = {}

            kargs['ln'] = CFG_SITE_LANG

            # We navigate from immediate son to immediate son...
            browser.open(make_url('/', **kargs))
            tryfollow(make_url('/collection/Articles%20%26%20Preprints',
                               **kargs))
            tryfollow(make_url('/collection/Articles', **kargs))

            # But we can also jump to a grandson immediately
            browser.back()
            browser.back()
            tryfollow(make_url('/collection/ALEPH', **kargs))

        return

    def test_records_links(self):
        """ websearch - check the links toward records in leaf collections """

        browser = Browser()
        browser.open(make_url('/collection/Preprints'))

        def harvest():

            """ Parse all the links in the page, and check that for
            each link to a detailed record, we also have the
            corresponding link to the similar records."""

            records = Set()
            similar = Set()

            for link in browser.links():
                path, q = parse_url(link.url)

                if not path:
                    continue

                if path[0] == 'record':
                    records.add(int(path[1]))
                    continue

                if path[0] == 'search':
                    if not q.get('rm') == ['wrd']:
                        continue

                    recid = q['p'][0].split(':')[1]
                    similar.add(int(recid))

            self.failUnlessEqual(records, similar)

            return records

        # We must have 10 links to the corresponding /records
        found = harvest()
        self.failUnlessEqual(len(found), 10)

        # When clicking on the "Search" button, we must also have
        # these 10 links on the records.
        browser.select_form(name="search")
        browser.submit()

        found = harvest()
        self.failUnlessEqual(len(found), 10)
        return


class WebSearchTestBrowse(unittest.TestCase):

    def test_browse_field(self):
        """ websearch - check that browsing works """

        browser = Browser()
        browser.open(make_url('/'))

        browser.select_form(name='search')
        browser['f'] = ['title']
        browser.submit(name='action_browse')

        def collect():
            # We'll get a few links to search for the actual hits, plus a
            # link to the following results.
            res = []
            for link in browser.links(url_regex=re.compile(CFG_SITE_URL +
                                                           r'/search\?')):
                if link.text == 'Advanced Search':
                    continue

                dummy, q = parse_url(link.url)
                res.append((link, q))

            return res

        # if we follow the last link, we should get another
        # batch. There is an overlap of one item.
        batch_1 = collect()

        browser.follow_link(link=batch_1[-1][0])

        batch_2 = collect()

        # FIXME: we cannot compare the whole query, as the collection
        # set is not equal
        self.failUnlessEqual(batch_1[-2][1]['p'], batch_2[0][1]['p'])

class WebSearchTestOpenURL(unittest.TestCase):

    def test_isbn_01(self):
        """ websearch - isbn query via OpenURL 0.1"""

        browser = Browser()

        # We do a precise search in an isolated collection
        browser.open(make_url('/openurl', isbn='0387940758'))

        dummy, current_q = parse_url(browser.geturl())

        self.failUnlessEqual(current_q, {
            'sc' : ['1'],
            'p' : ['isbn:"0387940758"'],
            'of' : ['hd']
        })

    def test_isbn_10_rft_id(self):
        """ websearch - isbn query via OpenURL 1.0 - rft_id"""

        browser = Browser()

        # We do a precise search in an isolated collection
        browser.open(make_url('/openurl', rft_id='urn:ISBN:0387940758'))

        dummy, current_q = parse_url(browser.geturl())

        self.failUnlessEqual(current_q, {
            'sc' : ['1'],
            'p' : ['isbn:"0387940758"'],
            'of' : ['hd']
        })

    def test_isbn_10(self):
        """ websearch - isbn query via OpenURL 1.0"""

        browser = Browser()

        # We do a precise search in an isolated collection
        browser.open(make_url('/openurl?rft.isbn=0387940758'))

        dummy, current_q = parse_url(browser.geturl())

        self.failUnlessEqual(current_q, {
            'sc' : ['1'],
            'p' : ['isbn:"0387940758"'],
            'of' : ['hd']
        })


class WebSearchTestSearch(unittest.TestCase):

    def test_hits_in_other_collection(self):
        """ websearch - check extension of a query to the home collection """

        browser = Browser()

        # We do a precise search in an isolated collection
        browser.open(make_url('/collection/ISOLDE', ln='en'))

        browser.select_form(name='search')
        browser['f'] = ['author']
        browser['p'] = 'matsubara'
        browser.submit()

        dummy, current_q = parse_url(browser.geturl())

        link = browser.find_link(text_regex=re.compile('.*hit', re.I))
        dummy, target_q = parse_url(link.url)

        # the target query should be the current query without any c
        # or cc specified.
        for f in ('cc', 'c', 'action_search', 'ln'):
            if f in current_q:
                del current_q[f]

        self.failUnlessEqual(current_q, target_q)

    def test_nearest_terms(self):
        """ websearch - provide a list of nearest terms """

        browser = Browser()
        browser.open(make_url(''))

        # Search something weird
        browser.select_form(name='search')
        browser['p'] = 'gronf'
        browser.submit()

        dummy, original = parse_url(browser.geturl())

        for to_drop in ('cc', 'action_search', 'f'):
            if to_drop in original:
                del original[to_drop]

        if 'ln' not in original:
            original['ln'] = [CFG_SITE_LANG]

        # we should get a few searches back, which are identical
        # except for the p field being substituted (and the cc field
        # being dropped).
        if 'cc' in original:
            del original['cc']

        for link in browser.links(url_regex=re.compile(CFG_SITE_URL + r'/search\?')):
            if link.text == 'Advanced Search':
                continue

            dummy, target = parse_url(link.url)

            if 'ln' not in target:
                target['ln'] = [CFG_SITE_LANG]

            original['p'] = [link.text]
            self.failUnlessEqual(original, target)

        return

    def test_switch_to_simple_search(self):
        """ websearch - switch to simple search """

        browser = Browser()
        browser.open(make_url('/collection/ISOLDE', as=1))

        browser.select_form(name='search')
        browser['p1'] = 'tandem'
        browser['f1'] = ['title']
        browser.submit()

        browser.follow_link(text='Simple Search')

        dummy, q = parse_url(browser.geturl())

        self.failUnlessEqual(q, {'cc': ['ISOLDE'],
                                 'p': ['tandem'],
                                 'f': ['title']})

    def test_switch_to_advanced_search(self):
        """ websearch - switch to advanced search """

        browser = Browser()
        browser.open(make_url('/collection/ISOLDE'))

        browser.select_form(name='search')
        browser['p'] = 'tandem'
        browser['f'] = ['title']
        browser.submit()

        browser.follow_link(text='Advanced Search')

        dummy, q = parse_url(browser.geturl())

        self.failUnlessEqual(q, {'cc': ['ISOLDE'],
                                 'p1': ['tandem'],
                                 'f1': ['title'],
                                 'as': ['1']})

    def test_no_boolean_hits(self):
        """ websearch - check the 'no boolean hits' proposed links """

        browser = Browser()
        browser.open(make_url(''))

        browser.select_form(name='search')
        browser['p'] = 'quasinormal muon'
        browser.submit()

        dummy, q = parse_url(browser.geturl())

        for to_drop in ('cc', 'action_search', 'f'):
            if to_drop in q:
                del q[to_drop]

        for bsu in ('quasinormal', 'muon'):
            l = browser.find_link(text=bsu)
            q['p'] = bsu
            if 'ln' in q:
                del q['ln']

            if not same_urls_p(l.url, make_url('/search', **q)):
                self.fail(repr((l.url, make_url('/search', **q))))

    def test_similar_authors(self):
        """ websearch - test similar authors box """

        browser = Browser()
        browser.open(make_url(''))

        browser.select_form(name='search')
        browser['p'] = 'Ellis, R K'
        browser['f'] = ['author']
        browser.submit()

        l = browser.find_link(text="Ellis, R S")
        self.failUnless(same_urls_p(l.url, make_url('/search',
                                                    p="Ellis, R S",
                                                    f='author')))

class WebSearchNearestTermsTest(unittest.TestCase):
    """Check various alternatives of searches leading to the nearest
    terms box."""

    def test_nearest_terms_box_in_okay_query(self):
        """ websearch - no nearest terms box for a successful query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellis',
                                               expected_text="jump to record"))

    def test_nearest_terms_box_in_unsuccessful_simple_query(self):
        """ websearch - nearest terms box for unsuccessful simple query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellisz',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=embed",
                                               expected_link_label='embed'))

    def test_nearest_terms_box_in_unsuccessful_structured_query(self):
        """ websearch - nearest terms box for unsuccessful structured query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellisz&f=author',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=fabbro&f=author",
                                               expected_link_label='fabbro'))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=author%3Aellisz',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=author%3Afabbro",
                                               expected_link_label='fabbro'))

    def test_nearest_terms_box_in_unsuccessful_phrase_query(self):
        """ websearch - nearest terms box for unsuccessful phrase query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=author%3A%22Ellis%2C+Z%22',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=author%3A%22Enqvist%2C+K%22",
                                               expected_link_label='Enqvist, K'))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=%22ellisz%22&f=author',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=%22Enqvist%2C+K%22&f=author",
                                               expected_link_label='Enqvist, K'))

    def test_nearest_terms_box_in_unsuccessful_boolean_query(self):
        """ websearch - nearest terms box for unsuccessful boolean query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=title%3Aellisz+author%3Aellisz',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=title%3Aenergie+author%3Aellisz",
                                               expected_link_label='energie'))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=title%3Aenergie+author%3Aenergie',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=title%3Aenergie+author%3Aenqvist",
                                               expected_link_label='enqvist'))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=title%3Aellisz+author%3Aellisz&f=keyword',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=title%3Aenergie+author%3Aellisz&f=keyword",
                                               expected_link_label='energie'))
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=title%3Aenergie+author%3Aenergie&f=keyword',
                                               expected_text="Nearest terms in any collection are",
                                               expected_link_target=CFG_SITE_URL+"/search?p=title%3Aenergie+author%3Aenqvist&f=keyword",
                                               expected_link_label='enqvist'))

class WebSearchBooleanQueryTest(unittest.TestCase):
    """Check various boolean queries."""

    def test_successful_boolean_query(self):
        """ websearch - successful boolean query """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellis+muon',
                                               expected_text="records found",
                                               expected_link_label="Detailed record"))

    def test_unsuccessful_boolean_query_where_all_individual_terms_match(self):
        """ websearch - unsuccessful boolean query where all individual terms match """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellis+muon+letter',
                                               expected_text="Boolean query returned no hits. Please combine your search terms differently."))

class WebSearchAuthorQueryTest(unittest.TestCase):
    """Check various author-related queries."""

    def test_propose_similar_author_names_box(self):
        """ websearch - propose similar author names box """
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=Ellis%2C+R&f=author',
                                               expected_text="See also: similar author names",
                                               expected_link_target=CFG_SITE_URL+"/search?p=Ellis%2C+R+K&f=author",
                                               expected_link_label="Ellis, R K"))

    def test_do_not_propose_similar_author_names_box(self):
        """ websearch - do not propose similar author names box """
        errmsgs = test_web_page_content(CFG_SITE_URL + '/search?p=author%3A%22Ellis%2C+R%22',
                                        expected_link_target=CFG_SITE_URL+"/search?p=Ellis%2C+R+K&f=author",
                                        expected_link_label="Ellis, R K")
        if errmsgs[0].find("does not contain link to") > -1:
            pass
        else:
            self.fail("Should not propose similar author names box.")
        return

class WebSearchSearchEnginePythonAPITest(unittest.TestCase):
    """Check typical search engine Python API calls on the demo data."""

    def test_search_engine_python_api_for_failed_query(self):
        """websearch - search engine Python API for failed query"""
        self.assertEqual([],
                         perform_request_search(p='aoeuidhtns'))

    def test_search_engine_python_api_for_successful_query(self):
        """websearch - search engine Python API for successful query"""
        self.assertEqual([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 47],
                         perform_request_search(p='ellis'))

    def test_search_engine_python_api_for_existing_record(self):
        """websearch - search engine Python API for existing record"""
        self.assertEqual([8],
                         perform_request_search(recid=8))

    def test_search_engine_python_api_for_nonexisting_record(self):
        """websearch - search engine Python API for non-existing record"""
        self.assertEqual([],
                         perform_request_search(recid=1234567809))

    def test_search_engine_python_api_for_nonexisting_collection(self):
        """websearch - search engine Python API for non-existing collection"""
        self.assertEqual([],
                         perform_request_search(c='Foo'))

    def test_search_engine_python_api_for_range_of_records(self):
        """websearch - search engine Python API for range of records"""
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8, 9],
                         perform_request_search(recid=1, recidb=10))

class WebSearchSearchEngineWebAPITest(unittest.TestCase):
    """Check typical search engine Web API calls on the demo data."""

    def test_search_engine_web_api_for_failed_query(self):
        """websearch - search engine Web API for failed query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=aoeuidhtns&of=id',
                                               expected_text="[]"))


    def test_search_engine_web_api_for_successful_query(self):
        """websearch - search engine Web API for successful query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=ellis&of=id',
                                               expected_text="[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 47]"))

    def test_search_engine_web_api_for_existing_record(self):
        """websearch - search engine Web API for existing record"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?recid=8&of=id',
                                               expected_text="[8]"))

    def test_search_engine_web_api_for_nonexisting_record(self):
        """websearch - search engine Web API for non-existing record"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?recid=123456789&of=id',
                                               expected_text="[]"))

    def test_search_engine_web_api_for_nonexisting_collection(self):
        """websearch - search engine Web API for non-existing collection"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?c=Foo&of=id',
                                               expected_text="[]"))

    def test_search_engine_web_api_for_range_of_records(self):
        """websearch - search engine Web API for range of records"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?recid=1&recidb=10&of=id',
                                               expected_text="[1, 2, 3, 4, 5, 6, 7, 8, 9]"))

class WebSearchRestrictedCollectionTest(unittest.TestCase):
    """Test of the restricted Theses collection behaviour."""

    def test_restricted_collection_interface_page(self):
        """websearch - restricted collection interface page body"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/collection/Theses',
                                               expected_text="The contents of this collection is restricted."))

    def test_restricted_search_as_anonymous_guest(self):
        """websearch - restricted collection not searchable by anonymous guest"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?c=Theses')
        response = browser.response().read()
        if response.find("If you think you have right to access it, please authenticate yourself.") > -1:
            pass
        else:
            self.fail("Oops, searching restricted collection without password should have redirected to login dialog.")
        return

    def test_restricted_search_as_authorized_person(self):
        """websearch - restricted collection searchable by authorized person"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?c=Theses')
        browser.select_form(nr=0)
        browser['p_un'] = 'jekyll'
        browser['p_pw'] = 'j123ekyll'
        browser.submit()
        if browser.response().read().find("records found") > -1:
            pass
        else:
            self.fail("Oops, Dr. Jekyll should be able to search Theses collection.")

    def test_restricted_search_as_unauthorized_person(self):
        """websearch - restricted collection not searchable by unauthorized person"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?c=Theses')
        browser.select_form(nr=0)
        browser['p_un'] = 'hyde'
        browser['p_pw'] = 'h123yde'
        browser.submit()
        # Mr. Hyde should not be able to connect:
        if browser.response().read().find("You are not authorized") <= -1:
            # if we got here, things are broken:
            self.fail("Oops, Mr.Hyde should not be able to search Theses collection.")

    def test_restricted_detailed_record_page_as_anonymous_guest(self):
        """websearch - restricted detailed record page not accessible to guests"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/record/35')
        if browser.response().read().find("You can use your nickname or your email address to login.") > -1:
            pass
        else:
            self.fail("Oops, searching restricted collection without password should have redirected to login dialog.")
        return

    def test_restricted_detailed_record_page_as_authorized_person(self):
        """websearch - restricted detailed record page accessible to authorized person"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/youraccount/login')
        browser.select_form(nr=0)
        browser['p_un'] = 'jekyll'
        browser['p_pw'] = 'j123ekyll'
        browser.submit()
        browser.open(CFG_SITE_URL + '/record/35')
        # Dr. Jekyll should be able to connect
        # (add the pw to the whole CFG_SITE_URL because we shall be
        # redirected to '/reordrestricted/'):
        if browser.response().read().find("A High-performance Video Browsing System") > -1:
            pass
        else:
            self.fail("Oops, Dr. Jekyll should be able to access restricted detailed record page.")

    def test_restricted_detailed_record_page_as_unauthorized_person(self):
        """websearch - restricted detailed record page not accessible to unauthorized person"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/youraccount/login')
        browser.select_form(nr=0)
        browser['p_un'] = 'hyde'
        browser['p_pw'] = 'h123yde'
        browser.submit()
        browser.open(CFG_SITE_URL + '/record/35')
        # Mr. Hyde should not be able to connect:
        if browser.response().read().find('You are not authorized') <= -1:
            # if we got here, things are broken:
            self.fail("Oops, Mr.Hyde should not be able to access restricted detailed record page.")

class WebSearchRSSFeedServiceTest(unittest.TestCase):
    """Test of the RSS feed service."""

    def test_rss_feed_service(self):
        """websearch - RSS feed service"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/rss',
                                               expected_text='<rss version="2.0">'))

class WebSearchXSSVulnerabilityTest(unittest.TestCase):
    """Test possible XSS vulnerabilities of the search engine."""

    def test_xss_in_collection_interface_page(self):
        """websearch - no XSS vulnerability in collection interface pages"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/?c=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E',
                                               expected_text='Collection &amp;lt;SCRIPT&amp;gt;alert("XSS");&amp;lt;/SCRIPT&amp;gt; Not Found'))

    def test_xss_in_collection_search_page(self):
        """websearch - no XSS vulnerability in collection search pages"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?c=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E',
                                               expected_text='Collection &lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt; Not Found'))

    def test_xss_in_simple_search(self):
        """websearch - no XSS vulnerability in simple search"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E',
                                               expected_text='Search term <em>&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;</em> did not match any record.'))

    def test_xss_in_structured_search(self):
        """websearch - no XSS vulnerability in structured search"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E&f=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E',
                                               expected_text='Search term <em>&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;</em> inside index <em>&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;</em> did not match any record.'))


    def test_xss_in_advanced_search(self):
        """websearch - no XSS vulnerability in advanced search"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?as=1&p1=ellis&f1=author&op1=a&p2=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E&f2=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E',
                                               expected_text='Search term <em>&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;</em> inside index <em>&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;</em> did not match any record.'))



    def test_xss_in_browse(self):
        """websearch - no XSS vulnerability in browse"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E&f=%3CSCRIPT%3Ealert%28%22XSS%22%29%3B%3C%2FSCRIPT%3E&action_browse=Browse',
                                               expected_text='&lt;SCRIPT&gt;alert("XSS");&lt;/SCRIPT&gt;'))

class WebSearchResultsOverview(unittest.TestCase):
    """Test of the search results page's Results overview box and links."""

    def test_results_overview_split_off(self):
        """websearch - results overview box when split by collection is off"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?p=of&sc=0')
        body = browser.response().read()
        if body.find("Results overview") > -1:
            self.fail("Oops, when split by collection is off, "
                      "results overview should not be present.")
        if body.find('<a name="1"></a>') == -1:
            self.fail("Oops, when split by collection is off, "
                      "Atlantis collection should be found.")
        if body.find('<a name="15"></a>') > -1:
            self.fail("Oops, when split by collection is off, "
                      "Multimedia & Arts should not be found.")
        try:
            browser.find_link(url='#15')
            self.fail("Oops, when split by collection is off, "
                      "a link to Multimedia & Arts should not be found.")
        except LinkNotFoundError:
            pass

    def test_results_overview_split_on(self):
        """websearch - results overview box when split by collection is on"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?p=of&sc=1')
        body = browser.response().read()
        if body.find("Results overview") == -1:
            self.fail("Oops, when split by collection is on, "
                      "results overview should be present.")
        if body.find('<a name="Atlantis%20Institute%20of%20Fictive%20Science"></a>') > -1:
            self.fail("Oops, when split by collection is on, "
                      "Atlantis collection should not be found.")
        if body.find('<a name="15"></a>') == -1:
            self.fail("Oops, when split by collection is on, "
                      "Multimedia & Arts should be found.")
        try:
            browser.find_link(url='#15')
        except LinkNotFoundError:
            self.fail("Oops, when split by collection is on, "
                      "a link to Multimedia & Arts should be found.")

class WebSearchSortResultsTest(unittest.TestCase):
    """Test of the search results page's sorting capability."""

    def test_sort_results_default(self):
        """websearch - search results sorting, default method"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=of&f=title&rg=1',
                                               expected_text="[hep-th/9809057]"))

    def test_sort_results_ascending(self):
        """websearch - search results sorting, ascending field"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=of&f=title&rg=1&sf=reportnumber&so=a',
                                               expected_text="ISOLTRAP"))

    def test_sort_results_descending(self):
        """websearch - search results sorting, descending field"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=of&f=title&rg=1&sf=reportnumber&so=d',
                                               expected_text=" [SCAN-9605071]"))

    def test_sort_results_sort_pattern(self):
        """websearch - search results sorting, preferential sort pattern"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=of&f=title&rg=1&sf=reportnumber&so=d&sp=cern',
                                               expected_text="[CERN-TH-2002-069]"))

class WebSearchSearchResultsXML(unittest.TestCase):
    """Test search results in various output"""

    def test_search_results_xm_output_split_on(self):
        """ websearch - check document element of search results in xm output (split by collection on)"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?sc=1&of=xm')
        body = browser.response().read()

        num_doc_element = body.count("<collection "
                                     "xmlns=\"http://www.loc.gov/MARC21/slim\">")
        if num_doc_element == 0:
            self.fail("Oops, no document element <collection "
                      "xmlns=\"http://www.loc.gov/MARC21/slim\">"
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements <collection> "
                      "found in search results.")

        num_doc_element = body.count("</collection>")
        if num_doc_element == 0:
            self.fail("Oops, no document element </collection> "
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements </collection> "
                      "found in search results.")


    def test_search_results_xm_output_split_off(self):
        """ websearch - check document element of search results in xm output (split by collection off)"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?sc=0&of=xm')
        body = browser.response().read()

        num_doc_element = body.count("<collection "
                                     "xmlns=\"http://www.loc.gov/MARC21/slim\">")
        if num_doc_element == 0:
            self.fail("Oops, no document element <collection "
                      "xmlns=\"http://www.loc.gov/MARC21/slim\">"
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements <collection> "
                      "found in search results.")

        num_doc_element = body.count("</collection>")
        if num_doc_element == 0:
            self.fail("Oops, no document element </collection> "
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements </collection> "
                      "found in search results.")

    def test_search_results_xd_output_split_on(self):
        """ websearch - check document element of search results in xd output (split by collection on)"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?sc=1&of=xd')
        body = browser.response().read()

        num_doc_element = body.count("<collection")
        if num_doc_element == 0:
            self.fail("Oops, no document element <collection "
                      "xmlns=\"http://www.loc.gov/MARC21/slim\">"
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements <collection> "
                      "found in search results.")

        num_doc_element = body.count("</collection>")
        if num_doc_element == 0:
            self.fail("Oops, no document element </collection> "
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements </collection> "
                      "found in search results.")


    def test_search_results_xd_output_split_off(self):
        """ websearch - check document element of search results in xd output (split by collection off)"""
        browser = Browser()
        browser.open(CFG_SITE_URL + '/search?sc=0&of=xd')
        body = browser.response().read()

        num_doc_element = body.count("<collection>")
        if num_doc_element == 0:
            self.fail("Oops, no document element <collection "
                      "xmlns=\"http://www.loc.gov/MARC21/slim\">"
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements <collection> "
                      "found in search results.")

        num_doc_element = body.count("</collection>")
        if num_doc_element == 0:
            self.fail("Oops, no document element </collection> "
                      "found in search results.")
        elif num_doc_element > 1:
            self.fail("Oops, multiple document elements </collection> "
                      "found in search results.")

class WebSearchUnicodeQueryTest(unittest.TestCase):
    """Test of the search results for queries containing Unicode characters."""

    def test_unicode_word_query(self):
        """websearch - Unicode word query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=title%3A%CE%99%CE%B8%CE%AC%CE%BA%CE%B7',
                                               expected_text="[76]"))

    def test_unicode_word_query_not_found_term(self):
        """websearch - Unicode word query, not found term"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?p=title%3A%CE%99%CE%B8',
                                               expected_text="ιθάκη"))

    def test_unicode_exact_phrase_query(self):
        """websearch - Unicode exact phrase query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=title%3A%22%CE%99%CE%B8%CE%AC%CE%BA%CE%B7%22',
                                               expected_text="[76]"))

    def test_unicode_partial_phrase_query(self):
        """websearch - Unicode partial phrase query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=title%3A%27%CE%B7%27',
                                               expected_text="[76]"))

    def test_unicode_regexp_query(self):
        """websearch - Unicode regexp query"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=title%3A%2F%CE%B7%2F',
                                               expected_text="[76]"))

class WebSearchMARCQueryTest(unittest.TestCase):
    """Test of the search results for queries containing physical MARC tags."""

    def test_single_marc_tag_exact_phrase_query(self):
        """websearch - single MARC tag, exact phrase query (100__a)"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=100__a%3A%22Ellis%2C+J%22',
                                               expected_text="[9, 14, 18]"))

    def test_single_marc_tag_partial_phrase_query(self):
        """websearch - single MARC tag, partial phrase query (245__b)"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=245__b%3A%27and%27',
                                               expected_text="[28]"))

    def test_many_marc_tags_partial_phrase_query(self):
        """websearch - many MARC tags, partial phrase query (245)"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=245%3A%27and%27',
                                               expected_text="[1, 8, 9, 14, 15, 20, 22, 24, 28, 33, 47, 48, 49, 51, 53, 64, 69, 71, 79, 82, 83, 85, 91]"))

    def test_single_marc_tag_regexp_query(self):
        """websearch - single MARC tag, regexp query"""
        # NOTE: regexp queries for physical MARC tags (e.g. 245:/and/)
        # are not treated by the search engine by purpose.  But maybe
        # we should support them?!
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?of=id&p=245%3A%2Fand%2F',
                                               expected_text="[]"))

class WebSearchExtSysnoQueryTest(unittest.TestCase):
    """Test of queries using external system numbers."""

    def test_existing_sysno_html_output(self):
        """websearch - external sysno query, existing sysno, HTML output"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?sysno=000289446CER',
                                               expected_text="The wall of the cave"))

    def test_existing_sysno_id_output(self):
        """websearch - external sysno query, existing sysno, ID output"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?sysno=000289446CER&of=id',
                                               expected_text="[95]"))


    def test_nonexisting_sysno_html_output(self):
        """websearch - external sysno query, non-existing sysno, HTML output"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?sysno=000289446CERRRR',
                                               expected_text="Requested record does not seem to exist."))

    def test_nonexisting_sysno_id_output(self):
        """websearch - external sysno query, non-existing sysno, ID output"""
        self.assertEqual([],
                         test_web_page_content(CFG_SITE_URL + '/search?sysno=000289446CERRRR&of=id',
                                               expected_text="[]"))

TEST_SUITE = make_test_suite(WebSearchWebPagesAvailabilityTest,
                             WebSearchTestSearch,
                             WebSearchTestBrowse,
                             WebSearchTestOpenURL,
                             WebSearchTestCollections,
                             WebSearchTestRecord,
                             WebSearchTestLegacyURLs,
                             WebSearchNearestTermsTest,
                             WebSearchBooleanQueryTest,
                             WebSearchAuthorQueryTest,
                             WebSearchSearchEnginePythonAPITest,
                             WebSearchSearchEngineWebAPITest,
                             WebSearchRestrictedCollectionTest,
                             WebSearchRSSFeedServiceTest,
                             WebSearchXSSVulnerabilityTest,
                             WebSearchResultsOverview,
                             WebSearchSortResultsTest,
                             WebSearchSearchResultsXML,
                             WebSearchUnicodeQueryTest,
                             WebSearchMARCQueryTest,
                             WebSearchExtSysnoQueryTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE, warn_user=True)

