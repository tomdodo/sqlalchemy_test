from unittest import TestCase
from sqlalchemy import event
from example import db, dump_results, get_user_companies, get_user_emails, get_user_phones


class TestSqlalchemyQueryLoading(TestCase):

    def setUp(self):
        super(TestSqlalchemyQueryLoading, self).setUp()
        self.emitted_queries = []

    def _activate_query_listener(self):
        def spy_select_statements(
                conn, cursor, statement, parameters, context, executemany):
            self.emitted_queries.append({
                'statement': statement,
                'parameters': parameters,
                'full': statement % parameters
            })
        event.listen(
            db.connection().engine,
            'before_cursor_execute', spy_select_statements)
        # commit necessary otherwise the listener does not activate
        db.commit()

    def test_get_user_companies(self):
        self._activate_query_listener()

        results = get_user_companies()

        dump_results(results)
        self.assertIn(
            {
                'name': u"Tommaso D'Odorico",
                'company_name': u'Zinc co.'
            }, results)
        self.assertIn(
            {
                'name': u'Iain Brown',
                'company_name': u'Cobalt co.'
            }, results)

        # self.assertEquals(1, len(self.emitted_queries))

    def test_get_user_emails(self):
        self._activate_query_listener()

        results = get_user_emails()
        dump_results(results)

        self.assertIn(
            {
                'name': u"Tommaso D'Odorico",
                'emails': [
                    {'type': u'home', 'email': u'tommaso.dodorico@gmail.com'},
                    {'type': u'work', 'email': u'tod@getadministrate.com'}
                ]
            }, results)
        self.assertIn(
            {
                'name': u'Peter Beckham',
                'emails': [
                    {'type': u'work', 'email': u'pcb@getadministrate.com'}
                ]
            }, results)

        # self.assertEquals(1, len(self.emitted_queries))

    def test_get_user_phones_all_types(self):
        self._activate_query_listener()

        results = get_user_phones()
        dump_results(results)

        self.assertIn(
            {
                'name': u"Tommaso D'Odorico",
                'phones': [
                    {'phone_number': u'111 111 1111', 'type': u'home'},
                    {'phone_number': u'222 222 2222', 'type': u'work'}
                ]
            }, results)
        self.assertIn(
            {
                'name': u'Gordon Coupar',
                'phones': [
                    {'phone_number': u'333 333 3333', 'type': u'work'}
                ]
            }, results)

        # self.assertEquals(2, len(self.emitted_queries))

    def test_get_user_phones_home_only(self):
        self._activate_query_listener()

        results = get_user_phones(phone_type='home')
        dump_results(results)

        self.assertIn(
            {
                'name': u"Tommaso D'Odorico",
                'phones': [
                    {'phone_number': u'111 111 1111', 'type': u'home'}
                ]
            }, results)
        self.assertIn(
            {
                'name': u'David Gentles',
                'phones': []
            }, results)
