from django.test import TestCase
from auctions.forms import CommentForm

class TestForms(TestCase):

    def testCommentFormValid(self):
        testForm = CommentForm(data={
            "content": "TestContent",
        })

        self.assertTrue(testForm.is_valid())

    def testCommentFormInvalid(self):
        testForm = CommentForm(data={})

        self.assertFalse(testForm.is_valid())
        self.assertEquals(len(testForm.errors), 1)