import sys
sys.path.append("listable-demo")

import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.test import Client, TestCase
from django.test.utils import override_settings

from mock import Mock

from staff.views import StaffList
from staff.models import Staff, INACTIVE, GenericModelA, GenericModelB
from listable import utils


class TestViews(TestCase):

    fixtures = ["initial_data.json"]

    def test_basic_get(self):
        client = Client()
        response = client.get(reverse("staff-list"))
        self.assertEqual(response.status_code, 200)

    def test_data_load(self):
        # full query = "sEcho=1&iColumns=8&sColumns=&iDisplayStart=10&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=0&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&_=1414439607636"
        client = Client()
        num_records = 23
        response = client.get(reverse("staff-list")+"?sEcho=1&iColumns=8&sColumns=&iDisplayStart=1&iDisplayLength={0}".format(num_records),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        payload = json.loads(response.content)
        data = payload.pop("aaData")
        self.assertEqual(len(data), num_records)
        self.assertEqual(payload['iTotalRecords'], Staff.objects.count())

    def test_filter_select(self):
        """Test filtering based on a select widget"""

        client = Client()
        url = reverse("staff-list")+"?sEcho=1&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=inactive&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=0&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607637"
        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        num_records = Staff.objects.filter(active=INACTIVE).count()
        self.assertEqual(len(data), num_records)

    def test_filter_extra_select(self):
        """Test filtering based on a extra clause (e.g. for Generic Foreign Key content)"""

        client = Client()
        search_term =  "a3"
        url = reverse("staff-list")+"?sEcho=1&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7={search_term}&bRegex_7=false&bSearchable_7=true&iSortingCols=0&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607640".format(search_term=search_term)
        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        num_records = len([1 for s in Staff.objects.all() if search_term in s.generic_object.name.lower()])

        self.assertTrue(len(data) > 0)
        self.assertEqual(payload["iTotalDisplayRecords"], num_records)


    def test_filter_plain(self):
        """Test filtering based on a plain text input"""

        client = Client()
        search_term =  "Amet"
        url = reverse("staff-list")+"?sEcho=1&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3={search_term}&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=0&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607643".format(search_term=search_term)

        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        num_records = Staff.objects.filter(department__name=search_term).count()

        self.assertTrue(len(data) > 0)
        self.assertEqual(payload["iTotalDisplayRecords"], num_records)


    def test_filter_iterable(self):
        """Test filtering based on a plain text input"""

        client = Client()
        search_term =  "Abbott"
        url = reverse("staff-list")+"?sEcho=19&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1={search_term}&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=0&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607645".format(search_term=search_term)

        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        num_records = Staff.objects.filter(last_name=search_term).count()

        self.assertTrue(len(data) > 0)
        self.assertEqual(payload["iTotalDisplayRecords"], num_records)

    def test_order_basic_with_search(self):
        """Test basic ordered results with a filter"""

        client = Client()
        search_term =  "Maiores"
        url = reverse("staff-list")+"?sEcho=19&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4={search_term}&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607645".format(search_term=search_term)

        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        pks = Staff.objects.filter(position__name__icontains=search_term).order_by('-pk').values_list("pk", flat=True)[:settings.LISTABLE_PAGINATE_BY]
        payload_pks= [int(x[0]) for x in data]

        self.assertListEqual(list(pks), payload_pks)


    def test_order_iterable_with_search(self):
        """Test that filtering fails"""

        client = Client()
        search_term =  "Maiores"
        url = reverse("staff-list")+"?sEcho=19&iColumns=8&sColumns=&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4={search_term}&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&iSortingCols=1&iSortCol_0=1&sSortDir_0=asc&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&sRangeSeparator=~&_=1414439607645".format(search_term=search_term)

        response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        payload = json.loads(response.content)
        data = payload.pop("aaData")
        staff = Staff.objects.filter(position__name__icontains=search_term).order_by('last_name',"first_name")[:settings.LISTABLE_PAGINATE_BY]
        names = [s.name() for s in staff]

        payload_names = [x[1] for x in data]


        self.assertListEqual(names, payload_names)
