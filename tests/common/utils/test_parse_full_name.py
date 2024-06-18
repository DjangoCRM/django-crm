from django.test import SimpleTestCase

from common.utils.parse_full_name import parse_contacts_name
from common.utils.parse_full_name import parse_full_name
from crm.models import Contact
from crm.models import Lead
from crm.models import Request


# manage.py test tests.common.utils.test_parse_full_name


class TestParseFullName(SimpleTestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_no_name(self):
        first_name, middle_name, last_name = parse_full_name("")
        if any((first_name, middle_name, last_name)):
            self.fail()

    def test_first_name_and_last_name(self):
        full_name = "Mark Twain"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Mark")
        self.assertEqual(last_name, "Twain")
        self.assertEqual(middle_name, "")

    def test_full_name(self):
        full_name = """Pablo Diego José Francisco 
        de Paula Juan Nepomuceno Ruiz Picasso"""
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(
            middle_name,
            "Diego José Francisco de Paula Juan Nepomuceno Ruiz"
        )

    def test_obj_contacts_name(self):
        for model in (Contact, Lead, Request):
            obj = model(
                first_name="Pablo Diego José Francisco",
                last_name="de Paula Juan Nepomuceno Ruiz Picasso"
            )
            parse_contacts_name(obj)
            self.assertEqual(obj.first_name, "Pablo")
            self.assertEqual(obj.last_name, "Picasso")
            self.assertEqual(
                obj.middle_name,
                "Diego José Francisco de Paula Juan Nepomuceno Ruiz"
            )

    def test_name_prefix(self):
        full_name = "Mr. Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Mr. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")

        full_name = "Mr Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Mr Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")        
        
        full_name = "mr.Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Mr. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
        
        full_name = "Ms.Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Ms. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")   
        
        full_name = "Mrs.Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Mrs. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
        
        full_name = "Miss Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Miss Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
        
        full_name = "Md. Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Md. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
         
        full_name = "Dr. Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Dr. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
         
        full_name = "PhD. Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "PhD. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
         
        full_name = "Eng. Pablo Picasso"
        first_name, middle_name, last_name = parse_full_name(full_name)
        self.assertEqual(first_name, "Eng. Pablo")
        self.assertEqual(last_name, "Picasso")
        self.assertEqual(middle_name, "")
